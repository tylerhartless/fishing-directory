"""
Configuration file for database connection and settings
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# Mapbox (optional, for geocoding)
MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN', '')

# Data source paths
RAW_DATA_DIR = '../raw-data'
PROCESSED_DATA_DIR = '../processed-data'

# Validate required config
def validate_config():
    """Check if required environment variables are set"""
    required = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing = [key for key in required if not os.getenv(key)]

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    print("✓ Configuration validated successfully")

if __name__ == "__main__":
    validate_config()
    print(f"Database: {DB_CONFIG['database']} @ {DB_CONFIG['host']}")