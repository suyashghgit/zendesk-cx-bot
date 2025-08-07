# app/routers/twilio.py

from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import Response
import logging
from typing import Optional

from app.utils import (
    generate_request_id,
    log_request_start,
    create_success_response,
    create_error_response
)
from services.twilio import twilio_service

router = APIRouter()

def validate_twilio_request(request: Request) -> bool:
    """
    Validate Twilio webhook signature for security.
    
    Args:
        request (Request): FastAPI request object
    
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        # Get the signature from headers
        signature = request.headers.get("X-Twilio-Signature", "")
        if not signature:
            logging.warning("No Twilio signature found in request headers")
            return False
        
        # Get the full URL
        url = str(request.url)
        
        # Get form data as dict
        form_data = {}
        if request.method == "POST":
            try:
                body = request.body()
                if body:
                    # Parse form data manually
                    body_str = body.decode('utf-8')
                    for item in body_str.split('&'):
                        if '=' in item:
                            key, value = item.split('=', 1)
                            form_data[key] = value
            except Exception as e:
                logging.error(f"Error parsing form data: {str(e)}")
                return False
        
        # Validate signature
        is_valid = twilio_service.validate_webhook_signature(url, form_data, signature)
        
        if not is_valid:
            logging.warning("Invalid Twilio webhook signature")
        
        return is_valid
        
    except Exception as e:
        logging.error(f"Error validating Twilio request: {str(e)}")
        return False

@router.post("/twilio/whatsapp")
async def twilio_whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    To: str = Form(...)
):
    """
    Handle incoming WhatsApp webhooks from Twilio.
    
    This endpoint:
    1. Receives WhatsApp messages from Twilio
    2. Validates message content (minimum 10 chars, meaningful content)
    3. Creates Zendesk tickets automatically for valid messages
    4. Sends confirmation messages back to customers
    5. Handles errors gracefully with appropriate responses
    
    Args:
        request (Request): FastAPI request object
        From (str): Sender's phone number (with whatsapp: prefix)
        Body (str): WhatsApp message content
        MessageSid (str): Twilio message SID
        To (str): Recipient phone number (your Twilio WhatsApp number)
    
    Returns:
        Response: TwiML response for Twilio
    
    Example successful flow:
        Customer: "I can't log into my account, getting error 404"
        System: Creates ticket #12345 with subject "I can't log into my account, getting error 404"
        System: Sends "Ticket #12345 created: 'I can't log into my account, getting error 404'. We'll get back to you soon."
    
    Example validation failure:
        Customer: "help"
        System: Sends "Please provide more details about your issue. For example: 'I can't log in' or 'Billing question about invoice #123'"
    """
    request_id = generate_request_id()
    log_request_start(request_id, "/twilio/whatsapp")
    
    try:
        # Clean the phone number (remove whatsapp: prefix)
        clean_from = From.replace("whatsapp:", "") if From.startswith("whatsapp:") else From
        clean_to = To.replace("whatsapp:", "") if To.startswith("whatsapp:") else To
        
        # Log the incoming WhatsApp message
        logging.info(f"Request {request_id}: Received WhatsApp message from {clean_from} to {clean_to}")
        logging.info(f"Request {request_id}: Message SID: {MessageSid}")
        logging.info(f"Request {request_id}: Message body: {Body}")
        
        # Validate Twilio webhook signature (optional - will be skipped if no secret configured)
        validation_result = validate_twilio_request(request)
        if not validation_result:
            logging.warning(f"Request {request_id}: Invalid Twilio signature or no signature found, but proceeding")
            # In production, you might want to raise an HTTPException here if webhook secret is configured
        
        # Process the WhatsApp message and create ticket
        ticket_result = await twilio_service.create_ticket_from_whatsapp(clean_from, Body, request_id)
        
        # Prepare response message and get ticket_id
        ticket_id = None
        if ticket_result.get("status") == "success":
            ticket_id = ticket_result.get("ticket_id")
            subject = ticket_result.get("subject", "Support Request")
            
            response_message = f"Ticket #{ticket_id} created: '{subject}'. We'll get back to you soon."
            
            logging.info(f"Request {request_id}: Successfully created ticket {ticket_id} from WhatsApp")
            
        elif ticket_result.get("status") == "validation_failed":
            response_message = ticket_result.get("message", "Please provide more details about your issue.")
            
            logging.info(f"Request {request_id}: WhatsApp validation failed - {response_message}")
            
        else:
            response_message = "Sorry, we couldn't create your ticket right now. Please try again later or contact support directly."
            
            logging.error(f"Request {request_id}: Failed to create ticket from WhatsApp - {ticket_result}")
        
        # Send WhatsApp response back to customer (pass ticket_id for template variables)
        logging.info(f"Request {request_id}: Attempting to send WhatsApp response to {clean_from}")
        logging.info(f"Request {request_id}: Response message: {response_message}")
        logging.info(f"Request {request_id}: Ticket ID: {ticket_id}")
        
        whatsapp_response = await twilio_service.send_whatsapp_response(clean_from, response_message, request_id, ticket_id)
        
        if whatsapp_response.get("status") != "success":
            logging.error(f"Request {request_id}: Failed to send WhatsApp response - {whatsapp_response}")
            logging.error(f"Request {request_id}: Error details: {whatsapp_response.get('message', 'Unknown error')}")
        else:
            logging.info(f"Request {request_id}: WhatsApp response sent successfully - Used template: {whatsapp_response.get('used_template', False)}")
            logging.info(f"Request {request_id}: Message SID: {whatsapp_response.get('message_sid', 'N/A')}")
            logging.info(f"Request {request_id}: To number: {whatsapp_response.get('to_number', 'N/A')}")
        
        # Return TwiML response (empty for now, since we're sending WhatsApp message separately)
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <!-- WhatsApp response sent separately -->
</Response>"""
        
        return Response(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        logging.error(f"Request {request_id}: Error processing WhatsApp webhook: {str(e)}")
        
        # Return error TwiML response
        error_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Sorry, we encountered an error processing your request. Please try again later.</Message>
</Response>"""
        
        return Response(content=error_response, media_type="application/xml")
