import json
import os
from typing import Dict, List, Any, Optional
from api.api_client import OpenRouterClient
from dotenv import load_dotenv

# Import Gemini client with error handling
try:
    from api.gemini_client import GeminiClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("WARNING: Gemini client not available for analytics. Install google-generativeai to enable Gemini support.")

load_dotenv()

class AIAnalytics:
    """AI-powered analytics engine using OpenRouter API or Gemini"""
    
    def __init__(self):
        """Initialize the AI analytics engine"""
        self.enabled = os.getenv("AI_ANALYTICS_ENABLED", "true").lower() == "true"
        self.max_data_points = int(os.getenv("MAX_DATA_POINTS_FOR_AI", "1000"))
        
        if self.enabled:
            try:
                self.openrouter_client = OpenRouterClient()
            except Exception as e:
                print(f"Warning: Could not initialize OpenRouter client: {e}")
                self.openrouter_client = None
            
            # Initialize Gemini client if available
            if GEMINI_AVAILABLE:
                try:
                    self.gemini_client = GeminiClient()
                except Exception as e:
                    print(f"Warning: Could not initialize Gemini client: {e}")
                    self.gemini_client = None
            else:
                self.gemini_client = None
    
    def generate_ai_insights(self, data_summary: Dict[str, Any], sample_data: List[Dict], mode: str = "online") -> Dict[str, Any]:
        """
        Generate AI-powered insights and chart recommendations
        
        Args:
            data_summary: Summary statistics about the dataset
            sample_data: Sample records from the dataset (limited for API efficiency)
            mode: API mode to use - "online" for OpenRouter or "gemini" for Google AI
            
        Returns:
            Dict containing AI insights, chart recommendations, and analysis
        """
        if not self.enabled:
            return self._fallback_response()
        
        try:
            # Prepare data for AI analysis
            analysis_prompt = self._create_analysis_prompt(data_summary, sample_data)
            
            # Choose client based on mode
            if mode == "gemini" and self.gemini_client:
                # Use Gemini API
                full_prompt = self._get_system_prompt() + "\n\n" + analysis_prompt
                response = self.gemini_client.generate_content(full_prompt, temperature=0.1)
            elif mode == "online" and self.openrouter_client:
                # Use OpenRouter API
                messages = [
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ]
                response = self.openrouter_client.generate_chat_completion(messages, temperature=0.1)
            else:
                # Fallback if requested client is not available
                print(f"Warning: Requested mode '{mode}' not available, using fallback")
                return self._fallback_response()
            
            # Parse AI response
            ai_insights = self._parse_ai_response(response)
            
            return ai_insights
            
        except Exception as e:
            print(f"AI Analytics error: {e}")
            return self._fallback_response()
    
    def _create_analysis_prompt(self, data_summary: Dict[str, Any], sample_data: List[Dict]) -> str:
        """Create a structured prompt for AI analysis"""
        
        # Limit sample data for API efficiency
        limited_sample = sample_data[:min(len(sample_data), 10)]
        
        prompt = f"""
Please analyze this dataset and provide insights with chart recommendations.

DATASET SUMMARY:
- Total Records: {data_summary.get('total_records', 'Unknown')}
- Columns: {', '.join(data_summary.get('columns', []))}
- Data Types: {json.dumps(data_summary.get('column_types', {}), indent=2)}

SAMPLE DATA (first 10 records):
{json.dumps(limited_sample, indent=2, default=str)}

ANALYSIS REQUEST:
1. Identify the most interesting patterns and insights
2. Recommend the best chart types for visualization
3. Suggest key metrics to highlight
4. Provide business insights and recommendations

Please respond with a valid JSON object following this exact structure:
{{
    "insights": [
        {{
            "title": "Insight Title",
            "description": "Detailed insight description",
            "importance": "high|medium|low",
            "category": "demographic|statistical|quality|business"
        }}
    ],
    "recommended_charts": [
        {{
            "type": "bar|pie|line|scatter|histogram|donut",
            "title": "Chart Title",
            "description": "What this chart shows",
            "x_axis": "column_name_for_x_axis",
            "y_axis": "column_name_for_y_axis_or_count",
            "data_processing": "count|sum|average|group_by",
            "priority": 1
        }}
    ],
    "key_metrics": [
        {{
            "name": "Metric Name",
            "value": "calculated_value_or_column_name",
            "format": "number|percentage|currency|text",
            "description": "What this metric represents"
        }}
    ],
    "summary": "Overall analysis summary and business recommendations"
}}

Ensure all field names in x_axis and y_axis exactly match the column names from the dataset.
"""
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI analytics"""
        return """You are an expert data analyst and visualization specialist. 

Your task is to analyze datasets and provide:
1. Meaningful business insights
2. Optimal chart type recommendations
3. Key metrics to track
4. Actionable recommendations

Always respond with valid JSON following the exact schema provided. 
Be specific about column names and ensure they match the actual data.
Focus on practical, actionable insights that would be valuable for business decision-making.
Consider data quality, distributions, correlations, and anomalies in your analysis."""
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate AI response"""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Handle cases where response might have extra text
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            # Clean up the response
            response = response.strip()
            
            # Parse JSON
            ai_data = json.loads(response)
            
            # Validate required fields
            required_fields = ['insights', 'recommended_charts', 'key_metrics', 'summary']
            for field in required_fields:
                if field not in ai_data:
                    ai_data[field] = []
            
            return {
                "success": True,
                "ai_powered": True,
                "insights": ai_data.get('insights', []),
                "recommended_charts": ai_data.get('recommended_charts', []),
                "key_metrics": ai_data.get('key_metrics', []),
                "summary": ai_data.get('summary', 'AI analysis completed successfully'),
                "timestamp": None
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response}")
            return self._fallback_response()
        except Exception as e:
            print(f"Response parsing error: {e}")
            return self._fallback_response()
    
    def _fallback_response(self) -> Dict[str, Any]:
        """Provide fallback response when AI is unavailable"""
        return {
            "success": True,
            "ai_powered": False,
            "insights": [
                {
                    "title": "Data Overview",
                    "description": "Your dataset has been processed successfully. AI insights are currently unavailable.",
                    "importance": "medium",
                    "category": "statistical"
                }
            ],
            "recommended_charts": [
                {
                    "type": "bar",
                    "title": "Column Distribution",
                    "description": "Overview of data distribution",
                    "x_axis": "category",
                    "y_axis": "count",
                    "data_processing": "count",
                    "priority": 1
                }
            ],
            "key_metrics": [
                {
                    "name": "Total Records",
                    "value": "dataset_size",
                    "format": "number",
                    "description": "Total number of records in the dataset"
                }
            ],
            "summary": "Standard analytics completed. Enable AI analytics with OpenRouter API key for enhanced insights."
        }

    def create_chart_data(self, data: List[Dict], chart_config: Dict) -> Dict[str, Any]:
        """
        Convert raw data into Chart.js format based on AI recommendations
        
        Args:
            data: Raw dataset
            chart_config: Chart configuration from AI recommendations
            
        Returns:
            Chart.js compatible data structure
        """
        try:
            chart_type = chart_config.get('type', 'bar')
            x_axis = chart_config.get('x_axis')
            y_axis = chart_config.get('y_axis', 'count')
            processing = chart_config.get('data_processing', 'count')
            
            if not x_axis:
                return {"error": "No x_axis specified"}
            
            # Process data based on chart type and processing method
            if processing == 'count':
                return self._create_count_chart(data, x_axis, chart_type)
            elif processing == 'sum':
                return self._create_sum_chart(data, x_axis, y_axis, chart_type)
            elif processing == 'average':
                return self._create_average_chart(data, x_axis, y_axis, chart_type)
            elif processing == 'group_by':
                return self._create_group_chart(data, x_axis, y_axis, chart_type)
            else:
                return self._create_count_chart(data, x_axis, chart_type)
                
        except Exception as e:
            return {"error": f"Chart data creation failed: {str(e)}"}
    
    def _create_count_chart(self, data: List[Dict], x_axis: str, chart_type: str) -> Dict[str, Any]:
        """Create count-based chart data"""
        counts = {}
        for record in data:
            value = str(record.get(x_axis, 'Unknown'))
            counts[value] = counts.get(value, 0) + 1
        
        # Sort by count (descending) and limit to top 20
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "type": chart_type,
            "data": {
                "labels": [item[0] for item in sorted_counts],
                "datasets": [{
                    "label": f"Count of {x_axis}",
                    "data": [item[1] for item in sorted_counts],
                    "backgroundColor": self._generate_colors(len(sorted_counts)),
                    "borderColor": self._generate_border_colors(len(sorted_counts)),
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"Distribution of {x_axis}"
                    }
                }
            }
        }
    
    def _create_sum_chart(self, data: List[Dict], x_axis: str, y_axis: str, chart_type: str) -> Dict[str, Any]:
        """Create sum-based chart data"""
        sums = {}
        for record in data:
            x_value = str(record.get(x_axis, 'Unknown'))
            y_value = self._safe_numeric(record.get(y_axis, 0))
            sums[x_value] = sums.get(x_value, 0) + y_value
        
        sorted_sums = sorted(sums.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "type": chart_type,
            "data": {
                "labels": [item[0] for item in sorted_sums],
                "datasets": [{
                    "label": f"Sum of {y_axis}",
                    "data": [item[1] for item in sorted_sums],
                    "backgroundColor": self._generate_colors(len(sorted_sums)),
                    "borderColor": self._generate_border_colors(len(sorted_sums)),
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"Total {y_axis} by {x_axis}"
                    }
                }
            }
        }
    
    def _create_average_chart(self, data: List[Dict], x_axis: str, y_axis: str, chart_type: str) -> Dict[str, Any]:
        """Create average-based chart data"""
        groups = {}
        for record in data:
            x_value = str(record.get(x_axis, 'Unknown'))
            y_value = self._safe_numeric(record.get(y_axis, 0))
            
            if x_value not in groups:
                groups[x_value] = []
            groups[x_value].append(y_value)
        
        averages = {k: sum(v) / len(v) for k, v in groups.items()}
        sorted_averages = sorted(averages.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "type": chart_type,
            "data": {
                "labels": [item[0] for item in sorted_averages],
                "datasets": [{
                    "label": f"Average {y_axis}",
                    "data": [round(item[1], 2) for item in sorted_averages],
                    "backgroundColor": self._generate_colors(len(sorted_averages)),
                    "borderColor": self._generate_border_colors(len(sorted_averages)),
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"Average {y_axis} by {x_axis}"
                    }
                }
            }
        }
    
    def _create_group_chart(self, data: List[Dict], x_axis: str, y_axis: str, chart_type: str) -> Dict[str, Any]:
        """Create grouped chart data"""
        return self._create_count_chart(data, x_axis, chart_type)
    
    def _safe_numeric(self, value) -> float:
        """Safely convert value to numeric"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _generate_colors(self, count: int) -> List[str]:
        """Generate color palette for charts"""
        base_colors = [
            'rgba(54, 162, 235, 0.6)',  # Blue
            'rgba(255, 99, 132, 0.6)',  # Red
            'rgba(255, 205, 86, 0.6)',  # Yellow
            'rgba(75, 192, 192, 0.6)',  # Green
            'rgba(153, 102, 255, 0.6)', # Purple
            'rgba(255, 159, 64, 0.6)',  # Orange
            'rgba(199, 199, 199, 0.6)', # Grey
            'rgba(83, 102, 255, 0.6)',  # Indigo
            'rgba(255, 99, 255, 0.6)',  # Pink
            'rgba(99, 255, 132, 0.6)'   # Light Green
        ]
        
        colors = []
        for i in range(count):
            colors.append(base_colors[i % len(base_colors)])
        return colors
    
    def _generate_border_colors(self, count: int) -> List[str]:
        """Generate border color palette for charts"""
        base_colors = [
            'rgba(54, 162, 235, 1)',
            'rgba(255, 99, 132, 1)',
            'rgba(255, 205, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(199, 199, 199, 1)',
            'rgba(83, 102, 255, 1)',
            'rgba(255, 99, 255, 1)',
            'rgba(99, 255, 132, 1)'
        ]
        
        colors = []
        for i in range(count):
            colors.append(base_colors[i % len(base_colors)])
        return colors