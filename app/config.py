import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
