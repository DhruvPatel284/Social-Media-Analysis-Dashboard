from flask import Flask, jsonify, request
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from datetime import datetime, timedelta
import pandas as pd
from collections import Counter
from flask_cors import CORS
import json
import logging
from config import *

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database table setup queries
SETUP_QUERIES = [
    f"""
    CREATE TABLE IF NOT EXISTS {ASTRA_DB_KEYSPACE}.youtube_data (
        video_id text,
        category text,
        query text,
        title text,
        description text,
        published_at timestamp,
        channel_id text,
        channel_title text,
        view_count bigint,
        like_count bigint,
        comment_count bigint,
        engagement_rate double,
        collected_at timestamp,
        PRIMARY KEY ((category), engagement_rate, video_id)
    ) WITH CLUSTERING ORDER BY (engagement_rate DESC, video_id ASC)
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {ASTRA_DB_KEYSPACE}.search_data (
        category text,
        query text,
        collected_at timestamp,
        organic_results text,
        news_results text,
        knowledge_graph text,
        related_searches text,
        PRIMARY KEY ((category), query, collected_at)
    ) WITH CLUSTERING ORDER BY (query ASC, collected_at DESC)
    """
]

class DashboardAnalytics:
    def __init__(self):
        self._init_astra_connection()
        self._setup_tables()

    def _init_astra_connection(self):
        """Initialize Astra DB connection"""
        try:
            cloud_config = {
                'secure_connect_bundle': SECURE_BUNDLE_PATH
            }
            auth_provider = PlainTextAuthProvider('token', ASTRA_DB_TOKEN)
            self.cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
            self.session = self.cluster.connect()
            logger.info("Successfully connected to Astra DB")
        except Exception as e:
            logger.error(f"Failed to connect to Astra DB: {str(e)}")
            raise

    def _setup_tables(self):
        """Setup database tables"""
        try:
            for query in SETUP_QUERIES:
                self.session.execute(query)
            logger.info("Successfully set up database tables")
        except Exception as e:
            logger.error(f"Failed to setup tables: {str(e)}")
            raise

    def get_engagement_metrics(self, category):
        """Get engagement metrics for videos in a category"""
        try:
            query = f"""
                SELECT video_id, title, view_count, like_count, 
                       comment_count, engagement_rate, channel_title,
                       published_at
                FROM {ASTRA_DB_KEYSPACE}.youtube_data
                WHERE category = %s
            """
            rows = self.session.execute(query, [category])
            return [dict(row._asdict()) for row in rows]
        except Exception as e:
            logger.error(f"Error getting engagement metrics: {str(e)}")
            return []

    def get_channel_performance(self, category):
        """Analyze channel performance in a category"""
        try:
            query = f"""
                SELECT channel_title, view_count, like_count, 
                       comment_count, engagement_rate
                FROM {ASTRA_DB_KEYSPACE}.youtube_data
                WHERE category = %s
            """
            rows = self.session.execute(query, [category])
            
            channel_metrics = {}
            for row in rows:
                channel = row.channel_title
                if channel not in channel_metrics:
                    channel_metrics[channel] = {
                        'total_views': 0,
                        'total_likes': 0,
                        'total_comments': 0,
                        'avg_engagement': 0,
                        'video_count': 0
                    }
                
                metrics = channel_metrics[channel]
                metrics['total_views'] += row.view_count
                metrics['total_likes'] += row.like_count
                metrics['total_comments'] += row.comment_count
                metrics['avg_engagement'] += row.engagement_rate
                metrics['video_count'] += 1

            # Calculate averages and add engagement rate
            for channel in channel_metrics:
                metrics = channel_metrics[channel]
                metrics['avg_engagement'] = round(metrics['avg_engagement'] / metrics['video_count'], 2)
                metrics['engagement_rate'] = round(
                    (metrics['total_likes'] + metrics['total_comments']) / 
                    metrics['total_views'] * 100 if metrics['total_views'] > 0 else 0,
                    2
                )
                
            return channel_metrics
        except Exception as e:
            logger.error(f"Error getting channel performance: {str(e)}")
            return {}

    def get_search_trends(self, category):
        """Analyze search trends for a category"""
        try:
            query = f"""
                SELECT organic_results, news_results, related_searches
                FROM {ASTRA_DB_KEYSPACE}.search_data
                WHERE category = %s
                ALLOW FILTERING
            """
            rows = self.session.execute(query, [category])
            
            all_keywords = []
            news_topics = []
            
            for row in rows:
                # Process organic results
                organic = json.loads(row.organic_results)
                for result in organic:
                    if isinstance(result, dict):  # Ensure result is a dictionary
                        title = result.get('title', '')
                        snippet = result.get('snippet', '')
                        if title:
                            # Process title words
                            words = [word.strip().lower() for word in title.split() 
                                if len(word.strip()) > 3]
                            all_keywords.extend(words)
                        if snippet:
                            # Process snippet words
                            words = [word.strip().lower() for word in snippet.split() 
                                if len(word.strip()) > 3]
                            all_keywords.extend(words)
                
                # Process news results
                news = json.loads(row.news_results)
                for article in news:
                    if isinstance(article, dict):  # Ensure article is a dictionary
                        title = article.get('title', '')
                        snippet = article.get('snippet', '')
                        if title:
                            words = [word.strip().lower() for word in title.split() 
                                if len(word.strip()) > 3]
                            news_topics.extend(words)
                        if snippet:
                            words = [word.strip().lower() for word in snippet.split() 
                                if len(word.strip()) > 3]
                            news_topics.extend(words)
                
                # Process related searches
                related = json.loads(row.related_searches)
                if isinstance(related, list):  # Ensure related is a list
                    for search in related:
                        if isinstance(search, str):  # Ensure search is a string
                            words = [word.strip().lower() for word in search.split() 
                                if len(word.strip()) > 3]
                            all_keywords.extend(words)

            # Filter out common stop words and technical terms
            stop_words = {
                'the', 'and', 'for', 'with', 'this', 'that', 'from', 'what',
                'how', 'why', 'when', 'where', 'who', 'which', 'best', 'top',
                'new', 'latest', 'update', 'review', 'vs', 'comparison'
            }
            
            # Filter keywords and count occurrences
            filtered_keywords = [word for word in all_keywords 
                            if word not in stop_words]
            filtered_news = [topic for topic in news_topics 
                            if topic not in stop_words]
            
            # Count occurrences and get top results
            keyword_counter = Counter(filtered_keywords)
            news_counter = Counter(filtered_news)
            
            return {
                'top_keywords': dict(keyword_counter.most_common(10)),
                'news_topics': dict(news_counter.most_common(10)),
                'total_keywords': len(filtered_keywords),
                'total_news_topics': len(filtered_news),
                'keyword_count': len(keyword_counter),
                'news_topic_count': len(news_counter)
            }
        except Exception as e:
            logger.error(f"Error getting search trends: {str(e)}")
            return {
                'top_keywords': {},
                'news_topics': {},
                'total_keywords': 0,
                'total_news_topics': 0,
                'error': str(e)
            }

    def get_time_based_metrics(self, category):
        """Get time-based engagement metrics"""
        try:
            query = f"""
                SELECT published_at, view_count, like_count, 
                       comment_count, engagement_rate
                FROM {ASTRA_DB_KEYSPACE}.youtube_data
                WHERE category = %s
            """
            rows = self.session.execute(query, [category])
            
            time_metrics = {}
            for row in rows:
                date_key = row.published_at.strftime('%Y-%m')
                if date_key not in time_metrics:
                    time_metrics[date_key] = {
                        'views': 0,
                        'likes': 0,
                        'comments': 0,
                        'avg_engagement': 0,
                        'video_count': 0
                    }
                
                metrics = time_metrics[date_key]
                metrics['views'] += row.view_count
                metrics['likes'] += row.like_count
                metrics['comments'] += row.comment_count
                metrics['avg_engagement'] += row.engagement_rate
                metrics['video_count'] += 1

            # Calculate averages
            for date in time_metrics:
                metrics = time_metrics[date]
                metrics['avg_engagement'] = round(metrics['avg_engagement'] / metrics['video_count'], 2)
                
            return time_metrics
        except Exception as e:
            logger.error(f"Error getting time-based metrics: {str(e)}")
            return {}
