from typing import Dict, List, Any
from datetime import datetime
import json
from groq import Groq
from config import GROQ_API_KEY
from simple_analytics import DashboardAnalytics
from advanced_analytics import AdvancedAnalytics
import numpy as np

class TextAnalytics:
    def __init__(self):
        self.simple_analytics = DashboardAnalytics()
        self.advanced_analytics = AdvancedAnalytics()
        self.groq_client = Groq(api_key=GROQ_API_KEY)
        
    def generate_comprehensive_report(self, category: str) -> Dict[str, Any]:
        """Generate a comprehensive text analysis report for a category"""
        try:
            # Gather all relevant data
            engagement_data = self.simple_analytics.get_engagement_metrics(category)
            channel_data = self.simple_analytics.get_channel_performance(category)
            trend_data = self.simple_analytics.get_search_trends(category)
            timeline_data = self.simple_analytics.get_time_based_metrics(category)
            
            # Get advanced analytics
            videos = [self._format_video_data(video) for video in engagement_data]
            overview_data = {
                'top_videos': videos,
                'total_views': sum(video['view_count'] for video in videos),
                'total_likes': sum(video['like_count'] for video in videos),
                'total_comments': sum(video['comment_count'] for video in videos),
                'total_videos': len(videos)
            }
            
            engagement_patterns = self.advanced_analytics.analyze_engagement_patterns(overview_data)
            timeseries_analysis = self.advanced_analytics.analyze_time_series(timeline_data)
            composite_metrics = self.advanced_analytics.calculate_composite_metrics(overview_data, timeline_data)
            
            # Prepare context for AI analysis
            analysis_context = {
                'category': category,
                'top_performers': self._analyze_top_performers(videos[:5]),
                'channel_insights': self._analyze_channels(channel_data),
                'trend_insights': self._analyze_trends(trend_data),
                'performance_metrics': {
                    'engagement_patterns': engagement_patterns,
                    'timeline_trends': timeseries_analysis,
                    'composite_scores': composite_metrics['composite_scores']
                }
            }
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(analysis_context)
            
            return {
                'overview': ai_insights['overview'],
                'content_strategy': ai_insights['content_strategy'],
                'trend_analysis': ai_insights['trend_analysis'],
                'channel_analysis': ai_insights['channel_analysis'],
                'recommendations': ai_insights['recommendations'],
                'metadata': {
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'data_points_analyzed': len(videos),
                    'time_range': self._get_time_range(timeline_data)
                }
            }
            
        except Exception as e:
            return {'error': f"Error generating report: {str(e)}"}
    
    def _analyze_top_performers(self, top_videos: List[Dict]) -> Dict:
        """Analyze characteristics of top-performing content"""
        return {
            'videos': [
                {
                    'title': video['title'],
                    'engagement_rate': video['engagement_rate'],
                    'view_count': video['view_count'],
                    'channel': video['channel_title']
                }
                for video in top_videos
            ]
        }
    
    def _analyze_channels(self, channel_data: Dict) -> Dict:
        """Analyze channel performance and characteristics"""
        top_channels = sorted(
            channel_data.items(),
            key=lambda x: x[1]['total_views'],
            reverse=True
        )[:5]
        
        return {
            'top_channels': [
                {
                    'name': channel[0],
                    'total_views': channel[1]['total_views'],
                    'engagement_rate': channel[1]['engagement_rate'],
                    'video_count': channel[1]['video_count']
                }
                for channel in top_channels
            ]
        }
    
    def _analyze_trends(self, trend_data: Dict) -> Dict:
        """Analyze search and topic trends"""
        return {
            'top_keywords': list(trend_data['top_keywords'].items())[:5],
            'top_topics': list(trend_data['news_topics'].items())[:5]
        }
    
    def _generate_ai_insights(self, context: Dict) -> Dict:
        """Generate AI-powered insights using Groq's Mistral model"""
        try:
            # Convert numpy types to native Python types
            context = convert_numpy_types(context)
            
            # Prepare prompt for the AI
            prompt = self._create_analysis_prompt(context)
            
            # Get AI response
            response = self.groq_client.chat.completions.create(
                messages=[{
                    "role": "system",
                    "content": "You are an expert social media and content analytics advisor. Provide detailed, actionable insights based on the data provided."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=2048
            )
            
            # Parse and structure the response
            insights = json.loads(response.choices[0].message.content)
            return insights
            
        except Exception as e:
            return {
                'overview': f"Error generating AI insights: {str(e)}",
                'content_strategy': '',
                'trend_analysis': '',
                'channel_analysis': '',
                'recommendations': []
            }
    
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
        - overview: High-level category performance summary (2-3 sentences)
        - content_strategy: Key working strategies (3 points)
        - trend_analysis: Main trend insights (2-3 points)
        - channel_analysis: Top channel performance insights (2-3 points)
        - recommendations: 3-5 specific, actionable recommendations

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
    
    def _get_time_range(self, timeline_data: Dict) -> Dict:
        """Get the time range of the analyzed data"""
        dates = list(timeline_data.keys())
        return {
            'start': min(dates),
            'end': max(dates)
        }

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    return obj