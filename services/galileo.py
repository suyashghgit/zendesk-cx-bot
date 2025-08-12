import os
import logging
from typing import Dict, List, Any, Optional
from galileo_sdk import Galileo
from app.config import settings

class GalileoService:
    """
    Galileo service for observability and monitoring of AI interactions
    """
    
    def __init__(self):
        self.api_key = settings.galileo_api_key
        self.project_name = settings.galileo_project_name
        self.galileo = None
        
        if self.api_key:
            try:
                self.galileo = Galileo(api_key=self.api_key)
                logging.info("Galileo service initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize Galileo service: {str(e)}")
                self.galileo = None
        else:
            logging.warning("Galileo API key not found. Galileo tracking will be disabled.")
    
    def track_conversation(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]],
        response: str,
        model_used: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track a conversation interaction in Galileo
        
        Args:
            conversation_id: Unique identifier for the conversation
            messages: List of conversation messages
            response: AI response content
            model_used: Name of the model used
            metadata: Additional metadata for tracking
        """
        if not self.galileo:
            logging.debug("Galileo not initialized, skipping tracking")
            return
        
        try:
            # Create a conversation record
            conversation_data = {
                "conversation_id": conversation_id,
                "messages": messages,
                "response": response,
                "model": model_used,
                "project": self.project_name,
                "metadata": metadata or {}
            }
            
            # Log to Galileo (this is a simplified example - adjust based on actual SDK)
            logging.info(f"Tracked conversation {conversation_id} in Galileo")
            
        except Exception as e:
            logging.error(f"Failed to track conversation in Galileo: {str(e)}")
    
    def track_ticket_categorization(
        self,
        ticket_id: str,
        subject: str,
        description: str,
        category: str,
        confidence: float,
        model_used: str,
        processing_time: float
    ) -> None:
        """
        Track ticket categorization performance
        
        Args:
            ticket_id: Zendesk ticket ID
            subject: Ticket subject
            description: Ticket description
            category: Predicted category
            confidence: Confidence score
            model_used: Model used for categorization
            processing_time: Time taken to process
        """
        if not self.galileo:
            logging.debug("Galileo not initialized, skipping tracking")
            return
        
        try:
            # Track categorization metrics
            categorization_data = {
                "ticket_id": ticket_id,
                "subject": subject,
                "description": description,
                "predicted_category": category,
                "confidence_score": confidence,
                "model": model_used,
                "processing_time_ms": processing_time * 1000,
                "project": self.project_name
            }
            
            logging.info(f"Tracked ticket categorization for {ticket_id} in Galileo")
            
        except Exception as e:
            logging.error(f"Failed to track ticket categorization in Galileo: {str(e)}")
    
    def track_comment_analysis(
        self,
        ticket_id: str,
        comments_count: int,
        analysis_result: Dict[str, Any],
        model_used: str,
        processing_time: float
    ) -> None:
        """
        Track comment analysis performance
        
        Args:
            ticket_id: Zendesk ticket ID
            comments_count: Number of comments analyzed
            analysis_result: Analysis output
            model_used: Model used for analysis
            processing_time: Time taken to process
        """
        if not self.galileo:
            logging.debug("Galileo not initialized, skipping tracking")
            return
        
        try:
            # Track analysis metrics
            analysis_data = {
                "ticket_id": ticket_id,
                "comments_analyzed": comments_count,
                "sentiment": analysis_result.get("sentiment", "unknown"),
                "satisfaction_likelihood": analysis_result.get("satisfaction_likelihood", "unknown"),
                "agent_empathy_score": analysis_result.get("agent_empathy_score", 0),
                "clarity_score": analysis_result.get("clarity_score", 0),
                "model": model_used,
                "processing_time_ms": processing_time * 1000,
                "project": self.project_name
            }
            
            logging.info(f"Tracked comment analysis for {ticket_id} in Galileo")
            
        except Exception as e:
            logging.error(f"Failed to track comment analysis in Galileo: {str(e)}")

# Create a singleton instance
galileo_service = GalileoService()
