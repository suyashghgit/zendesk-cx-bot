from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime

# Create FastAPI app instance
app = FastAPI(
    title="FastAPI Boilerplate",
    description="A basic FastAPI boilerplate application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to FastAPI Boilerplate!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Service is running"}

@app.post("/ticketCreatedWebhook")
async def ticket_created_webhook(request: Request):
    """Webhook endpoint to receive ticket creation events"""
    try:
        # Get the raw request body
        body = await request.body()
        
        # Get headers
        headers = dict(request.headers)
        
        # Try to parse as JSON, fallback to string if it fails
        try:
            data = json.loads(body)
            data_type = "JSON"
        except json.JSONDecodeError:
            data = body.decode('utf-8')
            data_type = "TEXT"
        
        # Log everything
        print(f"\n{'='*50}")
        print(f"[{datetime.now()}] WEBHOOK RECEIVED")
        print(f"{'='*50}")
        print(f"Headers:")
        for key, value in headers.items():
            print(f"  {key}: {value}")
        print(f"\nBody Type: {data_type}")
        print(f"Body:")
        print(json.dumps(data, indent=2) if data_type == "JSON" else data)
        print(f"{'='*50}\n")
        
        return {
            "status": "success",
            "message": "Webhook logged successfully",
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type
        }
        
    except Exception as e:
        print(f"[{datetime.now()}] Error processing webhook: {str(e)}")
        return {
            "status": "error",
            "message": f"Error processing webhook: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True) 