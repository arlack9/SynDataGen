// File Upload Component
function loadFileUpload() {
    const fileUploadHTML = `
        <div class="file-input">
            <input type="file" id="schema-file-input" accept=".csv,.json,.sql,.txt" style="margin-bottom:0.5rem;">
            <p style="margin:0; font-size:0.9rem; color:#666;">
                Upload CSV, JSON, SQL, or TXT files (max 2MB)<br>
                📊 CSV: Column headers and sample data<br>
                🔧 JSON: Data structure examples<br>
                🗃️ SQL: Database schema/CREATE statements
            </p>
        </div>
        <button type="button" class="btn-small btn-secondary" onclick="clearFileSchema()">Clear File</button>
    `;
    
    const fileContainer = document.getElementById('file-upload-container');
    if (fileContainer) {
        fileContainer.innerHTML = fileUploadHTML;
        
        // Add event listener for file input
        const fileInput = document.getElementById('schema-file-input');
        if (fileInput) {
            fileInput.addEventListener('change', handleFileUpload);
        }
    }
}

// File upload handling
function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate file
    const allowedTypes = ['text/csv', 'application/json', 'text/plain', 'application/sql'];
    const allowedExts = ['.csv', '.json', '.sql', '.txt'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedExts.includes(fileExt)) {
        alert('Please upload CSV, JSON, SQL, or TXT files only.');
        e.target.value = '';
        return;
    }
    
    if (file.size > 2 * 1024 * 1024) {
        alert('File size must be less than 2MB.');
        e.target.value = '';
        return;
    }
    
    // Read and preview file
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        let context = `File: ${file.name}\n\n${content}`;
        if (window.showSchemaPreview) {
            window.showSchemaPreview(context);
        }
    };
    reader.readAsText(file);
}

function clearFileSchema() {
    const fileInput = document.getElementById('schema-file-input');
    if (fileInput) {
        fileInput.value = '';
    }
    if (window.clearSchemaPreview) {
        window.clearSchemaPreview();
    }
}

// Load file upload when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadFileUpload);
} else {
    loadFileUpload();
}
