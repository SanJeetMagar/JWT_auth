import os
from pathlib import Path
from dotenv import load_dotenv

# Check current directory
current_dir = Path(__file__).resolve().parent
print(f"Current directory: {current_dir}")

# Look for .env file
env_path = current_dir / '.env'
print(f".env file path: {env_path}")
print(f".env file exists: {env_path.exists()}")

# Try to load it
load_dotenv(env_path)

# Print values
print(f"\nEMAIL_HOST: {os.environ.get('EMAIL_HOST')}")
print(f"EMAIL_PORT: {os.environ.get('EMAIL_PORT')}")
print(f"EMAIL_HOST_USER: {os.environ.get('EMAIL_HOST_USER')}")
print(f"EMAIL_HOST_PASSWORD: {os.environ.get('EMAIL_HOST_PASSWORD')}")
print(f"EMAIL_USE_TLS: {os.environ.get('EMAIL_USE_TLS')}")