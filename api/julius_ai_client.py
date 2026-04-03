"""
Julius.ai API Client for Real-time Analytics Integration
Provides connection to actual Julius.ai service for demographic analytics
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class JuliusAnalyticsRequest:
    """Request structure for Julius.ai API"""
    data: List[Dict[str, Any]]
    analysis_type: str
    demographic_focus: Optional[str] = None
    region: Optional[str] = None
    include_outliers: bool = False
    validation_level: str = "standard"

@dataclass
class JuliusAnalyticsResponse:
    """Response structure from Julius.ai API"""
    success: bool
    analytics_summary: Dict[str, Any]
    enhanced_data: List[Dict[str, Any]]
    processing_time: float
    tokens_used: int
    error_message: Optional[str] = None

class JuliusAIClient:
    """
    Client for connecting to Julius.ai API
    Handles authentication, requests, and response processing
    """
    
    def __init__(self):
        self.api_key = os.getenv("JULIUS_AI_API_KEY")
        self.base_url = os.getenv("JULIUS_AI_BASE_URL", "https://api.julius.ai/v1")
        self.app_url = os.getenv("APP_URL", "http://localhost:5000")
        
        if not self.api_key:
            logging.warning("JULIUS_AI_API_KEY not found in environment variables. Julius.ai features will be limited.")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"SyntheticDataGenerator/1.0 ({self.app_url})",
            "X-Client-Version": "1.0.0"
        })
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Julius.ai API"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "api_version": response.json().get("version", "unknown"),
                    "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining"),
                    "message": "Successfully connected to Julius.ai API"
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "message": "Failed to connect to Julius.ai API"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Network error connecting to Julius.ai API"
            }
    
    def analyze_demographic_data(self, 
                                data: List[Dict[str, Any]], 
                                demographic_focus: str = "balanced",
                                region: str = "global",
                                include_outliers: bool = False) -> JuliusAnalyticsResponse:
        """
        Send data to Julius.ai for demographic analysis and enhancement
        
        Args:
            data: List of data records to analyze
            demographic_focus: Age group focus (gen-z, millennials, gen-x, boomers, balanced)
            region: Regional focus (global, north-america, europe, asia-pacific, india)
            include_outliers: Whether to include statistical outliers
            
        Returns:
            JuliusAnalyticsResponse with enhanced data and analytics
        """
        
        if not self.api_key:
            self.logger.warning("No Julius.ai API key configured, falling back to local simulation")
            return self._fallback_analysis(data, demographic_focus, region, include_outliers)
        
        try:
            # Prepare request payload
            request_data = JuliusAnalyticsRequest(
                data=data,
                analysis_type="demographic_enhancement",
                demographic_focus=demographic_focus,
                region=region,
                include_outliers=include_outliers,
                validation_level="enhanced"
            )
            
            self.logger.info(f"Sending {len(data)} records to Julius.ai for analysis")
            
            # Make API request
            response = self.session.post(
                f"{self.base_url}/analytics/demographic",
                json=asdict(request_data),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                return JuliusAnalyticsResponse(
                    success=True,
                    analytics_summary=result.get("analytics_summary", {}),
                    enhanced_data=result.get("enhanced_data", data),
                    processing_time=result.get("processing_time", 0.0),
                    tokens_used=result.get("tokens_used", 0)
                )
                
            elif response.status_code == 429:
                # Rate limit exceeded
                self.logger.warning("Julius.ai rate limit exceeded, falling back to local analysis")
                return self._fallback_analysis(data, demographic_focus, region, include_outliers)
                
            else:
                error_msg = f"Julius.ai API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return JuliusAnalyticsResponse(
                    success=False,
                    analytics_summary={},
                    enhanced_data=data,
                    processing_time=0.0,
                    tokens_used=0,
                    error_message=error_msg
                )
                
        except requests.exceptions.Timeout:
            self.logger.warning("Julius.ai API timeout, falling back to local analysis")
            return self._fallback_analysis(data, demographic_focus, region, include_outliers)
            
        except Exception as e:
            error_msg = f"Julius.ai API client error: {str(e)}"
            self.logger.error(error_msg)
            return JuliusAnalyticsResponse(
                success=False,
                analytics_summary={},
                enhanced_data=data,
                processing_time=0.0,
                tokens_used=0,
                error_message=error_msg
            )
    
    def enhance_field_demographics(self, 
                                 field_name: str, 
                                 field_type: str,
                                 age_distribution: str,
                                 region: str,
                                 sample_size: int = 1) -> List[Any]:
        """
        Generate demographically-aware field values using Julius.ai
        
        Args:
            field_name: Name of the field (e.g., "name", "email", "age")
            field_type: Data type of the field
            age_distribution: Target age distribution
            region: Target region
            sample_size: Number of values to generate
            
        Returns:
            List of generated values
        """
        
        try:
            payload = {
                "field_name": field_name,
                "field_type": field_type,
                "age_distribution": age_distribution,
                "region": region,
                "sample_size": sample_size,
                "generation_mode": "demographic_aware"
            }
            
            response = self.session.post(
                f"{self.base_url}/generate/field",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("generated_values", [])
            else:
                self.logger.warning(f"Julius.ai field generation failed: {response.status_code}")
                return self._fallback_field_generation(field_name, field_type, age_distribution, region, sample_size)
                
        except Exception as e:
            self.logger.warning(f"Julius.ai field generation error: {str(e)}")
            return self._fallback_field_generation(field_name, field_type, age_distribution, region, sample_size)
    
    def validate_data_quality(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate data quality using Julius.ai quality metrics
        
        Args:
            data: Data to validate
            
        Returns:
            Quality metrics and validation results
        """
        
        try:
            payload = {
                "data": data,
                "validation_types": ["format", "consistency", "demographic_realism", "outlier_detection"],
                "return_suggestions": True
            }
            
            response = self.session.post(
                f"{self.base_url}/validate/quality",
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Julius.ai validation failed: {response.status_code}")
                return self._fallback_validation(data)
                
        except Exception as e:
            self.logger.warning(f"Julius.ai validation error: {str(e)}")
            return self._fallback_validation(data)
    
    def _fallback_analysis(self, data: List[Dict[str, Any]], 
                          demographic_focus: str, 
                          region: str, 
                          include_outliers: bool) -> JuliusAnalyticsResponse:
        """Fallback to local analysis when Julius.ai API is unavailable"""
        
        # Import local Julius analytics for fallback
        try:
            from .julius_analytics import JuliusAnalytics
            local_julius = JuliusAnalytics()
            
            # Use local methods to simulate Julius.ai response
            analytics_summary = local_julius.generate_analytics_summary(data, {
                'age_distribution': demographic_focus,
                'demographics_region': region,
                'include_outliers': include_outliers
            })
            
            # Apply local enhancements
            enhanced_data = data.copy()
            for i, row in enumerate(enhanced_data):
                for field_name, field_value in row.items():
                    if field_name.lower() in ['name', 'email', 'age', 'phone', 'city']:
                        try:
                            enhanced_value = local_julius.generate_demographic_aware_value(
                                field_name=field_name,
                                field_type=type(field_value).__name__,
                                age_distribution=demographic_focus,
                                region=region,
                                include_outliers=include_outliers
                            )
                            enhanced_data[i][field_name] = enhanced_value
                        except:
                            continue  # Keep original value if enhancement fails
            
            return JuliusAnalyticsResponse(
                success=True,
                analytics_summary=analytics_summary,
                enhanced_data=enhanced_data,
                processing_time=0.1,
                tokens_used=0
            )
            
        except ImportError:
            # If local Julius analytics is not available, return basic response
            return JuliusAnalyticsResponse(
                success=False,
                analytics_summary={
                    'total_records': len(data),
                    'fallback_mode': True,
                    'message': 'Julius.ai API unavailable, no local fallback'
                },
                enhanced_data=data,
                processing_time=0.0,
                tokens_used=0,
                error_message="Julius.ai API unavailable and no local fallback"
            )
    
    def _fallback_field_generation(self, field_name: str, field_type: str, 
                                 age_distribution: str, region: str, sample_size: int) -> List[Any]:
        """Fallback field generation using local methods"""
        
        try:
            from .julius_analytics import JuliusAnalytics
            local_julius = JuliusAnalytics()
            
            values = []
            for _ in range(sample_size):
                value = local_julius.generate_demographic_aware_value(
                    field_name=field_name,
                    field_type=field_type,
                    age_distribution=age_distribution,
                    region=region
                )
                values.append(value)
            
            return values
            
        except ImportError:
            # Basic fallback values
            if field_name.lower() in ['name', 'first_name', 'last_name']:
                return ['John Doe'] * sample_size
            elif field_name.lower() in ['email']:
                return ['user@example.com'] * sample_size
            elif field_name.lower() in ['age']:
                return [25] * sample_size
            else:
                return [None] * sample_size
    
    def _fallback_validation(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback validation using local methods"""
        
        return {
            'validation_status': 'fallback',
            'total_records': len(data),
            'validated_fields': list(data[0].keys() if data else []),
            'quality_score': 0.8,  # Default quality score
            'suggestions': ['Consider using Julius.ai API for enhanced validation'],
            'fallback_mode': True
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics from Julius.ai"""
        
        try:
            response = self.session.get(
                f"{self.base_url}/account/usage",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f"Failed to get usage stats: {response.status_code}",
                    'api_key_valid': False
                }
                
        except Exception as e:
            return {
                'error': f"Usage stats error: {str(e)}",
                'api_key_valid': False
            }
