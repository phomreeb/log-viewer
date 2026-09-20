from pathlib import Path

# Base settings
BASE_DIR = Path("./logs")

# UI Settings
DEFAULT_ROW_LIMIT = 1000
MAX_ROW_LIMIT = 10000
MIN_ROW_LIMIT = 100

# Cache Settings
CACHE_TTL_DATA = 5
CACHE_TTL_NAMES = 10

# Chart Settings
COLOR_MAPPING = {
    "ERROR": "#ef4444",   # Red
    "WARN": "#f59e0b",    # Orange
    "WARNING": "#f59e0b", # Orange
    "INFO": "#10b981",    # Green
    "DEBUG": "#3b82f6",   # Blue
    "CRITICAL": "#7f1d1d" # Dark Red
}
