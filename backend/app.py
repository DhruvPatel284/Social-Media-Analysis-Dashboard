from flask import Flask, jsonify, request
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from datetime import datetime, timedelta
import pandas as pd
from collections import Counter
from flask_cors import CORS
import json
import numpy as np

import logging
from config import *
from simple_analytics import DashboardAnalytics
from advanced_analytics import AdvancedAnalytics
from text_analytics import TextAnalytics
from chatbot import MarketingChatbot
from adgenerator import AdImageGenerator
import asyncio 
from improved_text_analytics import ImprovedTextAnalytics


app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle special types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.bool_, bool)):  # Handle numpy and native booleans
            return bool(obj)
        return super().default(obj)

@app.route('/api/generate-ads/<category>')
def generate_ads(category):
    """Generate advertising images for a category"""
    try:
        # Create generator instance
        generator = AdImageGenerator()
        
        # Run async generation in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(generator.generate_ad_images(category))
        loop.close()
        
        if "error" in result:
            return jsonify(result), 500
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in generate_ads endpoint: {str(e)}")
        return jsonify({
            "error": str(e),
            "category": category
        }), 500
    
@app.route('/api/chat', methods=['POST'])
def chat():
    """Chatbot endpoint for marketing-related queries with script modes"""
    try:
        data = request.get_json()
        if not data or 'category' not in data or 'question' not in data:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        category = data['category']
        question = data['question']
        mode = data.get('mode')  # Optional mode parameter
        script_content = data.get('script_content')  # Optional script content for enhancement
        
        # Validate mode if provided
        if mode and mode not in ["script_creation", "script_enhance"]:
            return jsonify({'error': 'Invalid mode. Must be either "script_creation" or "script_enhance"'}), 400
            
        # Validate script content for enhancement mode
        if mode == "script_enhance" and not script_content:
            return jsonify({'error': 'Script content is required for enhancement mode'}), 400
        
        chatbot = MarketingChatbot()

        # Generate response with mode and script content
        response = chatbot.generate_response(
            category=category,
            user_question=question,
            mode=mode,
            script_content=script_content
        )
        
        if 'error' in response:
            return jsonify(response), 500
            
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

text_analytics = TextAnalytics()
# text_analysis = ImprovedTextAnalytics()
@app.route('/api/dashboard/<category>/text-analysis')
def text_analysis(category):
    """Get comprehensive text analysis for a category"""
    try:
        analysis_report = text_analytics.generate_comprehensive_report(category)
        return jsonify(analysis_report)
    except Exception as e:
        logger.error(f"Error in text analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500



advanced = AdvancedAnalytics()

def format_video_data(video):
    """Format video data to ensure datetime compatibility"""
    return {
        'video_id': video.get('video_id'),  # Use .get() to safely access dictionary keys
        'title': video.get('title'),
        'channel_title': video.get('channel_title'),
        'view_count': video.get('view_count'),
        'like_count': video.get('like_count'),
        'comment_count': video.get('comment_count'),
        'engagement_rate': video.get('engagement_rate'),
        'published_at': video.get('published_at').isoformat() if isinstance(video.get('published_at'), datetime) else video.get('published_at')
    }

@app.route('/api/dashboard/<category>/advanced/engagement')
def advanced_engagement_analysis(category):
    """Get advanced engagement analysis for a category"""
    try:
        # Get base metrics from existing endpoint
        videos = analytics.get_engagement_metrics(category)
        if not videos:
            return jsonify({'error': 'No data found for category'}), 404

        # Format video data
        formatted_videos = [format_video_data(video) for video in videos]
        
        # Calculate total metrics
        overview_data = {
            'top_videos': formatted_videos,
            'total_views': sum(video['view_count'] for video in formatted_videos),
            'total_likes': sum(video['like_count'] for video in formatted_videos),
            'total_comments': sum(video['comment_count'] for video in formatted_videos),
            'total_videos': len(formatted_videos)
        }

        # Calculate advanced engagement patterns
        engagement_patterns = advanced.analyze_engagement_patterns(overview_data)

        return json.dumps({
            'patterns': engagement_patterns,
            'metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'data_points': len(formatted_videos)
            }
        }, cls=CustomJSONEncoder)
    except Exception as e:
        logger.error(f"Error in advanced engagement analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/<category>/advanced/timeseries')
def advanced_timeseries_analysis(category):
    """Get advanced time series analysis for a category"""
    try:
        # Get timeline data from existing endpoint
        timeline_data = analytics.get_time_based_metrics(category)
        if not timeline_data:
            return jsonify({'error': 'No timeline data found for category'}), 404

        # Perform advanced time series analysis
        timeseries_analysis = advanced.analyze_time_series(timeline_data)

        return json.dumps({
            'analysis': timeseries_analysis,
            'metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'time_range': {
                    'start': min(timeline_data.keys()),
                    'end': max(timeline_data.keys())
                }
            }
        }, cls=CustomJSONEncoder)
    except Exception as e:
        logger.error(f"Error in advanced timeseries analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/<category>/advanced/composite')
def composite_metrics_analysis(category):
    """Get composite metrics combining multiple data sources"""
    try:
        # Get data from both existing endpoints
        videos = analytics.get_engagement_metrics(category)
        timeline_data = analytics.get_time_based_metrics(category)
        
        if not videos or not timeline_data:
            return jsonify({'error': 'Insufficient data for composite analysis'}), 404

        # Format video data
        formatted_videos = [format_video_data(video) for video in videos]
        
        # Calculate overview metrics
        overview_data = {
            'total_videos': len(formatted_videos),
            'total_views': sum(video['view_count'] for video in formatted_videos),
            'total_likes': sum(video['like_count'] for video in formatted_videos),
            'total_comments': sum(video['comment_count'] for video in formatted_videos)
        }

        # Calculate composite metrics
        composite_analysis = advanced.calculate_composite_metrics(overview_data, timeline_data)

        # Generate visualization data
        viz_data = generate_visualization_data(composite_analysis)

        # Log data for debugging
        # logger.info(f"Composite analysis data: {composite_analysis}")
        # logger.info(f"Visualization data: {viz_data}")

        return json.dumps({
            'composite_metrics': composite_analysis,
            'visualization_data': viz_data,
            'metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'metrics_included': list(composite_analysis.keys())
            }
        }, cls=CustomJSONEncoder)  # Ensure the custom encoder is used
    except Exception as e:
        logger.error(f"Error in composite metrics analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/<category>/advanced/summary')
def comprehensive_analysis(category):
    """Get comprehensive analysis combining all advanced metrics"""
    try:
        # Collect all data
        videos = analytics.get_engagement_metrics(category)
        timeline_data = analytics.get_time_based_metrics(category)
        trends_data = analytics.get_search_trends(category)
        
        if not all([videos, timeline_data, trends_data]):
            return jsonify({'error': 'Insufficient data for comprehensive analysis'}), 404

        # Format video data
        formatted_videos = [format_video_data(video) for video in videos]
        
        # Prepare overview data
        overview_data = {
            'top_videos': formatted_videos,
            'total_views': sum(video['view_count'] for video in formatted_videos),
            'total_likes': sum(video['like_count'] for video in formatted_videos),
            'total_comments': sum(video['comment_count'] for video in formatted_videos),
            'total_videos': len(formatted_videos)
        }

        # Perform all analyses
        engagement_patterns = advanced.analyze_engagement_patterns(overview_data)
        timeseries_analysis = advanced.analyze_time_series(timeline_data)
        composite_analysis = advanced.calculate_composite_metrics(overview_data, timeline_data)
        viz_data = generate_visualization_data(composite_analysis)

        # Log data for debugging
        logger.info(f"Engagement patterns: {engagement_patterns}")
        logger.info(f"Timeseries analysis: {timeseries_analysis}")
        logger.info(f"Composite analysis: {composite_analysis}")
        logger.info(f"Visualization data: {viz_data}")

        return json.dumps({
            'engagement_patterns': engagement_patterns,
            'timeseries_analysis': timeseries_analysis,
            'composite_metrics': composite_analysis,
            'visualization_data': viz_data,
            'search_trends': trends_data,
            'metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'data_freshness': {
                    'overview': max(video['published_at'] for video in formatted_videos),
                    'timeline': max(timeline_data.keys())
                }
            }
        }, cls=CustomJSONEncoder)  # Ensure the custom encoder is used
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Helper function to generate visualization data
def generate_visualization_data(analytics_results):
    """
    Transform analytics results into formats suitable for various chart types
    """
    try:
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
    except Exception as e:
        logger.error(f"Error generating visualization data: {str(e)}")
        return {}




analytics = DashboardAnalytics()

@app.route('/api/dashboard/<category>/overview')
def category_overview(category):
    """Get overall metrics for a category"""
    try:
        engagement_data = analytics.get_engagement_metrics(category)
        
        if not engagement_data:
            return jsonify({
                'error': 'No data found for category'
            }), 404

        total_views = sum(video['view_count'] for video in engagement_data)
        total_likes = sum(video['like_count'] for video in engagement_data)
        total_comments = sum(video['comment_count'] for video in engagement_data)
        avg_engagement = sum(video['engagement_rate'] for video in engagement_data) / len(engagement_data)

        return jsonify({
            'total_videos': len(engagement_data),
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'average_engagement_rate': round(avg_engagement, 2),
            'top_videos': sorted(
                engagement_data,
                key=lambda x: x['engagement_rate'],
                reverse=True
            )[:5]
        })
    except Exception as e:
        logger.error(f"Error in category overview: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/<category>/channels')
def channel_analysis(category):
    """Get channel performance analysis"""
    try:
        channel_metrics = analytics.get_channel_performance(category)
        
        # Sort channels by total views
        sorted_channels = sorted(
            channel_metrics.items(),
            key=lambda x: x[1]['total_views'],
            reverse=True
        )

        return jsonify({
            'channel_metrics': dict(sorted_channels),
            'top_channels': dict(sorted_channels[:5])
        })
    except Exception as e:
        logger.error(f"Error in channel analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/<category>/trends')
def trend_analysis(category):
    """Get trend analysis for a category"""
    try:
        trends = analytics.get_search_trends(category)
        return jsonify(trends)
    except Exception as e:
        logger.error(f"Error in trend analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/<category>/timeline')
def timeline_analysis(category):
    """Get time-based analysis for a category"""
    try:
        time_metrics = analytics.get_time_based_metrics(category)
        return jsonify(time_metrics)
    except Exception as e:
        logger.error(f"Error in timeline analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/categories')
def get_categories():
    """Get list of available categories"""
    return jsonify({
        'categories': [
            'Smartphones',
            'Electric Vehicles',
            'Gaming Consoles'
        ]
    })

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)