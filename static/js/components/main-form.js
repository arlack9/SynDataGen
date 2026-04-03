// Main Form Component
function loadMainForm() {
    const formHTML = `
        <form id="data-form" method="POST" autocomplete="off" enctype="multipart/form-data">
            <div class="form-group">
                <label for="prompt">Your Prompt:</label>
                <textarea id="prompt" name="prompt"
                          placeholder="e.g., Generate 20 restaurants with name, cuisine, rating and location&#10;&#10;Generate 100 hotels with name, location, rating and price per night&#10;&#10;Generate 50 insurance agencies with agency name, location, services offered"
                          required></textarea>
            </div>

            <div class="form-group">
                <label for="mode">Generation Mode:</label>
                <select id="mode" name="mode">
                    <option value="online">Online (OpenRouter API)</option>
                    <option value="gemini">Gemini (Google AI Studio)</option>
                </select>
            </div>

            <div class="form-group" id="template-group" style="display:none;">
                <label for="template">Template Data (Optional):</label>
                <textarea id="template" name="template"
                          placeholder="Provide 2-3 example rows to help the model understand your data structure:&#10;&#10;For Hotels (CSV):&#10;name,location,rating,price_per_night&#10;The Grand Palace Hotel,New York,4.5,250&#10;Ocean View Resort,Miami,4.2,180&#10;&#10;For Restaurants (JSON):&#10;{&quot;name&quot;: &quot;Crab Foods Restaurant&quot;, &quot;cuisine&quot;: &quot;Seafood&quot;, &quot;rating&quot;: 4.3, &quot;location&quot;: &quot;Boston&quot;}&#10;{&quot;name&quot;: &quot;Indian Spice Palace&quot;, &quot;cuisine&quot;: &quot;Indian&quot;, &quot;rating&quot;: 4.6, &quot;location&quot;: &quot;Chicago&quot;}"
                          style="height:120px;"></textarea>
                <small style="color:#666; font-size:0.85rem;">
                    💡 Tip: Use specific business names like "Crab Foods", "Sea Breeze Cafe", "Golden Dragon Restaurant" to help the AI understand the domain better
                </small>
            </div>

            <div class="form-group" id="format-group">
                <label for="format">Output Format:</label>
                <select id="format" name="format">
                    <option value="csv">CSV</option>
                    <option value="json">JSON</option>
                </select>
            </div>

            <!-- Hidden input for schema context -->
            <input type="hidden" id="schema-context" name="schema-context" value="">

            <button id="submit-btn" type="submit">
                Generate and Download CSV
            </button>
        </form>
    `;
    
    const formContainer = document.getElementById('main-form-container');
    if (formContainer) {
        formContainer.innerHTML = formHTML;
    }
}

// Load form when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadMainForm);
} else {
    loadMainForm();
}
