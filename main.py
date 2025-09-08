import os

import uvicorn

from src.controller import app
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv() # init env variables from .env file
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", "8000")),
        log_level=os.getenv("LOG_LEVEL", "info"),
    )
