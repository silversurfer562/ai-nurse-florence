# Environment setup for serverless deployment
import os

# Set reasonable defaults for serverless environment
os.environ.setdefault('API_BEARER', 'development-key')
os.environ.setdefault('CORS_ORIGINS', '*')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('USE_LIVE', 'false')
os.environ.setdefault('RATE_LIMIT_PER_MINUTE', '60')
os.environ.setdefault('JWT_SECRET_KEY', 'development-jwt-secret-change-in-production')
os.environ.setdefault('JWT_ALGORITHM', 'HS256')
os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '10080')

# For serverless, disable features that require persistent connections
os.environ.setdefault('REDIS_URL', '')  # Disable Redis caching
os.environ.setdefault('DATABASE_URL', 'sqlite:///./temp.db')  # Use local SQLite for simplicity