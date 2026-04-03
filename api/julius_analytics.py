"""
Julius AI Analytics Integration for Synthetic Data Generator
Provides advanced analytics and demographic-aware data generation
Now supports both Julius.ai API and local fallback
"""

import json
import re
import random
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# Try to import the Julius.ai API client
try:
    from .julius_ai_client import JuliusAIClient, JuliusAnalyticsResponse
    JULIUS_API_AVAILABLE = True
except ImportError:
    JULIUS_API_AVAILABLE = False
    logging.warning("Julius.ai API client not available, using local simulation only")


@dataclass
class DemographicProfile:
    """Demographics profile for data generation"""
    age_distribution: Dict[str, float]
    region_weights: Dict[str, float]
    email_providers: Dict[str, float]
    name_patterns: Dict[str, List[str]]


class JuliusAnalytics:
    """Julius AI-powered analytics and data generation with API integration"""
    
    def __init__(self, use_api: bool = True):
        """
        Initialize Julius Analytics
        
        Args:
            use_api: Whether to use Julius.ai API (True) or local simulation (False)
        """
        self.use_api = use_api and JULIUS_API_AVAILABLE
        self.demographic_profiles = self._initialize_profiles()
        self.email_providers = {
            'gmail.com': 0.60,
            'outlook.com': 0.25,
            'hotmail.com': 0.10,
            'yahoo.com': 0.03,
            'icloud.com': 0.02
        }
        
        # Initialize Julius.ai API client if available
        if self.use_api:
            try:
                self.api_client = JuliusAIClient()
                connection_test = self.api_client.test_connection()
                if connection_test['status'] == 'connected':
                    logging.info(f"✅ Connected to Julius.ai API - {connection_test['message']}")
                else:
                    logging.warning(f"⚠️ Julius.ai API connection failed: {connection_test['message']}")
                    self.use_api = False
            except Exception as e:
                logging.error(f"❌ Failed to initialize Julius.ai API client: {str(e)}")
                self.use_api = False
        
        if not self.use_api:
            logging.info("🔄 Using local Julius Analytics simulation")
            self.api_client = None
        
    def _initialize_profiles(self) -> Dict[str, DemographicProfile]:
        """Initialize demographic profiles for different regions and age groups"""
        return {
            'gen-z': DemographicProfile(
                age_distribution={'18-22': 0.30, '23-26': 0.45, '27-30': 0.20, '31-35': 0.05},
                region_weights={'north-america': 0.35, 'europe': 0.25, 'asia-pacific': 0.30, 'india': 0.10},
                email_providers={'gmail.com': 0.70, 'outlook.com': 0.15, 'hotmail.com': 0.05, 'yahoo.com': 0.05, 'icloud.com': 0.05},
                name_patterns={
                    'north-america': ['Aiden', 'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Mason', 'Sophia'],
                    'europe': ['Lucas', 'Marie', 'Alexander', 'Emma', 'Oliver', 'Anna', 'Leo', 'Sofia'],
                    'asia-pacific': ['Hiroshi', 'Yuki', 'Akira', 'Sakura', 'Ravi', 'Priya', 'Wei', 'Li'],
                    'india': ['Arjun', 'Priya', 'Rohan', 'Ananya', 'Vikram', 'Shreya', 'Aditya', 'Kavya']
                }
            ),
            'millennials': DemographicProfile(
                age_distribution={'27-30': 0.25, '31-35': 0.35, '36-40': 0.30, '41-42': 0.10},
                region_weights={'north-america': 0.40, 'europe': 0.30, 'asia-pacific': 0.20, 'india': 0.10},
                email_providers={'gmail.com': 0.55, 'outlook.com': 0.30, 'hotmail.com': 0.10, 'yahoo.com': 0.05},
                name_patterns={
                    'north-america': ['Michael', 'Jennifer', 'Christopher', 'Jessica', 'Matthew', 'Amanda', 'Joshua', 'Sarah'],
                    'europe': ['David', 'Laura', 'James', 'Sarah', 'Daniel', 'Emma', 'Thomas', 'Sophie'],
                    'asia-pacific': ['Takeshi', 'Keiko', 'Rajesh', 'Meera', 'Chang', 'Min', 'Taro', 'Yuki'],
                    'india': ['Amit', 'Sunita', 'Rajesh', 'Deepika', 'Suresh', 'Meera', 'Karan', 'Neha']
                }
            ),
            'gen-x': DemographicProfile(
                age_distribution={'43-50': 0.40, '51-55': 0.35, '56-58': 0.25},
                region_weights={'north-america': 0.45, 'europe': 0.35, 'asia-pacific': 0.15, 'india': 0.05},
                email_providers={'gmail.com': 0.40, 'outlook.com': 0.35, 'hotmail.com': 0.15, 'yahoo.com': 0.10},
                name_patterns={
                    'north-america': ['Robert', 'Lisa', 'William', 'Karen', 'Richard', 'Nancy', 'Thomas', 'Betty'],
                    'europe': ['John', 'Helen', 'Peter', 'Margaret', 'Paul', 'Catherine', 'Andrew', 'Susan'],
                    'asia-pacific': ['Satoshi', 'Michiko', 'Kumar', 'Sita', 'Wong', 'Lin', 'Yamamoto', 'Tanaka'],
                    'india': ['Rajesh', 'Kamala', 'Suresh', 'Lakshmi', 'Ramesh', 'Sita', 'Mahesh', 'Geeta']
                }
            ),
            'boomers': DemographicProfile(
                age_distribution={'59-65': 0.35, '66-70': 0.30, '71-75': 0.25, '76-80': 0.10},
                region_weights={'north-america': 0.50, 'europe': 0.40, 'asia-pacific': 0.08, 'india': 0.02},
                email_providers={'gmail.com': 0.30, 'outlook.com': 0.40, 'hotmail.com': 0.20, 'yahoo.com': 0.10},
                name_patterns={
                    'north-america': ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Linda', 'Michael', 'Barbara'],
                    'europe': ['William', 'Margaret', 'Charles', 'Dorothy', 'George', 'Helen', 'Frank', 'Ruth'],
                    'asia-pacific': ['Ichiro', 'Hanako', 'Shyam', 'Radha', 'Chen', 'Wang', 'Sato', 'Suzuki'],
                    'india': ['Ram', 'Sita', 'Krishna', 'Radha', 'Gopal', 'Lakshmi', 'Mohan', 'Ganga']
                }
            )
        }

    def get_connection_status(self) -> Dict[str, Any]:
        """Get Julius.ai API connection status and configuration"""
        if self.use_api and self.api_client:
            try:
                status = self.api_client.test_connection()
                usage_stats = self.api_client.get_usage_stats()
                return {
                    'api_enabled': True,
                    'connection_status': status['status'],
                    'api_version': status.get('api_version', 'unknown'),
                    'rate_limit_remaining': status.get('rate_limit_remaining'),
                    'usage_stats': usage_stats,
                    'message': status.get('message', 'Connected to Julius.ai API')
                }
            except Exception as e:
                return {
                    'api_enabled': True,
                    'connection_status': 'error',
                    'error': str(e),
                    'message': 'Julius.ai API connection error'
                }
        else:
            return {
                'api_enabled': False,
                'connection_status': 'local_mode',
                'message': 'Using local Julius Analytics simulation'
            }

    def analyze_prompt_intent(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt to understand data generation intent"""
        prompt_lower = prompt.lower()
        
        # Detect data types and domains
        domains = []
        if any(word in prompt_lower for word in ['restaurant', 'food', 'cuisine', 'dining']):
            domains.append('restaurants')
        if any(word in prompt_lower for word in ['hotel', 'accommodation', 'booking', 'room']):
            domains.append('hotels')
        if any(word in prompt_lower for word in ['insurance', 'policy', 'claim', 'coverage']):
            domains.append('insurance')
        if any(word in prompt_lower for word in ['company', 'business', 'corporation', 'enterprise']):
            domains.append('business')
        if any(word in prompt_lower for word in ['employee', 'staff', 'worker', 'personnel']):
            domains.append('hr')
        if any(word in prompt_lower for word in ['customer', 'client', 'user', 'buyer']):
            domains.append('customers')
        
        # Extract row count
        row_count = 20  # default
        numbers = re.findall(r'\b(\d+)\b', prompt)
        if numbers:
            row_count = int(numbers[0])
            
        # Detect required fields
        required_fields = []
        if 'name' in prompt_lower:
            required_fields.append('name')
        if any(word in prompt_lower for word in ['email', 'e-mail']):
            required_fields.append('email')
        if any(word in prompt_lower for word in ['age', 'birth', 'born']):
            required_fields.append('age')
        if any(word in prompt_lower for word in ['phone', 'contact', 'mobile']):
            required_fields.append('phone')
        if any(word in prompt_lower for word in ['address', 'location', 'city', 'country']):
            required_fields.append('address')
            
        return {
            'domains': domains,
            'row_count': row_count,
            'required_fields': required_fields,
            'complexity': len(domains) + len(required_fields)
        }

    def generate_demographic_aware_value(self, field_name: str, field_type: str, 
                                       age_distribution: str, region: str, 
                                       include_outliers: bool = False) -> Any:
        """Generate demographically aware field values using Julius.ai API or local fallback"""
        
        # Try Julius.ai API first if enabled
        if self.use_api and self.api_client:
            try:
                api_values = self.api_client.enhance_field_demographics(
                    field_name=field_name,
                    field_type=field_type,
                    age_distribution=age_distribution,
                    region=region,
                    sample_size=1
                )
                
                if api_values and len(api_values) > 0:
                    logging.debug(f"✅ Julius.ai API generated value for {field_name}")
                    return api_values[0]
                else:
                    logging.debug(f"⚠️ Julius.ai API returned empty result for {field_name}, using local fallback")
                    
            except Exception as e:
                logging.warning(f"⚠️ Julius.ai API error for {field_name}: {str(e)}, using local fallback")
        
        # Local fallback generation
        if field_name.lower() in ['name', 'first_name', 'last_name', 'full_name']:
            return self._generate_demographic_name(age_distribution, region)
            
        elif field_name.lower() in ['email', 'email_address']:
            return self._generate_demographic_email(age_distribution, region)
            
        elif field_name.lower() in ['age', 'age_years']:
            return self._generate_demographic_age(age_distribution, include_outliers)
            
        elif field_name.lower() in ['phone', 'phone_number', 'mobile']:
            return self._generate_demographic_phone(region)
            
        elif field_name.lower() in ['city', 'location', 'address']:
            return self._generate_demographic_location(region)
            
        else:
            # Generic field generation with demographic influence
            return self._generate_generic_field(field_name, field_type, region, include_outliers)

    def _generate_demographic_name(self, age_distribution: str, region: str) -> str:
        """Generate names based on age and region demographics"""
        profile = self.demographic_profiles.get(age_distribution, self.demographic_profiles['millennials'])
        
        # Choose region based on weights
        if region == 'global':
            chosen_region = random.choices(
                list(profile.region_weights.keys()),
                weights=list(profile.region_weights.values())
            )[0]
        else:
            chosen_region = region.replace('-', '-')
            
        names = profile.name_patterns.get(chosen_region, profile.name_patterns['north-america'])
        first_name = random.choice(names)
        
        # Generate last names based on region
        last_names = {
            'north-america': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'],
            'europe': ['Mueller', 'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer', 'Wagner', 'Becker'],
            'asia-pacific': ['Tanaka', 'Suzuki', 'Takahashi', 'Watanabe', 'Ito', 'Yamamoto', 'Nakamura', 'Kobayashi'],
            'india': ['Sharma', 'Verma', 'Singh', 'Kumar', 'Gupta', 'Agarwal', 'Jain', 'Patel']
        }
        
        last_name = random.choice(last_names.get(chosen_region, last_names['north-america']))
        return f"{first_name} {last_name}"

    def _generate_demographic_email(self, age_distribution: str, region: str) -> str:
        """Generate emails based on age demographics"""
        profile = self.demographic_profiles.get(age_distribution, self.demographic_profiles['millennials'])
        
        # Choose email provider based on age group preferences
        provider = random.choices(
            list(profile.email_providers.keys()),
            weights=list(profile.email_providers.values())
        )[0]
        
        # Generate username patterns based on age
        patterns = {
            'gen-z': ['{}{}{}', '{}.{}', '{}_{}_{}', '{}_{}'],
            'millennials': ['{}.{}', '{}{}', '{}_{}'],
            'gen-x': ['{}.{}', '{}{}'],
            'boomers': ['{}.{}', '{}{}']
        }
        
        pattern = random.choice(patterns.get(age_distribution, patterns['millennials']))
        
        # Generate base username components
        first_part = random.choice(['john', 'mary', 'david', 'sarah', 'mike', 'anna', 'alex', 'lisa'])
        second_part = random.choice(['smith', 'jones', 'brown', 'davis', '123', '2024', 'work'])
        third_part = random.choice(['01', '99', 'x', ''])
        
        username = pattern.format(first_part, second_part, third_part).replace('_', '').replace('..', '.')
        return f"{username}@{provider}"

    def _generate_demographic_age(self, age_distribution: str, include_outliers: bool) -> int:
        """Generate age based on demographic distribution"""
        profile = self.demographic_profiles.get(age_distribution, self.demographic_profiles['millennials'])
        
        # Choose age range based on distribution
        age_range = random.choices(
            list(profile.age_distribution.keys()),
            weights=list(profile.age_distribution.values())
        )[0]
        
        # Parse age range and generate specific age
        if '-' in age_range:
            min_age, max_age = map(int, age_range.split('-'))
        else:
            min_age = max_age = int(age_range.replace('+', ''))
            
        age = random.randint(min_age, max_age)
        
        # Add outliers if requested (5% chance)
        if include_outliers and random.random() < 0.05:
            outlier_ranges = [(16, 17), (85, 95)]  # Very young or very old
            outlier_min, outlier_max = random.choice(outlier_ranges)
            age = random.randint(outlier_min, outlier_max)
            
        return age

    def _generate_demographic_phone(self, region: str) -> str:
        """Generate phone numbers based on region"""
        formats = {
            'north-america': '+1-{}-{}-{}',
            'europe': '+{}-{}-{}-{}',
            'asia-pacific': '+{}-{}-{}-{}',
            'india': '+91-{}-{}-{}'
        }
        
        format_pattern = formats.get(region, formats['north-america'])
        
        if region == 'north-america':
            area_code = random.randint(200, 999)
            exchange = random.randint(200, 999)
            number = random.randint(1000, 9999)
            return format_pattern.format(area_code, exchange, number)
        elif region == 'india':
            area_code = random.randint(70, 99)
            number1 = random.randint(100, 999)
            number2 = random.randint(1000, 9999)
            return format_pattern.format(area_code, number1, number2)
        else:
            country_code = random.randint(30, 99)
            area_code = random.randint(10, 999)
            number1 = random.randint(100, 999)
            number2 = random.randint(1000, 9999)
            return format_pattern.format(country_code, area_code, number1, number2)

    def _generate_demographic_location(self, region: str) -> str:
        """Generate locations based on region"""
        cities = {
            'north-america': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Toronto', 'Vancouver'],
            'europe': ['London', 'Paris', 'Berlin', 'Madrid', 'Rome', 'Amsterdam'],
            'asia-pacific': ['Tokyo', 'Seoul', 'Sydney', 'Singapore', 'Bangkok', 'Manila'],
            'india': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad']
        }
        
        city_list = cities.get(region, cities['north-america'])
        return random.choice(city_list)

    def _generate_generic_field(self, field_name: str, field_type: str, region: str, include_outliers: bool) -> Any:
        """Generate generic fields with demographic influence"""
        
        if 'rating' in field_name.lower():
            base_rating = round(random.uniform(3.5, 4.8), 1)
            if include_outliers and random.random() < 0.10:
                base_rating = round(random.uniform(1.0, 3.0), 1)  # Bad outlier
            return base_rating
            
        elif 'price' in field_name.lower() or 'cost' in field_name.lower():
            base_price = random.randint(50, 500)
            if include_outliers and random.random() < 0.10:
                base_price = random.randint(1000, 5000)  # Expensive outlier
            return base_price
            
        elif 'salary' in field_name.lower() or 'income' in field_name.lower():
            regional_multipliers = {
                'north-america': 1.2,
                'europe': 1.0,
                'asia-pacific': 0.8,
                'india': 0.4
            }
            multiplier = regional_multipliers.get(region, 1.0)
            base_salary = int(random.randint(40000, 120000) * multiplier)
            
            if include_outliers and random.random() < 0.05:
                base_salary = int(random.randint(200000, 500000) * multiplier)  # High earner
            return base_salary
            
        else:
            # Default generation
            return f"Generated_{field_name}_{random.randint(1, 1000)}"

    def apply_conditional_logic(self, data: List[Dict], age_conditions: str, 
                              min_age: Optional[int] = None, max_age: Optional[int] = None) -> List[Dict]:
        """Apply conditional logic to generated data"""
        
        if age_conditions == 'none':
            return data
            
        filtered_data = []
        
        for row in data:
            age = row.get('age', 25)  # Default age if not present
            
            if age_conditions == 'adults' and age <= 18:
                row['age'] = random.randint(19, 65)
            elif age_conditions == 'young-adults' and not (18 < age < 30):
                row['age'] = random.randint(19, 29)
            elif age_conditions == 'working-age' and not (25 < age < 65):
                row['age'] = random.randint(26, 64)
            elif age_conditions == 'seniors' and age <= 60:
                row['age'] = random.randint(61, 85)
            elif age_conditions == 'custom' and min_age and max_age:
                if not (min_age <= age <= max_age):
                    row['age'] = random.randint(min_age, max_age)
                    
            filtered_data.append(row)
            
        return filtered_data

    def validate_data_fields(self, data: List[Dict], email_validation: bool = True, 
                           data_validation: bool = True) -> List[Dict]:
        """Validate and correct data fields"""
        
        for row in data:
            # Email validation
            if email_validation and 'email' in row:
                email = row['email']
                if '@' not in email or '.' not in email:
                    # Fix malformed email
                    username = email.split('@')[0] if '@' in email else email.replace(' ', '')
                    provider = random.choice(list(self.email_providers.keys()))
                    row['email'] = f"{username}@{provider}"
                    
            # Phone number validation
            if data_validation and 'phone' in row:
                phone = str(row['phone'])
                if not any(char.isdigit() for char in phone):
                    row['phone'] = f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"
                    
            # Date validation
            if data_validation:
                for key, value in row.items():
                    if 'date' in key.lower() and isinstance(value, str):
                        try:
                            datetime.strptime(value, '%Y-%m-%d')
                        except ValueError:
                            # Generate valid date
                            base_date = datetime.now() - timedelta(days=random.randint(0, 365))
                            row[key] = base_date.strftime('%Y-%m-%d')
                            
        return data

    def add_outliers(self, data: List[Dict], outlier_percentage: float = 0.05) -> List[Dict]:
        """Add outliers to specified percentage of data"""
        
        outlier_count = max(1, int(len(data) * outlier_percentage))
        outlier_indices = random.sample(range(len(data)), min(outlier_count, len(data)))
        
        for idx in outlier_indices:
            row = data[idx]
            
            # Add outlier characteristics
            for key, value in row.items():
                if key == 'age' and isinstance(value, int):
                    # Extreme age outliers
                    row[key] = random.choice([16, 17, 85, 90, 95])
                elif key == 'rating' and isinstance(value, (int, float)):
                    # Extreme rating outliers
                    row[key] = random.choice([1.0, 5.0])
                elif 'price' in key.lower() and isinstance(value, (int, float)):
                    # Price outliers (very cheap or very expensive)
                    if random.random() < 0.5:
                        row[key] = random.randint(1, 10)  # Very cheap
                    else:
                        row[key] = random.randint(1000, 5000)  # Very expensive
                elif 'salary' in key.lower() and isinstance(value, (int, float)):
                    # Salary outliers
                    row[key] = random.choice([15000, 500000, 1000000])  # Very low or very high
                    
        return data

    def analyze_and_enhance_data(self, data: List[Dict], advanced_options: Dict) -> Dict[str, Any]:
        """
        Comprehensive data analysis and enhancement using Julius.ai API
        
        Args:
            data: List of data records to analyze and enhance
            advanced_options: Advanced options for analysis (age_distribution, region, etc.)
            
        Returns:
            Dictionary containing enhanced data and analytics summary
        """
        
        # Extract options
        age_distribution = advanced_options.get("age_distribution", "balanced")
        region = advanced_options.get("demographics_region", "global")
        include_outliers = advanced_options.get("include_outliers", False)
        
        start_time = datetime.now()
        
        # Try Julius.ai API for comprehensive analysis
        if self.use_api and self.api_client and len(data) > 0:
            try:
                logging.info(f"🚀 Sending {len(data)} records to Julius.ai for comprehensive analysis")
                
                api_response = self.api_client.analyze_demographic_data(
                    data=data,
                    demographic_focus=age_distribution,
                    region=region,
                    include_outliers=include_outliers
                )
                
                if api_response.success:
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    logging.info(f"✅ Julius.ai API analysis completed in {api_response.processing_time}s")
                    logging.info(f"📊 Tokens used: {api_response.tokens_used}")
                    
                    return {
                        'enhanced_data': api_response.enhanced_data,
                        'analytics_summary': api_response.analytics_summary,
                        'processing_time': api_response.processing_time,
                        'tokens_used': api_response.tokens_used,
                        'source': 'julius_ai_api',
                        'api_success': True
                    }
                else:
                    logging.warning(f"⚠️ Julius.ai API analysis failed: {api_response.error_message}")
                    
            except Exception as e:
                logging.error(f"❌ Julius.ai API comprehensive analysis error: {str(e)}")
        
        # Fallback to local processing
        logging.info("🔄 Using local processing for data analysis and enhancement")
        
        # Apply local enhancements step by step
        enhanced_data = data.copy()
        
        # 1. Enhance fields with demographic awareness
        if advanced_options.get("enable_analytics", False):
            for i, row in enumerate(enhanced_data):
                for field_name, field_value in row.items():
                    if field_name.lower() in ['name', 'email', 'age', 'phone', 'city', 'location']:
                        try:
                            enhanced_value = self.generate_demographic_aware_value(
                                field_name=field_name,
                                field_type=type(field_value).__name__,
                                age_distribution=age_distribution,
                                region=region,
                                include_outliers=include_outliers
                            )
                            enhanced_data[i][field_name] = enhanced_value
                        except Exception as e:
                            logging.debug(f"Field enhancement failed for {field_name}: {str(e)}")
                            continue
        
        # 2. Apply conditional logic
        age_conditions = advanced_options.get("age_conditions", "none")
        min_age = advanced_options.get("min_age")
        max_age = advanced_options.get("max_age")
        
        if age_conditions != "none":
            enhanced_data = self.apply_conditional_logic(
                enhanced_data, age_conditions, 
                int(min_age) if min_age else None,
                int(max_age) if max_age else None
            )
        
        # 3. Validate and correct data fields
        enhanced_data = self.validate_data_fields(
            enhanced_data,
            email_validation=advanced_options.get("email_validation", True),
            data_validation=advanced_options.get("data_validation", True)
        )
        
        # 4. Add outliers if requested
        if include_outliers:
            enhanced_data = self.add_outliers(enhanced_data, outlier_percentage=0.08)
        
        # 5. Generate analytics summary
        analytics_summary = self.generate_analytics_summary(enhanced_data, advanced_options)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'enhanced_data': enhanced_data,
            'analytics_summary': analytics_summary,
            'processing_time': processing_time,
            'tokens_used': 0,
            'source': 'local_processing',
            'api_success': False
        }

    def generate_analytics_summary(self, data: List[Dict], advanced_options: Dict) -> Dict[str, Any]:
        """Generate analytics summary for the generated data"""
        
        summary = {
            'total_records': len(data),
            'generation_timestamp': datetime.now().isoformat(),
            'demographic_analysis': {},
            'data_quality_metrics': {},
            'field_analysis': {}
        }
        
        # Age distribution analysis
        ages = [row.get('age') for row in data if row.get('age')]
        if ages:
            age_groups = {
                'Gen-Z (18-26)': len([a for a in ages if 18 <= a <= 26]),
                'Millennials (27-42)': len([a for a in ages if 27 <= a <= 42]),
                'Gen-X (43-58)': len([a for a in ages if 43 <= a <= 58]),
                'Boomers (59+)': len([a for a in ages if a >= 59])
            }
            
            total_with_age = sum(age_groups.values())
            if total_with_age > 0:
                age_percentages = {k: round((v / total_with_age) * 100, 1) for k, v in age_groups.items()}
                summary['demographic_analysis']['age_distribution'] = age_percentages
                
        # Email provider analysis
        emails = [row.get('email', '') for row in data if row.get('email')]
        if emails:
            providers = {}
            for email in emails:
                if '@' in email:
                    provider = email.split('@')[1]
                    providers[provider] = providers.get(provider, 0) + 1
                    
            total_emails = len(emails)
            provider_percentages = {k: round((v / total_emails) * 100, 1) for k, v in providers.items()}
            summary['data_quality_metrics']['email_providers'] = provider_percentages
            
        # Field completeness analysis
        if data:
            field_completeness = {}
            total_records = len(data)
            
            all_fields = set()
            for row in data:
                all_fields.update(row.keys())
                
            for field in all_fields:
                non_empty_count = len([row for row in data if row.get(field) not in [None, '', 'N/A']])
                field_completeness[field] = round((non_empty_count / total_records) * 100, 1)
                
            summary['field_analysis']['completeness'] = field_completeness
            
        # Outlier detection
        if advanced_options.get('include_outliers'):
            outlier_fields = []
            
            for field in ['age', 'rating', 'price', 'salary']:
                values = [row.get(field) for row in data if isinstance(row.get(field), (int, float))]
                if values and len(values) > 1:
                    mean_val = sum(values) / len(values)
                    std_dev = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5
                    
                    outliers = [v for v in values if abs(v - mean_val) > 2 * std_dev]
                    if outliers:
                        outlier_fields.append({
                            'field': field,
                            'outlier_count': len(outliers),
                            'outlier_percentage': round((len(outliers) / len(values)) * 100, 1)
                        })
                        
            summary['data_quality_metrics']['outliers'] = outlier_fields
            
        return summary
