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

@dataclass
class PerformanceMetrics:
    total_records: int
    total_time: float
    avg_time_per_record: float
    data_size_bytes: int
    records_per_second: float

@dataclass
class TimeEstimate:
    youtube_time: float
    search_time: float
    total_time: float
    videos_collected: int
    queries_processed: int

class AstraDataCollector:
    def __init__(self):
        # Existing initialization code...
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
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
    
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
    
    def get_top_engaged_videos(self, category: str, limit: int = 10) -> List[Dict]:
        """Get top engaged videos for a category"""
        try:
            query = f"""
                SELECT * FROM {ASTRA_DB_KEYSPACE}.youtube_data 
                WHERE category = %s 
                LIMIT %s
            """
            rows = self.session.execute(query, [category, limit])
            return [dict(row._asdict()) for row in rows]
        except Exception as e:
            self.logger.error(f"Error fetching top engaged videos: {str(e)}")
            return []
    
    @sleep_and_retry
    @limits(calls=RATE_LIMIT_YOUTUBE, period=100)
    def collect_youtube_data(self, category: str, query: str) -> PerformanceMetrics:
        """Collect YouTube data with batch processing"""
        start_time = time.time()
        records = []
        data_size = 0
        batch = BatchStatement()
        
        try:
            next_page_token = None
            while len(records) < VIDEOS_PER_QUERY:
                # Search for videos
                search_response = self.youtube.search().list(
                    q=query,
                    type='video',
                    part='id,snippet',
                    maxResults=50,
                    pageToken=next_page_token,
                    publishedAfter=(datetime.utcnow() - timedelta(days=365)).isoformat() + 'Z'
                ).execute()
                
                video_ids = [item['id']['videoId'] for item in search_response['items']]
                
                # Get detailed video information
                if video_ids:
                    videos_response = self.youtube.videos().list(
                        id=','.join(video_ids),
                        part='statistics,contentDetails'
                    ).execute()
                    
                    for video in videos_response['items']:
                        stats = video['statistics']
                        
                        # Find matching snippet from search results
                        snippet = next(
                            item['snippet'] for item in search_response['items']
                            if item['id']['videoId'] == video['id']
                        )
                        
                        # Calculate engagement rate first to use in PRIMARY KEY
                        view_count = int(stats.get('viewCount', 0))
                        like_count = int(stats.get('likeCount', 0))
                        comment_count = int(stats.get('commentCount', 0))
                        engagement_rate = (
                            (like_count + comment_count) /
                            view_count * 100 if view_count > 0 else 0
                        )
                        
                        video_data = {
                            'video_id': video['id'],
                            'category': category,
                            'query': query,
                            'title': snippet['title'],
                            'description': snippet['description'],
                            'published_at': datetime.strptime(
                                snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'
                            ),
                            'channel_id': snippet['channelId'],
                            'channel_title': snippet['channelTitle'],
                            'view_count': view_count,
                            'like_count': like_count,
                            'comment_count': comment_count,
                            'engagement_rate': engagement_rate,
                            'collected_at': datetime.utcnow()
                        }
                        
                        # Convert datetime objects to strings for JSON serialization
                        video_data_json = video_data.copy()
                        video_data_json['published_at'] = video_data_json['published_at'].isoformat()
                        video_data_json['collected_at'] = video_data_json['collected_at'].isoformat()
                        
                        # Add to batch
                        prepared = self.session.prepare(f"""
                            INSERT INTO {ASTRA_DB_KEYSPACE}.youtube_data 
                            (video_id, category, query, title, description, published_at, 
                            channel_id, channel_title, view_count, like_count, 
                            comment_count, engagement_rate, collected_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """)
                        
                        batch.add(prepared, [
                            video_data['video_id'],
                            video_data['category'],
                            video_data['query'],
                            video_data['title'],
                            video_data['description'],
                            video_data['published_at'],
                            video_data['channel_id'],
                            video_data['channel_title'],
                            video_data['view_count'],
                            video_data['like_count'],
                            video_data['comment_count'],
                            video_data['engagement_rate'],
                            video_data['collected_at']
                        ])
                        
                        data_size += len(json.dumps(video_data_json).encode('utf-8'))
                        records.append(video_data)
                
                next_page_token = search_response.get('nextPageToken')
                if not next_page_token or len(records) >= VIDEOS_PER_QUERY:
                    break
            
            # Execute batch
            if records:
                self.session.execute(batch)
                self.logger.info(f"Stored {len(records)} YouTube videos for {category} - {query}")
                
        except Exception as e:
            self.logger.error(f"Error collecting YouTube data: {str(e)}")
        
        end_time = time.time()
        return PerformanceMetrics(
            total_records=len(records),
            total_time=end_time - start_time,
            avg_time_per_record=(end_time - start_time) / len(records) if records else 0,
            data_size_bytes=data_size,
            records_per_second=len(records) / (end_time - start_time) if end_time > start_time else 0
        )
    
    @sleep_and_retry
    @limits(calls=RATE_LIMIT_SEARCH, period=60)
    def collect_search_data(self, category: str, query: str) -> PerformanceMetrics:
        """Collect search data with performance monitoring"""
        start_time = time.time()
        data_size = 0
        
        try:
            headers = {
                'X-API-KEY': SERPER_API_KEY,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': 100,
                'timeframe': 'last12m'
            }
            
            response = requests.post(
                'https://google.serper.dev/search',
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                search_data = response.json()
                
                prepared = self.session.prepare(f"""
                    INSERT INTO {ASTRA_DB_KEYSPACE}.search_data 
                    (query, category, collected_at, organic_results, 
                     news_results, knowledge_graph, related_searches)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """)
                
                self.session.execute(prepared, [
                    query,
                    category,
                    datetime.utcnow(),
                    json.dumps(search_data.get('organic', [])),
                    json.dumps(search_data.get('news', [])),
                    json.dumps(search_data.get('knowledgeGraph', {})),
                    json.dumps(search_data.get('relatedSearches', []))
                ])
                
                data_size = len(json.dumps(search_data).encode('utf-8'))
                self.logger.info(f"Stored search data for {category} - {query}")
                
        except Exception as e:
            self.logger.error(f"Error collecting search data: {str(e)}")
        
        end_time = time.time()
        return PerformanceMetrics(
            total_records=1,
            total_time=end_time - start_time,
            avg_time_per_record=end_time - start_time,
            data_size_bytes=data_size,
            records_per_second=1 / (end_time - start_time) if end_time > start_time else 0
        )
    
    def estimate_total_time(self, categories: Dict[str, List[str]]) -> TimeEstimate:
        """Estimate total time for data collection"""
        total_queries = sum(len(queries) for queries in categories.values())
        total_videos = total_queries * VIDEOS_PER_QUERY
        
        # Average time estimates
        avg_time_per_video = 0.02  # 20ms per video with batch processing
        avg_time_per_query = 1     # 1 second per search query
        
        youtube_time = (total_videos * avg_time_per_video) + \
                      (total_queries * 2)  # Additional 2s per query for API overhead
        search_time = total_queries * avg_time_per_query
        
        # Add 10% buffer for network variance
        buffer_factor = 1.1
        total_time = (youtube_time + search_time) * buffer_factor
        
        return TimeEstimate(
            youtube_time=youtube_time,
            search_time=search_time,
            total_time=total_time,
            videos_collected=total_videos,
            queries_processed=total_queries
        )
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

    def get_top_channels(self, category: str) -> List[Dict[str, str]]:
        """Get top YouTube channels for a category using OpenAI."""
        try:
            prompt = f"""Given the category '{category}', provide the top 5 most influential YouTube channels in this space and try to get Indian Channels based on their content focus and typical content they produce.
            Return the response as a JSON array with objects containing:
            - channel_name: The channel's name
            - description: Brief description of their content focus
            - typical_content: Types of videos they typically produce
            
            Focus on channels that are:
            1. Highly relevant to the {category} category
            2. Have significant following and engagement
            3. Regularly produce content
            4. Known for quality content in this space"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a YouTube analytics expert."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            channels = json.loads(response.choices[0].message.content)['channels']
            self.logger.info(f"Successfully retrieved {len(channels)} channels for category: {category}")
            return channels
        except Exception as e:
            self.logger.error(f"Error getting top channels for {category}: {str(e)}")
            return []

    def generate_search_queries(self, channel_info: Dict[str, str]) -> List[str]:
        """Generate relevant search queries for a channel."""
        channel_name = channel_info['channel_name']
        content_focus = channel_info['typical_content']
        
        queries = [
            f"site:youtube.com {channel_name} {content_focus}",
            f"{channel_name} best videos {content_focus}",
            f"{channel_name} latest {content_focus}",
            f"{channel_name} popular {content_focus}"
        ]
        return queries

    def collect_category_data(self, category: str):
        """Collect data for a category using AI-discovered channels."""
        try:
            # Get top channels for the category
            top_channels = self.get_top_channels(category)
            
            # Generate queries for each channel
            all_queries = []
            for channel in top_channels:
                channel_queries = self.generate_search_queries(channel)
                all_queries.extend(channel_queries)
            
            # Collect data using the generated queries
            for query in all_queries:
                self.collect_youtube_data(category, query)
                self.collect_search_data(category, query)
                
            self.logger.info(f"Completed data collection for category: {category}")
            
        except Exception as e:
            self.logger.error(f"Error in collect_category_data for {category}: {str(e)}")

    def collect_data(self, categories: List[str] = None, progress_callback=None):
        """Collect all data with AI-powered channel discovery."""
        if categories is None:
            categories = list(CATEGORIES.keys())
            
        start_time = time.time()
        total_categories = len(categories)
        processed_categories = 0

        for category in categories:
            category_start = time.time()
            
            # Collect data for the category using AI-discovered channels
            self.collect_category_data(category)
            
            processed_categories += 1
            progress = (processed_categories / total_categories) * 100
            
            if progress_callback:
                progress_callback(progress, {
                    'category': category,
                    'time_taken': time.time() - category_start
                })

        return {
            'total_time': time.time() - start_time,
            'metrics': self.time_tracking
        }

def main():
    # Example categories
    categories = [
        "Tech Reviews",
        "Motivational",
        "Educational"
    ]
    
    collector = AstraDataCollector()
    
    def show_progress(progress, details):
        print(f"\rProgress: {progress:.1f}% - Processing category: {details['category']}", end="")
    
    print("\nStarting AI-powered data collection...")
    results = collector.collect_data(categories, progress_callback=show_progress)
    
    print("\n\nCollection completed!")
    print(f"Total time taken: {results['total_time']/60:.1f} minutes")
    print(f"Videos collected: {results['metrics']['videos_collected']}")
    print(f"Queries processed: {results['metrics']['queries_processed']}")

if __name__ == "__main__":
    main()