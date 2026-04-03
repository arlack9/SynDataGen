from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import traceback
import pandas as pd
import numpy as np
import json
from datetime import datetime

from api.api_client import OpenRouterClient
from api.julius_analytics import JuliusAnalytics

# Import Gemini client with error handling
try:
    from api.gemini_client import GeminiClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("WARNING: Gemini client not available. Install google-generativeai to enable Gemini support.")
from parser.data_parser import parse_llm_output
from uploads.schema_validator import SchemaValidator
from uploads.schema_validator import get_sql_server_schema as extract_sql_server_schema, list_sql_server_tables
from analytics.data_analyzer import DataAnalyzer
from analytics.visualization_engine import VisualizationEngine
from analytics.insights_generator import InsightsGenerator
from analytics.ai_analytics import AIAnalytics

OUTPUT_DIR = "output"
TEMPLATES_DIR = "templates"
UPLOAD_DIR = "uploads"

class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, np.dtype):
            return str(obj)
        elif hasattr(obj, 'dtype') and hasattr(obj, 'item'):
            # Handle pandas/numpy scalar types
            try:
                return obj.item()
            except (ValueError, TypeError):
                return str(obj)
        elif pd.isna(obj):
            return None
        elif hasattr(obj, '__dict__'):
            # Handle complex objects by converting to string
            try:
                return str(obj)
            except:
                return None
        return super().default(obj)

def convert_numpy_types(obj):
    """Recursively convert numpy types to Python native types"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.dtype):
        return str(obj)
    elif hasattr(obj, 'dtype') and hasattr(obj, 'item'):
        # Handle pandas/numpy scalar types
        try:
            return obj.item()
        except (ValueError, TypeError):
            return str(obj)
    elif pd.isna(obj):
        return None
    elif hasattr(obj, '__dict__'):
        # Handle objects with attributes
        try:
            return str(obj)
        except:
            return None
    return obj

def extract_keywords_from_prompt(text):
    """Extract meaningful keywords from user prompt for filename generation."""
    if not text:
        return "data"
    
    import re
    
    # Convert to lowercase for processing
    text_lower = text.lower()
    
    # Remove common words and extract meaningful keywords
    common_words = {'generate', 'create', 'make', 'give', 'me', 'a', 'an', 'the', 'with', 'and', 'or', 'of', 'for', 'in', 'on', 'at', 'to', 'from', 'by', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall', 'need', 'want', 'like', 'rows', 'data', 'dataset', 'table', 'records', 'entries', 'list', 'some', 'any', 'all', 'each', 'every', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
    
    # Extract words (alphanumeric sequences)
    words = re.findall(r'\b[a-zA-Z0-9]+\b', text_lower)
    
    # Filter out common words and keep meaningful ones
    keywords = [word for word in words if word not in common_words and len(word) > 2]
    
    # Take first 3-4 meaningful keywords
    meaningful_keywords = keywords[:4]
    
    # If no meaningful keywords found, try to extract numbers + nouns
    if not meaningful_keywords:
        # Look for patterns like "20 restaurants", "50 users", etc.
        patterns = re.findall(r'(\d+)\s+([a-zA-Z]+)', text)
        if patterns:
            num, noun = patterns[0]
            meaningful_keywords = [num, noun]
        else:
            # Fallback to first few words (excluding very common ones)
            words_filtered = [w for w in words if w not in {'generate', 'create', 'give', 'me', 'make'}]
            meaningful_keywords = words_filtered[:3] if words_filtered else ['data']
    
    return '_'.join(meaningful_keywords[:4]) if meaningful_keywords else 'data'

def sanitize_filename(text):
    """Sanitize text for use in filename by removing/replacing invalid characters."""
    if not text:
        return "data"
    
    # Replace or remove invalid filename characters
    safe_text = (text.replace(' ', '_')
                    .replace('/', '_')
                    .replace('\\', '_')
                    .replace('"', '')
                    .replace("'", "")
                    .replace('%', 'pct')
                    .replace(',', '_')
                    .replace('?', '')
                    .replace(':', '_')
                    .replace('*', '')
                    .replace('<', '')
                    .replace('>', '')
                    .replace('|', '_')
                    .replace('&', '_')
                    .replace('\n', '_')
                    .replace('\r', '_')
                    .replace('\t', '_'))
    
    # Remove any remaining non-ASCII characters and limit length
    safe_text = ''.join(c for c in safe_text if ord(c) < 128)[:50]
    
    # Return sanitized text or fallback to "data"
    return safe_text if safe_text.strip() else "data"
    

def extract_chartjs_configs(visualization_suite):
    """Extract all Chart.js configurations from visualization suite for easy rendering"""
    configs = {}
    
    try:
        # Extract from summary dashboard
        if 'summary_dashboard' in visualization_suite:
            dashboard = visualization_suite['summary_dashboard']
            if 'quick_stats' in dashboard and 'config' in dashboard['quick_stats']:
                configs['quick_stats'] = dashboard['quick_stats']['config']
        
        # Extract from demographic charts
        if 'demographic_charts' in visualization_suite and 'charts' in visualization_suite['demographic_charts']:
            for i, chart in enumerate(visualization_suite['demographic_charts']['charts']):
                if 'config' in chart:
                    chart_id = chart.get('id', f'demographic_chart_{i}')
                    configs[chart_id] = chart['config']
        
        # Extract from distribution charts
        if 'distribution_charts' in visualization_suite and 'charts' in visualization_suite['distribution_charts']:
            for i, chart in enumerate(visualization_suite['distribution_charts']['charts']):
                if 'config' in chart:
                    chart_id = chart.get('id', f'distribution_chart_{i}')
                    configs[chart_id] = chart['config']
        
        # Extract from quality metrics
        if 'quality_metrics' in visualization_suite and 'charts' in visualization_suite['quality_metrics']:
            for i, chart in enumerate(visualization_suite['quality_metrics']['charts']):
                if 'config' in chart:
                    chart_id = chart.get('id', f'quality_chart_{i}')
                    configs[chart_id] = chart['config']
                    
    except Exception as e:
        print(f"Warning: Error extracting Chart.js configs: {e}")
    
    return configs

    return safe_text if safe_text else "data"

app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.json_encoder = NumpyJSONEncoder

# Configure upload settings for schema files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables
llm_manager = None

# Initialize Julius Analytics with API support
julius_analytics = JuliusAnalytics(use_api=True)

# Initialize Advanced Analytics System
data_analyzer = DataAnalyzer()
visualization_engine = VisualizationEngine(chart_library='chartjs')
insights_generator = InsightsGenerator()
ai_analytics = AIAnalytics()



# Initialize OpenRouter client only when needed to avoid startup issues
def get_openrouter_client():
    try:
        return OpenRouterClient()
    except Exception as e:
        print(f"DEBUG:app.py:OpenRouter client initialization failed: {e}")
        return None

# Initialize Gemini client only when needed to avoid startup issues
def get_gemini_client():
    try:
        if not GEMINI_AVAILABLE:
            return None
        return GeminiClient()
    except Exception as e:
        print(f"DEBUG:app.py:Gemini client initialization failed: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            prompt = request.form.get("prompt", "").strip()
            template = request.form.get("template", "").strip()
            mode = request.form.get("mode", "online").lower()
            
            # Extract rows from prompt or use default
            rows_param = request.form.get("rows")
            if rows_param:
                rows = int(rows_param)
            else:
                # Try to extract number from prompt
                import re
                numbers = re.findall(r'\b(\d+)\b', prompt)
                if numbers:
                    rows = int(numbers[0])  # Use first number found
                else:
                    rows = 20  # Default fallback
            
            format = request.form.get("format", "csv").lower()
            
            # Get analytics options from form
            enable_analytics = request.form.get("enable-analytics") == "on"
            advanced_options = {}
            if enable_analytics:
                advanced_options = {
                    "enable_analytics": True,
                    "include_outliers": request.form.get("include-outliers") == "on",
                    "email_validation": request.form.get("email-validation") == "on",
                    "data_validation": request.form.get("data-validation") == "on",
                    "age_distribution": request.form.get("age-distribution", "balanced"),
                    "demographics_region": request.form.get("demographics-region", "global"),
                    "age_conditions": request.form.get("age-conditions", "none"),
                    "min_age": request.form.get("min-age"),
                    "max_age": request.form.get("max-age"),
                    "common_emails": request.form.get("common-emails") == "on",
                    "realistic_names": request.form.get("realistic-names") == "on",
                    "business_context": request.form.get("business-context") == "on"
                }
            
            # DEBUG: Original request info
            print(f"DEBUG:app.py:index:original_prompt: {prompt}")
            print(f"DEBUG:app.py:index:template: {template}")
            print(f"DEBUG:app.py:index:rows: {rows}")
            print(f"DEBUG:app.py:index:format: {format}")
            print(f"DEBUG:app.py:index:mode: {mode}")
            print(f"DEBUG:app.py:index:enable_analytics: {enable_analytics}")
            if enable_analytics:
                print(f"DEBUG:app.py:index:advanced_options: {advanced_options}")
            
            # Handle schema file upload (NEW FEATURE)
            schema_context = ""
            if 'schema_file' in request.files:
                file = request.files['schema_file']
                print(f"DEBUG:app.py:index:schema_file_present: {bool(file and file.filename)}")
                if file and file.filename:
                    print(f"DEBUG:app.py:index:schema_filename: {file.filename}")
                    # FIXED: Use the correct method name
                    success, context_or_error = SchemaValidator.process_file(file)
                    print(f"DEBUG:app.py:index:schema_processing_success: {success}")
                    if success:
                        schema_context = context_or_error
                        original_prompt = prompt
                        prompt = f"{schema_context}\n\n{prompt}"
                        print(f"DEBUG:app.py:index:schema_processed_successfully")
                        print(f"DEBUG:app.py:index:schema_context_length: {len(schema_context)}")
                        print(f"DEBUG:app.py:index:enhanced_prompt_length: {len(prompt)}")
                    else:
                        print(f"DEBUG:app.py:index:schema_processing_error: {context_or_error}")
                        # Return error page with schema validation error
                        return render_template("error.html", 
                                             error=f"Schema validation failed: {context_or_error}",
                                             traceback="Please check your schema file format and try again.")
            
            # Use mode-based generation (online or gemini)
            try:
                if mode == "online":
                    # Initialize OpenRouter client
                    openrouter_client = get_openrouter_client()
                    if not openrouter_client:
                        return render_template("error.html", 
                                             error="OpenRouter client not available",
                                             traceback="Please configure OpenRouter API key")
                    
                    # Generate data using OpenRouter API
                    df = openrouter_client.generate_data(prompt, rows, output_format=format, template=template)
                    print(f"DEBUG:app.py:OpenRouter data generation successful, shape: {df.shape if hasattr(df, 'shape') else 'None'}")
                
                elif mode == "gemini":
                    # Initialize Gemini client
                    gemini_client = get_gemini_client()
                    if not gemini_client:
                        return render_template("error.html", 
                                             error="Gemini client not available",
                                             traceback="Please configure GEMINI_API_KEY in .env file")
                    
                    # Generate data using Gemini API
                    df = gemini_client.generate_data(prompt, rows, output_format=format, template=template)
                    print(f"DEBUG:app.py:Gemini data generation successful, shape: {df.shape if hasattr(df, 'shape') else 'None'}")
                
                else:
                    return render_template("error.html", 
                                         error=f"Unsupported generation mode: {mode}",
                                         traceback="Please select either 'online' or 'gemini' mode.")
                
                # Process analytics if enabled in form mode
                analytics_summary = None
                julius_result = None
                if enable_analytics and not df.empty:
                    print("DEBUG:app.py:index:Starting analytics processing for form mode")
                    try:
                        # Convert to list of dicts for Julius AI processing
                        if hasattr(df, 'to_dict'):
                            data_list = df.to_dict('records')
                        else:
                            data_list = df if isinstance(df, list) else []
                        
                        if data_list:
                            # Use Julius AI analytics
                            julius_result = julius_analytics.analyze_and_enhance_data(data_list, advanced_options)
                            
                            if julius_result:
                                analytics_summary = julius_result['analytics_summary']
                                # Update dataframe with enhanced data
                                df = pd.DataFrame(julius_result['enhanced_data'])
                                print(f"DEBUG:app.py:index:Julius analysis completed for form mode")
                            
                    except Exception as analytics_error:
                        print(f"DEBUG:app.py:index:Analytics processing failed: {analytics_error}")
                        # Continue without analytics if there's an error
                
            except Exception as e:
                print(f"DEBUG:app.py:index:generation_failed: {e}")
                
                # Parse structured error messages for better user experience
                error_str = str(e)
                if error_str.startswith("API_KEY_INVALID:"):
                    return render_template("error.html", 
                                         error="Invalid API Key",
                                         traceback="Your OpenRouter API key is invalid or expired. Please check your .env file and ensure OPENROUTER_API_KEY is set correctly.")
                elif error_str.startswith("RATE_LIMIT:"):
                    return render_template("error.html", 
                                         error="Rate Limit Exceeded",
                                         traceback="You've hit the API rate limit. Please wait a moment and try again.")
                elif error_str.startswith("QUOTA_EXCEEDED:"):
                    return render_template("error.html", 
                                         error="API Quota Exceeded",
                                         traceback="Your API quota has been exceeded. Please check your OpenRouter account balance.")
                elif error_str.startswith("NETWORK_ERROR:"):
                    return render_template("error.html", 
                                         error="Network Connection Failed",
                                         traceback="Unable to connect to the API. Please check your internet connection and try again.")
                else:
                    return render_template("error.html", 
                                         error=f"Data generation failed: {str(e)}",
                                         traceback=traceback.format_exc())
            
            # Filename generation logic with meaningful keywords from prompt
            keywords = extract_keywords_from_prompt(prompt)
            safe_keywords = sanitize_filename(keywords)
            
            if format == 'json':
                filename = f"{safe_keywords}_{mode}.json"
                filepath = os.path.join(OUTPUT_DIR, filename)
                df.to_json(filepath, orient='records', indent=4)
            else:
                filename = f"{safe_keywords}_{mode}.csv"
                filepath = os.path.join(OUTPUT_DIR, filename)
                df.to_csv(filepath, index=False)
            
            # Save analytics file if analytics are enabled in form mode
            if enable_analytics and analytics_summary:
                analytics_filename = f"analytics_{safe_keywords}_{mode}.json"
                analytics_filepath = os.path.join(OUTPUT_DIR, analytics_filename)
                
                try:
                    # Generate visualizations and insights
                    visualization_suite = visualization_engine.create_visualization_suite(analytics_summary)
                    insights = insights_generator.generate_comprehensive_insights(analytics_summary, advanced_options.get('business_context'))
                    
                    # Create complete analytics package
                    analytics_package = {
                        "metadata": {
                            "generated_at": datetime.now().isoformat(),
                            "data_file": filename,
                            "generation_mode": f"form_{mode}",
                            "total_records": len(df) if hasattr(df, '__len__') else 0,
                            "julius_ai_enabled": True if julius_result else False,
                            "form_submission": True
                        },
                        "analytics_summary": analytics_summary,
                        "visualizations": visualization_suite,
                        "insights": insights,
                        "chart_js_configs": visualization_suite.get('chart_configs', {}),
                        "download_info": {
                            "data_file": filename,
                            "analytics_file": analytics_filename,
                            "note": "Analytics file generated separately. Download from /download/" + analytics_filename
                        }
                    }
                    
                    # Save analytics file
                    with open(analytics_filepath, 'w', encoding='utf-8') as f:
                        json.dump(analytics_package, f, indent=4, ensure_ascii=False, cls=NumpyJSONEncoder)
                    
                    print(f"DEBUG:app.py:index:analytics_file_saved: {os.path.exists(analytics_filepath)}")
                    print(f"DEBUG:app.py:index:analytics_download_url: /download/{analytics_filename}")
                    
                except Exception as analytics_error:
                    print(f"DEBUG:app.py:index:Analytics file save failed: {analytics_error}")
            
            print(f"DEBUG:app.py:index:final_filename: {filename}")
            print(f"DEBUG:app.py:index:file_exists: {os.path.exists(filepath)}")
            
            return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)
            
        except Exception as e:
            print(f"DEBUG:app.py:index:Exception: {e}")
            print(traceback.format_exc())
            return render_template("error.html", error=str(e), traceback=traceback.format_exc())
    return render_template("index.html", success=False)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@app.route("/api/generate", methods=["POST"])
def api_generate():
    try:
        # Handle both JSON and form data (NEW: support for multipart form data with schema files)
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            print("DEBUG:app.py:api_generate:multipart_form_data_detected")
            # Form data with potential file upload
            data = {
                'prompt': request.form.get("prompt", ""),
                'template': request.form.get("template", ""),
                'format': request.form.get("format", "csv"),
                'rows': request.form.get("rows"),  # Can be None
                'mode': request.form.get("mode", "online").lower()
            }
            
            # Handle schema file upload in API mode (NEW FEATURE)
            schema_context = ""
            if 'schema_file' in request.files:
                file = request.files['schema_file']
                print(f"DEBUG:app.py:api_generate:schema_file_present: {bool(file and file.filename)}")
                if file and file.filename:
                    print(f"DEBUG:app.py:api_generate:schema_filename: {file.filename}")
                    # FIXED: Use the correct method name
                    success, context_or_error = SchemaValidator.process_file(file)
                    print(f"DEBUG:app.py:api_generate:schema_processing_success: {success}")
                    if success:
                        schema_context = context_or_error
                        original_prompt = data['prompt']
                        data['prompt'] = f"{schema_context}\n\n{data['prompt']}"
                        print(f"DEBUG:app.py:api_generate:schema_processed_successfully")
                        print(f"DEBUG:app.py:api_generate:schema_context_length: {len(schema_context)}")
                    else:
                        print(f"DEBUG:app.py:api_generate:schema_processing_error: {context_or_error}")
                        return jsonify({"success": False, "error": f"Schema validation failed: {context_or_error}"}), 400
        else:
            # Enhanced JSON data handling (NEW: support for SQL Server schema context)
            data = request.json
            print("DEBUG:app.py:api_generate:json_data_detected")
            
            # Handle SQL Server schema context (NEW FEATURE)
            sql_schema_context = data.get("sql_schema_context", "")
            if sql_schema_context:
                print("DEBUG:app.py:api_generate:sql_schema_context_detected")
                original_prompt = data.get("prompt", "")
                data["prompt"] = f"{sql_schema_context}\n\n{original_prompt}"
                print(f"DEBUG:app.py:api_generate:sql_schema_context_length: {len(sql_schema_context)}")

        # Existing debug logging (PRESERVED)
        print(f"DEBUG:app.py:data: {data}")
        prompt = data.get("prompt", "")
        template = data.get("template", "")
        format = data.get("format", "csv")  # Get the format from the request
        clean_prompt = data.get("clean_prompt", prompt[:50])  # Use clean_prompt for filename
        print(f"DEBUG:app.py:prompt: {prompt}")
        print(f"DEBUG:app.py:clean_prompt: {clean_prompt}")
        print(f"DEBUG:app.py:template: {template}")
        
        # Extract rows from prompt or use default
        rows = data.get("rows")
        if not rows:
            # Try to extract number from prompt
            import re
            numbers = re.findall(r'\b(\d+)\b', prompt)
            if numbers:
                rows = int(numbers[0])  # Use first number found
            else:
                rows = 20  # Default fallback
        else:
            rows = int(rows)
        
        print(f"DEBUG:app.py:rows: {rows}")
        mode = data.get("mode", "online").lower()
        print(f"DEBUG:app.py:mode: {mode}")

        # Existing mode handling logic (ENHANCED with Julius AI Analytics)
        if mode == "online":
            print("DEBUG:app.py:Using ONLINE generation with Julius AI Analytics")
            try:
                # Get advanced options for Julius AI
                advanced_options = data.get("advanced_options", {})
                print(f"DEBUG:app.py:advanced_options: {advanced_options}")
                
                # Initialize OpenRouter client only when needed
                openrouter_client = get_openrouter_client()
                if not openrouter_client:
                    return jsonify({"success": False, "error": "OpenRouter client not available"}), 500
                
                # Analyze prompt intent using Julius AI
                intent_analysis = julius_analytics.analyze_prompt_intent(prompt)
                print(f"DEBUG:app.py:intent_analysis: {intent_analysis}")
                
                # Enhance prompt with Julius AI analytics if enabled
                enhanced_prompt = prompt
                if advanced_options.get("enable_analytics", False):
                    age_dist = advanced_options.get("age_distribution", "balanced")
                    region = advanced_options.get("demographics_region", "global")
                    
                    analytics_context = f"""
                    Generate data with the following analytics requirements:
                    - Age Distribution: {age_dist}
                    - Regional Demographics: {region}
                    - Include outliers: {advanced_options.get('include_outliers', False)}
                    - Email validation required: {advanced_options.get('email_validation', True)}
                    - Business context aware: {advanced_options.get('business_context', False)}
                    
                    """
                    enhanced_prompt = f"{analytics_context}\n\n{prompt}"
                
                # Construct the messages list with the format included in the prompt
                messages = [{"role": "user", "content": f"{enhanced_prompt} Provide the output strictly in {format} format."}]
                llm_output = openrouter_client.generate_chat_completion(messages=messages)
                print(f"DEBUG:app.py:llm_output (first 200): {llm_output[:200]}")

                # Parse the LLM output based on the format
                # Generate meaningful filename from prompt keywords
                keywords = extract_keywords_from_prompt(prompt)
                safe_name = sanitize_filename(keywords)
                
                if format == 'csv':
                    df = parse_llm_output(llm_output, format='csv')
                    filename = f"{safe_name}_online.csv"
                elif format == 'json':
                    df = parse_llm_output(llm_output, format='json')
                    filename = f"{safe_name}_online.json"
                else:
                    return jsonify({"success": False, "error": "Unsupported format"}), 400

                # Convert to list of dicts for Julius AI processing
                if hasattr(df, 'to_dict'):
                    data_list = df.to_dict('records')
                else:
                    data_list = df if isinstance(df, list) else []
                
                print(f"DEBUG:app.py:data_list_length: {len(data_list)}")
                
                # Apply Julius AI enhancements using comprehensive analysis
                analytics_summary = None
                julius_result = None
                
                if advanced_options.get("enable_analytics", False) and data_list:
                    print("DEBUG:app.py:Starting Julius AI comprehensive analysis")
                    
                    # Use new comprehensive analysis method
                    julius_result = julius_analytics.analyze_and_enhance_data(data_list, advanced_options)
                    
                    if julius_result:
                        data_list = julius_result['enhanced_data']
                        analytics_summary = julius_result['analytics_summary']
                        
                        # Add Julius.ai specific metadata to analytics
                        analytics_summary['julius_ai_info'] = {
                            'processing_time': julius_result['processing_time'],
                            'tokens_used': julius_result['tokens_used'],
                            'data_source': julius_result['source'],
                            'api_success': julius_result['api_success'],
                            'enhanced_records': len(data_list)
                        }
                        
                        print(f"DEBUG:app.py:Julius analysis completed - Source: {julius_result['source']}")
                        print(f"DEBUG:app.py:Processing time: {julius_result['processing_time']:.2f}s")
                        if julius_result['tokens_used'] > 0:
                            print(f"DEBUG:app.py:Julius.ai tokens used: {julius_result['tokens_used']}")
                    else:
                        print("DEBUG:app.py:Julius analysis returned no results")
                
                # Convert back to DataFrame
                df = pd.DataFrame(data_list)

                filepath = os.path.join(OUTPUT_DIR, filename)

                if format == 'csv':
                    df.to_csv(filepath, index=False)
                elif format == 'json':
                    df.to_json(filepath, orient='records', indent=4)

                print(f"DEBUG:app.py:file_saved: {os.path.exists(filepath)}")
                
                # Save analytics file if analytics are enabled (ONLINE MODE)
                analytics_filename = None
                if advanced_options.get("enable_analytics", False) and analytics_summary:
                    analytics_filename = f"analytics_{safe_name}_online.json"
                    analytics_filepath = os.path.join(OUTPUT_DIR, analytics_filename)
                    
                    try:
                        # Generate visualizations and insights
                        visualization_suite = visualization_engine.create_visualization_suite(analytics_summary)
                        insights = insights_generator.generate_comprehensive_insights(analytics_summary, advanced_options.get('business_context'))
                        
                        # Extract Chart.js configurations for easy rendering
                        chart_js_configs = extract_chartjs_configs(visualization_suite)
                        
                        # Create complete analytics package
                        analytics_package = {
                            "metadata": {
                                "generated_at": datetime.now().isoformat(),
                                "data_file": filename,
                                "generation_mode": "online_openrouter",
                                "total_records": len(data_list),
                                "julius_ai_enabled": True if julius_result else False
                            },
                            "analytics_summary": analytics_summary,
                            "visualizations": visualization_suite,
                            "insights": insights,
                            "chart_js_configs": chart_js_configs,
                            "download_info": {
                                "data_file": filename,
                                "analytics_file": analytics_filename
                            }
                        }
                        
                        # Save analytics file
                        with open(analytics_filepath, 'w', encoding='utf-8') as f:
                            json.dump(analytics_package, f, indent=4, ensure_ascii=False, cls=NumpyJSONEncoder)
                        
                        print(f"DEBUG:app.py:analytics_file_saved: {os.path.exists(analytics_filepath)}")
                        
                    except Exception as analytics_error:
                        print(f"DEBUG:app.py:Analytics file save failed: {analytics_error}")
                        analytics_filename = None
                
                # Return response with analytics if enabled
                response = {"success": True, "filename": filename}
                if advanced_options.get("enable_analytics", False) and analytics_summary:
                    response["analytics"] = analytics_summary
                    if analytics_filename:
                        response["analytics_file"] = analytics_filename
                        response["download_files"] = {
                            "data": filename,
                            "analytics": analytics_filename
                        }
                    
                return jsonify(response)
            except Exception as e:
                print(f"DEBUG:app.py:ONLINE Exception: {e}")
                print(traceback.format_exc())
                
                # Parse structured error messages from API client
                error_str = str(e)
                error_type = "GENERAL_ERROR"
                user_message = error_str
                
                if error_str.startswith("API_KEY_INVALID:"):
                    error_type = "API_KEY_INVALID"
                    user_message = error_str[16:].strip()  # Remove prefix
                elif error_str.startswith("RATE_LIMIT:"):
                    error_type = "RATE_LIMIT"
                    user_message = error_str[11:].strip()
                elif error_str.startswith("QUOTA_EXCEEDED:"):
                    error_type = "QUOTA_EXCEEDED"
                    user_message = error_str[15:].strip()
                elif error_str.startswith("ACCESS_FORBIDDEN:"):
                    error_type = "ACCESS_FORBIDDEN"
                    user_message = error_str[17:].strip()
                elif error_str.startswith("NETWORK_ERROR:"):
                    error_type = "NETWORK_ERROR"
                    user_message = error_str[14:].strip()
                elif error_str.startswith("MODEL_ERROR:"):
                    error_type = "MODEL_ERROR"
                    user_message = error_str[12:].strip()
                elif error_str.startswith("API_ERROR:"):
                    error_type = "API_ERROR"
                    user_message = error_str[10:].strip()
                
                return jsonify({
                    "success": False, 
                    "error": user_message,
                    "error_type": error_type,
                    "technical_details": str(e),
                    "model_used": os.getenv("MODEL_ID", "deepseek/deepseek-r1:free"),
                    "timestamp": datetime.now().isoformat()
                }), 500
        elif mode == "gemini":
            print("DEBUG:app.py:Using GEMINI generation with Google AI Studio")
            try:
                # Get advanced options for Julius AI (same as online mode)
                advanced_options = data.get("advanced_options", {})
                print(f"DEBUG:app.py:advanced_options: {advanced_options}")
                
                # Initialize Gemini client
                gemini_client = get_gemini_client()
                if not gemini_client:
                    return jsonify({"success": False, "error": "Gemini client not available. Please check GEMINI_API_KEY in .env"}), 500
                
                # Analyze prompt intent using Julius AI
                intent_analysis = julius_analytics.analyze_prompt_intent(prompt)
                print(f"DEBUG:app.py:intent_analysis: {intent_analysis}")
                
                # Enhance prompt with Julius AI analytics if enabled
                enhanced_prompt = prompt
                if advanced_options.get("enable_analytics", False):
                    age_dist = advanced_options.get("age_distribution", "balanced")
                    region = advanced_options.get("demographics_region", "global")
                    
                    analytics_context = f"""
                    Generate data with the following analytics requirements:
                    - Age Distribution: {age_dist}
                    - Regional Demographics: {region}
                    - Include outliers: {advanced_options.get('include_outliers', False)}
                    - Email validation required: {advanced_options.get('email_validation', True)}
                    - Business context aware: {advanced_options.get('business_context', False)}
                    
                    """
                    enhanced_prompt = f"{analytics_context}\n\n{prompt}"
                
                # Generate data using Gemini API
                df = gemini_client.generate_data(enhanced_prompt, rows, output_format=format, template=template)
                print(f"DEBUG:app.py:Gemini data generation successful, shape: {df.shape if hasattr(df, 'shape') else 'None'}")

                # Generate meaningful filename from prompt keywords
                keywords = extract_keywords_from_prompt(prompt)
                safe_name = sanitize_filename(keywords)
                
                if format == 'csv':
                    filename = f"{safe_name}_gemini.csv"
                elif format == 'json':
                    filename = f"{safe_name}_gemini.json"
                else:
                    return jsonify({"success": False, "error": "Unsupported format"}), 400

                # Convert to list of dicts for Julius AI processing
                if hasattr(df, 'to_dict'):
                    data_list = df.to_dict('records')
                else:
                    data_list = df if isinstance(df, list) else []
                
                print(f"DEBUG:app.py:data_list_length: {len(data_list)}")
                
                # Apply Julius AI enhancements using comprehensive analysis (same as online mode)
                analytics_summary = None
                julius_result = None
                
                if advanced_options.get("enable_analytics", False) and data_list:
                    print("DEBUG:app.py:Starting Julius AI comprehensive analysis")
                    
                    # Use new comprehensive analysis method
                    julius_result = julius_analytics.analyze_and_enhance_data(data_list, advanced_options)
                    
                    if julius_result:
                        data_list = julius_result['enhanced_data']
                        analytics_summary = julius_result['analytics_summary']
                        
                        # Add Julius.ai specific metadata to analytics
                        analytics_summary['julius_ai_info'] = {
                            'processing_time': julius_result['processing_time'],
                            'tokens_used': julius_result['tokens_used'],
                            'data_source': julius_result['source'],
                            'api_success': julius_result['api_success'],
                            'enhanced_records': len(data_list)
                        }
                        
                        print(f"DEBUG:app.py:Julius analysis completed - Source: {julius_result['source']}")
                        print(f"DEBUG:app.py:Processing time: {julius_result['processing_time']:.2f}s")
                        if julius_result['tokens_used'] > 0:
                            print(f"DEBUG:app.py:Julius.ai tokens used: {julius_result['tokens_used']}")
                    else:
                        print("DEBUG:app.py:Julius analysis returned no results")
                
                # Convert back to DataFrame
                df = pd.DataFrame(data_list)

                filepath = os.path.join(OUTPUT_DIR, filename)

                if format == 'csv':
                    df.to_csv(filepath, index=False)
                elif format == 'json':
                    df.to_json(filepath, orient='records', indent=4)

                print(f"DEBUG:app.py:file_saved: {os.path.exists(filepath)}")
                
                # Save analytics file if analytics are enabled (GEMINI MODE)
                analytics_filename = None
                if advanced_options.get("enable_analytics", False) and analytics_summary:
                    analytics_filename = f"analytics_{safe_name}_gemini.json"
                    analytics_filepath = os.path.join(OUTPUT_DIR, analytics_filename)
                    
                    try:
                        # Generate visualizations and insights
                        visualization_suite = visualization_engine.create_visualization_suite(analytics_summary)
                        insights = insights_generator.generate_comprehensive_insights(analytics_summary, advanced_options.get('business_context'))
                        
                        # Extract Chart.js configurations for easy rendering
                        chart_js_configs = extract_chartjs_configs(visualization_suite)
                        
                        # Create complete analytics package
                        analytics_package = {
                            "metadata": {
                                "generated_at": datetime.now().isoformat(),
                                "data_file": filename,
                                "generation_mode": "gemini_google_ai",
                                "total_records": len(data_list),
                                "julius_ai_enabled": True if julius_result else False
                            },
                            "analytics_summary": analytics_summary,
                            "visualizations": visualization_suite,
                            "insights": insights,
                            "chart_js_configs": chart_js_configs,
                            "download_info": {
                                "data_file": filename,
                                "analytics_file": analytics_filename
                            }
                        }
                        
                        # Save analytics file
                        with open(analytics_filepath, 'w', encoding='utf-8') as f:
                            json.dump(analytics_package, f, indent=4, ensure_ascii=False, cls=NumpyJSONEncoder)
                        
                        print(f"DEBUG:app.py:analytics_file_saved: {os.path.exists(analytics_filepath)}")
                        
                    except Exception as analytics_error:
                        print(f"DEBUG:app.py:Analytics file save failed: {analytics_error}")
                        analytics_filename = None
                
                # Return response with analytics if enabled
                response = {"success": True, "filename": filename}
                if advanced_options.get("enable_analytics", False) and analytics_summary:
                    response["analytics"] = analytics_summary
                    if analytics_filename:
                        response["analytics_file"] = analytics_filename
                        response["download_files"] = {
                            "data": filename,
                            "analytics": analytics_filename
                        }
                    
                return jsonify(response)
            except Exception as e:
                print(f"DEBUG:app.py:GEMINI Exception: {e}")
                print(traceback.format_exc())
                
                # Parse structured error messages from Gemini client
                error_str = str(e)
                error_type = "GENERAL_ERROR"
                user_message = error_str
                
                if error_str.startswith("API_KEY_INVALID:"):
                    error_type = "API_KEY_INVALID"
                    user_message = error_str[16:].strip()
                elif error_str.startswith("RATE_LIMIT:"):
                    error_type = "RATE_LIMIT"
                    user_message = error_str[11:].strip()
                elif error_str.startswith("QUOTA_EXCEEDED:"):
                    error_type = "QUOTA_EXCEEDED"
                    user_message = error_str[15:].strip()
                elif error_str.startswith("ACCESS_FORBIDDEN:"):
                    error_type = "ACCESS_FORBIDDEN"
                    user_message = error_str[17:].strip()
                elif error_str.startswith("NETWORK_ERROR:"):
                    error_type = "NETWORK_ERROR"
                    user_message = error_str[14:].strip()
                elif error_str.startswith("MODEL_ERROR:"):
                    error_type = "MODEL_ERROR"
                    user_message = error_str[12:].strip()
                elif error_str.startswith("API_ERROR:"):
                    error_type = "API_ERROR"
                    user_message = error_str[10:].strip()
                
                return jsonify({
                    "success": False, 
                    "error": user_message,
                    "error_type": error_type,
                    "technical_details": str(e),
                    "model_used": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                    "timestamp": datetime.now().isoformat()
                }), 500
        else:
            # Offline mode is no longer supported, only online and gemini modes are available
            return jsonify({"success": False, "error": f"Unsupported mode '{mode}'. Please use 'online' or 'gemini' mode."}), 400
    except Exception as e:
        print(f"DEBUG:app.py:Exception: {e}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/sql-server/test-connection", methods=["POST"])
def test_sql_server_connection():
    """Test SQL Server database connection."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        server = data.get("server", "")
        database = data.get("database", "")
        username = data.get("username", "")
        password = data.get("password", "")
        use_windows_auth = data.get("use_windows_auth", True)
        
        # Clean and validate parameters
        server = str(server).strip() if server else ""
        database = str(database).strip() if database else ""
        username = str(username).strip() if username else None
        password = str(password).strip() if password else None
        
        if not server or not database:
            return jsonify({
                "success": False,
                "error": "Server and database are required"
            }), 400
        
        # Import here to avoid startup issues if pypyodbc not available
        from uploads.sql_schema_extractor import test_connection_params
        
        success, message = test_connection_params(
            server=server,
            database=database,
            username=username,
            password=password,
            use_windows_auth=use_windows_auth
        )
        
        return jsonify({
            "success": success,
            "message": message
        })
        
    except ImportError:
        return jsonify({
            "success": False,
            "error": "pypyodbc not available. Please install: pip install pypyodbc"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Connection test failed: {str(e)}"
        }), 500

@app.route("/api/sql-server/tables", methods=["POST"])
def get_sql_server_tables():
    """Get list of tables from SQL Server database."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        server = data.get("server", "")
        database = data.get("database", "")
        schema_name = data.get("schema_name", "dbo")
        username = data.get("username", "")
        password = data.get("password", "")
        use_windows_auth = data.get("use_windows_auth", True)
        
        # Clean and validate parameters
        server = str(server).strip() if server else ""
        database = str(database).strip() if database else ""
        schema_name = str(schema_name).strip() if schema_name else "dbo"
        username = str(username).strip() if username else None
        password = str(password).strip() if password else None
        
        if not server or not database:
            return jsonify({
                "success": False,
                "error": "Server and database are required"
            }), 400
        
        success, tables = list_sql_server_tables(
            server=server,
            database=database,
            schema_name=schema_name,
            username=username,
            password=password,
            use_windows_auth=use_windows_auth
        )
        
        if success:
            return jsonify({
                "success": True,
                "tables": tables
            })
        else:
            return jsonify({
                "success": False,
                "error": tables[0] if tables else "Failed to retrieve tables"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error retrieving tables: {str(e)}"
        }), 500

@app.route("/api/sql-server/schema", methods=["POST"])
def get_sql_server_schema():
    """Generate schema context from SQL Server tables."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        server = data.get("server", "")
        database = data.get("database", "")
        tables = data.get("tables", [])
        schema_name = data.get("schema_name", "dbo")
        username = data.get("username", "")
        password = data.get("password", "")
        use_windows_auth = data.get("use_windows_auth", True)
        include_sample_data = data.get("include_sample_data", False)
        
        # Clean and validate parameters
        server = str(server).strip() if server else ""
        database = str(database).strip() if database else ""
        schema_name = str(schema_name).strip() if schema_name else "dbo"
        username = str(username).strip() if username else None
        password = str(password).strip() if password else None
        
        if not server or not database:
            return jsonify({
                "success": False,
                "error": "Server and database are required"
            }), 400
        
        if not tables or not isinstance(tables, list):
            return jsonify({
                "success": False,
                "error": "At least one table must be selected"
            }), 400
        
        print(f"DEBUG:app.py:SQL schema generation:")
        print(f"  server: {server}")
        print(f"  database: {database}")
        print(f"  schema_name: {schema_name}")
        print(f"  tables: {tables}")
        print(f"  use_windows_auth: {use_windows_auth}")
        print(f"  include_sample_data: {include_sample_data}")
        
        success, context = extract_sql_server_schema(
            server=server,
            database=database,
            tables=tables,
            schema_name=schema_name,
            username=username,
            password=password,
            use_windows_auth=use_windows_auth,
            include_sample_data=include_sample_data
        )
        
        print(f"DEBUG:app.py:SQL schema result: success={success}")
        if not success:
            print(f"DEBUG:app.py:SQL schema error: {context}")
        else:
            print(f"DEBUG:app.py:SQL schema context length: {len(context)}")
        
        if success:
            return jsonify({
                "success": True,
                "schema_context": context
            })
        else:
            return jsonify({
                "success": False,
                "error": context
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Schema extraction failed: {str(e)}"
        }), 500

@app.route("/llm-status", methods=["GET"])
def llm_status():
    """Get current LLM status - offline generation has been removed."""
    return jsonify({
        "success": False,
        "error": "Offline LLM generation has been removed",
        "llm_status": "offline_removed",
        "available": False
    }), 410

@app.route("/llm-restart", methods=["POST"])
def llm_restart():
    """LLM restart is no longer supported - offline generation has been removed."""
    return jsonify({
        "success": False,
        "error": "Offline LLM generation has been removed",
        "message": "LLM restart is no longer available"
    }), 410

@app.route("/julius-status")
def julius_status():
    """Get Julius.ai integration status and configuration"""
    try:
        status = julius_analytics.get_connection_status()
        return jsonify({
            "success": True,
            "julius_status": status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/gemini-status")
def gemini_status():
    """Get Gemini API integration status and configuration"""
    try:
        if not GEMINI_AVAILABLE:
            return jsonify({
                "success": False,
                "gemini_status": {
                    "available": False,
                    "error": "google-generativeai package not installed",
                    "install_command": "pip install google-generativeai"
                },
                "timestamp": datetime.now().isoformat()
            }), 503
        
        gemini_client = get_gemini_client()
        if not gemini_client:
            return jsonify({
                "success": False,
                "gemini_status": {
                    "available": False,
                    "error": "Gemini client initialization failed",
                    "check": "Verify GEMINI_API_KEY in .env file"
                },
                "timestamp": datetime.now().isoformat()
            }), 503
        
        # Test connection
        connection_test = gemini_client.test_connection()
        
        return jsonify({
            "success": True,
            "gemini_status": {
                "available": True,
                "api_key_configured": bool(os.getenv("GEMINI_API_KEY")),
                "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                "connection_test": connection_test
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/analyze-data", methods=["POST"])
def analyze_data():
    """Comprehensive data analysis endpoint"""
    try:
        # Get data from request
        data = request.get_json()
        if not data or 'records' not in data:
            return jsonify({
                "success": False,
                "error": "No data provided. Expected JSON with 'records' array."
            }), 400
        
        records = data['records']
        analysis_options = data.get('options', {})
        
        # Perform comprehensive analysis
        analysis_result = data_analyzer.analyze_dataset(records, analysis_options)
        
        if 'error' in analysis_result:
            return jsonify({
                "success": False,
                "error": analysis_result['error']
            }), 500
        
        # Generate visualizations
        visualization_suite = visualization_engine.create_visualization_suite(analysis_result)
        
        # Generate insights
        insights = insights_generator.generate_comprehensive_insights(
            analysis_result, 
            data.get('business_context')
        )
        
        return jsonify({
            "success": True,
            "analysis": analysis_result,
            "visualizations": visualization_suite,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/analytics-dashboard")
def analytics_dashboard():
    """Render analytics dashboard page"""
    try:
        return render_template('analytics_dashboard.html')
    except Exception as e:
        return f"Dashboard error: {str(e)}", 500

@app.route("/visualization-config")
def get_visualization_config():
    """Get visualization configuration for frontend"""
    try:
        config = visualization_engine.export_visualization_config()
        return jsonify({
            "success": True,
            "config": config,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/quick-analysis", methods=["POST"])
def quick_analysis():
    """Quick analysis endpoint for existing generated data"""
    try:
        # Get the most recent output file
        output_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')]
        if not output_files:
            return jsonify({
                "success": False,
                "error": "No data files found for analysis"
            }), 404
        
        # Get the most recent file
        latest_file = max(output_files, key=lambda x: os.path.getctime(os.path.join(OUTPUT_DIR, x)))
        file_path = os.path.join(OUTPUT_DIR, latest_file)
        
        # Load and analyze data
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
        
        # Extract records from file data
        if isinstance(file_data, dict) and 'data' in file_data:
            records = file_data['data']
        elif isinstance(file_data, list):
            records = file_data
        else:
            return jsonify({
                "success": False,
                "error": "Invalid data format in file"
            }), 400
        
        # Perform quick analysis (limited depth for speed)
        analysis_options = {'quick_mode': True, 'max_fields': 10}
        analysis_result = data_analyzer.analyze_dataset(records, analysis_options)
        
        # Generate basic visualizations
        visualization_suite = visualization_engine.create_visualization_suite(analysis_result)
        
        return jsonify({
            "success": True,
            "file_analyzed": latest_file,
            "analysis": analysis_result,
            "visualizations": visualization_suite,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Quick analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/analytics-status")
def analytics_status():
    """Get status of analytics system"""
    try:
        return jsonify({
            "success": True,
            "analytics_status": {
                "data_analyzer": "ready",
                "visualization_engine": {
                    "status": "ready",
                    "chart_library": visualization_engine.chart_library,
                    "supported_charts": ["bar", "line", "pie", "doughnut", "scatter"]
                },
                "insights_generator": "ready",
                "integration_status": "fully_operational"
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/list-output-files", methods=["GET"])
def list_output_files():
    """List all output files with metadata"""
    try:
        import os
        import json
        from datetime import datetime
        
        output_files = []
        
        # Get all JSON and CSV files from output directory
        output_dir_abs = os.path.abspath(OUTPUT_DIR)
        for filename in os.listdir(output_dir_abs):
            if filename.endswith(('.json', '.csv')):
                file_path = os.path.join(output_dir_abs, filename)
                file_stat = os.stat(file_path)
                
                # Get file size
                size_bytes = file_stat.st_size
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                
                # Get modification time
                mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                
                # Try to count records
                record_count = "Unknown"
                try:
                    if filename.endswith('.json'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_data = json.load(f)
                            if isinstance(file_data, dict) and 'data' in file_data:
                                record_count = len(file_data['data'])
                            elif isinstance(file_data, list):
                                record_count = len(file_data)
                    elif filename.endswith('.csv'):
                        import csv
                        with open(file_path, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f)
                            record_count = sum(1 for row in reader) - 1  # Subtract header
                except:
                    record_count = "Error reading"
                
                output_files.append({
                    'name': filename,
                    'path': filename,  # Use just filename for relative access
                    'size': size_str,
                    'modified': mod_time.strftime('%Y-%m-%d %H:%M'),
                    'modified_timestamp': file_stat.st_mtime,
                    'records': record_count
                })
        
        # Sort by modification time (newest first)
        output_files.sort(key=lambda x: x['modified_timestamp'], reverse=True)
        
        # Remove timestamp from response
        for file_info in output_files:
            del file_info['modified_timestamp']
        
        return jsonify({
            "success": True,
            "files": output_files,
            "total_files": len(output_files)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list files: {str(e)}"
        }), 500

@app.route("/analyze-file", methods=["POST"])
def analyze_file():
    """Analyze a specific file from the output directory"""
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return jsonify({
                "success": False,
                "error": "File path is required"
            }), 400
        
        file_path = data['file_path']
        file_name = data.get('file_name', file_path)
        mode = data.get('mode', 'online').lower()  # Get analytics API mode
        
        # Security check - ensure file path is just a filename (no directory traversal)
        if '/' in file_path or '\\' in file_path or '..' in file_path:
            return jsonify({
                "success": False,
                "error": "Invalid file path - only filenames allowed"
            }), 400
        
        # Construct full path within output directory
        full_file_path = os.path.join(OUTPUT_DIR, file_path)
        
        if not os.path.exists(full_file_path):
            return jsonify({
                "success": False,
                "error": "File not found"
            }), 404
        
        # Load and parse the file
        import json
        import csv
        
        records = []
        
        if full_file_path.endswith('.json'):
            with open(full_file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                
            if isinstance(file_data, dict) and 'data' in file_data:
                records = file_data['data']
            elif isinstance(file_data, list):
                records = file_data
            else:
                return jsonify({
                    "success": False,
                    "error": "Invalid JSON format - expected array or object with 'data' field"
                }), 400
                
        elif full_file_path.endswith('.csv'):
            with open(full_file_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                records = [row for row in csv_reader]
        
        if not records:
            return jsonify({
                "success": False,
                "error": "No records found in file"
            }), 400
        
        # Perform analysis
        analysis_options = {'file_source': file_name}
        analysis_result = data_analyzer.analyze_dataset(records, analysis_options)
        
        if 'error' in analysis_result:
            return jsonify({
                "success": False,
                "error": analysis_result['error']
            }), 500
        
        # Generate visualizations
        visualization_suite = visualization_engine.create_visualization_suite(analysis_result)
        
        # Generate insights
        insights = insights_generator.generate_comprehensive_insights(analysis_result)
        
        # Generate AI-powered insights and chart recommendations
        data_summary = {
            'total_records': len(records),
            'columns': list(records[0].keys()) if records else [],
            'column_types': {k: type(v).__name__ for k, v in records[0].items()} if records else {}
        }
        ai_insights = ai_analytics.generate_ai_insights(data_summary, records[:50], mode=mode)  # Limit sample for API
        
        # Generate AI-recommended charts
        ai_charts = []
        if ai_insights.get('recommended_charts'):
            for chart_config in ai_insights['recommended_charts']:
                chart_data = ai_analytics.create_chart_data(records, chart_config)
                ai_charts.append({
                    'config': chart_config,
                    'data': chart_data
                })
        
        # Convert numpy types to JSON-serializable types with error handling
        try:
            converted_analysis = convert_numpy_types(analysis_result)
        except Exception as e:
            print(f"Error converting analysis result: {e}")
            converted_analysis = {"error": "Analysis conversion failed"}
        
        try:
            converted_visualizations = convert_numpy_types(visualization_suite)
        except Exception as e:
            print(f"Error converting visualizations: {e}")
            converted_visualizations = {"error": "Visualization conversion failed"}
        
        try:
            converted_insights = convert_numpy_types(insights)
        except Exception as e:
            print(f"Error converting insights: {e}")
            converted_insights = {"error": "Insights conversion failed"}
        
        try:
            converted_ai_insights = convert_numpy_types(ai_insights)
        except Exception as e:
            print(f"Error converting AI insights: {e}")
            converted_ai_insights = {"error": "AI insights conversion failed"}
        
        try:
            converted_ai_charts = convert_numpy_types(ai_charts)
        except Exception as e:
            print(f"Error converting AI charts: {e}")
            converted_ai_charts = {"error": "AI charts conversion failed"}
        
        response_data = {
            "success": True,
            "file_analyzed": file_name,
            "analysis": converted_analysis,
            "visualizations": converted_visualizations,
            "insights": converted_insights,
            "ai_insights": converted_ai_insights,
            "ai_charts": converted_ai_charts,
            "timestamp": datetime.now().isoformat()
        }
        
        # Final JSON serialization test
        try:
            json.dumps(response_data, cls=NumpyJSONEncoder)
        except Exception as e:
            print(f"Final JSON serialization error: {e}")
            return jsonify({
                "success": False,
                "error": f"JSON serialization failed: {str(e)}"
            }), 500
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"File analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/load-analytics-file", methods=["POST"])
def load_analytics_file():
    """Load a pre-analyzed analytics file"""
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return jsonify({
                "success": False,
                "error": "File path is required"
            }), 400
        
        file_path = data['file_path']
        file_name = data.get('file_name', file_path)
        
        # Security check - ensure file path is just a filename (no directory traversal)
        if '/' in file_path or '\\' in file_path or '..' in file_path:
            return jsonify({
                "success": False,
                "error": "Invalid file path - only filenames allowed"
            }), 400
        
        # Verify it's an analytics file
        if not file_path.startswith('analytics_'):
            return jsonify({
                "success": False,
                "error": "This endpoint is only for pre-analyzed analytics files"
            }), 400
        
        # Construct full path within output directory
        full_file_path = os.path.join(OUTPUT_DIR, file_path)
        
        if not os.path.exists(full_file_path):
            return jsonify({
                "success": False,
                "error": "Analytics file not found"
            }), 404
        
        # Load the analytics file
        with open(full_file_path, 'r', encoding='utf-8') as f:
            analytics_data = json.load(f)
        
        # Verify it has the expected structure
        if 'metadata' not in analytics_data or 'analytics_summary' not in analytics_data:
            return jsonify({
                "success": False,
                "error": "Invalid analytics file format"
            }), 400
        
        # Return the analytics data in a format compatible with the dashboard
        response_data = {
            "success": True,
            "file_analyzed": file_name,
            "is_preanalyzed": True,
            "metadata": analytics_data.get('metadata', {}),
            "analysis": analytics_data.get('analytics_summary', {}),
            "visualizations": analytics_data.get('visualizations', {}),
            "insights": analytics_data.get('insights', {}),
            "ai_insights": analytics_data.get('ai_insights', {}),
            "ai_charts": analytics_data.get('ai_charts', []),
            "chart_js_configs": analytics_data.get('chart_js_configs', {}),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except json.JSONDecodeError as e:
        return jsonify({
            "success": False,
            "error": f"Invalid JSON in analytics file: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to load analytics file: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/output/<filename>")
def serve_output_file(filename):
    """Serve files from the output directory"""
    # Security check - prevent directory traversal
    if '/' in filename or '\\' in filename or '..' in filename:
        return "Invalid filename", 400
    
    return send_from_directory(OUTPUT_DIR, filename)

@app.route("/test-error/<error_type>", methods=["POST"])
def test_error_handling(error_type):
    """Test endpoint to verify error handling - development only"""
    try:
        openrouter_client = get_openrouter_client()
        if not openrouter_client:
            return jsonify({"success": False, "error": "OpenRouter client not available"}), 500
        
        # Simulate the error
        openrouter_client.test_error_handling(error_type)
        
        return jsonify({"success": True, "message": "No error occurred"})
        
    except Exception as e:
        print(f"DEBUG:app.py:test-error Exception: {e}")
        
        # Parse structured error messages (same logic as main API)
        error_str = str(e)
        error_type_parsed = "GENERAL_ERROR"
        user_message = error_str
        
        if error_str.startswith("API_KEY_INVALID:"):
            error_type_parsed = "API_KEY_INVALID"
            user_message = error_str[16:].strip()
        elif error_str.startswith("RATE_LIMIT:"):
            error_type_parsed = "RATE_LIMIT"
            user_message = error_str[11:].strip()
        elif error_str.startswith("QUOTA_EXCEEDED:"):
            error_type_parsed = "QUOTA_EXCEEDED"
            user_message = error_str[15:].strip()
        elif error_str.startswith("ACCESS_FORBIDDEN:"):
            error_type_parsed = "ACCESS_FORBIDDEN"
            user_message = error_str[17:].strip()
        elif error_str.startswith("NETWORK_ERROR:"):
            error_type_parsed = "NETWORK_ERROR"
            user_message = error_str[14:].strip()
        elif error_str.startswith("MODEL_ERROR:"):
            error_type_parsed = "MODEL_ERROR"
            user_message = error_str[12:].strip()
        elif error_str.startswith("API_ERROR:"):
            error_type_parsed = "API_ERROR"
            user_message = error_str[10:].strip()
        
        return jsonify({
            "success": False, 
            "error": user_message,
            "error_type": error_type_parsed,
            "technical_details": str(e) if error_type_parsed == "GENERAL_ERROR" else None
        }), 500

if __name__ == "__main__":
    print("DEBUG:app.py:Starting Flask server...")
    # Existing directory creation (PRESERVED) + new upload directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    print(f"DEBUG:app.py:Directories created: {OUTPUT_DIR}, {UPLOAD_DIR}")
    
    print("DEBUG:app.py:Server starting on http://127.0.0.1:5000")
    print("DEBUG:app.py:Offline generation has been removed, using online mode only")
    app.run(debug=True, host='127.0.0.1', port=5000)
