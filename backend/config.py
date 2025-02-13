# config.py
"""Configuration settings for the data collector"""
import os
from dotenv import load_dotenv

load_dotenv()

CATEGORIES = {
    "Smartphones": [
        "iPhone 15 reviews",
        "Samsung S24 Ultra features",
        "Google Pixel 8 comparison",
        "OnePlus 12 launch",
        "Best smartphones 2024"
    ],
    "Electric Vehicles": [
        "Tesla Model Y review",
        "Ford Mustang Mach-E specs",
        "Rivian R1T features",
        "Hyundai IONIQ 6 launch",
        "Best EVs 2024"
    ],
    "Gaming Consoles": [
        "PS5 Slim review",
        "Xbox Series X games",
        "Nintendo Switch 2 rumors",
        "Steam Deck OLED features",
        "Best gaming consoles 2024"
    ]
}

# API Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
ASTRA_DB_TOKEN = os.getenv('ASTRA_DB_TOKEN')
ASTRA_DB_KEYSPACE = os.getenv('ASTRA_DB_KEYSPACE', 'social_dashboard')
SECURE_BUNDLE_PATH = os.getenv('SECURE_BUNDLE_PATH', 'secure-connect-your-db.zip')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SEGMIND_API_KEY = os.getenv('SEGMIND_API_KEY')

# Collection Settings
VIDEOS_PER_QUERY = 100
RATE_LIMIT_YOUTUBE = 50  # calls per 100 seconds
RATE_LIMIT_SEARCH = 10   # calls per 60 seconds
DATA_RETENTION_DAYS = 30