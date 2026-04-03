"""
Comprehensive Data Analyzer for Synthetic Data Generation
Provides advanced analytics, demographics analysis, and data insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import re
from collections import Counter, defaultdict
import json
import logging

class DataAnalyzer:
    """
    Advanced data analysis engine for synthetic data
    Provides demographic analysis, statistical insights, and data quality metrics
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analysis_cache = {}
        
    def analyze_dataset(self, data: List[Dict[str, Any]], 
                       analysis_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Comprehensive analysis of the entire dataset
        
        Args:
            data: List of data records
            analysis_options: Options for analysis depth and focus areas
            
        Returns:
            Complete analysis results with demographics, statistics, and insights
        """
        if not data:
            return {"error": "No data provided for analysis"}
            
        try:
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(data)
            
            # Core analysis components
            basic_stats = self._calculate_basic_statistics(df)
            demographic_analysis = self._analyze_demographics(df)
            data_quality = self._assess_data_quality(df)
            field_analysis = self._analyze_fields(df)
            distribution_analysis = self._analyze_distributions(df)
            correlation_analysis = self._analyze_correlations(df)
            pattern_analysis = self._analyze_patterns(df)
            
            # Generate insights and recommendations
            insights = self._generate_insights(df, {
                'basic_stats': basic_stats,
                'demographics': demographic_analysis,
                'quality': data_quality,
                'fields': field_analysis,
                'distributions': distribution_analysis,
                'correlations': correlation_analysis,
                'patterns': pattern_analysis
            })
            
            # Compile comprehensive results
            analysis_result = {
                'timestamp': datetime.now().isoformat(),
                'dataset_info': {
                    'total_records': len(df),
                    'total_fields': len(df.columns),
                    'field_names': list(df.columns),
                    'data_types': df.dtypes.to_dict()
                },
                'basic_statistics': basic_stats,
                'demographic_analysis': demographic_analysis,
                'data_quality': data_quality,
                'field_analysis': field_analysis,
                'distribution_analysis': distribution_analysis,
                'correlation_analysis': correlation_analysis,
                'pattern_analysis': pattern_analysis,
                'insights_and_recommendations': insights,
                'visualization_data': self._prepare_visualization_data(df),
                'analysis_metadata': {
                    'analysis_version': '2.0',
                    'processing_time': datetime.now().isoformat(),
                    'options_used': analysis_options or {}
                }
            }
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error in dataset analysis: {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic statistical measures"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        text_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        stats = {
            'record_count': len(df),
            'field_count': len(df.columns),
            'numeric_fields': len(numeric_columns),
            'text_fields': len(text_columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        }
        
        # Numeric field statistics
        if numeric_columns:
            numeric_stats = df[numeric_columns].describe().to_dict()
            stats['numeric_statistics'] = numeric_stats
        
        # Text field statistics
        if text_columns:
            text_stats = {}
            for col in text_columns:
                text_stats[col] = {
                    'unique_values': df[col].nunique(),
                    'most_common': df[col].value_counts().head(5).to_dict(),
                    'average_length': df[col].astype(str).str.len().mean(),
                    'null_count': df[col].isnull().sum()
                }
            stats['text_statistics'] = text_stats
            
        return stats
    
    def _analyze_demographics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze demographic patterns in the data"""
        demographics = {
            'age_analysis': {},
            'gender_analysis': {},
            'location_analysis': {},
            'name_analysis': {},
            'email_analysis': {},
            'phone_analysis': {}
        }
        
        # Age analysis
        age_fields = [col for col in df.columns if 'age' in col.lower()]
        for field in age_fields:
            if field in df.columns:
                demographics['age_analysis'][field] = {
                    'distribution': df[field].value_counts().to_dict(),
                    'age_groups': self._categorize_ages(df[field]),
                    'average_age': df[field].mean() if pd.api.types.is_numeric_dtype(df[field]) else None
                }
        
        # Gender analysis
        gender_fields = [col for col in df.columns if 'gender' in col.lower() or 'sex' in col.lower()]
        for field in gender_fields:
            if field in df.columns:
                demographics['gender_analysis'][field] = {
                    'distribution': df[field].value_counts().to_dict(),
                    'gender_ratio': self._calculate_gender_ratio(df[field])
                }
        
        # Location analysis
        location_fields = [col for col in df.columns if any(loc in col.lower() for loc in ['city', 'state', 'country', 'address', 'location'])]
        for field in location_fields:
            if field in df.columns:
                demographics['location_analysis'][field] = {
                    'top_locations': df[field].value_counts().head(10).to_dict(),
                    'unique_locations': df[field].nunique(),
                    'geographic_diversity': df[field].nunique() / len(df) if len(df) > 0 else 0
                }
        
        # Name analysis
        name_fields = [col for col in df.columns if 'name' in col.lower()]
        for field in name_fields:
            if field in df.columns:
                demographics['name_analysis'][field] = {
                    'name_patterns': self._analyze_name_patterns(df[field]),
                    'cultural_diversity': self._analyze_cultural_names(df[field])
                }
        
        # Email analysis
        email_fields = [col for col in df.columns if 'email' in col.lower()]
        for field in email_fields:
            if field in df.columns:
                demographics['email_analysis'][field] = {
                    'domain_distribution': self._analyze_email_domains(df[field]),
                    'email_patterns': self._analyze_email_patterns(df[field])
                }
        
        # Phone analysis
        phone_fields = [col for col in df.columns if 'phone' in col.lower()]
        for field in phone_fields:
            if field in df.columns:
                demographics['phone_analysis'][field] = {
                    'country_codes': self._analyze_phone_patterns(df[field]),
                    'format_patterns': self._analyze_phone_formats(df[field])
                }
        
        return demographics
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data quality metrics"""
        quality_metrics = {
            'completeness': {},
            'consistency': {},
            'validity': {},
            'uniqueness': {},
            'accuracy_indicators': {}
        }
        
        # Completeness analysis
        null_counts = df.isnull().sum()
        quality_metrics['completeness'] = {
            'overall_completeness': (1 - null_counts.sum() / (len(df) * len(df.columns))) * 100,
            'field_completeness': ((len(df) - null_counts) / len(df) * 100).to_dict(),
            'complete_records': len(df.dropna()),
            'incomplete_records': len(df) - len(df.dropna())
        }
        
        # Consistency analysis
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for formatting consistency
                patterns = df[col].dropna().astype(str).apply(self._extract_pattern).value_counts()
                quality_metrics['consistency'][col] = {
                    'pattern_consistency': len(patterns) <= 3,  # Good if few patterns
                    'dominant_pattern': patterns.index[0] if len(patterns) > 0 else None,
                    'pattern_distribution': patterns.head(5).to_dict()
                }
        
        # Validity analysis
        for col in df.columns:
            quality_metrics['validity'][col] = {
                'has_invalid_values': self._check_invalid_values(df[col]),
                'data_type_consistency': df[col].dtype != 'object' or self._check_type_consistency(df[col])
            }
        
        # Uniqueness analysis
        for col in df.columns:
            unique_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
            quality_metrics['uniqueness'][col] = {
                'unique_values': df[col].nunique(),
                'uniqueness_ratio': unique_ratio,
                'is_likely_identifier': unique_ratio > 0.95,
                'duplicates': len(df) - df[col].nunique()
            }
        
        # Overall quality score
        quality_metrics['overall_quality_score'] = self._calculate_quality_score(quality_metrics)
        
        return quality_metrics
    
    def _analyze_fields(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze individual fields in detail"""
        field_analysis = {}
        
        for col in df.columns:
            field_info = {
                'field_name': col,
                'data_type': str(df[col].dtype),
                'unique_values': df[col].nunique(),
                'null_values': df[col].isnull().sum(),
                'most_frequent': df[col].value_counts().head(3).to_dict() if df[col].nunique() > 0 else {},
                'field_type_classification': self._classify_field_type(col, df[col])
            }
            
            # Add specific analysis based on field type
            if pd.api.types.is_numeric_dtype(df[col]):
                field_info['numeric_analysis'] = {
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'mean': df[col].mean(),
                    'median': df[col].median(),
                    'std': df[col].std(),
                    'outliers': self._detect_outliers(df[col])
                }
            
            if df[col].dtype == 'object':
                field_info['text_analysis'] = {
                    'avg_length': df[col].astype(str).str.len().mean(),
                    'max_length': df[col].astype(str).str.len().max(),
                    'min_length': df[col].astype(str).str.len().min(),
                    'common_patterns': self._find_common_patterns(df[col])
                }
            
            field_analysis[col] = field_info
        
        return field_analysis
    
    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data distributions"""
        distributions = {}
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            distributions[col] = {
                'distribution_type': self._identify_distribution_type(df[col]),
                'histogram_data': self._create_histogram_data(df[col]),
                'percentiles': df[col].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).to_dict(),
                'skewness': df[col].skew(),
                'kurtosis': df[col].kurtosis()
            }
        
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            value_counts = df[col].value_counts()
            distributions[col] = {
                'category_distribution': value_counts.to_dict(),
                'entropy': self._calculate_entropy(value_counts),
                'concentration_ratio': value_counts.iloc[0] / len(df) if len(value_counts) > 0 else 0
            }
        
        return distributions
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between fields"""
        correlations = {}
        
        # Numeric correlations
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            correlations['numeric_correlations'] = {
                'correlation_matrix': corr_matrix.to_dict(),
                'strong_correlations': self._find_strong_correlations(corr_matrix),
                'correlation_insights': self._interpret_correlations(corr_matrix)
            }
        
        # Categorical associations
        categorical_df = df.select_dtypes(include=['object'])
        if len(categorical_df.columns) > 1:
            correlations['categorical_associations'] = self._analyze_categorical_associations(categorical_df)
        
        return correlations
    
    def _analyze_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns in the data"""
        patterns = {
            'temporal_patterns': {},
            'sequential_patterns': {},
            'format_patterns': {},
            'business_logic_patterns': {}
        }
        
        # Look for date/time patterns
        date_columns = [col for col in df.columns if any(date_word in col.lower() for date_word in ['date', 'time', 'created', 'updated'])]
        for col in date_columns:
            if col in df.columns:
                patterns['temporal_patterns'][col] = self._analyze_temporal_patterns(df[col])
        
        # Format patterns for text fields
        for col in df.select_dtypes(include=['object']).columns:
            patterns['format_patterns'][col] = {
                'common_formats': self._identify_format_patterns(df[col]),
                'format_consistency': self._check_format_consistency(df[col])
            }
        
        # Business logic patterns
        patterns['business_logic_patterns'] = self._identify_business_patterns(df)
        
        return patterns
    
    def _generate_insights(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights from analysis results"""
        insights = {
            'data_quality_insights': [],
            'demographic_insights': [],
            'distribution_insights': [],
            'correlation_insights': [],
            'recommendations': [],
            'potential_issues': [],
            'optimization_suggestions': []
        }
        
        # Data quality insights
        completeness = analysis_results['quality']['completeness']['overall_completeness']
        if completeness < 95:
            insights['data_quality_insights'].append(f"Data completeness is {completeness:.1f}%, consider improving data collection")
        
        # Demographic insights
        demo_analysis = analysis_results['demographics']
        if demo_analysis.get('age_analysis'):
            insights['demographic_insights'].append("Age distribution analysis available")
        
        # Distribution insights
        for field, dist_info in analysis_results['distributions'].items():
            if isinstance(dist_info, dict) and 'skewness' in dist_info:
                if abs(dist_info['skewness']) > 2:
                    insights['distribution_insights'].append(f"Field '{field}' shows high skewness ({dist_info['skewness']:.2f})")
        
        # Recommendations
        insights['recommendations'].extend(self._generate_recommendations(df, analysis_results))
        
        return insights
    
    def _prepare_visualization_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data for visualization components"""
        viz_data = {
            'charts': [],
            'summary_cards': [],
            'tables': []
        }
        
        # Summary cards
        viz_data['summary_cards'] = [
            {'title': 'Total Records', 'value': len(df), 'type': 'number'},
            {'title': 'Total Fields', 'value': len(df.columns), 'type': 'number'},
            {'title': 'Completeness', 'value': f"{(1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100:.1f}%", 'type': 'percentage'},
            {'title': 'Unique Records', 'value': len(df.drop_duplicates()), 'type': 'number'}
        ]
        
        # Chart data for numeric fields
        numeric_columns = df.select_dtypes(include=[np.number]).columns[:5]  # Limit to first 5
        for col in numeric_columns:
            viz_data['charts'].append({
                'type': 'histogram',
                'title': f'Distribution of {col}',
                'data': df[col].value_counts().head(10).to_dict(),
                'field': col
            })
        
        # Chart data for categorical fields
        categorical_columns = df.select_dtypes(include=['object']).columns[:5]  # Limit to first 5
        for col in categorical_columns:
            viz_data['charts'].append({
                'type': 'pie',
                'title': f'Distribution of {col}',
                'data': df[col].value_counts().head(8).to_dict(),
                'field': col
            })
        
        return viz_data
    
    # Helper methods for various analysis functions
    def _categorize_ages(self, age_series: pd.Series) -> Dict[str, int]:
        """Categorize ages into groups"""
        if not pd.api.types.is_numeric_dtype(age_series):
            return {}
        
        age_groups = {
            'Gen Z (18-27)': 0, 'Millennials (28-43)': 0, 'Gen X (44-59)': 0, 'Boomers (60+)': 0
        }
        
        for age in age_series.dropna():
            if 18 <= age <= 27:
                age_groups['Gen Z (18-27)'] += 1
            elif 28 <= age <= 43:
                age_groups['Millennials (28-43)'] += 1
            elif 44 <= age <= 59:
                age_groups['Gen X (44-59)'] += 1
            elif age >= 60:
                age_groups['Boomers (60+)'] += 1
        
        return age_groups
    
    def _calculate_gender_ratio(self, gender_series: pd.Series) -> Dict[str, float]:
        """Calculate gender distribution ratios"""
        counts = gender_series.value_counts()
        total = len(gender_series.dropna())
        return {gender: (count/total)*100 for gender, count in counts.items()} if total > 0 else {}
    
    def _analyze_name_patterns(self, name_series: pd.Series) -> Dict[str, Any]:
        """Analyze patterns in names"""
        names = name_series.dropna().astype(str)
        return {
            'avg_length': names.str.len().mean(),
            'has_middle_names': (names.str.count(' ') > 1).sum(),
            'common_first_letters': names.str[0].value_counts().head(5).to_dict()
        }
    
    def _analyze_cultural_names(self, name_series: pd.Series) -> Dict[str, Any]:
        """Analyze cultural diversity in names"""
        # This is a simplified version - could be enhanced with more sophisticated name origin detection
        names = name_series.dropna().astype(str)
        return {
            'unique_names': names.nunique(),
            'name_diversity_ratio': names.nunique() / len(names) if len(names) > 0 else 0
        }
    
    def _analyze_email_domains(self, email_series: pd.Series) -> Dict[str, int]:
        """Analyze email domain distribution"""
        emails = email_series.dropna().astype(str)
        domains = emails.str.extract(r'@(.+)')[0].value_counts()
        return domains.head(10).to_dict()
    
    def _analyze_email_patterns(self, email_series: pd.Series) -> Dict[str, Any]:
        """Analyze email format patterns"""
        emails = email_series.dropna().astype(str)
        return {
            'valid_format_count': emails.str.contains(r'^[^@]+@[^@]+\.[^@]+$', regex=True).sum(),
            'invalid_format_count': (~emails.str.contains(r'^[^@]+@[^@]+\.[^@]+$', regex=True)).sum()
        }
    
    def _analyze_phone_patterns(self, phone_series: pd.Series) -> Dict[str, Any]:
        """Analyze phone number patterns"""
        phones = phone_series.dropna().astype(str)
        return {
            'with_country_code': phones.str.startswith('+').sum(),
            'us_format': phones.str.contains(r'\(\d{3}\)|\d{3}-\d{3}-\d{4}', regex=True).sum()
        }
    
    def _analyze_phone_formats(self, phone_series: pd.Series) -> Dict[str, int]:
        """Analyze phone number format patterns"""
        phones = phone_series.dropna().astype(str)
        formats = phones.apply(self._extract_phone_format).value_counts()
        return formats.head(5).to_dict()
    
    def _extract_pattern(self, value: str) -> str:
        """Extract general pattern from string"""
        if pd.isna(value):
            return 'null'
        pattern = re.sub(r'\d', 'N', str(value))
        pattern = re.sub(r'[a-zA-Z]', 'A', pattern)
        return pattern
    
    def _extract_phone_format(self, phone: str) -> str:
        """Extract phone number format pattern"""
        if pd.isna(phone):
            return 'null'
        pattern = re.sub(r'\d', 'N', str(phone))
        return pattern
    
    def _check_invalid_values(self, series: pd.Series) -> bool:
        """Check for obviously invalid values"""
        if series.dtype == 'object':
            invalid_patterns = ['null', 'none', 'n/a', '', 'invalid', 'test']
            return series.astype(str).str.lower().isin(invalid_patterns).any()
        return False
    
    def _check_type_consistency(self, series: pd.Series) -> bool:
        """Check if object series has consistent data types"""
        try:
            pd.to_numeric(series.dropna())
            return True
        except:
            try:
                pd.to_datetime(series.dropna())
                return True
            except:
                return True  # Assume text is consistent
    
    def _calculate_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate overall data quality score"""
        completeness_score = quality_metrics['completeness']['overall_completeness']
        
        # Simple scoring - can be enhanced
        consistency_scores = []
        for field_consistency in quality_metrics['consistency'].values():
            if isinstance(field_consistency, dict) and 'pattern_consistency' in field_consistency:
                consistency_scores.append(90 if field_consistency['pattern_consistency'] else 60)
        
        avg_consistency = np.mean(consistency_scores) if consistency_scores else 80
        
        return (completeness_score + avg_consistency) / 2
    
    def _classify_field_type(self, field_name: str, series: pd.Series) -> str:
        """Classify the semantic type of a field"""
        field_lower = field_name.lower()
        
        if 'email' in field_lower:
            return 'email'
        elif 'phone' in field_lower:
            return 'phone'
        elif 'name' in field_lower:
            return 'name'
        elif 'age' in field_lower:
            return 'age'
        elif any(word in field_lower for word in ['address', 'city', 'state', 'country']):
            return 'location'
        elif 'id' in field_lower:
            return 'identifier'
        elif pd.api.types.is_numeric_dtype(series):
            return 'numeric'
        elif series.dtype == 'object':
            return 'categorical'
        else:
            return 'unknown'
    
    def _detect_outliers(self, series: pd.Series) -> Dict[str, Any]:
        """Detect outliers in numeric series"""
        if not pd.api.types.is_numeric_dtype(series):
            return {}
        
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        
        return {
            'count': len(outliers),
            'percentage': (len(outliers) / len(series)) * 100,
            'values': outliers.tolist()[:10]  # Show first 10 outliers
        }
    
    def _find_common_patterns(self, series: pd.Series) -> Dict[str, int]:
        """Find common patterns in text series"""
        patterns = series.dropna().astype(str).apply(self._extract_pattern).value_counts()
        return patterns.head(5).to_dict()
    
    def _identify_distribution_type(self, series: pd.Series) -> str:
        """Identify the type of distribution for numeric data"""
        if not pd.api.types.is_numeric_dtype(series):
            return 'non-numeric'
        
        skewness = series.skew()
        kurtosis = series.kurtosis()
        
        if abs(skewness) < 0.5 and abs(kurtosis) < 3:
            return 'normal'
        elif skewness > 1:
            return 'right-skewed'
        elif skewness < -1:
            return 'left-skewed'
        elif kurtosis > 3:
            return 'heavy-tailed'
        else:
            return 'unknown'
    
    def _create_histogram_data(self, series: pd.Series, bins: int = 10) -> Dict[str, Any]:
        """Create histogram data for visualization"""
        if not pd.api.types.is_numeric_dtype(series):
            return {}
        
        hist, bin_edges = np.histogram(series.dropna(), bins=bins)
        return {
            'counts': hist.tolist(),
            'bin_edges': bin_edges.tolist(),
            'bin_centers': ((bin_edges[:-1] + bin_edges[1:]) / 2).tolist()
        }
    
    def _calculate_entropy(self, value_counts: pd.Series) -> float:
        """Calculate entropy of categorical distribution"""
        probabilities = value_counts / value_counts.sum()
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return entropy
    
    def _find_strong_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find strong correlations in correlation matrix"""
        strong_corrs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > threshold:
                    strong_corrs.append({
                        'field1': corr_matrix.columns[i],
                        'field2': corr_matrix.columns[j],
                        'correlation': corr_value,
                        'strength': 'strong' if abs(corr_value) > 0.8 else 'moderate'
                    })
        
        return strong_corrs
    
    def _interpret_correlations(self, corr_matrix: pd.DataFrame) -> List[str]:
        """Generate interpretation of correlations"""
        interpretations = []
        strong_corrs = self._find_strong_correlations(corr_matrix)
        
        for corr in strong_corrs[:5]:  # Top 5 correlations
            direction = "positively" if corr['correlation'] > 0 else "negatively"
            interpretations.append(
                f"{corr['field1']} and {corr['field2']} are {direction} correlated ({corr['correlation']:.2f})"
            )
        
        return interpretations
    
    def _analyze_categorical_associations(self, categorical_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze associations between categorical variables"""
        # This would typically use Chi-square tests or Cramer's V
        # Simplified version for now
        associations = {}
        
        for col1 in categorical_df.columns:
            for col2 in categorical_df.columns:
                if col1 != col2:
                    # Simple association measure based on value overlap
                    cross_tab = pd.crosstab(categorical_df[col1], categorical_df[col2])
                    association_strength = cross_tab.max().max() / len(categorical_df)
                    
                    if association_strength > 0.3:  # Threshold for noteworthy association
                        associations[f"{col1}_vs_{col2}"] = {
                            'strength': association_strength,
                            'interpretation': f"Potential association between {col1} and {col2}"
                        }
        
        return associations
    
    def _analyze_temporal_patterns(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze temporal patterns in date/time data"""
        # This would need more sophisticated date parsing
        # Simplified version
        return {
            'pattern_detected': False,
            'note': 'Temporal analysis requires datetime conversion'
        }
    
    def _identify_format_patterns(self, series: pd.Series) -> Dict[str, int]:
        """Identify format patterns in text data"""
        formats = series.dropna().astype(str).apply(self._extract_pattern).value_counts()
        return formats.head(5).to_dict()
    
    def _check_format_consistency(self, series: pd.Series) -> float:
        """Check consistency of formats in text data"""
        formats = series.dropna().astype(str).apply(self._extract_pattern).value_counts()
        if len(formats) == 0:
            return 0.0
        return formats.iloc[0] / formats.sum()  # Ratio of most common format
    
    def _identify_business_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify business logic patterns"""
        patterns = {}
        
        # Example: Check if email domains correlate with other fields
        if 'email' in df.columns and len(df.columns) > 1:
            patterns['email_domain_patterns'] = "Email domain analysis available"
        
        # Example: Check age vs other demographic correlations
        age_cols = [col for col in df.columns if 'age' in col.lower()]
        if age_cols:
            patterns['age_related_patterns'] = f"Age analysis available for {len(age_cols)} fields"
        
        return patterns
    
    def _generate_recommendations(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Data quality recommendations
        completeness = analysis_results['quality']['completeness']['overall_completeness']
        if completeness < 90:
            recommendations.append(f"Improve data completeness (currently {completeness:.1f}%)")
        
        # Field-specific recommendations
        for field, field_info in analysis_results['fields'].items():
            if field_info['null_values'] > len(df) * 0.2:
                recommendations.append(f"Field '{field}' has high null rate ({field_info['null_values']} nulls)")
        
        # Distribution recommendations
        for field, dist_info in analysis_results['distributions'].items():
            if isinstance(dist_info, dict) and 'skewness' in dist_info:
                if abs(dist_info['skewness']) > 2:
                    recommendations.append(f"Consider normalizing '{field}' (high skewness: {dist_info['skewness']:.2f})")
        
        return recommendations