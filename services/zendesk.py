# services/zendesk.py

import os
import base64
import requests
import logging
import json
from typing import Dict, List, Any
from app.config import settings

class ZendeskService:
    """Service class for handling all Zendesk API operations."""
    
    def __init__(self):
        self.zendesk_domain = settings.zendesk_domain
        self.zendesk_email = settings.zendesk_email
        self.zendesk_api_token = settings.zendesk_api_key
        self.headers = None
    
    def _get_headers(self):
        """Lazy initialization of Zendesk headers"""
        if not all([self.zendesk_domain, self.zendesk_email, self.zendesk_api_token]):
            raise ValueError("Missing Zendesk configuration. Please set zendesk_domain, zendesk_email, and zendesk_api_key environment variables.")
        
        if self.headers is None:
            # Prepare the authorization header
            auth_string = f"{self.zendesk_email}/token:{self.zendesk_api_token}"
            auth_header = base64.b64encode(auth_string.encode()).decode()
            
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {auth_header}"
            }
            
            # Log the configuration (without exposing sensitive data)
            logging.info(f"Zendesk configuration loaded - Domain: {self.zendesk_domain}, Email: {self.zendesk_email}")
        
        return self.headers
    
    async def update_ticket(self, ticket_id: str, update_data: dict, operation_description: str = "update") -> dict:
        """
        Generic function to update a Zendesk ticket with any data.
        
        Args:
            ticket_id (str): The Zendesk ticket ID to update
            update_data (dict): The data to update the ticket with
            operation_description (str): Description of the operation for logging
        
        Returns:
            dict: Response from Zendesk API with status and details
        """
        try:
            # Zendesk API URL for updating ticket
            zendesk_url = f"https://{self.zendesk_domain}/api/v2/tickets/{ticket_id}.json"
            
            # Make the API call to update the ticket
            headers = self._get_headers()
            response = requests.put(
                zendesk_url,
                headers=headers,
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logging.info(f"Successfully {operation_description} Zendesk ticket {ticket_id}")
                return {
                    "status": "success",
                    "message": f"Ticket {ticket_id} {operation_description} successfully",
                    "zendesk_response": response.json()
                }
            else:
                logging.error(f"Failed to {operation_description} Zendesk ticket {ticket_id}: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"Failed to {operation_description} Zendesk ticket: {response.status_code}",
                    "zendesk_response": response.text
                }
                
        except Exception as e:
            logging.error(f"Error {operation_description} Zendesk ticket {ticket_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Exception occurred while {operation_description} ticket: {str(e)}"
            }
    
    async def update_ticket_tags(self, categorization_response: dict, ticket_id: str) -> dict:
        """
        Update a Zendesk ticket with tags from Azure OpenAI categorization.
        
        Args:
            categorization_response (dict): The response from Azure OpenAI API containing category and confidence
            ticket_id (str): The Zendesk ticket ID to update
        
        Returns:
            dict: Response from Zendesk API with status and details
        """
        try:
            # Extract category and confidence from Azure OpenAI response
            if categorization_response.get("status") == "success":
                category = categorization_response.get("category", "unknown")
                confidence = categorization_response.get("confidence", 0.0)
                model_used = categorization_response.get("model_used", "unknown")
            else:
                logging.error(f"Invalid Azure OpenAI response: {categorization_response}")
                return {
                    "status": "error",
                    "message": "Invalid Azure OpenAI response",
                    "categorization_response": categorization_response
                }
            
            # Prepare the update data for Zendesk
            update_data = {
                "ticket": {
                    "tags": [f"auto_categorized_{category}"],
                    "comment": {
                        "body": f"Ticket automatically categorized as '{category}' with {confidence:.2%}.",
                        "public": False
                    }
                }
            }
            
            # Use the reusable function
            result = await self.update_ticket(ticket_id, update_data, "categorized")
            
            # Add additional context to the result
            if result["status"] == "success":
                result["category"] = category
                result["confidence"] = confidence
                
            return result
                
        except Exception as e:
            logging.error(f"Error updating Zendesk ticket {ticket_id} with tags: {str(e)}")
            return {
                "status": "error",
                "message": f"Exception occurred while updating ticket tags: {str(e)}"
            }
    
    async def update_ticket_with_analysis(self, analysis: dict, ticket_id: str) -> dict:
        """
        Update a Zendesk ticket with analysis results as a comment.
        
        Args:
            analysis (dict): The analysis data containing insights about the ticket
            ticket_id (str): The Zendesk ticket ID to update
        
        Returns:
            dict: Response from Zendesk API with status and details
        """
        try:
            # Format the analysis data for the comment
            comment_body = self._format_analysis_for_comment(analysis)
            
            # Prepare the update data for Zendesk
            update_data = {
                "ticket": {
                    "comment": {
                        "body": comment_body,
                        "public": False
                    }
                }
            }
            
            # Use the reusable function
            return await self.update_ticket(ticket_id, update_data, "analyzed")
                
        except Exception as e:
            logging.error(f"Error updating Zendesk ticket {ticket_id} with analysis: {str(e)}")
            return {
                "status": "error",
                "message": f"Exception occurred while updating ticket with analysis: {str(e)}"
            }
    
    def _format_analysis_for_comment(self, analysis: dict) -> str:
        """
        Format analysis data into a readable comment for Zendesk.
        
        Args:
            analysis (dict): The analysis data
        
        Returns:
            str: Formatted comment text
        """
        try:
            comment_parts = []
            comment_parts.append("🤖 **AI Analysis Report**")
            comment_parts.append("")
            
            # Add summary if available
            if analysis.get("summary"):
                comment_parts.append(f"**Summary:** {analysis['summary']}")
                comment_parts.append("")
            
            # Add sentiment analysis
            if analysis.get("sentiment"):
                sentiment_emoji = {
                    "Positive": "😊",
                    "Neutral": "😐", 
                    "Negative": "😞"
                }.get(analysis["sentiment"], "❓")
                comment_parts.append(f"**Sentiment:** {sentiment_emoji} {analysis['sentiment']}")
            
            # Add satisfaction likelihood
            if analysis.get("satisfaction_likelihood"):
                satisfaction_emoji = {
                    "High": "✅",
                    "Medium": "⚠️",
                    "Low": "❌"
                }.get(analysis["satisfaction_likelihood"], "❓")
                comment_parts.append(f"**Satisfaction Likelihood:** {satisfaction_emoji} {analysis['satisfaction_likelihood']}")
            
            # Add scores
            if analysis.get("agent_empathy_score"):
                comment_parts.append(f"**Agent Empathy Score:** {analysis['agent_empathy_score']}/5")
            
            if analysis.get("clarity_score"):
                comment_parts.append(f"**Clarity Score:** {analysis['clarity_score']}/5")
            
            # Add pain points if available
            if analysis.get("pain_points") and analysis["pain_points"]:
                comment_parts.append("")
                comment_parts.append("**Pain Points:**")
                for point in analysis["pain_points"]:
                    comment_parts.append(f"• {point}")
            
            # Add frustration signals if available
            if analysis.get("frustration_signals") and analysis["frustration_signals"]:
                comment_parts.append("")
                comment_parts.append("**Frustration Signals:**")
                for signal in analysis["frustration_signals"]:
                    comment_parts.append(f"• {signal}")
            
            # Add action recommendations if available
            if analysis.get("action_recommendations") and analysis["action_recommendations"]:
                comment_parts.append("")
                comment_parts.append("**Action Recommendations:**")
                for rec in analysis["action_recommendations"]:
                    comment_parts.append(f"• {rec}")
            
            # Add resolution confidence if available
            if analysis.get("resolution_confidence"):
                comment_parts.append("")
                comment_parts.append(f"**Resolution Confidence:** {analysis['resolution_confidence']}")
            
            return "\n".join(comment_parts)
            
        except Exception as e:
            logging.error(f"Error formatting analysis for comment: {str(e)}")
            return f"🤖 **AI Analysis Report**\n\nError formatting analysis: {str(e)}"
    
    async def extract_ticket_comments(self, ticket_id: str, ticket_data: dict) -> dict:
        """
        Fetch comments from a Zendesk ticket and extract only public comments.
        
        Args:
            ticket_id (str): The Zendesk ticket ID to fetch comments from
            ticket_data (dict): The ticket data containing subject, description, etc.
        
        Returns:
            dict: Response containing public comments from the ticket
        """
        try:
            # Zendesk API URL for fetching comments
            comments_url = f"https://{self.zendesk_domain}/api/v2/tickets/{ticket_id}/comments.json"
            
            # Make the GET request to fetch comments
            headers = self._get_headers()
            logging.info(f"Making request to: {comments_url}")
            logging.info(f"Headers: {headers}")
            
            response = requests.get(
                comments_url,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                comments_data = response.json()
                comments = comments_data.get("comments", [])
                
                # Extract only public comments with only plain_body, created_at, and author_id fields
                public_comments = [
                    {
                        "plain_body": comment.get("plain_body", ""),
                        "created_at": comment.get("created_at", ""),
                        "author_id": comment.get("author_id", "")
                    }
                    for comment in comments if comment.get("public", False)
                ]
                
                logging.info(f"Successfully fetched comments for Zendesk ticket {ticket_id}. Found {len(public_comments)} public comments out of {len(comments)} total comments.")
                
                return public_comments
            else:
                logging.error(f"Failed to fetch comments for Zendesk ticket {ticket_id}: {response.status_code} - {response.text}")
                logging.error(f"Request URL: {comments_url}")
                logging.error(f"Response headers: {dict(response.headers)}")
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

# Create a singleton instance
zendesk_service = ZendeskService() 