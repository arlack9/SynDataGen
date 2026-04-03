// Schema Upload Component
function loadSchemaUpload() {
    const schemaHTML = `
        <div class="schema-section">
            <h3>📁 Schema Upload (Optional - Online Mode Only)</h3>
            <p>Upload schema files or connect to SQL Server to enhance data generation with your specific structure.</p>
            
            <div class="schema-tabs">
                <button class="schema-tab active" onclick="switchSchemaTab('file')">📄 File Upload</button>
                <button class="schema-tab" onclick="switchSchemaTab('sql')">🗄️ SQL Server</button>
            </div>
            
            <!-- File Upload Tab -->
            <div class="schema-content active" id="schema-file">
                <div id="file-upload-container"></div>
            </div>
            
            <!-- SQL Server Tab -->
            <div class="schema-content" id="schema-sql">
                <div id="sql-server-container"></div>
            </div>
            
            <!-- Schema Preview -->
            <div id="schema-preview" class="schema-preview" style="display:none;">
                <strong style="font-size:0.85rem;">Schema Preview:</strong><br>
                <div id="schema-preview-content"></div>
            </div>
            
            <!-- Include Schema Checkbox -->
            <div style="margin-top:1rem;">
                <label>
                    <input type="checkbox" id="include-schema" style="width:auto; margin-right:0.5rem;" checked>
                    <strong>Include schema in data generation</strong>
                </label>
                <p style="margin:0.5rem 0 0 1.5rem; font-size:0.85rem; color:#666;">
                    When checked, the uploaded schema will be used to guide data generation. 
                    Uncheck to generate data without schema constraints.
                </p>
            </div>
        </div>
    `;
    
    const schemaContainer = document.getElementById('schema-upload-container');
    if (schemaContainer) {
        schemaContainer.innerHTML = schemaHTML;
    }
}

// Schema tab switching function
function switchSchemaTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.schema-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`button[onclick="switchSchemaTab('${tab}')"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.schema-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`schema-${tab}`).classList.add('active');
    
    // Clear schema context when switching tabs
    if (window.clearSchemaPreview) {
        window.clearSchemaPreview();
    }
}

// Load schema upload when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadSchemaUpload);
} else {
    loadSchemaUpload();
}
