# app/routers/webhook.py

from fastapi import APIRouter, Request
import json, uuid, logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from services.huggingface import send_to_huggingface  # Import helper

router = APIRouter()

@router.post("/ticketCreatedWebhook")
async def ticket_created_webhook(request: Request):
    request_id = str(uuid.uuid4())
    
    # Log incoming request
    logging.info(f"Request {request_id}: Webhook endpoint called")

    try:
        body = await request.body()
        headers = dict(request.headers)
        
        # Log entire request body
        try:
            body_text = body.decode('utf-8')
            logging.info(f"Request {request_id}: Complete request body - {body_text}")
        except UnicodeDecodeError:
            logging.info(f"Request {request_id}: Complete request body (binary) - {body}")

        try:
            data = json.loads(body)
            data_type = "JSON"
            logging.info(f"Request {request_id}: Parsed JSON data successfully")
        except json.JSONDecodeError:
            data = body.decode('utf-8')
            data_type = "TEXT"
            logging.info(f"Request {request_id}: Body treated as text")

        subject = ""
        description = ""

        if data_type == "JSON" and isinstance(data, dict):
            logging.info(f"Request {request_id}: Processing JSON data")
            if "detail" in data:
                detail = data["detail"]
                subject = detail.get("subject", "")
                description = detail.get("description", "")
                logging.info(f"Request {request_id}: Extracted subject - {subject[:50]}...")
                logging.info(f"Request {request_id}: Extracted description - {description[:100]}...")
            else:
                logging.warning(f"Request {request_id}: No 'detail' field found in JSON data")
        else:
            logging.info(f"Request {request_id}: Processing text data")

        # Template processing
        logging.info(f"Request {request_id}: Loading Jinja2 template")
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("ticket_categorizer.jinja")
        rendered_template = template.render(subject=subject, description=description)
        logging.info(f"Request {request_id}: Template rendered successfully")

        # HuggingFace API call
        logging.info(f"Request {request_id}: Sending to HuggingFace API")
        huggingface_response = await send_to_huggingface(rendered_template)
        logging.info(f"Request {request_id}: HuggingFace API response received")
        logging.info(f"Request {request_id}: HuggingFace Response - {huggingface_response}")

        # Success response
        logging.info(f"Request {request_id}: Webhook processed successfully")
        return {
            "status": "success",
            "message": "Webhook logged successfully",
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type,
            "huggingface_response": huggingface_response
        }

    except Exception as e:
        logging.error(f"Request {request_id}: Error occurred - {str(e)}")
        logging.error(f"Request {request_id}: Error type - {type(e).__name__}")
        return {
            "status": "error",
            "message": str(e),
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }
