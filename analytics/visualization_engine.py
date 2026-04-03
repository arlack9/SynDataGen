"""
Visualization Engine for Data Analytics
Generates interactive charts and visualizations for web interface
"""

import json
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from datetime import datetime
import logging

class VisualizationEngine:
    """
    Creates visualization configurations for Chart.js, Plotly, and other charting libraries
    Generates interactive charts for demographics, statistics, and data insights
    """
    
    def __init__(self, chart_library: str = 'chartjs'):
        self.chart_library = chart_library.lower()
        self.logger = logging.getLogger(__name__)
        self.color_palette = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
        ]
        
    def create_visualization_suite(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete suite of visualizations from analysis data
        
        Args:
            analysis_data: Output from DataAnalyzer
            
        Returns:
            Complete visualization configuration for web interface
        """
        try:
            viz_suite = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'chart_library': self.chart_library,
                    'total_visualizations': 0
                },
                'summary_dashboard': self._create_summary_dashboard(analysis_data),
                'demographic_charts': self._create_demographic_visualizations(analysis_data),
                'distribution_charts': self._create_distribution_visualizations(analysis_data),
                'quality_metrics': self._create_quality_visualizations(analysis_data),
                'correlation_heatmap': self._create_correlation_heatmap(analysis_data),
                'interactive_filters': self._create_filter_options(analysis_data),
                'insights_display': self._create_insights_visualization(analysis_data)
            }
            
            # Count total visualizations
            total_viz = sum(len(section.get('charts', [])) for section in viz_suite.values() if isinstance(section, dict) and 'charts' in section)
            viz_suite['metadata']['total_visualizations'] = total_viz
            
            return viz_suite
            
        except Exception as e:
            self.logger.error(f"Error creating visualization suite: {str(e)}")
            return {
                'error': f"Visualization creation failed: {str(e)}",
                'metadata': {'generated_at': datetime.now().isoformat()}
            }
    
    def _create_summary_dashboard(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary dashboard with key metrics"""
        dataset_info = analysis_data.get('dataset_info', {})
        basic_stats = analysis_data.get('basic_statistics', {})
        quality_data = analysis_data.get('data_quality', {})
        
        summary = {
            'type': 'dashboard',
            'title': 'Dataset Overview',
            'metrics_cards': [
                {
                    'title': 'Total Records',
                    'value': dataset_info.get('total_records', 0),
                    'type': 'number',
                    'icon': 'database',
                    'color': 'primary'
                },
                {
                    'title': 'Total Fields',
                    'value': dataset_info.get('total_fields', 0),
                    'type': 'number',
                    'icon': 'columns',
                    'color': 'info'
                },
                {
                    'title': 'Data Completeness',
                    'value': f"{basic_stats.get('completeness', 0):.1f}%",
                    'type': 'percentage',
                    'icon': 'check-circle',
                    'color': 'success' if basic_stats.get('completeness', 0) > 90 else 'warning'
                },
                {
                    'title': 'Quality Score',
                    'value': f"{quality_data.get('overall_quality_score', 0):.0f}/100",
                    'type': 'score',
                    'icon': 'star',
                    'color': 'success' if quality_data.get('overall_quality_score', 0) > 80 else 'warning'
                }
            ],
            'quick_stats': self._create_quick_stats_chart(basic_stats)
        }
        
        return summary
    
    def _create_demographic_visualizations(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create demographic analysis visualizations"""
        demo_data = analysis_data.get('demographic_analysis', {})
        charts = []
        
        # Age distribution charts
        if demo_data.get('age_analysis'):
            for field, age_info in demo_data['age_analysis'].items():
                if 'age_groups' in age_info:
                    charts.append(self._create_age_group_chart(field, age_info['age_groups']))
                
                if 'distribution' in age_info:
                    charts.append(self._create_age_distribution_chart(field, age_info['distribution']))
        
        # Gender distribution charts
        if demo_data.get('gender_analysis'):
            for field, gender_info in demo_data['gender_analysis'].items():
                if 'distribution' in gender_info:
                    charts.append(self._create_gender_chart(field, gender_info['distribution']))
        
        # Location analysis charts
        if demo_data.get('location_analysis'):
            for field, location_info in demo_data['location_analysis'].items():
                if 'top_locations' in location_info:
                    charts.append(self._create_location_chart(field, location_info['top_locations']))
        
        # Email domain analysis
        if demo_data.get('email_analysis'):
            for field, email_info in demo_data['email_analysis'].items():
                if 'domain_distribution' in email_info:
                    charts.append(self._create_email_domain_chart(field, email_info['domain_distribution']))
        
        return {
            'type': 'demographic_section',
            'title': 'Demographic Analysis',
            'charts': charts,
            'total_charts': len(charts)
        }
    
    def _create_distribution_visualizations(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create data distribution visualizations"""
        dist_data = analysis_data.get('distribution_analysis', {})
        charts = []
        
        for field, dist_info in dist_data.items():
            if isinstance(dist_info, dict):
                # Numeric distributions
                if 'histogram_data' in dist_info:
                    charts.append(self._create_histogram_chart(field, dist_info))
                
                # Categorical distributions
                if 'category_distribution' in dist_info:
                    charts.append(self._create_category_chart(field, dist_info['category_distribution']))
                
                # Box plots for numeric data
                if 'percentiles' in dist_info:
                    charts.append(self._create_box_plot(field, dist_info))
        
        return {
            'type': 'distribution_section',
            'title': 'Data Distributions',
            'charts': charts,
            'total_charts': len(charts)
        }
    
    def _create_quality_visualizations(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create data quality visualizations"""
        quality_data = analysis_data.get('data_quality', {})
        charts = []
        
        # Completeness chart
        if 'completeness' in quality_data and 'field_completeness' in quality_data['completeness']:
            charts.append(self._create_completeness_chart(quality_data['completeness']['field_completeness']))
        
        # Quality score breakdown
        if 'overall_quality_score' in quality_data:
            charts.append(self._create_quality_score_chart(quality_data))
        
        # Uniqueness analysis
        if 'uniqueness' in quality_data:
            charts.append(self._create_uniqueness_chart(quality_data['uniqueness']))
        
        return {
            'type': 'quality_section',
            'title': 'Data Quality Metrics',
            'charts': charts,
            'total_charts': len(charts)
        }
    
    def _create_correlation_heatmap(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create correlation heatmap visualization"""
        corr_data = analysis_data.get('correlation_analysis', {})
        
        if 'numeric_correlations' in corr_data and 'correlation_matrix' in corr_data['numeric_correlations']:
            corr_matrix = corr_data['numeric_correlations']['correlation_matrix']
            
            return {
                'type': 'heatmap',
                'title': 'Field Correlations',
                'chart_config': self._create_heatmap_config(corr_matrix),
                'insights': corr_data['numeric_correlations'].get('correlation_insights', [])
            }
        
        return {
            'type': 'heatmap',
            'title': 'Field Correlations',
            'message': 'No numeric correlations available',
            'chart_config': None
        }
    
    def _create_filter_options(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create interactive filter options"""
        dataset_info = analysis_data.get('dataset_info', {})
        field_analysis = analysis_data.get('field_analysis', {})
        
        filters = {
            'type': 'filter_panel',
            'title': 'Interactive Filters',
            'filters': []
        }
        
        # Create filters for categorical fields
        for field, field_info in field_analysis.items():
            if field_info.get('field_type_classification') == 'categorical':
                if 'most_frequent' in field_info and field_info['most_frequent']:
                    filters['filters'].append({
                        'field': field,
                        'type': 'multiselect',
                        'label': field.replace('_', ' ').title(),
                        'options': list(field_info['most_frequent'].keys())
                    })
        
        # Add numeric range filters
        for field, field_info in field_analysis.items():
            if field_info.get('field_type_classification') == 'numeric' and 'numeric_analysis' in field_info:
                numeric_info = field_info['numeric_analysis']
                filters['filters'].append({
                    'field': field,
                    'type': 'range',
                    'label': field.replace('_', ' ').title(),
                    'min': numeric_info.get('min', 0),
                    'max': numeric_info.get('max', 100),
                    'step': 1
                })
        
        return filters
    
    def _create_insights_visualization(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create visualization for insights and recommendations"""
        insights_data = analysis_data.get('insights_and_recommendations', {})
        
        return {
            'type': 'insights_panel',
            'title': 'Key Insights & Recommendations',
            'sections': [
                {
                    'title': 'Data Quality Insights',
                    'items': insights_data.get('data_quality_insights', []),
                    'icon': 'shield-check',
                    'color': 'info'
                },
                {
                    'title': 'Demographic Insights',
                    'items': insights_data.get('demographic_insights', []),
                    'icon': 'users',
                    'color': 'primary'
                },
                {
                    'title': 'Distribution Insights',
                    'items': insights_data.get('distribution_insights', []),
                    'icon': 'bar-chart',
                    'color': 'success'
                },
                {
                    'title': 'Recommendations',
                    'items': insights_data.get('recommendations', []),
                    'icon': 'lightbulb',
                    'color': 'warning'
                },
                {
                    'title': 'Optimization Suggestions',
                    'items': insights_data.get('optimization_suggestions', []),
                    'icon': 'trending-up',
                    'color': 'success'
                }
            ]
        }
    
    # Chart creation methods for different chart types
    def _create_quick_stats_chart(self, basic_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Create quick statistics overview chart"""
        if self.chart_library == 'chartjs':
            return {
                'type': 'doughnut',
                'id': 'quick-stats-chart',
                'config': {
                    'type': 'doughnut',
                    'data': {
                        'labels': ['Numeric Fields', 'Text Fields'],
                        'datasets': [{
                            'data': [basic_stats.get('numeric_fields', 0), basic_stats.get('text_fields', 0)],
                            'backgroundColor': [self.color_palette[0], self.color_palette[1]],
                            'borderWidth': 2
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': 'Field Types Distribution'},
                            'legend': {'position': 'bottom'}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_age_group_chart(self, field: str, age_groups: Dict[str, int]) -> Dict[str, Any]:
        """Create age group distribution chart"""
        if self.chart_library == 'chartjs':
            return {
                'type': 'bar',
                'id': f'age-groups-{field.replace(" ", "-").lower()}',
                'title': f'Age Groups Distribution - {field}',
                'config': {
                    'type': 'bar',
                    'data': {
                        'labels': list(age_groups.keys()),
                        'datasets': [{
                            'label': 'Count',
                            'data': list(age_groups.values()),
                            'backgroundColor': self.color_palette[:len(age_groups)],
                            'borderWidth': 1
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': f'Age Groups - {field}'},
                            'legend': {'display': False}
                        },
                        'scales': {
                            'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Number of People'}}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_age_distribution_chart(self, field: str, distribution: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed age distribution chart"""
        if self.chart_library == 'chartjs':
            # Take top 10 ages for readability
            sorted_ages = sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'type': 'line',
                'id': f'age-dist-{field.replace(" ", "-").lower()}',
                'title': f'Age Distribution - {field}',
                'config': {
                    'type': 'line',
                    'data': {
                        'labels': [str(age) for age, _ in sorted_ages],
                        'datasets': [{
                            'label': 'Frequency',
                            'data': [count for _, count in sorted_ages],
                            'borderColor': self.color_palette[2],
                            'backgroundColor': self.color_palette[2] + '20',
                            'fill': True,
                            'tension': 0.4
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': f'Age Distribution - {field}'},
                            'legend': {'display': False}
                        },
                        'scales': {
                            'x': {'title': {'display': True, 'text': 'Age'}},
                            'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Frequency'}}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_gender_chart(self, field: str, distribution: Dict[str, int]) -> Dict[str, Any]:
        """Create gender distribution chart"""
        if self.chart_library == 'chartjs':
            return {
                'type': 'pie',
                'id': f'gender-{field.replace(" ", "-").lower()}',
                'title': f'Gender Distribution - {field}',
                'config': {
                    'type': 'pie',
                    'data': {
                        'labels': list(distribution.keys()),
                        'datasets': [{
                            'data': list(distribution.values()),
                            'backgroundColor': self.color_palette[:len(distribution)],
                            'borderWidth': 2
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': f'Gender Distribution - {field}'},
                            'legend': {'position': 'right'}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_location_chart(self, field: str, locations: Dict[str, int]) -> Dict[str, Any]:
        """Create location distribution chart"""
        if self.chart_library == 'chartjs':
            # Top 8 locations for readability
            top_locations = dict(list(locations.items())[:8])
            
            return {
                'type': 'horizontalBar',
                'id': f'location-{field.replace(" ", "-").lower()}',
                'title': f'Top Locations - {field}',
                'config': {
                    'type': 'bar',
                    'data': {
                        'labels': list(top_locations.keys()),
                        'datasets': [{
                            'label': 'Count',
                            'data': list(top_locations.values()),
                            'backgroundColor': self.color_palette[3],
                            'borderWidth': 1
                        }]
                    },
                    'options': {
                        'indexAxis': 'y',
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': f'Top Locations - {field}'},
                            'legend': {'display': False}
                        },
                        'scales': {
                            'x': {'beginAtZero': True, 'title': {'display': True, 'text': 'Count'}}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_email_domain_chart(self, field: str, domains: Dict[str, int]) -> Dict[str, Any]:
        """Create email domain distribution chart"""
        if self.chart_library == 'chartjs':
            return {
                'type': 'doughnut',
                'id': f'email-domains-{field.replace(" ", "-").lower()}',
                'title': f'Email Domains - {field}',
                'config': {
                    'type': 'doughnut',
                    'data': {
                        'labels': list(domains.keys()),
                        'datasets': [{
                            'data': list(domains.values()),
                            'backgroundColor': self.color_palette[:len(domains)],
                            'borderWidth': 2
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': f'Email Domains - {field}'},
                            'legend': {'position': 'bottom'}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_histogram_chart(self, field: str, dist_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create histogram chart for numeric distributions"""
        if self.chart_library == 'chartjs' and 'histogram_data' in dist_info:
            hist_data = dist_info['histogram_data']
            
            return {
                'type': 'bar',
                'id': f'histogram-{field.replace(" ", "-").lower()}',
                'title': f'Distribution - {field}',
                'config': {
                    'type': 'bar',
                    'data': {
                        'labels': [f"{edge:.1f}" for edge in hist_data.get('bin_centers', [])],
                        'datasets': [{
                            'label': 'Frequency',
                            'data': hist_data.get('counts', []),
                            'backgroundColor': self.color_palette[4] + '80',
                            'borderColor': self.color_palette[4],
                            'borderWidth': 1
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': f'Distribution - {field}'},
                            'legend': {'display': False}
                        },
                        'scales': {
                            'x': {'title': {'display': True, 'text': field}},
                            'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Frequency'}}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_category_chart(self, field: str, categories: Dict[str, int]) -> Dict[str, Any]:
        """Create categorical distribution chart"""
        if self.chart_library == 'chartjs':
            # Top 8 categories for readability
            top_categories = dict(list(categories.items())[:8])
            
            return {
                'type': 'bar',
                'id': f'categories-{field.replace(" ", "-").lower()}',
                'title': f'Categories - {field}',
                'config': {
                    'type': 'bar',
                    'data': {
                        'labels': list(top_categories.keys()),
                        'datasets': [{
                            'label': 'Count',
                            'data': list(top_categories.values()),
                            'backgroundColor': self.color_palette[5],
                            'borderWidth': 1
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': f'Categories - {field}'},
                            'legend': {'display': False}
                        },
                        'scales': {
                            'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Count'}}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_box_plot(self, field: str, dist_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create box plot for numeric data (simplified as bar chart)"""
        if self.chart_library == 'chartjs' and 'percentiles' in dist_info:
            percentiles = dist_info['percentiles']
            
            return {
                'type': 'bar',
                'id': f'boxplot-{field.replace(" ", "-").lower()}',
                'title': f'Quartiles - {field}',
                'config': {
                    'type': 'bar',
                    'data': {
                        'labels': ['Q1 (25%)', 'Q2 (50%)', 'Q3 (75%)'],
                        'datasets': [{
                            'label': 'Value',
                            'data': [percentiles.get(0.25, 0), percentiles.get(0.5, 0), percentiles.get(0.75, 0)],
                            'backgroundColor': [self.color_palette[0], self.color_palette[1], self.color_palette[2]],
                            'borderWidth': 1
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': f'Quartiles - {field}'},
                            'legend': {'display': False}
                        },
                        'scales': {
                            'y': {'beginAtZero': True, 'title': {'display': True, 'text': 'Value'}}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_completeness_chart(self, field_completeness: Dict[str, float]) -> Dict[str, Any]:
        """Create data completeness chart"""
        if self.chart_library == 'chartjs':
            return {
                'type': 'bar',
                'id': 'data-completeness',
                'title': 'Field Completeness',
                'config': {
                    'type': 'bar',
                    'data': {
                        'labels': list(field_completeness.keys()),
                        'datasets': [{
                            'label': 'Completeness %',
                            'data': list(field_completeness.values()),
                            'backgroundColor': [
                                self.color_palette[0] if val >= 95 else 
                                self.color_palette[5] if val >= 80 else 
                                self.color_palette[6] for val in field_completeness.values()
                            ],
                            'borderWidth': 1
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': 'Field Completeness'},
                            'legend': {'display': False}
                        },
                        'scales': {
                            'y': {'beginAtZero': True, 'max': 100, 'title': {'display': True, 'text': 'Completeness %'}}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_quality_score_chart(self, quality_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create overall quality score visualization"""
        if self.chart_library == 'chartjs':
            score = quality_data.get('overall_quality_score', 0)
            
            return {
                'type': 'gauge',
                'id': 'quality-score',
                'title': 'Overall Quality Score',
                'config': {
                    'type': 'doughnut',
                    'data': {
                        'labels': ['Quality Score', 'Remaining'],
                        'datasets': [{
                            'data': [score, 100 - score],
                            'backgroundColor': [
                                self.color_palette[0] if score >= 80 else 
                                self.color_palette[5] if score >= 60 else 
                                self.color_palette[6],
                                '#E0E0E0'
                            ],
                            'borderWidth': 0,
                            'cutout': '70%'
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': f'Quality Score: {score:.0f}/100'},
                            'legend': {'display': False}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_uniqueness_chart(self, uniqueness_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create uniqueness analysis chart"""
        if self.chart_library == 'chartjs':
            fields = list(uniqueness_data.keys())[:10]  # Top 10 fields
            uniqueness_ratios = [uniqueness_data[field].get('uniqueness_ratio', 0) * 100 for field in fields]
            
            return {
                'type': 'horizontalBar',
                'id': 'uniqueness-analysis',
                'title': 'Field Uniqueness',
                'config': {
                    'type': 'bar',
                    'data': {
                        'labels': fields,
                        'datasets': [{
                            'label': 'Uniqueness %',
                            'data': uniqueness_ratios,
                            'backgroundColor': self.color_palette[3],
                            'borderWidth': 1
                        }]
                    },
                    'options': {
                        'indexAxis': 'y',
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': 'Field Uniqueness'},
                            'legend': {'display': False}
                        },
                        'scales': {
                            'x': {'beginAtZero': True, 'max': 100, 'title': {'display': True, 'text': 'Uniqueness %'}}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Chart library {self.chart_library} not supported'}
    
    def _create_heatmap_config(self, corr_matrix: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Create correlation heatmap configuration"""
        if self.chart_library == 'chartjs':
            # Chart.js doesn't have native heatmap, so we'll create a matrix visualization
            fields = list(corr_matrix.keys())
            
            # Convert to flat data for heatmap
            heatmap_data = []
            for i, field1 in enumerate(fields):
                for j, field2 in enumerate(fields):
                    correlation = corr_matrix.get(field1, {}).get(field2, 0)
                    heatmap_data.append({
                        'x': field1,
                        'y': field2,
                        'v': correlation
                    })
            
            return {
                'type': 'scatter',
                'id': 'correlation-heatmap',
                'config': {
                    'type': 'scatter',
                    'data': {
                        'datasets': [{
                            'label': 'Correlation',
                            'data': heatmap_data,
                            'backgroundColor': self.color_palette[0]
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {'display': True, 'text': 'Correlation Matrix'},
                            'legend': {'display': False}
                        }
                    }
                }
            }
        
        return {'type': 'unsupported', 'message': f'Heatmap not supported for {self.chart_library}'}
    
    def generate_chart_html(self, chart_config: Dict[str, Any]) -> str:
        """Generate HTML for embedding charts in templates"""
        if self.chart_library == 'chartjs':
            return f"""
            <div class="chart-container" style="position: relative; height: 400px; margin: 20px 0;">
                <canvas id="{chart_config.get('id', 'chart')}"></canvas>
            </div>
            <script>
                const ctx_{chart_config.get('id', 'chart').replace('-', '_')} = document.getElementById('{chart_config.get('id', 'chart')}').getContext('2d');
                const chart_{chart_config.get('id', 'chart').replace('-', '_')} = new Chart(ctx_{chart_config.get('id', 'chart').replace('-', '_')}, {json.dumps(chart_config.get('config', {}))});
            </script>
            """
        
        return f"<div>Unsupported chart library: {self.chart_library}</div>"
    
    def export_visualization_config(self) -> Dict[str, Any]:
        """Export visualization configuration for frontend integration"""
        return {
            'chart_library': self.chart_library,
            'color_palette': self.color_palette,
            'supported_chart_types': [
                'bar', 'line', 'pie', 'doughnut', 'scatter', 'radar', 'polarArea'
            ],
            'cdn_links': {
                'chartjs': 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js'
            }
        }