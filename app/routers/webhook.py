# app/routers/webhook.py

from fastapi import APIRouter, Request
import logging
from jinja2 import Environment, FileSystemLoader

from app.utils import (
    generate_request_id,
    log_request_start,
    parse_request_body,
    log_request_body,
    extract_ticket_data,
    create_success_response,
    create_error_response
)
from app.services.webhook_services import (
    process_ticket_categorization,
    process_ticket_analysis
)
from services.zendesk import zendesk_service

router = APIRouter()

@router.post("/ticketCreatedWebhook")
async def ticket_created_webhook(request: Request):
    request_id = generate_request_id()
    log_request_start(request_id, "/ticketCreatedWebhook")

    try:
        body = await request.body()
        log_request_body(request_id, body)
        
        data, data_type = parse_request_body(body)
        
        subject, description, ticket_id = "", "", ""
        
        if data_type == "JSON" and isinstance(data, dict):
            logging.info(f"Request {request_id}: Processing JSON data")
            subject, description, ticket_id = extract_ticket_data(data, request_id)
        else:
            logging.info(f"Request {request_id}: Processing text data")

        # Template processing
        logging.info(f"Request {request_id}: Loading Jinja2 template")
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("ticket_categorizer.jinja")
        rendered_template = template.render(subject=subject, description=description)
        logging.info(f"Request {request_id}: Template rendered successfully")

        # Process ticket categorization
        categorization_response = await process_ticket_categorization(subject, description, request_id)

        # Update Zendesk ticket if we have a ticket ID
        zendesk_update_result = None
        if ticket_id:
            logging.info(f"Request {request_id}: Updating Zendesk ticket {ticket_id}")
            zendesk_update_result = await zendesk_service.update_ticket_tags(categorization_response, ticket_id)
            logging.info(f"Request {request_id}: Zendesk update result - {zendesk_update_result}")
        else:
            logging.warning(f"Request {request_id}: No ticket ID found, skipping Zendesk update")

        logging.info(f"Request {request_id}: Webhook processed successfully")
        return create_success_response(
            request_id,
            "Webhook logged successfully",
            data_type=data_type,
            categorization_response=categorization_response,
            zendesk_update_result=zendesk_update_result
        )

    except Exception as e:
        return create_error_response(request_id, e)

@router.post("/ticketStatusChangedWebhook")
async def ticket_status_changed_webhook(request: Request):
    request_id = generate_request_id()
    log_request_start(request_id, "/ticketStatusChangedWebhook")

    try:
        body = await request.body()
        data, data_type = parse_request_body(body)

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
                
                ticket_id = detail.get("id", "")
                llm_response = None
                analysis_update_result = None
                
                if ticket_id:
                    llm_response, analysis_update_result = await process_ticket_analysis(ticket_id, detail, request_id)
                else:
                    logging.warning(f"Request {request_id}: No ticket ID found, skipping summary update")
                
                return create_success_response(
                    request_id,
                    "Ticket status changed to SOLVED",
                    ticket_id=detail.get("id", ""),
                    current_status=current_status,
                    ticket_status=ticket_status,
                    llm_response=llm_response,
                    analysis_update_result=analysis_update_result
                )
            else:
                logging.info(f"Request {request_id}: Ticket status is not SOLVED (current: {current_status}, ticket: {ticket_status})")
                return create_success_response(
                    request_id,
                    "Ticket status changed but not to SOLVED",
                    ticket_id=detail.get("id", ""),
                    current_status=current_status,
                    ticket_status=ticket_status
                )
        else:
            logging.warning(f"Request {request_id}: Invalid data format")
            return create_error_response(request_id, Exception("Invalid data format"))

    except Exception as e:
        return create_error_response(request_id, e)
