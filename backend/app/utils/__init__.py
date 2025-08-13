# Timezone-aware datetime utilities
from datetime import datetime, timezone
import os

def get_local_timezone():
    """Get the local timezone, defaulting to system timezone"""
    # Try to get timezone from environment variable first
    tz_env = os.environ.get('TZ')
    if tz_env:
        # For container environments, this might be set
        return timezone.utc  # Fallback for now, could be enhanced
    
    # Use system timezone
    return datetime.now().astimezone().tzinfo

def now_local():
    """Get current datetime in local timezone"""
    return datetime.now(get_local_timezone())

def utc_to_local(utc_dt):
    """Convert UTC datetime to local timezone"""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(get_local_timezone())

def format_timestamp(dt=None, format_str="%Y-%m-%d %H:%M:%S"):
    """Format timestamp in local timezone"""
    if dt is None:
        dt = now_local()
    elif dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = dt.replace(tzinfo=timezone.utc).astimezone(get_local_timezone())
    return dt.strftime(format_str)

def format_filename_timestamp(dt=None):
    """Format timestamp for filenames (no spaces or colons)"""
    return format_timestamp(dt, "%Y%m%d_%H%M%S")

def format_log_timestamp(dt=None):
    """Format timestamp for log display"""
    return format_timestamp(dt, "%H:%M:%S") 