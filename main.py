# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging, os

from app.config import settings  # Import settings

from app.routers import webhook  # import your router

# Create logs directory
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webhook_requests.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI(
    title=settings.app_name,
    description="A basic FastAPI boilerplate application",
    version=settings.app_version
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Boilerplate!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

# Mount routers
app.include_router(webhook.router)

# Run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
