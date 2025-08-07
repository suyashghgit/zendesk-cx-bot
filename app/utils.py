import json, uuid, logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

def generate_request_id() -> str:
    """Generate a unique request ID for logging."""
    return str(uuid.uuid4())

def log_request_start(request_id: str, endpoint: str) -> None:
    """Log the start of a webhook request."""
    logging.info(f"Request {request_id}: {endpoint} webhook endpoint called")

def parse_request_body(body: bytes) -> Tuple[Any, str]:
    """
    Parse request body and return data and data type.
    
    Returns:
        Tuple[Any, str]: (parsed_data, data_type)
    """
    try:
        data = json.loads(body)
        return data, "JSON"
    except json.JSONDecodeError:
        return body.decode('utf-8'), "TEXT"

def log_request_body(request_id: str, body: bytes) -> None:
    """Log the complete request body."""
    try:
        body_text = body.decode('utf-8')
        logging.info(f"Request {request_id}: Complete request body - {body_text}")
    except UnicodeDecodeError:
        logging.info(f"Request {request_id}: Complete request body (binary) - {body}")

def extract_ticket_data(data: Dict[str, Any], request_id: str) -> Tuple[str, str, str]:
    """
    Extract ticket information from JSON data.
    
    Returns:
        Tuple[str, str, str]: (subject, description, ticket_id)
    """
    subject = ""
    description = ""
    ticket_id = ""
    
    if "detail" in data:
        detail = data["detail"]
        subject = detail.get("subject", "")
        description = detail.get("description", "")
        ticket_id = detail.get("id", "")
        logging.info(f"Request {request_id}: Extracted subject - {subject[:50]}...")
        logging.info(f"Request {request_id}: Extracted description - {description[:100]}...")
        logging.info(f"Request {request_id}: Extracted ticket ID - {ticket_id}")
    else:
        logging.warning(f"Request {request_id}: No 'detail' field found in JSON data")
    
    return subject, description, ticket_id 