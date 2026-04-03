import os
import json
from openai import OpenAI
from openai import RateLimitError, AuthenticationError, PermissionDeniedError, BadRequestError, APIError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class OpenRouterClient:
    """
    A client to interact with the OpenRouter API using the OpenAI SDK.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in .env file. Please set it.")

        self.app_url = os.getenv("APP_URL", "http://localhost:5000")
        self.model_id = os.getenv("MODEL_ID", "deepseek/deepseek-r1:free")  # Default model ID

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": self.app_url,
            }
        )

    def test_error_handling(self, error_type="401"):
        """
        Test method to simulate different API errors.
        This is for development/testing purposes only.
        """
        if error_type == "401":
            raise Exception("401 Unauthorized: Invalid API key")
        elif error_type == "429":
            raise Exception("429 Too Many Requests: Rate limit exceeded")
        elif error_type == "quota":
            raise Exception("Quota exceeded for this billing cycle")
        elif error_type == "403":
            raise Exception("403 Forbidden: Access denied")
        elif error_type == "network":
            raise Exception("Network timeout occurred")
        elif error_type == "model":
            raise Exception("Model 'gpt-4-invalid' not found or unavailable")
        else:
            raise Exception("Generic API error occurred")

    def generate_chat_completion(self, messages, temperature=0.1):
        """
        Generates a chat completion using a specified model on OpenRouter.

        Args:
            messages (list): A list of message dictionaries (e.g., [{'role': 'user', 'content': 'Hello!'}]).
            temperature (float): The sampling temperature.

        Returns:
            str: The content of the response message.
        """
        try:
            print(f"🔄 API Call Starting...")
            print(f"   Model: {self.model_id}")
            print(f"   API Key Present: {bool(self.api_key)}")
            print(f"   Base URL: https://openrouter.ai/api/v1")

            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=temperature
            )

            result = response.choices[0].message.content
            print(f"✅ API Call Successful - Response length: {len(result)} chars")
            return result

        except Exception as e:
            print(f"API CLIENT:❌ OpenRouter API FAILED:")
            print(f"API CLIENT:   Error Type: {type(e).__name__}")
            print(f"API CLIENT:   Error Message: {str(e)}")
            print(f"API CLIENT:   API Key (first 10 chars): {self.api_key[:10] if self.api_key else 'MISSING'}")
            
            # Extract detailed error information from OpenAI errors
            error_details = self._extract_error_details(e)
            error_type = error_details['type']
            user_message = error_details['message']
            technical_details = error_details['technical']
            
            print(f"API CLIENT:   Parsed Error Type: {error_type}")
            print(f"API CLIENT:   User Message: {user_message}")
            
            # Raise structured error with detailed information
            raise RuntimeError(f"{error_type}: {user_message}") from e

    def _extract_error_details(self, error):
        """Extract detailed error information from various error types"""
        error_str = str(error)
        error_type_name = type(error).__name__
        
        # Handle specific OpenAI error types
        if isinstance(error, RateLimitError):
            return self._parse_rate_limit_error(error, error_str)
        elif isinstance(error, AuthenticationError):
            return {
                'type': 'API_KEY_INVALID',
                'message': 'Your OpenRouter API key is invalid or expired. Please check your .env file.',
                'technical': error_str
            }
        elif isinstance(error, PermissionDeniedError):
            return {
                'type': 'ACCESS_FORBIDDEN', 
                'message': 'Access denied. Your API key may not have permission for this model or feature.',
                'technical': error_str
            }
        elif isinstance(error, BadRequestError):
            return self._parse_bad_request_error(error, error_str)
        elif isinstance(error, APIError):
            return self._parse_api_error(error, error_str)
        else:
            # Handle generic errors
            return self._parse_generic_error(error_str, error_type_name)
    
    def _parse_rate_limit_error(self, error, error_str):
        """Parse rate limit errors with detailed information"""
        user_message = "You've hit the API rate limit. Please wait a moment and try again."
        
        # Try to extract detailed information from the error
        if 'temporarily rate-limited upstream' in error_str:
            user_message = f"The model '{self.model_id}' is temporarily rate-limited. Please try again in a few moments or switch to a different model."
        elif 'add your own key' in error_str:
            user_message = f"Rate limit reached for free tier. Consider adding your own API key for higher limits. Model: {self.model_id}"
        
        return {
            'type': 'RATE_LIMIT',
            'message': user_message,
            'technical': error_str
        }
    
    def _parse_bad_request_error(self, error, error_str):
        """Parse bad request errors"""
        if 'model' in error_str.lower() and 'not found' in error_str.lower():
            return {
                'type': 'MODEL_ERROR',
                'message': f"The AI model '{self.model_id}' is not available. Please try a different model.",
                'technical': error_str
            }
        else:
            return {
                'type': 'API_ERROR',
                'message': f"Invalid request: {error_str}",
                'technical': error_str
            }
    
    def _parse_api_error(self, error, error_str):
        """Parse general API errors"""
        if 'quota' in error_str.lower() or 'billing' in error_str.lower():
            return {
                'type': 'QUOTA_EXCEEDED',
                'message': 'Your API quota has been exceeded. Please check your OpenRouter account balance.',
                'technical': error_str
            }
        else:
            return {
                'type': 'API_ERROR',
                'message': f"API error occurred: {error_str}",
                'technical': error_str
            }
    
    def _parse_generic_error(self, error_str, error_type_name):
        """Parse generic errors based on content"""
        error_lower = error_str.lower()
        
        if 'network' in error_lower or 'connection' in error_lower or 'timeout' in error_lower:
            return {
                'type': 'NETWORK_ERROR',
                'message': 'Network connection failed. Please check your internet connection and try again.',
                'technical': error_str
            }
        elif '401' in error_str or 'unauthorized' in error_lower:
            return {
                'type': 'API_KEY_INVALID',
                'message': 'Your OpenRouter API key is invalid or expired. Please check your .env file.',
                'technical': error_str
            }
        elif '403' in error_str or 'forbidden' in error_lower:
            return {
                'type': 'ACCESS_FORBIDDEN',
                'message': 'Access denied. Please check your API key permissions.',
                'technical': error_str
            }
        else:
            return {
                'type': 'API_ERROR',
                'message': f"OpenRouter API failed - {error_type_name}: {error_str}",
                'technical': error_str
            }
