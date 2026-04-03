// Main JavaScript Controller
// Global variables
let schemaContext = '';
let isGenerating = false;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Main app initializing...');
    
    // Load all components
    loadHeader();
    loadMainForm();
    loadSchemaUpload();
    
    // Initialize event listeners
    initializeEventListeners();
    
    console.log('Main app initialized');
});

function initializeEventListeners() {
    // Schema uploader toggle
    const schemaToggle = document.getElementById('schema-toggle');
    const schemaUploader = document.getElementById('schema-uploader');
    
    if (schemaToggle && schemaUploader) {
        schemaToggle.addEventListener('change', function() {
            schemaUploader.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // Include schema checkbox
    const includeSchema = document.getElementById('include-schema');
    if (includeSchema) {
        includeSchema.addEventListener('change', function() {
            console.log('Include schema:', this.checked);
        });
    }
    
    // Form submission
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateData);
    }
    
    // Export format change
    const exportFormat = document.getElementById('export-format');
    if (exportFormat) {
        exportFormat.addEventListener('change', function() {
            console.log('Export format changed to:', this.value);
        });
    }
    
    // Row count input validation
    const rowCountInput = document.getElementById('row-count');
    if (rowCountInput) {
        rowCountInput.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (value < 1) this.value = 1;
            if (value > 1000) this.value = 1000;
        });
    }
}

// Status display functions
function showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('status');
    if (!statusDiv) return;
    
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.style.display = 'block';
    
    // Auto-hide success/info messages after 5 seconds
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}

function hideStatus() {
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        statusDiv.style.display = 'none';
    }
}

// Schema preview functions
function showSchemaPreview(schema) {
    schemaContext = schema;
    const preview = document.getElementById('schema-preview');
    if (preview) {
        preview.textContent = schema;
        preview.style.display = 'block';
    }
    console.log('Schema context set:', schema.substring(0, 200) + '...');
}

function clearSchemaPreview() {
    schemaContext = '';
    const preview = document.getElementById('schema-preview');
    if (preview) {
        preview.textContent = '';
        preview.style.display = 'none';
    }
    console.log('Schema context cleared');
}

// Form validation
function validateForm() {
    const prompt = document.getElementById('prompt').value.trim();
    const rowCount = parseInt(document.getElementById('row-count').value);
    
    if (!prompt) {
        showStatus('❌ Please enter a data generation prompt', 'error');
        return false;
    }
    
    if (rowCount < 1 || rowCount > 1000) {
        showStatus('❌ Row count must be between 1 and 1000', 'error');
        return false;
    }
    
    return true;
}

// Main data generation function
async function generateData() {
    if (isGenerating) {
        console.log('Generation already in progress');
        return;
    }
    
    if (!validateForm()) {
        return;
    }
    
    isGenerating = true;
    const generateBtn = document.getElementById('generate-btn');
    const originalText = generateBtn ? generateBtn.textContent : '';
    
    try {
        // Update UI
        if (generateBtn) {
            generateBtn.textContent = '⏳ Generating...';
            generateBtn.disabled = true;
        }
        
        showStatus('🚀 Starting data generation...', 'info');
        
        // Collect form data
        const formData = collectFormData();
        console.log('Form data collected:', formData);
        
        // Make API call
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        console.log('API response:', data);
        
        if (data.success) {
            showStatus('✅ Data generated successfully!', 'success');
            displayResults(data);
        } else {
            // Handle different types of API errors with appropriate messages and icons
            let errorMessage = '';
            let errorIcon = '❌';
            
            switch(data.error_type) {
                case 'API_KEY_INVALID':
                    errorIcon = '🔑';
                    errorMessage = `${errorIcon} Invalid API Key: ${data.error}`;
                    break;
                case 'RATE_LIMIT':
                    errorIcon = '⏱️';
                    errorMessage = `${errorIcon} Rate Limited: ${data.error}`;
                    // Add model information if available
                    if (data.model_used) {
                        errorMessage += ` (Model: ${data.model_used})`;
                    }
                    break;
                case 'QUOTA_EXCEEDED':
                    errorIcon = '💳';
                    errorMessage = `${errorIcon} Quota Exceeded: ${data.error}`;
                    break;
                case 'ACCESS_FORBIDDEN':
                    errorIcon = '🚫';
                    errorMessage = `${errorIcon} Access Denied: ${data.error}`;
                    break;
                case 'NETWORK_ERROR':
                    errorIcon = '🌐';
                    errorMessage = `${errorIcon} Network Error: ${data.error}`;
                    break;
                case 'MODEL_ERROR':
                    errorIcon = '🤖';
                    errorMessage = `${errorIcon} Model Error: ${data.error}`;
                    if (data.model_used) {
                        errorMessage += ` Current model: ${data.model_used}`;
                    }
                    break;
                case 'API_ERROR':
                    errorIcon = '⚠️';
                    errorMessage = `${errorIcon} API Error: ${data.error}`;
                    break;
                default:
                    errorMessage = `❌ Generation failed: ${data.error || 'Unknown error'}`;
            }
            
            showStatus(errorMessage, 'error');
            
            // Store technical details for later display
            if (data.technical_details) {
                window.lastErrorDetails = {
                    type: data.error_type,
                    message: data.error,
                    technical: data.technical_details,
                    model: data.model_used,
                    timestamp: data.timestamp
                };
            }
            
            // For certain errors, show additional help text with action buttons
            if (data.error_type === 'API_KEY_INVALID') {
                setTimeout(() => {
                    showStatus('💡 Check your .env file and ensure OPENROUTER_API_KEY is set correctly', 'info');
                }, 2000);
            } else if (data.error_type === 'RATE_LIMIT') {
                let helpMessage = '💡 Rate limit suggestions: ';
                if (data.technical_details && data.technical_details.includes('free')) {
                    helpMessage += 'Consider upgrading your plan or trying a different model';
                } else {
                    helpMessage += 'Wait a few moments before trying again';
                }
                setTimeout(() => {
                    showStatus(helpMessage, 'info');
                }, 2000);
                
                // Show technical details button for rate limits
                setTimeout(() => {
                    addTechnicalDetailsButton();
                }, 3000);
            } else if (data.error_type === 'MODEL_ERROR') {
                setTimeout(() => {
                    showStatus('💡 Try switching to a different AI model in your .env file (MODEL_ID)', 'info');
                }, 2000);
            }
        }
        
    } catch (error) {
        console.error('Generation error:', error);
        showStatus('❌ Error: ' + error.message, 'error');
    } finally {
        // Reset UI
        isGenerating = false;
        if (generateBtn) {
            generateBtn.textContent = originalText;
            generateBtn.disabled = false;
        }
    }
}

function collectFormData() {
    const prompt = document.getElementById('prompt').value.trim();
    const rowCount = parseInt(document.getElementById('row-count').value);
    const exportFormat = document.getElementById('export-format').value;
    const includeSchema = document.getElementById('include-schema').checked;
    
    const formData = {
        prompt: prompt,
        row_count: rowCount,
        export_format: exportFormat,
        mode: 'online' // Fixed to online mode as requested
    };
    
    // Add schema context if enabled and available
    if (includeSchema && schemaContext) {
        formData.schema_context = schemaContext;
        console.log('Including schema context in request');
    }
    
    return formData;
}

function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    if (!resultsDiv) return;
    
    let resultsHTML = '<div class="results-container">';
    
    // Add download link if file was generated
    if (data.file_path) {
        const filename = data.file_path.split('/').pop();
        resultsHTML += `
            <div class="download-section">
                <h3>📁 Generated File</h3>
                <a href="/output/${filename}" download="${filename}" class="btn btn-primary">
                    📥 Download ${filename}
                </a>
            </div>
        `;
    }
    
    // Show preview of generated data
    if (data.preview_data) {
        resultsHTML += `
            <div class="preview-section">
                <h3>👁️ Data Preview</h3>
                <pre class="data-preview">${data.preview_data}</pre>
            </div>
        `;
    }
    
    // Show generation stats
    if (data.generation_time || data.rows_generated) {
        resultsHTML += '<div class="stats-section"><h3>📊 Generation Stats</h3>';
        if (data.rows_generated) {
            resultsHTML += `<p>Rows generated: <strong>${data.rows_generated}</strong></p>`;
        }
        if (data.generation_time) {
            resultsHTML += `<p>Generation time: <strong>${data.generation_time}s</strong></p>`;
        }
        resultsHTML += '</div>';
    }
    
    resultsHTML += '</div>';
    
    resultsDiv.innerHTML = resultsHTML;
    resultsDiv.style.display = 'block';
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

// Make functions available globally for component access
function addTechnicalDetailsButton() {
    const statusDiv = document.getElementById('status');
    if (statusDiv && window.lastErrorDetails) {
        const detailsButton = document.createElement('button');
        detailsButton.textContent = '🔍 Show Technical Details';
        detailsButton.style.cssText = 'margin-top: 10px; padding: 5px 10px; background: #3182ce; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85rem;';
        detailsButton.onclick = showTechnicalDetails;
        
        // Remove any existing button
        const existingButton = statusDiv.querySelector('button');
        if (existingButton) {
            existingButton.remove();
        }
        
        statusDiv.appendChild(detailsButton);
    }
}

function showTechnicalDetails() {
    if (!window.lastErrorDetails) return;
    
    const details = window.lastErrorDetails;
    const detailsHtml = `
        <div style="background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; margin-top: 10px; font-family: monospace; font-size: 0.8rem;">
            <h4 style="margin: 0 0 10px 0; color: #2d3748;">Technical Error Details</h4>
            <div><strong>Error Type:</strong> ${details.type}</div>
            <div><strong>Model:</strong> ${details.model || 'Unknown'}</div>
            <div><strong>Timestamp:</strong> ${details.timestamp || 'Unknown'}</div>
            <div style="margin-top: 10px;"><strong>Full Error:</strong></div>
            <div style="background: #edf2f7; padding: 8px; border-radius: 4px; margin-top: 5px; word-break: break-all; max-height: 200px; overflow-y: auto;">${details.technical}</div>
            <div style="margin-top: 10px; font-size: 0.75rem; color: #666;">
                💡 Share this information with support if you need help debugging the issue.
            </div>
        </div>
    `;
    
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        statusDiv.innerHTML = `
            <div style="color: #c53030;">🔍 Technical Error Details</div>
            ${detailsHtml}
            <button onclick="hideTechnicalDetails()" style="margin-top: 10px; padding: 5px 10px; background: #718096; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85rem;">Hide Details</button>
        `;
        statusDiv.className = 'status info';
    }
}

function hideTechnicalDetails() {
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        statusDiv.style.display = 'none';
    }
}

// Make functions globally available
window.showStatus = showStatus;
window.showTechnicalDetails = showTechnicalDetails;
window.hideTechnicalDetails = hideTechnicalDetails;
window.hideStatus = hideStatus;
window.showSchemaPreview = showSchemaPreview;
window.clearSchemaPreview = clearSchemaPreview;
window.generateData = generateData;

console.log('Main controller script loaded');
