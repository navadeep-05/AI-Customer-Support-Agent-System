import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Fallback API key from environment if provided
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-20b")
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/support.db")
