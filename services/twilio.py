# services/twilio.py

import os
import logging
import re
import json
from typing import Dict, Optional, Tuple
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from app.config import settings
from services.zendesk import zendesk_service

class TwilioService:
    """Service class for handling Twilio WhatsApp operations and ticket creation."""
    
    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.whatsapp_number = settings.twilio_whatsapp_number
        self.webhook_secret = settings.twilio_webhook_secret
        self.content_sid = settings.twilio_content_sid
        self.client = None
        self.validator = None
    
    def _get_client(self):
        """Lazy initialization of Twilio client"""
        if not all([self.account_sid, self.auth_token]):
            raise ValueError("Missing Twilio configuration. Please set twilio_account_sid and twilio_auth_token environment variables.")
        
        if self.client is None:
            self.client = Client(self.account_sid, self.auth_token)
            logging.info(f"Twilio client initialized - Account SID: {self.account_sid[:8]}...")
        
        return self.client
    
    def _get_validator(self):
        """Lazy initialization of Twilio request validator"""
        if not self.webhook_secret:
            logging.warning("No Twilio webhook secret configured. Webhook signature validation will be skipped.")
            return None
        
        if self.validator is None:
            self.validator = RequestValidator(self.webhook_secret)
            logging.info("Twilio request validator initialized")
        
        return self.validator
    
    def validate_webhook_signature(self, url: str, params: Dict, signature: str) -> bool:
        """
        Validate Twilio webhook signature for security.
        
        Args:
            url (str): The webhook URL
            params (Dict): The request parameters
            signature (str): The signature header from Twilio
        
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            validator = self._get_validator()
            if validator is None:
                logging.warning("Skipping webhook signature validation - no webhook secret configured")
                return True  # Allow request to proceed when no secret is configured
            
            return validator.validate(url, params, signature)
        except Exception as e:
            logging.error(f"Error validating Twilio webhook signature: {str(e)}")
            return False
    
    def validate_whatsapp_content(self, message_body: str) -> Tuple[bool, str]:
        """
        Validate WhatsApp content to ensure it's sufficient for ticket creation.
        
        Args:
            message_body (str): The WhatsApp message content
        
        Returns:
            Tuple[bool, str]: (is_valid, reason_or_suggestion)
        """
        if not message_body or not message_body.strip():
            return False, "Message is empty"
        
        # Remove whitespace and check length
        clean_message = message_body.strip()
        if len(clean_message) < 10:
            return False, "Please provide more details about your issue."
        
        # Check for generic/greeting messages
        generic_patterns = [
            r'^hi\b', r'^hello\b', r'^hey\b', r'^good\s*(morning|afternoon|evening)\b',
            r'^thanks?\b', r'^thank\s*you\b', r'^ok\b', r'^okay\b', r'^yes\b', r'^no\b',
            r'^help\b', r'^support\b'
        ]
        
        for pattern in generic_patterns:
            if re.match(pattern, clean_message.lower()):
                return False, "Please provide more details about your issue."
        
        # Check for actionable content (contains issue-related keywords)
        issue_keywords = [
            'problem', 'issue', 'error', 'bug', 'broken', 'not working', 'can\'t', 'cannot',
            'failed', 'failure', 'trouble', 'difficulty', 'question', 'inquiry', 'request',
            'need', 'want', 'looking for', 'searching for', 'trying to', 'attempting to'
        ]
        
        has_issue_keywords = any(keyword in clean_message.lower() for keyword in issue_keywords)
        
        if not has_issue_keywords and len(clean_message) < 20:
            return False, "Please describe your issue or request. For example: 'I can't log into my account' or 'Need help with billing'"
        
        return True, "Content is valid"
    
    async def create_ticket_from_whatsapp(self, phone_number: str, message_body: str, request_id: str) -> Dict:
        """
        Create a Zendesk ticket from WhatsApp content.
        
        Args:
            phone_number (str): The sender's phone number
            message_body (str): The WhatsApp message content
            request_id (str): Unique request ID for logging
        
        Returns:
            Dict: Response with ticket creation status and details
        """
        try:
            # Validate WhatsApp content
            is_valid, validation_message = self.validate_whatsapp_content(message_body)
            
            if not is_valid:
                logging.info(f"Request {request_id}: WhatsApp content validation failed - {validation_message}")
                return {
                    "status": "validation_failed",
                    "message": validation_message,
                    "requires_more_info": True
                }
            
            # Clean and format the message
            clean_message = message_body.strip()
            
            # Generate subject from first sentence or first 50 characters
            subject = self._generate_subject(clean_message)
            
            # Prepare ticket data
            ticket_data = {
                "ticket": {
                    "subject": subject,
                    "description": clean_message,
                    "requester": {
                        "name": f"WhatsApp User ({phone_number})",
                        "email": f"{phone_number}@whatsapp.zendesk.com"
                    },
                    "tags": ["whatsapp", "auto-created"],
                    "priority": self._determine_priority(clean_message),
                    "type": "incident"
                }
            }
            
            # Create ticket using Zendesk service
            logging.info(f"Request {request_id}: Creating Zendesk ticket from WhatsApp")
            ticket_result = await zendesk_service.create_ticket(ticket_data, request_id)
            
            if ticket_result.get("status") == "success":
                ticket_id = ticket_result.get("ticket_id")
                logging.info(f"Request {request_id}: Successfully created ticket {ticket_id} from WhatsApp")
                
                return {
                    "status": "success",
                    "message": f"Ticket #{ticket_id} created successfully",
                    "ticket_id": ticket_id,
                    "subject": subject,
                    "phone_number": phone_number
                }
            else:
                logging.error(f"Request {request_id}: Failed to create ticket from WhatsApp - {ticket_result}")
                return {
                    "status": "error",
                    "message": "Failed to create ticket. Please try again later.",
                    "zendesk_error": ticket_result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logging.error(f"Request {request_id}: Error creating ticket from WhatsApp: {str(e)}")
            return {
                "status": "error",
                "message": "An error occurred while creating your ticket. Please try again later.",
                "error": str(e)
            }
    
    def _generate_subject(self, message: str) -> str:
        """
        Generate a subject line from the WhatsApp message.
        
        Args:
            message (str): The WhatsApp message content
        
        Returns:
            str: Generated subject line
        """
        # Take first sentence or first 50 characters
        first_sentence = message.split('.')[0].strip()
        if len(first_sentence) > 50:
            first_sentence = first_sentence[:47] + "..."
        
        return first_sentence if first_sentence else "WhatsApp Support Request"
    
    def _determine_priority(self, message: str) -> str:
        """
        Determine ticket priority based on message content.
        
        Args:
            message (str): The WhatsApp message content
        
        Returns:
            str: Priority level (urgent, high, normal, low)
        """
        urgent_keywords = ['urgent', 'emergency', 'critical', 'broken', 'down', 'outage']
        high_keywords = ['important', 'issue', 'problem', 'error', 'failed', 'not working']
        
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in urgent_keywords):
            return "urgent"
        elif any(keyword in message_lower for keyword in high_keywords):
            return "high"
        else:
            return "normal"
    
    async def send_whatsapp_response(self, to_number: str, message: str, request_id: str, ticket_id: str = None) -> Dict:
        """
        Send WhatsApp response to customer using content templates.
        
        Args:
            to_number (str): Recipient phone number
            message (str): Message content
            request_id (str): Unique request ID for logging
            ticket_id (str): Optional ticket ID for template variables
        
        Returns:
            Dict: Response with WhatsApp sending status
        """
        try:
            client = self._get_client()
            
            # Format phone number for WhatsApp (add whatsapp: prefix)
            formatted_number = self._format_whatsapp_number(to_number)
            
            # Check if we have a content template configured
            if self.content_sid:
                # Use content template with variables
                content_variables = self._prepare_content_variables(message, ticket_id)
                
                logging.info(f"Request {request_id}: Sending WhatsApp template message to {formatted_number}")
                logging.info(f"Request {request_id}: Content SID: {self.content_sid}")
                logging.info(f"Request {request_id}: Content variables: {content_variables}")
                
                message_sid = client.messages.create(
                    from_=f"whatsapp:{self.whatsapp_number}",
                    content_sid=self.content_sid,
                    content_variables=json.dumps(content_variables),
                    to=formatted_number
                )
                
                logging.info(f"Request {request_id}: WhatsApp template message sent successfully - SID: {message_sid.sid}")
            else:
                # Fallback to regular message (for WhatsApp, we should use body)
                logging.info(f"Request {request_id}: Sending WhatsApp regular message to {formatted_number}")
                logging.info(f"Request {request_id}: Message: {message}")
                
                message_sid = client.messages.create(
                    body=message,
                    from_=f"whatsapp:{self.whatsapp_number}",
                    to=formatted_number
                )
                
                logging.info(f"Request {request_id}: WhatsApp message sent successfully - SID: {message_sid.sid}")
            
            return {
                "status": "success",
                "message_sid": message_sid.sid,
                "to_number": formatted_number,
                "used_template": bool(self.content_sid)
            }
            
        except Exception as e:
            logging.error(f"Request {request_id}: Error sending WhatsApp message: {str(e)}")
            logging.error(f"Request {request_id}: To number: {to_number}, Formatted number: {formatted_number if 'formatted_number' in locals() else 'N/A'}")
            logging.error(f"Request {request_id}: WhatsApp number: {self.whatsapp_number}")
            logging.error(f"Request {request_id}: Content SID: {self.content_sid}")
            return {
                "status": "error",
                "message": f"Failed to send WhatsApp message: {str(e)}"
            }
    
    def _prepare_content_variables(self, message: str, ticket_id: str = None) -> Dict:
        """
        Prepare content variables for WhatsApp template.
        
        Args:
            message (str): The message content
            ticket_id (str): Optional ticket ID
        
        Returns:
            Dict: Content variables for the template
        """
        # Truncate message to 50 characters for template variable
        truncated_message = message[:50] + "..." if len(message) > 50 else message
        
        # Prepare variables as strings (Twilio expects string values)
        variables = {
            "1": truncated_message,  # Truncated message content
            "2": str(ticket_id) if ticket_id else "N/A"  # Ticket ID as string
        }
        
        logging.info(f"Prepared content variables: {variables}")
        return variables
    
    def _format_whatsapp_number(self, phone_number: str) -> str:
        """
        Format phone number for WhatsApp.
        
        Args:
            phone_number (str): Raw phone number
        
        Returns:
            str: Formatted phone number with whatsapp: prefix
        """
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone_number)
        
        # If it's a 10-digit US number, add +1
        if len(digits_only) == 10:  
            return f"whatsapp:+1{digits_only}"
        # If it's already 11 digits with 1, add +
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            return f"whatsapp:+{digits_only}"
        # If it's already in international format, return as is
        elif digits_only.startswith('1') and len(digits_only) == 11:
            return f"whatsapp:+{digits_only}"
        else:
            # Assume it's already in international format or return as is
            if phone_number.startswith('+'):
                return f"whatsapp:{phone_number}"
            else:
                return f"whatsapp:+{digits_only}"

# Create a singleton instance
twilio_service = TwilioService() 