import json
import logging
from typing import Dict, Any, Optional, Tuple

from services.azure_openai import azure_openai_service
from services.zendesk import zendesk_service

async def process_ticket_categorization(subject: str, description: str, request_id: str) -> Dict[str, Any]:
    """Process ticket categorization using Azure OpenAI."""
    logging.info(f"Request {request_id}: Sending to Azure OpenAI API for categorization")
    try:
        categorization_response = await azure_openai_service.categorize_ticket(subject, description)
        logging.info(f"Request {request_id}: Azure OpenAI API response received")
        logging.info(f"Request {request_id}: Azure OpenAI Response - {categorization_response}")
        return categorization_response
    except Exception as e:
        logging.error(f"Request {request_id}: Error calling Azure OpenAI - {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to categorize ticket: {str(e)}"
        }

async def process_ticket_analysis(ticket_id: str, detail: Dict[str, Any], request_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Process ticket analysis when status is SOLVED."""
    logging.info(f"Request {request_id}: Updating ticket summary for ticket {ticket_id}")
    ticket_public_comments = await zendesk_service.extract_ticket_comments(ticket_id, detail)
    
    llm_response = None
    analysis_update_result = None
    
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
        
        # Extract and process analysis from generated content
        if llm_response and llm_response.get("status") == "success":
            try:
                generated_content = llm_response.get("generated_content", "{}")
                content_data = json.loads(generated_content)
                analysis = content_data
                logging.info(f"Request {request_id}: Ticket Analysis - {json.dumps(analysis, indent=2)}")
                
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
    
    return llm_response, analysis_update_result 