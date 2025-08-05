# app/routers/webhook.py

from fastapi import APIRouter, Request
import json, uuid, logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import requests
import os
import base64

from services.huggingface import send_to_huggingface  # Import helper

router = APIRouter()

async def update_zendesk_ticket_tags(huggingface_response: dict, ticket_id: str) -> dict:
    """
    Update a Zendesk ticket with the categorization results from HuggingFace.
    
    Args:
        huggingface_response (dict): The response from HuggingFace API containing category and confidence
        ticket_id (str): The Zendesk ticket ID to update
    
    Returns:
        dict: Response from Zendesk API with status and details
    """
    try:
        # Extract category and confidence from HuggingFace response
        if huggingface_response.get("status") == "success":
            category = huggingface_response.get("category", "unknown")
            confidence = huggingface_response.get("confidence", 0.0)
            model_used = huggingface_response.get("model_used", "unknown")
        else:
            logging.error(f"Invalid HuggingFace response: {huggingface_response}")
            return {
                "status": "error",
                "message": "Invalid HuggingFace response",
                "huggingface_response": huggingface_response
            }
        
        # Prepare the update data for Zendesk
        update_data = {
            "ticket": {
                "tags": [f"auto_categorized_{category}"],
                "comment": {
                    "body": f"Ticket automatically categorized as '{category}' with {confidence:.2%} confidence using {model_used} model.",
                    "public": False
                }
            }
        }
        
        # Zendesk API configuration
        zendesk_domain = os.getenv("ZENDESK_DOMAIN")
        zendesk_email = os.getenv("ZENDESK_EMAIL")
        zendesk_api_token = os.getenv("ZENDESK_API_KEY")
        
        if not all([zendesk_domain, zendesk_email, zendesk_api_token]):
            return {
                "status": "error",
                "message": "Missing Zendesk configuration. Please set ZENDESK_DOMAIN, ZENDESK_EMAIL, and ZENDESK_API_TOKEN environment variables."
            }
        
        #Prepare the authorization header
        auth_header = base64.b64encode(f"{zendesk_email}/token:{zendesk_api_token}".encode()).decode()
        
        # Zendesk API headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_header}"
        }
        
        # Zendesk API URL for updating ticket
        zendesk_url = f"https://{zendesk_domain}/api/v2/tickets/{ticket_id}.json"
        
        # Make the API call to update the ticket
        response = requests.put(
            zendesk_url,
            headers=headers,
            json=update_data,
            timeout=30
        )
        
        if response.status_code == 200:
            logging.info(f"Successfully updated Zendesk ticket {ticket_id} with category '{category}'")
            return {
                "status": "success",
                "message": f"Ticket {ticket_id} updated successfully",
                "category": category,
                "confidence": confidence,
                "zendesk_response": response.json()
            }
        else:
            logging.error(f"Failed to update Zendesk ticket {ticket_id}: {response.status_code} - {response.text}")
            return {
                "status": "error",
                "message": f"Failed to update Zendesk ticket: {response.status_code}",
                "zendesk_response": response.text
            }
            
    except Exception as e:
        logging.error(f"Error updating Zendesk ticket {ticket_id}: {str(e)}")
        return {
            "status": "error",
            "message": f"Exception occurred while updating ticket: {str(e)}"
        }

async def extract_ticket_comments(ticket_id: str, ticket_data: dict) -> dict:
    """
    Fetch comments from a Zendesk ticket and extract only public comments.
    
    Args:
        ticket_id (str): The Zendesk ticket ID to fetch comments from
        ticket_data (dict): The ticket data containing subject, description, etc.
    
    Returns:
        dict: Response containing public comments from the ticket
    """
    try:
        # Zendesk API configuration
        zendesk_domain = os.getenv("ZENDESK_DOMAIN")
        zendesk_email = os.getenv("ZENDESK_EMAIL")
        zendesk_api_token = os.getenv("ZENDESK_API_KEY")
        
        if not all([zendesk_domain, zendesk_email, zendesk_api_token]):
            return {
                "status": "error",
                "message": "Missing Zendesk configuration. Please set ZENDESK_DOMAIN, ZENDESK_EMAIL, and ZENDESK_API_TOKEN environment variables."
            }
        
        # Prepare the authorization header
        auth_header = base64.b64encode(f"{zendesk_email}/token:{zendesk_api_token}".encode()).decode()
        
        # Zendesk API headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_header}"
        }
        
        # Zendesk API URL for fetching comments
        comments_url = f"https://{zendesk_domain}/api/v2/tickets/{ticket_id}/comments.json"
        
        # Make the GET request to fetch comments
        response = requests.get(
            comments_url,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            comments_data = response.json()
            comments = comments_data.get("comments", [])
            
            # Extract only public comments
            public_comments = [comment for comment in comments if comment.get("public", False)]
            
            logging.info(f"Successfully fetched comments for Zendesk ticket {ticket_id}. Found {len(public_comments)} public comments out of {len(comments)} total comments.")
            
            return {
                "status": "success",
                "message": f"Successfully fetched comments for ticket {ticket_id}",
                "ticket_id": ticket_id,
                "total_comments": len(comments),
                "public_comments": public_comments,
                "public_comments_count": len(public_comments),
                "all_comments_response": comments_data
            }
        else:
            logging.error(f"Failed to fetch comments for Zendesk ticket {ticket_id}: {response.status_code} - {response.text}")
            return {
                "status": "error",
                "message": f"Failed to fetch comments: {response.status_code}",
                "zendesk_response": response.text
            }
            
    except Exception as e:
        logging.error(f"Error fetching comments for Zendesk ticket {ticket_id}: {str(e)}")
        return {
            "status": "error",
            "message": f"Exception occurred while fetching comments: {str(e)}"
        }

@router.post("/ticketCreatedWebhook")
async def ticket_created_webhook(request: Request):
    request_id = str(uuid.uuid4())
    
    # Log incoming request
    logging.info(f"Request {request_id}: /ticketCreatedWebhook webhook endpoint called")

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
        ticket_id = ""

        if data_type == "JSON" and isinstance(data, dict):
            logging.info(f"Request {request_id}: Processing JSON data")
            if "detail" in data:
                detail = data["detail"]
                subject = detail.get("subject", "")
                description = detail.get("description", "")
                ticket_id = detail.get("id", "")  # Extract ticket ID
                logging.info(f"Request {request_id}: Extracted subject - {subject[:50]}...")
                logging.info(f"Request {request_id}: Extracted description - {description[:100]}...")
                logging.info(f"Request {request_id}: Extracted ticket ID - {ticket_id}")
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

        # Update Zendesk ticket if we have a ticket ID
        zendesk_update_result = None
        if ticket_id:
            logging.info(f"Request {request_id}: Updating Zendesk ticket {ticket_id}")
            zendesk_update_result = await update_zendesk_ticket_tags(huggingface_response, ticket_id)
            logging.info(f"Request {request_id}: Zendesk update result - {zendesk_update_result}")
        else:
            logging.warning(f"Request {request_id}: No ticket ID found, skipping Zendesk update")

        # Success response
        logging.info(f"Request {request_id}: Webhook processed successfully")
        return {
            "status": "success",
            "message": "Webhook logged successfully",
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type,
            "huggingface_response": huggingface_response,
            "zendesk_update_result": zendesk_update_result
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

@router.post("/ticketStatusChangedWebhook")
async def ticket_status_changed_webhook(request: Request):
    request_id = str(uuid.uuid4())
    
    # Log incoming request
    logging.info(f"Request {request_id}: /ticketStatusChangedWebhook webhook endpoint called")

    try:
        body = await request.body()
        headers = dict(request.headers)

        try:
            data = json.loads(body)
            data_type = "JSON"
        except json.JSONDecodeError:
            data = body.decode('utf-8')
            data_type = "TEXT"

        # Check if this is a ticket status changed event
        if data_type == "JSON" and isinstance(data, dict):
            event = data.get("event", {})
            detail = data.get("detail", {})
            
            current_status = event.get("current", "")
            ticket_status = detail.get("status", "")
            
            logging.info(f"Request {request_id}: Event current status - {current_status}")
            
            # Check if both event.current and ticket status are "SOLVED"
            if current_status == "SOLVED" and ticket_status == "SOLVED":
                print(f"Ticket {detail.get('id', 'unknown')} is SOLVED!")
                logging.info(f"Request {request_id}: Ticket is SOLVED - {detail.get('id', 'unknown')}")
                
                # Update ticket summary when status is SOLVED
                ticket_id = detail.get("id", "")
                if ticket_id:
                    logging.info(f"Request {request_id}: Updating ticket summary for ticket {ticket_id}")
                    summary_update_result = await extract_ticket_comments(ticket_id, detail)
                    logging.info(f"Request {request_id}: Summary update result - {summary_update_result}")
                else:
                    logging.warning(f"Request {request_id}: No ticket ID found, skipping summary update")
                    summary_update_result = None
                
                return {
                    "status": "success",
                    "message": "Ticket status changed to SOLVED",
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat(),
                    "ticket_id": detail.get("id", ""),
                    "current_status": current_status,
                    "ticket_status": ticket_status
                }
            else:
                logging.info(f"Request {request_id}: Ticket status is not SOLVED (current: {current_status}, ticket: {ticket_status})")
                return {
                    "status": "success",
                    "message": "Ticket status changed but not to SOLVED",
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat(),
                    "ticket_id": detail.get("id", ""),
                    "current_status": current_status,
                    "ticket_status": ticket_status
                }
        else:
            logging.warning(f"Request {request_id}: Invalid data format")
            return {
                "status": "error",
                "message": "Invalid data format",
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
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
