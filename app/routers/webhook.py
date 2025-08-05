# app/routers/webhook.py

from fastapi import APIRouter, Request
import json, uuid, logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from services.azure_openai import azure_openai_service  # Import Azure OpenAI services
from services.zendesk import zendesk_service  # Import Zendesk service

router = APIRouter()

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

        # Azure OpenAI API call for ticket categorization
        logging.info(f"Request {request_id}: Sending to Azure OpenAI API for categorization")
        try:
            categorization_response = await azure_openai_service.categorize_ticket(subject, description)
            logging.info(f"Request {request_id}: Azure OpenAI API response received")
            logging.info(f"Request {request_id}: Azure OpenAI Response - {categorization_response}")
        except Exception as e:
            logging.error(f"Request {request_id}: Error calling Azure OpenAI - {str(e)}")
            categorization_response = {
                "status": "error",
                "message": f"Failed to categorize ticket: {str(e)}"
            }

        # Update Zendesk ticket if we have a ticket ID
        zendesk_update_result = None
        if ticket_id:
            logging.info(f"Request {request_id}: Updating Zendesk ticket {ticket_id}")
            zendesk_update_result = await zendesk_service.update_ticket_tags(categorization_response, ticket_id)
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
            "categorization_response": categorization_response,
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
                llm_response = None
                analysis_update_result = None
                
                if ticket_id:
                    logging.info(f"Request {request_id}: Updating ticket summary for ticket {ticket_id}")
                    ticket_public_comments = await zendesk_service.extract_ticket_comments(ticket_id, detail)
                    
                    # Call Azure LLM with the public comments
                    if isinstance(ticket_public_comments, list) and len(ticket_public_comments) > 0:
                        logging.info(f"Request {request_id}: Calling Azure LLM with {len(ticket_public_comments)} comments")
                        try:
                            llm_response = await azure_openai_service.analyze_ticket_comments(ticket_public_comments)
                            logging.info(f"Request {request_id}: LLM response - {llm_response}")
                        except Exception as e:
                            logging.error(f"Request {request_id}: Error calling Azure LLM - {str(e)}")
                            llm_response = {
                                "status": "error",
                                "message": f"Failed to analyze ticket comments: {str(e)}"
                            }
                        
                        # Extract and log the analysis from generated content
                        if llm_response and llm_response.get("status") == "success":
                            try:
                                generated_content = llm_response.get("generated_content", "{}")
                                content_data = json.loads(generated_content)
                                analysis = content_data.get("analysis", {})
                                logging.info(f"Request {request_id}: Ticket Analysis - {json.dumps(analysis, indent=2)}")
                                
                                # Update Zendesk ticket with analysis
                                if analysis:
                                    logging.info(f"Request {request_id}: Updating Zendesk ticket {ticket_id} with analysis")
                                    analysis_update_result = await zendesk_service.update_ticket_with_analysis(analysis, ticket_id)
                                    logging.info(f"Request {request_id}: Analysis update result - {analysis_update_result}")
                                else:
                                    logging.warning(f"Request {request_id}: No analysis data found to update ticket")
                                    
                            except (json.JSONDecodeError, KeyError) as e:
                                logging.error(f"Request {request_id}: Error extracting analysis from LLM response - {str(e)}")
                    else:
                        logging.warning(f"Request {request_id}: No public comments found or error occurred")
                else:
                    logging.warning(f"Request {request_id}: No ticket ID found, skipping summary update")
                
                return {
                    "status": "success",
                    "message": "Ticket status changed to SOLVED",
                    "request_id": request_id,
                    "timestamp": datetime.now().isoformat(),
                    "ticket_id": detail.get("id", ""),
                    "current_status": current_status,
                    "ticket_status": ticket_status,
                    "llm_response": llm_response,
                    "analysis_update_result": analysis_update_result
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
