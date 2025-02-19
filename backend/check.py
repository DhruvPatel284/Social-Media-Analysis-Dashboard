from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from config import *
import logging


class DataChecker:
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Astra DB connection
        self._init_astra_connection()

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

    def check_youtube_data(self, category: str = None, query: str = None):
        """
        Check YouTube data for a specific category or query.
        
        :param category: The category to filter by (optional)
        :param query: The query to filter by (optional)
        """
        try:
            if category and query:
                # Fetch data for a specific category and query
                fetch_query = f"""
                    SELECT * FROM {ASTRA_DB_KEYSPACE}.youtube_data 
                    WHERE category = %s AND query = %s
                """
                rows = self.session.execute(fetch_query, [category, query])
            elif category:
                # Fetch data for a specific category
                fetch_query = f"""
                    SELECT * FROM {ASTRA_DB_KEYSPACE}.youtube_data 
                    WHERE category = %s
                """
                rows = self.session.execute(fetch_query, [category])
            else:
                # Fetch all data (not recommended for large datasets)
                fetch_query = f"""
                    SELECT * FROM {ASTRA_DB_KEYSPACE}.youtube_data 
                    LIMIT 100
                """
                rows = self.session.execute(fetch_query)

            # Print the results
            print("\nYouTube Data:")
            for row in rows:
                row_dict = dict(row._asdict())
                print(f"Channel Name: {row_dict.get('channel_title')}")
                print(row_dict)  # Print the entire row for reference

        except Exception as e:
            self.logger.error(f"Error fetching YouTube data: {str(e)}")

    def check_search_data(self, category: str = None, query: str = None):
        """
        Check search data for a specific category or query.
        
        :param category: The category to filter by (optional)
        :param query: The query to filter by (optional)
        """
        try:
            if category and query:
                # Fetch data for a specific category and query
                fetch_query = f"""
                    SELECT * FROM {ASTRA_DB_KEYSPACE}.search_data 
                    WHERE category = %s AND query = %s
                """
                rows = self.session.execute(fetch_query, [category, query])
            elif category:
                # Fetch data for a specific category
                fetch_query = f"""
                    SELECT * FROM {ASTRA_DB_KEYSPACE}.search_data 
                    WHERE category = %s
                """
                rows = self.session.execute(fetch_query, [category])
            else:
                # Fetch all data (not recommended for large datasets)
                fetch_query = f"""
                    SELECT * FROM {ASTRA_DB_KEYSPACE}.search_data 
                    LIMIT 100
                """
                rows = self.session.execute(fetch_query)

            # Print the results
            print("\nSearch Data:")
            for row in rows:
                print(dict(row._asdict()))

        except Exception as e:
            self.logger.error(f"Error fetching search data: {str(e)}")

# Example usage
if __name__ == "__main__":
    checker = DataChecker()

    # Check YouTube data for a specific category
    print("Checking YouTube data for category: Smartphones")
    checker.check_youtube_data(category="Tech Reviews")

    # Check search data for a specific category and query
    # print("\nChecking search data for category: Smartphones, query: iPhone 15 reviews")
    # checker.check_search_data(category="Smartphones", query="iPhone 15 reviews")