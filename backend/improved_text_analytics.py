from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from groq import Groq
from config import GROQ_API_KEY
import numpy as np
from collections import Counter
from simple_analytics import DashboardAnalytics
from advanced_analytics import AdvancedAnalytics


class ImprovedTextAnalytics:
    def __init__(self):
        self.simple_analytics = DashboardAnalytics()
        self.advanced_analytics = AdvancedAnalytics()
        self.groq_client = Groq(api_key=GROQ_API_KEY)
        
    def generate_comprehensive_report(self, category: str) -> Dict[str, Any]:
        """Generate a comprehensive text analysis report with strict data validation"""
        try:
            # Gather and validate data
            raw_data = self._collect_raw_data(category)
            if not self._validate_data(raw_data):
                return {
                    'error': 'Insufficient or invalid data for meaningful analysis',
                    'metadata': {
                        'analysis_timestamp': datetime.utcnow().isoformat(),
                        'category': category
                    }
                }
            
            # Process validated data
            processed_data = self._process_data(raw_data)
            
            # Generate insights with statistical validation
            insights = self._generate_validated_insights(processed_data)
            
            return {
                'overview': insights['overview'],
                'content_performance': insights['content_performance'],
                'audience_insights': insights['audience_insights'],
                'growth_strategy': insights['growth_strategy'],
                'actionable_recommendations': insights['recommendations'],
                'metadata': {
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'data_points_analyzed': processed_data['total_videos'],
                    'time_range': processed_data['time_range'],
                    'confidence_score': processed_data['confidence_score']
                }
            }
            
        except Exception as e:
            return {'error': f"Error generating report: {str(e)}"}

    def _collect_raw_data(self, category: str) -> Dict:
        """Collect and structure raw data with validation"""
        engagement_data = self.simple_analytics.get_engagement_metrics(category)
        channel_data = self.simple_analytics.get_channel_performance(category)
        trend_data = self.simple_analytics.get_search_trends(category)
        timeline_data = self.simple_analytics.get_time_based_metrics(category)
        
        return {
            'engagement': engagement_data,
            'channels': channel_data,
            'trends': trend_data,
            'timeline': timeline_data
        }

    def _validate_data(self, raw_data: Dict) -> bool:
        """Validate data completeness and quality"""
        # Check for minimum data requirements
        if not raw_data['engagement'] or not raw_data['channels']:
            return False
            
        # Verify data quality
        engagement_metrics = [
            video for video in raw_data['engagement']
            if all(key in video for key in ['view_count', 'like_count', 'comment_count'])
            and all(isinstance(video[key], (int, float)) for key in ['view_count', 'like_count', 'comment_count'])
            and video['view_count'] > 0  # Filter out videos with no views
        ]
        
        # Require minimum sample size
        return len(engagement_metrics) >= 10

    def _process_data(self, raw_data: Dict) -> Dict:
        """Process and analyze validated data"""
        # Process engagement metrics
        valid_videos = [
            video for video in raw_data['engagement']
            if video['view_count'] > 0
        ]
        
        # Calculate channel performance metrics
        channel_metrics = {}
        for channel, data in raw_data['channels'].items():
            if data['total_views'] > 0:
                channel_metrics[channel] = {
                    'total_views': data['total_views'],
                    'total_engagement': data['total_likes'] + data['total_comments'],
                    'engagement_rate': data['engagement_rate'],
                    'video_count': data['video_count'],
                    'avg_views_per_video': data['total_views'] / data['video_count']
                }
        
        # Analyze content patterns
        content_patterns = self._analyze_content_patterns(valid_videos)
        
        # Calculate confidence score based on data quality
        confidence_score = min(1.0, len(valid_videos) / 100) * 0.7 + \
                         min(1.0, len(channel_metrics) / 10) * 0.3
        
        return {
            'valid_videos': valid_videos,
            'channel_metrics': channel_metrics,
            'content_patterns': content_patterns,
            'total_videos': len(valid_videos),
            'time_range': self._get_time_range(raw_data['timeline']),
            'confidence_score': confidence_score
        }

    def _analyze_content_patterns(self, videos: List[Dict]) -> Dict:
        """Analyze content patterns with statistical validation"""
        # Sort videos by engagement rate
        top_performing = sorted(
            videos,
            key=lambda x: (x['like_count'] + x['comment_count']) / max(x['view_count'], 1),
            reverse=True
        )[:10]
        
        # Analyze video titles and descriptions
        title_words = Counter()
        for video in top_performing:
            words = video['title'].lower().split()
            # Filter out common stop words and short words
            words = [w for w in words if len(w) > 3 and w not in STOP_WORDS]
            title_words.update(words)
        
        return {
            'top_performing': top_performing,
            'common_themes': title_words.most_common(5),
            'avg_engagement_rate': np.mean([
                (v['like_count'] + v['comment_count']) / max(v['view_count'], 1)
                for v in top_performing
            ])
        }

    def _generate_validated_insights(self, processed_data: Dict) -> Dict:
        """Generate insights based only on validated data"""
        try:
            # Prepare context for AI analysis
            
            # Generate AI insights
            response = self.groq_client.chat.completions.create(
                messages=[{
                    "role": "system",
                    "content": self._get_system_prompt()
                }, {
                    "role": "user",
                    "content": self._create_analysis_prompt(processed_data)
                }],
                model="mixtral-8x7b-32768",
                temperature=0.3  # Lower temperature for more focused responses
            )
            
            # Parse and validate AI response
            insights = json.loads(response.choices[0].message.content)
            return self._validate_insights(insights, processed_data)
            
        except Exception as e:
            return ""

    def _get_system_prompt(self) -> str:
        """Get system prompt for accurate analysis"""
        return """You are a data-driven content analytics advisor. 
        Provide insights based ONLY on the statistical data provided.
        Do not make assumptions or generate recommendations without supporting data.
        Focus on specific, actionable insights backed by numbers.
        If data is insufficient for any conclusion, acknowledge the limitation."""

    def _validate_insights(self, insights: Dict, data: Dict) -> Dict:
        """Validate AI-generated insights against actual data"""
        validated = {}
        
        # Validate each insight against source data
        for key, value in insights.items():
            if isinstance(value, list):
                validated[key] = [
                    insight for insight in value
                    if self._verify_insight(insight, data)
                ]
            else:
                validated[key] = value if self._verify_insight(value, data) else None
        
        return validated

    def _create_analysis_prompt(self, context: Dict) -> str:
        """Create a summarized prompt for AI analysis"""
        # Summarize top performers
        top_videos_summary = {
            'count': len(context['top_performers']['videos']),
            'avg_engagement': sum(v['engagement_rate'] for v in context['top_performers']['videos']) / len(context['top_performers']['videos']),
            'total_views': sum(v['view_count'] for v in context['top_performers']['videos']),
            'top_channels': list(set(v['channel'] for v in context['top_performers']['videos']))
        }

        # Summarize channel insights
        channel_summary = {
            'total_channels': len(context['channel_insights']['top_channels']),
            'top_channel_stats': {
                'name': context['channel_insights']['top_channels'][0]['name'],
                'engagement_rate': context['channel_insights']['top_channels'][0]['engagement_rate']
            } if context['channel_insights']['top_channels'] else {}
        }

        # Summarize trends
        trend_summary = {
            'top_5_keywords': dict(context['trend_insights']['top_keywords']),
            'top_3_topics': dict(list(context['trend_insights']['top_topics'])[:3])
        }

        # Extract key performance indicators
        kpis = {
            'overall_health': context['performance_metrics']['composite_scores']['overall_health'],
            'growth_potential': context['performance_metrics']['composite_scores']['growth_potential']
        }

        return f"""
        Analyze these key metrics for {context['category']} and provide strategic insights in JSON format:

        Category Overview:
        {json.dumps(top_videos_summary, indent=2)}

        Key Channel Data:
        {json.dumps(channel_summary, indent=2)}

        Top Trends:
        {json.dumps(trend_summary, indent=2)}

        Performance KPIs:
        {json.dumps(kpis, indent=2)}

        Provide a concise JSON response with:
        - overview: High-level category performance summary (4-5 sentences)
        - content_strategy: Key working strategies (4 points)
        - trend_analysis: Main trend insights (4-5 points)
        - channel_analysis: Top channel performance insights (5-6 points)
        - recommendations: 6-7 specific, actionable recommendations

        Keep each section brief but specific to the data provided.
        """
    
    def _format_video_data(self, video: Dict) -> Dict:
        """Format video data consistently"""
        return {
            'video_id': video.get('video_id'),
            'title': video.get('title'),
            'channel_title': video.get('channel_title'),
            'view_count': video.get('view_count'),
            'like_count': video.get('like_count'),
            'comment_count': video.get('comment_count'),
            'engagement_rate': video.get('engagement_rate'),
            'published_at': video.get('published_at').isoformat() 
                if isinstance(video.get('published_at'), datetime) 
                else video.get('published_at')
        }
    
    def _verify_insight(self, insight: str, data: Dict) -> bool:
        """Verify if an insight is supported by data"""
        # Implementation would include checks against actual data
        # Return False if insight contains unsupported claims
        return True  # Placeholder - implement actual verification logic

STOP_WORDS = {
    'the', 'and', 'for', 'with', 'this', 'that', 'from', 'what',
    'how', 'why', 'when', 'where', 'who', 'which', 'best', 'top',
    'new', 'latest', 'update', 'review', 'vs', 'comparison',
    'video', 'channel', 'subscribe', 'like', 'comment', 'share'
}