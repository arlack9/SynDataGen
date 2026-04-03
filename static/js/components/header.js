// Header Component
function loadHeader() {
    const headerHTML = `
        <h1>Synthetic Data Generator</h1>
        <p>Enter a prompt, choose your mode and desired format, and get your synthetic data.</p>
    `;
    
    const headerContainer = document.getElementById('header-container');
    if (headerContainer) {
        headerContainer.innerHTML = headerHTML;
    }
}

// Load header when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadHeader);
} else {
    loadHeader();
}
