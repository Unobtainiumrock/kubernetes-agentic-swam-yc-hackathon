import uvicorn
from .app import create_app

if __name__ == "__main__":
    # Use custom port 8888 to avoid conflicts with other services
    uvicorn.run(create_app(), host="0.0.0.0", port=8888, log_level="info")
