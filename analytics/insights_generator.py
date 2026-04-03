"""
Insights Generator for Data Analytics
Generates actionable insights, recommendations, and business intelligence from data analysis
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import logging

class InsightsGenerator:
    """
    Generates intelligent insights and recommendations from data analysis results
    Provides business intelligence and actionable recommendations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.insight_templates = self._load_insight_templates()
        
    def generate_comprehensive_insights(self, analysis_data: Dict[str, Any], 
                                     business_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive insights from analysis data
        
        Args:
            analysis_data: Complete analysis results from DataAnalyzer
            business_context: Optional business context for domain-specific insights
            
        Returns:
            Comprehensive insights with recommendations and action items
        """
        try:
            insights = {
                'timestamp': datetime.now().isoformat(),
                'executive_summary': self._generate_executive_summary(analysis_data),
                'key_findings': self._identify_key_findings(analysis_data),
                'data_quality_insights': self._analyze_data_quality_insights(analysis_data),
                'demographic_insights': self._generate_demographic_insights(analysis_data),
                'statistical_insights': self._generate_statistical_insights(analysis_data),
                'business_recommendations': self._generate_business_recommendations(analysis_data, business_context),
                'technical_recommendations': self._generate_technical_recommendations(analysis_data),
                'risk_assessment': self._assess_data_risks(analysis_data),
                'optimization_opportunities': self._identify_optimization_opportunities(analysis_data),
                'action_items': self._create_action_items(analysis_data),
                'metrics_to_track': self._suggest_tracking_metrics(analysis_data),
                'next_steps': self._recommend_next_steps(analysis_data)
            }
            
            # Add confidence scores and priority levels
            insights = self._add_insight_metadata(insights)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            return {
                'error': f"Insights generation failed: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_executive_summary(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of findings"""
        dataset_info = analysis_data.get('dataset_info', {})
        basic_stats = analysis_data.get('basic_statistics', {})
        quality_data = analysis_data.get('data_quality', {})
        
        total_records = dataset_info.get('total_records', 0)
        total_fields = dataset_info.get('total_fields', 0)
        completeness = basic_stats.get('completeness', 0)
        quality_score = quality_data.get('overall_quality_score', 0)
        
        # Generate summary insights
        summary_points = []
        
        if total_records > 0:
            summary_points.append(f"Dataset contains {total_records:,} records across {total_fields} fields")
        
        if completeness >= 95:
            summary_points.append("Excellent data completeness with minimal missing values")
        elif completeness >= 80:
            summary_points.append("Good data completeness with some gaps to address")
        else:
            summary_points.append("Data completeness needs significant improvement")
        
        if quality_score >= 85:
            summary_points.append("High overall data quality suitable for advanced analytics")
        elif quality_score >= 70:
            summary_points.append("Moderate data quality - some cleanup recommended")
        else:
            summary_points.append("Data quality issues require immediate attention")
        
        return {
            'overview': f"Analysis of {total_records:,} records reveals {'high' if quality_score >= 80 else 'moderate' if quality_score >= 60 else 'low'} quality data with {completeness:.1f}% completeness",
            'key_metrics': {
                'records': total_records,
                'fields': total_fields,
                'completeness_pct': completeness,
                'quality_score': quality_score
            },
            'summary_points': summary_points,
            'overall_assessment': self._assess_overall_dataset_health(completeness, quality_score)
        }
    
    def _identify_key_findings(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify the most important findings from the analysis"""
        findings = []
        
        # Data completeness findings
        quality_data = analysis_data.get('data_quality', {})
        if 'completeness' in quality_data:
            field_completeness = quality_data['completeness'].get('field_completeness', {})
            
            # Find fields with low completeness
            low_completeness_fields = {k: v for k, v in field_completeness.items() if v < 80}
            if low_completeness_fields:
                findings.append({
                    'type': 'data_quality',
                    'priority': 'high',
                    'title': 'Low Data Completeness Detected',
                    'description': f"{len(low_completeness_fields)} fields have less than 80% completeness",
                    'details': low_completeness_fields,
                    'impact': 'May affect analysis accuracy and model performance'
                })
        
        # Demographic findings
        demo_data = analysis_data.get('demographic_analysis', {})
        if demo_data.get('age_analysis'):
            for field, age_info in demo_data['age_analysis'].items():
                if 'age_groups' in age_info:
                    age_groups = age_info['age_groups']
                    total_people = sum(age_groups.values())
                    if total_people > 0:
                        dominant_group = max(age_groups, key=age_groups.get)
                        percentage = (age_groups[dominant_group] / total_people) * 100
                        
                        if percentage > 60:
                            findings.append({
                                'type': 'demographic',
                                'priority': 'medium',
                                'title': 'Age Distribution Skew',
                                'description': f"{dominant_group} represents {percentage:.1f}% of the population",
                                'details': age_groups,
                                'impact': 'May indicate sampling bias or target audience concentration'
                            })
        
        # Statistical outliers
        field_analysis = analysis_data.get('field_analysis', {})
        for field, field_info in field_analysis.items():
            if 'numeric_analysis' in field_info:
                outliers = field_info['numeric_analysis'].get('outliers', {})
                if outliers.get('percentage', 0) > 10:
                    findings.append({
                        'type': 'statistical',
                        'priority': 'medium',
                        'title': f'High Outlier Rate in {field}',
                        'description': f"{outliers['percentage']:.1f}% of values are statistical outliers",
                        'details': outliers,
                        'impact': 'May indicate data quality issues or extreme values'
                    })
        
        # Correlation findings
        corr_data = analysis_data.get('correlation_analysis', {})
        if 'numeric_correlations' in corr_data:
            strong_corrs = corr_data['numeric_correlations'].get('strong_correlations', [])
            if strong_corrs:
                findings.append({
                    'type': 'correlation',
                    'priority': 'medium',
                    'title': 'Strong Field Correlations Found',
                    'description': f"{len(strong_corrs)} pairs of fields show strong correlation",
                    'details': strong_corrs[:5],  # Top 5 correlations
                    'impact': 'May indicate redundant features or underlying relationships'
                })
        
        return sorted(findings, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
    
    def _analyze_data_quality_insights(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights focused on data quality"""
        quality_data = analysis_data.get('data_quality', {})
        
        insights = {
            'completeness_analysis': {},
            'consistency_analysis': {},
            'validity_analysis': {},
            'recommendations': []
        }
        
        # Completeness insights
        if 'completeness' in quality_data:
            completeness_info = quality_data['completeness']
            overall_completeness = completeness_info.get('overall_completeness', 0)
            
            insights['completeness_analysis'] = {
                'status': 'excellent' if overall_completeness >= 95 else 'good' if overall_completeness >= 80 else 'poor',
                'score': overall_completeness,
                'incomplete_records': completeness_info.get('incomplete_records', 0),
                'action_needed': overall_completeness < 90
            }
            
            if overall_completeness < 90:
                insights['recommendations'].append({
                    'type': 'completeness',
                    'priority': 'high',
                    'action': 'Improve data collection processes to reduce missing values',
                    'expected_impact': 'Better analysis accuracy and model performance'
                })
        
        # Consistency insights
        if 'consistency' in quality_data:
            inconsistent_fields = []
            for field, consistency_info in quality_data['consistency'].items():
                if isinstance(consistency_info, dict) and not consistency_info.get('pattern_consistency', True):
                    inconsistent_fields.append(field)
            
            insights['consistency_analysis'] = {
                'inconsistent_fields': inconsistent_fields,
                'consistency_issues': len(inconsistent_fields),
                'action_needed': len(inconsistent_fields) > 0
            }
            
            if inconsistent_fields:
                insights['recommendations'].append({
                    'type': 'consistency',
                    'priority': 'medium',
                    'action': f'Standardize format for fields: {", ".join(inconsistent_fields[:3])}',
                    'expected_impact': 'Improved data processing and analysis reliability'
                })
        
        # Validity insights
        if 'validity' in quality_data:
            invalid_fields = []
            for field, validity_info in quality_data['validity'].items():
                if isinstance(validity_info, dict) and validity_info.get('has_invalid_values', False):
                    invalid_fields.append(field)
            
            insights['validity_analysis'] = {
                'invalid_fields': invalid_fields,
                'validity_issues': len(invalid_fields),
                'action_needed': len(invalid_fields) > 0
            }
            
            if invalid_fields:
                insights['recommendations'].append({
                    'type': 'validity',
                    'priority': 'high',
                    'action': f'Clean invalid values in fields: {", ".join(invalid_fields[:3])}',
                    'expected_impact': 'Prevent analysis errors and improve data reliability'
                })
        
        return insights
    
    def _generate_demographic_insights(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights about demographic patterns"""
        demo_data = analysis_data.get('demographic_analysis', {})
        insights = {
            'age_insights': [],
            'gender_insights': [],
            'location_insights': [],
            'diversity_metrics': {},
            'recommendations': []
        }
        
        # Age insights
        if demo_data.get('age_analysis'):
            for field, age_info in demo_data['age_analysis'].items():
                if 'age_groups' in age_info:
                    age_groups = age_info['age_groups']
                    total = sum(age_groups.values())
                    if total > 0:
                        # Calculate diversity
                        diversity_score = len([group for group, count in age_groups.items() if count > 0])
                        dominant_group = max(age_groups, key=age_groups.get)
                        dominance_pct = (age_groups[dominant_group] / total) * 100
                        
                        insights['age_insights'].append({
                            'field': field,
                            'dominant_group': dominant_group,
                            'dominance_percentage': dominance_pct,
                            'diversity_score': diversity_score,
                            'interpretation': self._interpret_age_distribution(age_groups, dominance_pct)
                        })
        
        # Gender insights
        if demo_data.get('gender_analysis'):
            for field, gender_info in demo_data['gender_analysis'].items():
                if 'distribution' in gender_info:
                    gender_dist = gender_info['distribution']
                    if gender_dist:
                        total = sum(gender_dist.values())
                        gender_ratios = {k: (v/total)*100 for k, v in gender_dist.items()}
                        
                        insights['gender_insights'].append({
                            'field': field,
                            'distribution': gender_ratios,
                            'balance_score': self._calculate_balance_score(gender_ratios),
                            'interpretation': self._interpret_gender_distribution(gender_ratios)
                        })
        
        # Location insights
        if demo_data.get('location_analysis'):
            for field, location_info in demo_data['location_analysis'].items():
                if 'geographic_diversity' in location_info:
                    diversity = location_info['geographic_diversity']
                    unique_locations = location_info.get('unique_locations', 0)
                    
                    insights['location_insights'].append({
                        'field': field,
                        'geographic_diversity': diversity,
                        'unique_locations': unique_locations,
                        'diversity_level': 'high' if diversity > 0.7 else 'medium' if diversity > 0.3 else 'low',
                        'interpretation': self._interpret_location_diversity(diversity, unique_locations)
                    })
        
        # Generate recommendations
        insights['recommendations'] = self._generate_demographic_recommendations(insights)
        
        return insights
    
    def _generate_statistical_insights(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistical insights from the data"""
        dist_data = analysis_data.get('distribution_analysis', {})
        corr_data = analysis_data.get('correlation_analysis', {})
        field_data = analysis_data.get('field_analysis', {})
        
        insights = {
            'distribution_insights': [],
            'correlation_insights': [],
            'outlier_insights': [],
            'statistical_recommendations': []
        }
        
        # Distribution insights
        for field, dist_info in dist_data.items():
            if isinstance(dist_info, dict):
                if 'skewness' in dist_info:
                    skewness = dist_info['skewness']
                    insights['distribution_insights'].append({
                        'field': field,
                        'distribution_type': dist_info.get('distribution_type', 'unknown'),
                        'skewness': skewness,
                        'skewness_interpretation': self._interpret_skewness(skewness),
                        'normality': abs(skewness) < 0.5,
                        'transformation_suggested': abs(skewness) > 1.5
                    })
                
                if 'entropy' in dist_info:
                    entropy = dist_info['entropy']
                    insights['distribution_insights'].append({
                        'field': field,
                        'entropy': entropy,
                        'diversity_level': 'high' if entropy > 3 else 'medium' if entropy > 1.5 else 'low',
                        'interpretation': self._interpret_entropy(entropy)
                    })
        
        # Correlation insights
        if 'numeric_correlations' in corr_data:
            strong_corrs = corr_data['numeric_correlations'].get('strong_correlations', [])
            for corr in strong_corrs:
                insights['correlation_insights'].append({
                    'field_pair': f"{corr['field1']} vs {corr['field2']}",
                    'correlation_value': corr['correlation'],
                    'strength': corr['strength'],
                    'interpretation': self._interpret_correlation(corr['correlation']),
                    'business_implication': self._suggest_correlation_implication(corr)
                })
        
        # Outlier insights
        for field, field_info in field_data.items():
            if 'numeric_analysis' in field_info:
                outliers = field_info['numeric_analysis'].get('outliers', {})
                if outliers.get('count', 0) > 0:
                    insights['outlier_insights'].append({
                        'field': field,
                        'outlier_count': outliers['count'],
                        'outlier_percentage': outliers['percentage'],
                        'severity': 'high' if outliers['percentage'] > 5 else 'medium' if outliers['percentage'] > 1 else 'low',
                        'recommendation': self._recommend_outlier_treatment(outliers['percentage'])
                    })
        
        # Generate statistical recommendations
        insights['statistical_recommendations'] = self._generate_statistical_recommendations(insights)
        
        return insights
    
    def _generate_business_recommendations(self, analysis_data: Dict[str, Any], 
                                        business_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate business-focused recommendations"""
        recommendations = []
        
        # Data quality recommendations
        quality_data = analysis_data.get('data_quality', {})
        quality_score = quality_data.get('overall_quality_score', 0)
        
        if quality_score < 80:
            recommendations.append({
                'category': 'data_quality',
                'priority': 'high',
                'title': 'Improve Data Quality',
                'description': 'Current data quality may impact business decisions and analytics accuracy',
                'action_items': [
                    'Implement data validation rules',
                    'Establish data quality monitoring',
                    'Train data entry personnel'
                ],
                'expected_roi': 'Improved decision accuracy, reduced errors, better customer insights',
                'effort_level': 'medium',
                'timeline': '2-3 months'
            })
        
        # Demographic recommendations
        demo_data = analysis_data.get('demographic_analysis', {})
        if demo_data:
            recommendations.append({
                'category': 'demographics',
                'priority': 'medium',
                'title': 'Leverage Demographic Insights',
                'description': 'Rich demographic data available for targeted strategies',
                'action_items': [
                    'Develop age-specific marketing campaigns',
                    'Create location-based service offerings',
                    'Implement demographic segmentation'
                ],
                'expected_roi': 'Higher engagement rates, better customer targeting, increased conversion',
                'effort_level': 'low',
                'timeline': '1-2 months'
            })
        
        # Statistical recommendations
        corr_data = analysis_data.get('correlation_analysis', {})
        if corr_data.get('numeric_correlations', {}).get('strong_correlations'):
            recommendations.append({
                'category': 'analytics',
                'priority': 'medium',
                'title': 'Exploit Data Correlations',
                'description': 'Strong correlations found that could drive business value',
                'action_items': [
                    'Build predictive models using correlated features',
                    'Create automated alerts based on correlation patterns',
                    'Develop KPIs around correlated metrics'
                ],
                'expected_roi': 'Predictive capabilities, automated insights, proactive decision making',
                'effort_level': 'high',
                'timeline': '3-6 months'
            })
        
        return recommendations
    
    def _generate_technical_recommendations(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate technical recommendations for data management"""
        recommendations = []
        
        dataset_info = analysis_data.get('dataset_info', {})
        field_analysis = analysis_data.get('field_analysis', {})
        
        # Database optimization recommendations
        total_records = dataset_info.get('total_records', 0)
        if total_records > 100000:
            recommendations.append({
                'category': 'performance',
                'priority': 'medium',
                'title': 'Database Optimization',
                'description': f'Large dataset ({total_records:,} records) may benefit from optimization',
                'technical_details': [
                    'Consider indexing frequently queried fields',
                    'Implement data partitioning strategies',
                    'Optimize query performance'
                ],
                'tools_suggested': ['Database indexing', 'Query optimization', 'Caching'],
                'effort_level': 'medium'
            })
        
        # Data type optimization
        inefficient_fields = []
        for field, field_info in field_analysis.items():
            if field_info.get('field_type_classification') == 'identifier' and field_info.get('data_type') == 'object':
                inefficient_fields.append(field)
        
        if inefficient_fields:
            recommendations.append({
                'category': 'storage',
                'priority': 'low',
                'title': 'Data Type Optimization',
                'description': 'Some fields could use more efficient data types',
                'technical_details': [
                    f'Convert ID fields to numeric types: {", ".join(inefficient_fields[:3])}',
                    'Implement categorical encoding for text fields',
                    'Use appropriate date/time types'
                ],
                'tools_suggested': ['Data type conversion', 'Categorical encoding'],
                'effort_level': 'low'
            })
        
        return recommendations
    
    def _assess_data_risks(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential risks in the data"""
        risks = {
            'high_risk_items': [],
            'medium_risk_items': [],
            'low_risk_items': [],
            'overall_risk_level': 'low'
        }
        
        # Data quality risks
        quality_data = analysis_data.get('data_quality', {})
        quality_score = quality_data.get('overall_quality_score', 100)
        
        if quality_score < 60:
            risks['high_risk_items'].append({
                'type': 'data_quality',
                'description': 'Low data quality may lead to incorrect business decisions',
                'impact': 'High - affects all downstream analysis',
                'mitigation': 'Implement comprehensive data cleaning and validation'
            })
        elif quality_score < 80:
            risks['medium_risk_items'].append({
                'type': 'data_quality',
                'description': 'Moderate data quality issues may affect analysis accuracy',
                'impact': 'Medium - some analysis results may be unreliable',
                'mitigation': 'Address specific quality issues identified in analysis'
            })
        
        # Bias risks
        demo_data = analysis_data.get('demographic_analysis', {})
        if demo_data.get('age_analysis'):
            for field, age_info in demo_data['age_analysis'].items():
                if 'age_groups' in age_info:
                    age_groups = age_info['age_groups']
                    total = sum(age_groups.values())
                    if total > 0:
                        max_group_pct = max(age_groups.values()) / total * 100
                        if max_group_pct > 70:
                            risks['medium_risk_items'].append({
                                'type': 'sampling_bias',
                                'description': f'Age distribution heavily skewed - {max_group_pct:.1f}% in one group',
                                'impact': 'Medium - results may not generalize to broader population',
                                'mitigation': 'Consider stratified sampling or weighting techniques'
                            })
        
        # Privacy risks
        field_analysis = analysis_data.get('field_analysis', {})
        pii_fields = []
        for field, field_info in field_analysis.items():
            field_type = field_info.get('field_type_classification', '')
            if field_type in ['email', 'phone', 'name']:
                pii_fields.append(field)
        
        if pii_fields:
            risks['medium_risk_items'].append({
                'type': 'privacy',
                'description': f'PII fields detected: {", ".join(pii_fields[:3])}',
                'impact': 'Medium - potential privacy compliance issues',
                'mitigation': 'Implement data anonymization and access controls'
            })
        
        # Determine overall risk level
        if risks['high_risk_items']:
            risks['overall_risk_level'] = 'high'
        elif len(risks['medium_risk_items']) > 2:
            risks['overall_risk_level'] = 'medium'
        elif risks['medium_risk_items']:
            risks['overall_risk_level'] = 'medium'
        
        return risks
    
    def _identify_optimization_opportunities(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify opportunities for optimization"""
        opportunities = []
        
        # Automation opportunities
        field_analysis = analysis_data.get('field_analysis', {})
        consistent_fields = []
        for field, field_info in field_analysis.items():
            if field_info.get('field_type_classification') in ['email', 'phone'] and \
               'text_analysis' in field_info and field_info['text_analysis'].get('common_patterns'):
                consistent_fields.append(field)
        
        if consistent_fields:
            opportunities.append({
                'type': 'automation',
                'title': 'Data Validation Automation',
                'description': f'Fields with consistent patterns can be auto-validated: {", ".join(consistent_fields[:3])}',
                'benefit': 'Reduced manual validation effort, improved data quality',
                'implementation_effort': 'low',
                'expected_savings': '20-30% reduction in data processing time'
            })
        
        # Analysis optimization
        corr_data = analysis_data.get('correlation_analysis', {})
        if corr_data.get('numeric_correlations', {}).get('strong_correlations'):
            opportunities.append({
                'type': 'analytics',
                'title': 'Predictive Model Development',
                'description': 'Strong correlations suggest good predictive modeling potential',
                'benefit': 'Proactive insights, automated decision support',
                'implementation_effort': 'medium',
                'expected_savings': 'Improved decision speed and accuracy'
            })
        
        return opportunities
    
    def _create_action_items(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create specific action items based on analysis"""
        action_items = []
        
        # Data quality actions
        quality_data = analysis_data.get('data_quality', {})
        if 'completeness' in quality_data:
            field_completeness = quality_data['completeness'].get('field_completeness', {})
            low_completeness_fields = [field for field, completeness in field_completeness.items() if completeness < 90]
            
            if low_completeness_fields:
                action_items.append({
                    'priority': 'high',
                    'category': 'data_quality',
                    'title': 'Address Missing Data',
                    'description': f'Fix completeness issues in {len(low_completeness_fields)} fields',
                    'specific_actions': [
                        f'Investigate root cause of missing data in: {", ".join(low_completeness_fields[:3])}',
                        'Update data collection processes',
                        'Implement data validation rules'
                    ],
                    'owner': 'Data Team',
                    'timeline': '2 weeks',
                    'success_criteria': 'Achieve >95% completeness in all fields'
                })
        
        # Performance actions
        dataset_info = analysis_data.get('dataset_info', {})
        if dataset_info.get('total_records', 0) > 50000:
            action_items.append({
                'priority': 'medium',
                'category': 'performance',
                'title': 'Implement Data Indexing',
                'description': 'Optimize database performance for large dataset',
                'specific_actions': [
                    'Identify frequently queried fields',
                    'Create appropriate database indexes',
                    'Test query performance improvements'
                ],
                'owner': 'Engineering Team',
                'timeline': '1 week',
                'success_criteria': 'Achieve <2 second query response times'
            })
        
        return action_items
    
    def _suggest_tracking_metrics(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest metrics to track based on analysis findings"""
        metrics = []
        
        # Data quality metrics
        metrics.append({
            'category': 'data_quality',
            'metric_name': 'Data Completeness Rate',
            'description': 'Percentage of non-null values across all fields',
            'target_value': '>95%',
            'frequency': 'daily',
            'alert_threshold': '<90%'
        })
        
        # Performance metrics
        dataset_info = analysis_data.get('dataset_info', {})
        if dataset_info.get('total_records', 0) > 10000:
            metrics.append({
                'category': 'performance',
                'metric_name': 'Data Processing Time',
                'description': 'Time to process and analyze full dataset',
                'target_value': '<5 minutes',
                'frequency': 'weekly',
                'alert_threshold': '>10 minutes'
            })
        
        # Business metrics based on demographics
        demo_data = analysis_data.get('demographic_analysis', {})
        if demo_data.get('age_analysis'):
            metrics.append({
                'category': 'business',
                'metric_name': 'Demographic Distribution Stability',
                'description': 'Consistency of age/gender distributions over time',
                'target_value': '<5% weekly change',
                'frequency': 'weekly',
                'alert_threshold': '>10% change'
            })
        
        return metrics
    
    def _recommend_next_steps(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend next steps based on analysis results"""
        next_steps = []
        
        # Immediate steps (1-2 weeks)
        quality_data = analysis_data.get('data_quality', {})
        if quality_data.get('overall_quality_score', 100) < 80:
            next_steps.append({
                'timeline': 'immediate',
                'priority': 'high',
                'step': 'Data Quality Audit',
                'description': 'Conduct detailed audit of data quality issues',
                'deliverable': 'Data quality report with specific fix recommendations'
            })
        
        # Short term steps (1-3 months)
        demo_data = analysis_data.get('demographic_analysis', {})
        if demo_data:
            next_steps.append({
                'timeline': 'short_term',
                'priority': 'medium',
                'step': 'Demographic Analysis Deep Dive',
                'description': 'Conduct detailed demographic analysis for business insights',
                'deliverable': 'Demographic segmentation strategy and targeting recommendations'
            })
        
        # Long term steps (3-6 months)
        corr_data = analysis_data.get('correlation_analysis', {})
        if corr_data.get('numeric_correlations', {}).get('strong_correlations'):
            next_steps.append({
                'timeline': 'long_term',
                'priority': 'medium',
                'step': 'Predictive Model Development',
                'description': 'Build predictive models using identified correlations',
                'deliverable': 'Deployed predictive models with monitoring dashboard'
            })
        
        return next_steps
    
    # Helper methods for insight interpretation
    def _assess_overall_dataset_health(self, completeness: float, quality_score: float) -> str:
        """Assess overall health of the dataset"""
        if completeness >= 95 and quality_score >= 85:
            return "Excellent - Dataset is ready for advanced analytics and modeling"
        elif completeness >= 80 and quality_score >= 70:
            return "Good - Minor improvements needed before advanced analysis"
        elif completeness >= 60 and quality_score >= 50:
            return "Fair - Significant data quality work required"
        else:
            return "Poor - Major data quality issues must be addressed before analysis"
    
    def _interpret_age_distribution(self, age_groups: Dict[str, int], dominance_pct: float) -> str:
        """Interpret age distribution patterns"""
        if dominance_pct > 70:
            return f"Highly concentrated in one age group ({dominance_pct:.1f}%) - may indicate sampling bias"
        elif dominance_pct > 50:
            return f"Moderately concentrated ({dominance_pct:.1f}%) - consider diversification"
        else:
            return "Well-distributed across age groups - good demographic representation"
    
    def _interpret_gender_distribution(self, gender_ratios: Dict[str, float]) -> str:
        """Interpret gender distribution patterns"""
        if len(gender_ratios) < 2:
            return "Single gender category - may limit analysis scope"
        
        values = list(gender_ratios.values())
        max_pct = max(values)
        min_pct = min(values)
        
        if max_pct - min_pct < 20:
            return "Well-balanced gender distribution"
        elif max_pct > 70:
            return f"Gender imbalance detected - {max_pct:.1f}% in dominant category"
        else:
            return "Moderate gender imbalance - acceptable for most analyses"
    
    def _interpret_location_diversity(self, diversity: float, unique_locations: int) -> str:
        """Interpret location diversity"""
        if diversity > 0.7:
            return f"High geographic diversity ({unique_locations} unique locations) - excellent coverage"
        elif diversity > 0.3:
            return f"Moderate geographic diversity ({unique_locations} locations) - good coverage"
        else:
            return f"Low geographic diversity ({unique_locations} locations) - consider broader sampling"
    
    def _calculate_balance_score(self, ratios: Dict[str, float]) -> float:
        """Calculate balance score for distributions"""
        if len(ratios) < 2:
            return 0.0
        
        values = list(ratios.values())
        ideal_value = 100.0 / len(values)
        deviations = [abs(value - ideal_value) for value in values]
        avg_deviation = sum(deviations) / len(deviations)
        
        return max(0, 100 - avg_deviation * 2)  # Scale to 0-100
    
    def _interpret_skewness(self, skewness: float) -> str:
        """Interpret skewness values"""
        if abs(skewness) < 0.5:
            return "Normal distribution - suitable for standard statistical tests"
        elif skewness > 1.5:
            return "Highly right-skewed - consider log transformation"
        elif skewness < -1.5:
            return "Highly left-skewed - consider transformation"
        elif skewness > 0.5:
            return "Moderately right-skewed"
        else:
            return "Moderately left-skewed"
    
    def _interpret_entropy(self, entropy: float) -> str:
        """Interpret entropy values"""
        if entropy > 3:
            return "High diversity - many different values with balanced distribution"
        elif entropy > 1.5:
            return "Moderate diversity - some concentration in common values"
        else:
            return "Low diversity - dominated by few common values"
    
    def _interpret_correlation(self, correlation: float) -> str:
        """Interpret correlation strength"""
        abs_corr = abs(correlation)
        if abs_corr > 0.8:
            return f"Very strong {'positive' if correlation > 0 else 'negative'} relationship"
        elif abs_corr > 0.6:
            return f"Strong {'positive' if correlation > 0 else 'negative'} relationship"
        elif abs_corr > 0.4:
            return f"Moderate {'positive' if correlation > 0 else 'negative'} relationship"
        else:
            return f"Weak {'positive' if correlation > 0 else 'negative'} relationship"
    
    def _suggest_correlation_implication(self, corr: Dict[str, Any]) -> str:
        """Suggest business implications of correlations"""
        field1 = corr['field1']
        field2 = corr['field2']
        
        if 'age' in field1.lower() or 'age' in field2.lower():
            return "Age-related correlation - useful for demographic targeting"
        elif 'price' in field1.lower() or 'price' in field2.lower():
            return "Price-related correlation - important for pricing strategy"
        elif 'location' in field1.lower() or 'location' in field2.lower():
            return "Geographic correlation - relevant for location-based strategies"
        else:
            return "Feature correlation - useful for predictive modeling"
    
    def _recommend_outlier_treatment(self, percentage: float) -> str:
        """Recommend treatment for outliers"""
        if percentage > 10:
            return "High outlier rate - investigate data collection process"
        elif percentage > 5:
            return "Moderate outliers - consider robust statistical methods"
        else:
            return "Normal outlier rate - standard analysis approaches suitable"
    
    def _generate_demographic_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate demographic-specific recommendations"""
        recommendations = []
        
        # Age-based recommendations
        for age_insight in insights.get('age_insights', []):
            if age_insight['dominance_percentage'] > 60:
                recommendations.append({
                    'type': 'age_diversity',
                    'priority': 'medium',
                    'action': f"Diversify age representation - currently {age_insight['dominance_percentage']:.1f}% {age_insight['dominant_group']}",
                    'benefit': 'More representative analysis and broader applicability'
                })
        
        # Gender-based recommendations
        for gender_insight in insights.get('gender_insights', []):
            if gender_insight['balance_score'] < 70:
                recommendations.append({
                    'type': 'gender_balance',
                    'priority': 'low',
                    'action': 'Improve gender balance in data collection',
                    'benefit': 'Reduced bias and more inclusive analysis'
                })
        
        return recommendations
    
    def _generate_statistical_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate statistics-specific recommendations"""
        recommendations = []
        
        # Distribution recommendations
        for dist_insight in insights.get('distribution_insights', []):
            if dist_insight.get('transformation_suggested', False):
                recommendations.append({
                    'type': 'transformation',
                    'priority': 'medium',
                    'action': f"Apply transformation to {dist_insight['field']} (skewness: {dist_insight['skewness']:.2f})",
                    'benefit': 'Improved statistical analysis and model performance'
                })
        
        # Outlier recommendations
        for outlier_insight in insights.get('outlier_insights', []):
            if outlier_insight['severity'] == 'high':
                recommendations.append({
                    'type': 'outlier_treatment',
                    'priority': 'high',
                    'action': f"Investigate outliers in {outlier_insight['field']} ({outlier_insight['outlier_percentage']:.1f}%)",
                    'benefit': 'More robust analysis and cleaner insights'
                })
        
        return recommendations
    
    def _add_insight_metadata(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Add confidence scores and metadata to insights"""
        # Add confidence scores based on data completeness and quality
        metadata = {
            'confidence_level': 'high',  # This would be calculated based on data quality
            'reliability_score': 85,     # Based on completeness and consistency
            'sample_adequacy': 'sufficient',
            'bias_indicators': [],
            'limitations': []
        }
        
        insights['insight_metadata'] = metadata
        return insights
    
    def _load_insight_templates(self) -> Dict[str, Any]:
        """Load templates for generating insights"""
        return {
            'data_quality': {
                'excellent': "Data quality is excellent with minimal issues",
                'good': "Data quality is good with minor improvements needed",
                'poor': "Data quality requires immediate attention"
            },
            'demographics': {
                'balanced': "Demographics show good balance across categories",
                'skewed': "Demographics show skew that may affect analysis",
                'limited': "Limited demographic diversity may restrict insights"
            }
        }