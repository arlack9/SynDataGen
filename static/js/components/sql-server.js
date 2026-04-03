// SQL Server Component
function loadSQLServer() {
    const sqlHTML = `
        <div class="sql-form">
            <input type="text" id="sql-server" placeholder="Server (e.g., localhost)" />
            <input type="text" id="sql-database" placeholder="Database name" />
            <input type="text" id="sql-schema" placeholder="Schema (default: dbo)" value="dbo" />
            <select id="sql-auth-type">
                <option value="windows">Windows Authentication</option>
                <option value="sql">SQL Server Authentication</option>
            </select>
            <input type="text" id="sql-username" placeholder="Username (SQL Auth only)" style="display:none;" />
            <input type="password" id="sql-password" placeholder="Password (SQL Auth only)" style="display:none;" />
        </div>
        
        <div style="margin-bottom:1rem;">
            <button type="button" class="btn-small btn-secondary" onclick="testSqlConnection()">🔌 Test Connection</button>
            <button type="button" class="btn-small btn-secondary" onclick="loadSqlTables()">📋 Load Tables</button>
            <button type="button" class="btn-small btn-secondary" onclick="generateSqlSchema()">✨ Generate Schema</button>
            <button type="button" class="btn-small btn-secondary" onclick="clearSqlSchema()">🗑️ Clear</button>
        </div>
        
        <div class="tables-list" id="sql-tables-list" style="display:none;">
            <p style="margin:0 0 0.5rem 0; font-weight:600;">Select tables:</p>
        </div>
        
        <label>
            <input type="checkbox" id="include-sample-data" style="width:auto; margin-right:0.5rem;">
            Include sample data (may be slow for large tables)
        </label>
    `;
    
    const sqlContainer = document.getElementById('sql-server-container');
    if (sqlContainer) {
        sqlContainer.innerHTML = sqlHTML;
        
        // Add event listeners
        const sqlAuthType = document.getElementById('sql-auth-type');
        const sqlUsername = document.getElementById('sql-username');
        const sqlPassword = document.getElementById('sql-password');
        
        if (sqlAuthType) {
            sqlAuthType.addEventListener('change', function() {
                const isSQL = this.value === 'sql';
                if (sqlUsername) sqlUsername.style.display = isSQL ? 'block' : 'none';
                if (sqlPassword) sqlPassword.style.display = isSQL ? 'block' : 'none';
            });
        }
    }
}

// SQL Server functions
let selectedTables = [];

async function testSqlConnection() {
    const server = document.getElementById('sql-server').value || '';
    const database = document.getElementById('sql-database').value || '';
    const useWindowsAuth = document.getElementById('sql-auth-type').value === 'windows';
    const username = document.getElementById('sql-username').value || '';
    const password = document.getElementById('sql-password').value || '';
    
    // Validate inputs
    if (!server.trim() || !database.trim()) {
        alert('Please enter server and database name.');
        return;
    }
    
    // Prepare data
    const requestData = {
        server: server.trim(),
        database: database.trim(),
        use_windows_auth: useWindowsAuth
    };
    
    // Only add username/password if using SQL Server auth
    if (!useWindowsAuth) {
        if (!username.trim() || !password.trim()) {
            alert('Please enter username and password for SQL Server authentication.');
            return;
        }
        requestData.username = username.trim();
        requestData.password = password.trim();
    }
    
    try {
        if (window.showStatus) {
            window.showStatus('Testing SQL Server connection...', 'info');
        }
        
        console.log('Testing SQL connection with:', requestData);
        
        const response = await fetch('/api/sql-server/test-connection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        console.log('SQL connection test response:', data);
        
        if (data.success) {
            if (window.showStatus) {
                window.showStatus('✅ Connection successful! ' + data.message, 'success');
            }
        } else {
            if (window.showStatus) {
                window.showStatus('❌ Connection failed: ' + data.error, 'error');
            }
        }
        
    } catch (error) {
        console.error('SQL connection test error:', error);
        if (window.showStatus) {
            window.showStatus('❌ Error: ' + error.message, 'error');
        }
    }
}

async function loadSqlTables() {
    const server = document.getElementById('sql-server').value || '';
    const database = document.getElementById('sql-database').value || '';
    const schemaName = document.getElementById('sql-schema').value || 'dbo';
    const useWindowsAuth = document.getElementById('sql-auth-type').value === 'windows';
    const username = document.getElementById('sql-username').value || '';
    const password = document.getElementById('sql-password').value || '';
    
    if (!server.trim() || !database.trim()) {
        alert('Please enter server and database name.');
        return;
    }
    
    // Prepare data
    const requestData = {
        server: server.trim(),
        database: database.trim(),
        schema_name: schemaName.trim(),
        use_windows_auth: useWindowsAuth
    };
    
    // Only add username/password if using SQL Server auth
    if (!useWindowsAuth) {
        if (!username.trim() || !password.trim()) {
            alert('Please enter username and password for SQL Server authentication.');
            return;
        }
        requestData.username = username.trim();
        requestData.password = password.trim();
    }
    
    try {
        if (window.showStatus) {
            window.showStatus('Loading tables...', 'info');
        }
        
        console.log('Loading SQL tables with:', requestData);
        
        const response = await fetch('/api/sql-server/tables', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        console.log('SQL tables response:', data);
        
        if (data.success) {
            displayTables(data.tables);
            if (window.showStatus) {
                window.showStatus(`✅ Loaded ${data.tables.length} tables`, 'success');
            }
        } else {
            if (window.showStatus) {
                window.showStatus('❌ Failed to load tables: ' + data.error, 'error');
            }
        }
        
    } catch (error) {
        console.error('SQL tables loading error:', error);
        if (window.showStatus) {
            window.showStatus('❌ Error loading tables: ' + error.message, 'error');
        }
    }
}

function displayTables(tables) {
    const tablesList = document.getElementById('sql-tables-list');
    if (!tablesList) return;
    
    tablesList.innerHTML = '<p style="margin:0 0 0.5rem 0; font-weight:600;">Select tables:</p>';
    
    tables.forEach(table => {
        const div = document.createElement('div');
        div.className = 'table-item';
        div.textContent = table;
        div.onclick = () => toggleTableSelection(div, table);
        tablesList.appendChild(div);
    });
    
    tablesList.style.display = 'block';
    selectedTables = [];
}

function toggleTableSelection(element, tableName) {
    element.classList.toggle('selected');
    
    if (selectedTables.includes(tableName)) {
        selectedTables = selectedTables.filter(t => t !== tableName);
    } else {
        selectedTables.push(tableName);
    }
}

async function generateSqlSchema() {
    if (selectedTables.length === 0) {
        alert('Please select at least one table.');
        return;
    }
    
    const server = document.getElementById('sql-server').value || '';
    const database = document.getElementById('sql-database').value || '';
    const schemaName = document.getElementById('sql-schema').value || 'dbo';
    const useWindowsAuth = document.getElementById('sql-auth-type').value === 'windows';
    const username = document.getElementById('sql-username').value || '';
    const password = document.getElementById('sql-password').value || '';
    const includeSampleData = document.getElementById('include-sample-data').checked;
    
    if (!server.trim() || !database.trim()) {
        alert('Please enter server and database name.');
        return;
    }
    
    // Prepare data
    const requestData = {
        server: server.trim(),
        database: database.trim(),
        schema_name: schemaName.trim(),
        tables: selectedTables,
        include_sample_data: includeSampleData,
        use_windows_auth: useWindowsAuth
    };
    
    // Only add username/password if using SQL Server auth
    if (!useWindowsAuth) {
        if (!username.trim() || !password.trim()) {
            alert('Please enter username and password for SQL Server authentication.');
            return;
        }
        requestData.username = username.trim();
        requestData.password = password.trim();
    }
    
    try {
        if (window.showStatus) {
            window.showStatus('Generating schema context...', 'info');
        }
        
        console.log('Generating SQL schema with:', requestData);
        
        const response = await fetch('/api/sql-server/schema', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        console.log('SQL schema generation response:', data);
        
        if (data.success) {
            if (window.showSchemaPreview) {
                window.showSchemaPreview(data.schema_context);
            }
            if (window.showStatus) {
                window.showStatus('✅ Schema context generated successfully!', 'success');
            }
        } else {
            if (window.showStatus) {
                window.showStatus('❌ Schema generation failed: ' + data.error, 'error');
            }
        }
        
    } catch (error) {
        console.error('SQL schema generation error:', error);
        if (window.showStatus) {
            window.showStatus('❌ Error: ' + error.message, 'error');
        }
    }
}

function clearSqlSchema() {
    const tablesList = document.getElementById('sql-tables-list');
    if (tablesList) {
        tablesList.style.display = 'none';
    }
    selectedTables = [];
    if (window.clearSchemaPreview) {
        window.clearSchemaPreview();
    }
}

// Load SQL Server when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadSQLServer);
} else {
    loadSQLServer();
}
