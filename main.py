# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging, os

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
    title="FastAPI Boilerplate",
    description="A basic FastAPI boilerplate application",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
