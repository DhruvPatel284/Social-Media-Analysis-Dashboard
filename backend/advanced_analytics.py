from typing import Dict, List, Any
from datetime import datetime
import pandas as pd
import numpy as np
from collections import defaultdict

class AdvancedAnalytics:
    def analyze_engagement_patterns(self, overview_data: Dict) -> Dict[str, Any]:
        """
        Analyze engagement patterns from overview data
        """
        videos = overview_data['top_videos']
        total_metrics = {
            'views': overview_data['total_views'],
            'likes': overview_data['total_likes'],
            'comments': overview_data['total_comments']
        }
        
        # Calculate engagement distribution by channel
        channel_engagement = defaultdict(lambda: {
            'total_views': 0,
            'total_engagement': 0,
            'videos': 0,
            'avg_engagement_rate': 0
        })
        
        for video in videos:
            channel = video['channel_title']
            channel_engagement[channel]['total_views'] += video['view_count']
            channel_engagement[channel]['total_engagement'] += (
                video['like_count'] + video['comment_count']
            )
            channel_engagement[channel]['videos'] += 1
            channel_engagement[channel]['avg_engagement_rate'] += video['engagement_rate']

        for channel in channel_engagement:
            metrics = channel_engagement[channel]
            metrics['avg_engagement_rate'] /= metrics['videos']

        # Calculate engagement velocity (change over time)
        engagement_velocity = []
        sorted_videos = sorted(videos, key=lambda x: x['published_at'])
        for i in range(1, len(sorted_videos)):
            # Parse the ISO format datetime string
            time_diff = (datetime.fromisoformat(sorted_videos[i]['published_at']) - 
                        datetime.fromisoformat(sorted_videos[i-1]['published_at'])).days
            engagement_diff = sorted_videos[i]['engagement_rate'] - sorted_videos[i-1]['engagement_rate']
            if time_diff > 0:
                engagement_velocity.append({
                    'period': sorted_videos[i]['published_at'],
                    'velocity': engagement_diff / time_diff
                })

        return {
            'channel_engagement': dict(channel_engagement),
            'engagement_velocity': engagement_velocity,
            'engagement_ratios': {
                'likes_per_view': total_metrics['likes'] / total_metrics['views'],
                'comments_per_view': total_metrics['comments'] / total_metrics['views'],
                'comments_per_like': total_metrics['comments'] / total_metrics['likes']
            }
        }

    def analyze_time_series(self, timeline_data: Dict) -> Dict[str, Any]:
        """
        Perform advanced time series analysis
        """
        # Convert to pandas DataFrame for analysis
        df = pd.DataFrame([
            {
                'month': month,
                **metrics
            }
            for month, metrics in timeline_data.items()
        ])
        df['month'] = pd.to_datetime(df['month'])
        df = df.sort_values('month')

        # Calculate rolling metrics
        window_size = 3
        rolling_metrics = {
            'views_ma': df['views'].rolling(window=window_size).mean().tolist(),
            'engagement_ma': df['avg_engagement'].rolling(window=window_size).mean().tolist(),
            'video_count_ma': df['video_count'].rolling(window=window_size).mean().tolist()
        }

        # Calculate month-over-month changes
        mom_changes = {
            'views_change': df['views'].pct_change().fillna(0).tolist(),
            'engagement_change': df['avg_engagement'].pct_change().fillna(0).tolist(),
            'video_count_change': df['video_count'].pct_change().fillna(0).tolist()
        }

        # Calculate correlation matrix
        correlation_matrix = df[[
            'views', 'likes', 'comments', 'video_count', 'avg_engagement'
        ]].corr().to_dict()

        # Identify seasonal patterns
        seasonal_patterns = {
            'high_engagement_months': df.nlargest(3, 'avg_engagement')['month'].dt.strftime('%Y-%m').tolist(),
            'high_views_months': df.nlargest(3, 'views')['month'].dt.strftime('%Y-%m').tolist(),
            'high_activity_months': df.nlargest(3, 'video_count')['month'].dt.strftime('%Y-%m').tolist()
        }

        # Calculate performance scores
        df['engagement_score'] = (
            df['avg_engagement'] / df['avg_engagement'].mean() +
            df['views'] / df['views'].mean() +
            df['video_count'] / df['video_count'].mean()
        ) / 3

        performance_trends = {
            'months': df['month'].dt.strftime('%Y-%m').tolist(),
            'scores': df['engagement_score'].tolist()
        }

        return {
            'rolling_metrics': rolling_metrics,
            'mom_changes': mom_changes,
            'correlation_matrix': correlation_matrix,
            'seasonal_patterns': seasonal_patterns,
            'performance_trends': performance_trends,
            'summary_statistics': {
                'views': {
                    'mean': df['views'].mean(),
                    'std': df['views'].std(),
                    'min': df['views'].min(),
                    'max': df['views'].max()
                },
                'engagement': {
                    'mean': df['avg_engagement'].mean(),
                    'std': df['avg_engagement'].std(),
                    'min': df['avg_engagement'].min(),
                    'max': df['avg_engagement'].max()
                }
            }
        }

    def calculate_composite_metrics(self, overview_data: Dict, timeline_data: Dict) -> Dict[str, Any]:
        """
        Calculate composite metrics combining overview and timeline data
        """
        # Calculate engagement efficiency
        total_engagement = overview_data['total_likes'] + overview_data['total_comments']
        total_videos = overview_data['total_videos']
        
        engagement_efficiency = {
            'per_video': total_engagement / total_videos,
            'per_view': total_engagement / overview_data['total_views']
        }

        # Calculate content performance indicators
        monthly_metrics = []
        for month, data in timeline_data.items():
            engagement_score = (
                data['avg_engagement'] * 0.4 +
                (data['likes'] / data['views']) * 0.3 +
                (data['comments'] / data['views']) * 0.3
            )
            monthly_metrics.append({
                'month': month,
                'engagement_score': engagement_score,
                'efficiency_score': (data['likes'] + data['comments']) / data['video_count']
            })

        # Calculate trend indicators
        sorted_metrics = sorted(monthly_metrics, key=lambda x: x['month'])
        trend_indicators = {
            'engagement_trend': float(np.polyfit(
                range(len(sorted_metrics)),
                [m['engagement_score'] for m in sorted_metrics],
                1
            )[0]),
            'efficiency_trend': float(np.polyfit(
                range(len(sorted_metrics)),
                [m['efficiency_score'] for m in sorted_metrics],
                1
            )[0])
        }

        # Calculate composite scores
        overall_health = (
            trend_indicators['engagement_trend'] * 0.5 +
            trend_indicators['efficiency_trend'] * 0.3 +
            engagement_efficiency['per_video'] / 1000 * 0.2
        )
        growth_potential = trend_indicators['engagement_trend'] > 0 and trend_indicators['efficiency_trend'] > 0

        return {
            'engagement_efficiency': engagement_efficiency,
            'monthly_performance': monthly_metrics,
            'trend_indicators': trend_indicators,
            'composite_scores': {
                'overall_health': float(overall_health),  # Convert to native float
                'growth_potential': bool(growth_potential)  # Convert to native bool
            }
        }

    def generate_visualization_data(analytics_results: Dict) -> Dict[str, List]:
        """
        Transform analytics results into formats suitable for various chart types
        """
        return {
            'engagement_trends': {
                'line': {
                    'labels': [m['month'] for m in analytics_results['monthly_performance']],
                    'data': [m['engagement_score'] for m in analytics_results['monthly_performance']]
                },
                'radar': {
                    'metrics': ['Views', 'Likes', 'Comments', 'Engagement', 'Efficiency'],
                    'values': [
                        analytics_results['engagement_efficiency']['per_view'],
                        analytics_results['engagement_efficiency']['per_video'],
                        analytics_results['trend_indicators']['engagement_trend'],
                        analytics_results['trend_indicators']['efficiency_trend'],
                        analytics_results['composite_scores']['overall_health']
                    ]
                }
            },
            'performance_metrics': {
                'bubble': [
                    {
                        'x': m['efficiency_score'],
                        'y': m['engagement_score'],
                        'size': analytics_results['monthly_performance'][i]['efficiency_score'],
                        'month': m['month']
                    }
                    for i, m in enumerate(analytics_results['monthly_performance'])
                ],
                'heatmap': {
                    'months': [m['month'] for m in analytics_results['monthly_performance']],
                    'metrics': ['Engagement', 'Efficiency'],
                    'values': [
                        [m['engagement_score'] for m in analytics_results['monthly_performance']],
                        [m['efficiency_score'] for m in analytics_results['monthly_performance']]
                    ]
                }
            }
        }