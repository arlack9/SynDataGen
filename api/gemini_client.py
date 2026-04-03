"""
Google Gemini API Client for Synthetic Data Generation
Integrates with Google AI Studio API for data generation using Gemini models
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("WARNING: google-generativeai not installed. Install with: pip install google-generativeai")

from parser.data_parser import parse_llm_output

class GeminiClient:
    """
    A client to interact with Google Gemini API for synthetic data generation.
    """
    
    def __init__(self):
        """Initialize the Gemini client with API configuration."""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not available. Please install: pip install google-generativeai")
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file. Please set it.")
        
        # Validate API key format (should start with 'AIza')
        if not self.api_key.startswith('AIza'):
            raise ValueError("Invalid GEMINI_API_KEY format. Google AI Studio API keys should start with 'AIza'.")
        
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-pro")
        self.app_url = os.getenv("APP_URL", "http://localhost:5000")
        
        # Fallback models to try if primary model fails
        self.fallback_models = [
            "gemini-pro",
            "models/gemini-pro", 
            "models/gemini-1.5-pro-latest",
            "models/gemini-1.0-pro"
        ]
        
        print(f"🔄 Configuring Gemini API...")
        print(f"   API Key: {self.api_key[:10]}...")
        print(f"   Model: {self.model_name}")
        
        # Configure the Gemini API
        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            print(f"❌ Failed to configure Gemini API: {e}")
            raise ValueError(f"Failed to configure Gemini API: {e}")
        
        # Initialize the model with fallback support
        self.model = None
        models_to_try = [self.model_name] + [m for m in self.fallback_models if m != self.model_name]
        
        for model_name in models_to_try:
            try:
                print(f"🔄 Trying model: {model_name}")
                self.model = genai.GenerativeModel(model_name)
                self.model_name = model_name
                print(f"✅ Gemini client initialized with model: {self.model_name}")
                break
            except Exception as e:
                print(f"❌ Model {model_name} failed: {e}")
                continue
        
        if not self.model:
            raise ValueError("Failed to initialize any Gemini model. Please check your API key and model availability.")

    def generate_chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> str:
        """
        Generate text completion using Gemini API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            str: Generated text content
        """
        try:
            print(f"🔄 Gemini API Call Starting...")
            print(f"   Model: {self.model_name}")
            print(f"   API Key Present: {bool(self.api_key)}")
            print(f"   Temperature: {temperature}")
            
            # Convert messages to a single prompt (Gemini uses single prompt format)
            prompt = self._convert_messages_to_prompt(messages)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=8192,  # Adjust based on your needs
                top_p=0.95,
                top_k=64
            )
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if not response.text:
                raise Exception("Empty response from Gemini API")
            
            result = response.text
            print(f"✅ Gemini API Call Successful - Response length: {len(result)} chars")
            return result
            
        except Exception as e:
            print(f"❌ Gemini API FAILED:")
            print(f"   Error Type: {type(e).__name__}")
            print(f"   Error Message: {str(e)}")
            print(f"   API Key (first 10 chars): {self.api_key[:10] if self.api_key else 'MISSING'}")
            
            # Check for common error patterns
            error_str = str(e).lower()
            if "api key" in error_str and ("invalid" in error_str or "not valid" in error_str):
                print("   🔍 Detected: API Key validation issue")
                print(f"   🔍 Current API Key format: {self.api_key[:15]}..." if self.api_key else "No API key")
            elif "quota" in error_str or "exceeded" in error_str:
                print("   🔍 Detected: Quota or rate limit issue")
            elif "permission" in error_str or "forbidden" in error_str:
                print("   🔍 Detected: Permission/access issue")
            
            # Extract detailed error information
            error_details = self._extract_error_details(e)
            error_type = error_details['type']
            user_message = error_details['message']
            
            print(f"   Parsed Error Type: {error_type}")
            print(f"   User Message: {user_message}")
            
            # Raise structured error
            raise RuntimeError(f"{error_type}: {user_message}") from e

    def generate_data(self, prompt: str, rows: int, output_format: str = 'csv', template: str = '') -> pd.DataFrame:
        """
        Generate synthetic data based on prompt using Gemini API.
        
        Args:
            prompt: Description of data to generate
            rows: Number of rows to generate
            output_format: Output format ('csv' or 'json')
            template: Optional template data to guide generation
            
        Returns:
            pd.DataFrame: Generated data
        """
        try:
            # Construct enhanced prompt for data generation
            enhanced_prompt = self._build_data_generation_prompt(prompt, rows, output_format, template)
            
            # Create messages in OpenAI format for consistency
            messages = [{"role": "user", "content": enhanced_prompt}]
            
            # Generate raw output
            raw_output = self.generate_chat_completion(messages, temperature=0.1)
            
            # Debug: Log raw output length and first/last parts
            print(f"DEBUG: Raw output length: {len(raw_output)} characters")
            print(f"DEBUG: Raw output starts with: {raw_output[:100]}")
            print(f"DEBUG: Raw output ends with: {raw_output[-100:]}")
            
            # Parse the output with better error handling
            try:
                df = parse_llm_output(raw_output, format=output_format)
                print(f"✅ Gemini data generation successful - Shape: {df.shape}")
                
                # Validate that we have data
                if df.empty:
                    print("WARNING: DataFrame is empty, attempting to parse raw JSON directly")
                    if output_format.lower() == 'json':
                        # Try direct JSON parsing as fallback
                        import json
                        try:
                            # Clean the raw output - remove any markdown code blocks
                            cleaned_output = raw_output.strip()
                            if cleaned_output.startswith('```json'):
                                cleaned_output = cleaned_output[7:]
                            if cleaned_output.endswith('```'):
                                cleaned_output = cleaned_output[:-3]
                            cleaned_output = cleaned_output.strip()
                            
                            # Parse JSON directly
                            json_data = json.loads(cleaned_output)
                            df = pd.DataFrame(json_data)
                            print(f"✅ Fallback JSON parsing successful - Shape: {df.shape}")
                        except Exception as fallback_error:
                            print(f"❌ Fallback JSON parsing failed: {fallback_error}")
                            # Create a DataFrame with the raw output to preserve data
                            df = pd.DataFrame([{"raw_data": raw_output}])
                
                return df
                
            except Exception as parse_error:
                print(f"❌ Parse error: {parse_error}")
                print("Attempting to save raw data to preserve it...")
                
                # If parsing fails, create a DataFrame with raw data to avoid data loss
                if output_format.lower() == 'json':
                    # Try to extract JSON from raw output even if malformed
                    import re
                    json_match = re.search(r'\[.*\]', raw_output, re.DOTALL)
                    if json_match:
                        try:
                            import json
                            json_data = json.loads(json_match.group())
                            df = pd.DataFrame(json_data)
                            print(f"✅ Regex JSON extraction successful - Shape: {df.shape}")
                            return df
                        except:
                            pass
                
                # Last resort: save raw output as single field
                df = pd.DataFrame([{
                    "raw_gemini_output": raw_output,
                    "parse_error": str(parse_error),
                    "timestamp": datetime.now().isoformat()
                }])
                print("⚠️ Data preserved in raw format to prevent loss")
                return df
            
        except Exception as e:
            print(f"❌ Gemini data generation failed: {e}")
            raise

    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to single prompt for Gemini."""
        prompt_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"Instructions: {content}")
            elif role == 'user':
                prompt_parts.append(f"Request: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Response: {content}")
        
        return "\n\n".join(prompt_parts)

    def _build_data_generation_prompt(self, prompt: str, rows: int, output_format: str, template: str) -> str:
        """Build comprehensive prompt for data generation."""
        base_prompt = f"""Generate {rows} rows of synthetic data based on the following request:

{prompt}

Requirements:
1. Output format: {output_format.upper()}
2. Generate exactly {rows} rows
3. Use realistic and diverse data
4. Ensure proper formatting and structure
"""

        if template.strip():
            base_prompt += f"""
5. Follow this template structure:
{template}
"""

        if output_format.lower() == 'csv':
            base_prompt += """
6. For CSV format:
   - First line must be the header with column names
   - Use proper CSV escaping for special characters
   - Do not include row numbers or indices
   - Separate values with commas
"""
        else:
            base_prompt += """
6. For JSON format:
   - Return as an array of objects
   - Each object represents one row
   - Use proper JSON formatting
   - Ensure valid JSON syntax
"""

        base_prompt += f"""

Provide ONLY the {output_format.upper()} data without any additional text, explanations, or code blocks.
"""
        
        return base_prompt

    def _extract_error_details(self, error: Exception) -> Dict[str, str]:
        """Extract structured error information from Gemini API errors."""
        error_str = str(error)
        error_type_name = type(error).__name__
        
        # Handle specific Gemini/Google AI Studio error types
        if ("API_KEY_INVALID" in error_str or 
            "invalid API key" in error_str.lower() or 
            "api key not valid" in error_str.lower() or
            "authentication" in error_str.lower() or
            "401" in error_str):
            return {
                'type': 'API_KEY_INVALID',
                'message': 'Invalid Gemini API key. Please verify your GEMINI_API_KEY in .env file. Get a new key from https://makersuite.google.com/app/apikey',
                'technical': error_str
            }
        elif "quota" in error_str.lower() or "exceeded" in error_str.lower():
            return {
                'type': 'QUOTA_EXCEEDED',
                'message': 'Gemini API quota exceeded. Please check your Google AI Studio usage.',
                'technical': error_str
            }
        elif "rate" in error_str.lower() and "limit" in error_str.lower():
            return {
                'type': 'RATE_LIMIT',
                'message': 'Gemini API rate limit exceeded. Please wait and try again.',
                'technical': error_str
            }
        elif "forbidden" in error_str.lower() or "403" in error_str:
            return {
                'type': 'ACCESS_FORBIDDEN',
                'message': 'Access forbidden. Please check your Gemini API permissions.',
                'technical': error_str
            }
        elif "network" in error_str.lower() or "connection" in error_str.lower():
            return {
                'type': 'NETWORK_ERROR',
                'message': 'Network error connecting to Gemini API. Please check your internet connection.',
                'technical': error_str
            }
        elif "model" in error_str.lower() and ("not found" in error_str.lower() or "unavailable" in error_str.lower()):
            return {
                'type': 'MODEL_ERROR',
                'message': f'Gemini model "{self.model_name}" not found or unavailable.',
                'technical': error_str
            }
        else:
            return {
                'type': 'API_ERROR',
                'message': f'Gemini API error: {error_str}',
                'technical': error_str
            }

    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Gemini API with detailed diagnostics."""
        try:
            # First test: Check if we can list models (basic API access)
            try:
                available_models = list(genai.list_models())
                print(f"✅ Available models count: {len(available_models)}")
                model_names = [model.name for model in available_models[:5]]  # First 5 models
                print(f"   Sample models: {model_names}")
            except Exception as list_error:
                print(f"⚠️ Cannot list models: {list_error}")
                model_names = ["Unable to list models"]
            
            # Second test: Simple generation test
            test_messages = [{"role": "user", "content": "Say 'Hello' in one word."}]
            response = self.generate_chat_completion(test_messages, temperature=0.0)
            
            return {
                'success': True,
                'message': 'Gemini API connection and generation successful',
                'model': self.model_name,
                'available_models': model_names,
                'test_response': response[:100]  # First 100 chars of response
            }
        except Exception as e:
            error_details = self._extract_error_details(e)
            return {
                'success': False,
                'error': error_details['message'],
                'error_type': error_details['type'],
                'model': self.model_name,
                'technical_error': str(e)
            }