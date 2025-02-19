from openai import OpenAI
import json
from typing import List, Dict
import logging
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement, BatchStatement
from googleapiclient.discovery import build
import requests
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any
import json
import logging
from ratelimit import limits, sleep_and_retry
from config import *

class AstraDataCollector:
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize connections
        self._init_astra_connection()
        self._init_youtube_api()
        
        # Setup database
        self.setup_database()
        
        # Initialize metrics
        self.time_tracking = {
            'youtube_total': 0,
            'search_total': 0,
            'videos_collected': 0,
            'queries_processed': 0
        }
    def _init_astra_connection(self):
        """Initialize Astra DB connection"""
        try:
            cloud_config = {
                'secure_connect_bundle': SECURE_BUNDLE_PATH
            }
            auth_provider = PlainTextAuthProvider('token', ASTRA_DB_TOKEN)
            self.cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
            self.session = self.cluster.connect()
            self.logger.info("Successfully connected to Astra DB")
        except Exception as e:
            self.logger.error(f"Failed to connect to Astra DB: {str(e)}")
            raise
    def _init_youtube_api(self):
        """Initialize YouTube API client"""
        try:
            self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
            self.logger.info("Successfully initialized YouTube API client")
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube API: {str(e)}")
            raise

    def setup_database(self):
        """Setup Astra DB schema with optimized tables"""
        try:
            # Create keyspace if not exists (if allowed by permissions)
            self.session.execute(f"""
                CREATE KEYSPACE IF NOT EXISTS {ASTRA_DB_KEYSPACE} 
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
            """)
            
            # YouTube data table - Optimized schema with engagement_rate as clustering key
            self.session.execute(f"""
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
                AND default_time_to_live = {DATA_RETENTION_DAYS * 24 * 3600}
            """)
            
            # Search data table
            self.session.execute(f"""
                CREATE TABLE IF NOT EXISTS {ASTRA_DB_KEYSPACE}.search_data (
                    query text,
                    category text,
                    collected_at timestamp,
                    organic_results text,
                    news_results text,
                    knowledge_graph text,
                    related_searches text,
                    PRIMARY KEY ((category, query), collected_at)
                ) WITH default_time_to_live = {DATA_RETENTION_DAYS * 24 * 3600}
            """)
            
            self.logger.info("Successfully set up database schema")
        except Exception as e:
            self.logger.error(f"Failed to setup database: {str(e)}")
            raise


    def delete_category_data(self, category: str):
        """
        Delete all data for a specific category from both youtube_data and search_data tables.
        
        :param category: The category to delete (e.g., "Smartphones")
        """
        try:
            # Delete from youtube_data table
            delete_youtube_query = f"""
                DELETE FROM {ASTRA_DB_KEYSPACE}.youtube_data 
                WHERE category = %s
            """
            self.session.execute(delete_youtube_query, [category])
            self.logger.info(f"Deleted all YouTube data for category: {category}")

            # Fetch all queries for the category in search_data table
            fetch_queries_query = f"""
                SELECT query FROM {ASTRA_DB_KEYSPACE}.search_data 
                WHERE category = %s
                ALLOW FILTERING
            """
            rows = self.session.execute(fetch_queries_query, [category])
            queries = [row.query for row in rows]

            # Delete from search_data table for each query
            delete_search_query = f"""
                DELETE FROM {ASTRA_DB_KEYSPACE}.search_data 
                WHERE category = %s AND query = %s
            """
            for query in queries:
                self.session.execute(delete_search_query, [category, query])
                self.logger.info(f"Deleted search data for category: {category}, query: {query}")

        except Exception as e:
            self.logger.error(f"Error deleting data for category {category}: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    collector = AstraDataCollector()
    category_to_delete = "Tech Reviews"
    
    print(f"Deleting all data for category: {category_to_delete}")
    collector.delete_category_data(category_to_delete)
    print("Deletion completed!")