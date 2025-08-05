from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime
import uuid
import logging
import os
from jinja2 import Environment, FileSystemLoader

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webhook_requests.log'),
        logging.StreamHandler()
    ]
)

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
    # Generate unique UUID for this request
    request_id = str(uuid.uuid4())
    
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
        
        # Extract subject and description from Zendesk webhook data
        subject = ""
        description = ""
        
        if data_type == "JSON" and isinstance(data, dict):
            # Navigate through the Zendesk webhook structure
            if "detail" in data:
                detail = data["detail"]
                subject = detail.get("subject", "")
                description = detail.get("description", "")
        
        # Render Jinja template with extracted data
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("ticket_categorizer.jinja")
        rendered_template = template.render(subject=subject, description=description)
        
        # Create log entry with UUID
        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "endpoint": "/ticketCreatedWebhook",
            "method": "POST",
            "headers": headers,
            "body_type": data_type,
            "body": data if data_type == "TEXT" else data,
            "status": "success"
        }
        
        # Log to file
        logging.info(f"Request {request_id}: Webhook received successfully")
        logging.info(f"Request {request_id}: Body Type - {data_type}")
        logging.info(f"Request {request_id}: Body - {json.dumps(data, indent=2) if data_type == 'JSON' else data}")
        logging.info(f"Request {request_id}: Rendered Template - {rendered_template}")
        
        # Also print to console for immediate visibility
        print(f"\n{'='*50}")
        print(f"[{datetime.now()}] WEBHOOK RECEIVED - Request ID: {request_id}")
        print(f"{'='*50}")
        print(f"\nBody Type: {data_type}")
        print(f"Body:")
        print(json.dumps(data, indent=2) if data_type == "JSON" else data)
        print(f"{'='*50}\n")
        
        return {
            "status": "success",
            "message": "Webhook logged successfully",
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type
        }
        
    except Exception as e:
        error_msg = f"Error processing webhook: {str(e)}"
        logging.error(f"Request {request_id}: {error_msg}")
        print(f"[{datetime.now()}] Request {request_id}: Error processing webhook: {str(e)}")
        
        return {
            "status": "error",
            "message": error_msg,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True) 