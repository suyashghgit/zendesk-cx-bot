import os
import json
import logging
import time
from typing import Dict, List, Optional, Any
from openai import AzureOpenAI
from dotenv import load_dotenv
from app.config import settings
import httpx 
from services.galileo import galileo_service

# Load environment variables
load_dotenv()

class AzureOpenAIService:
    """
    Generic Azure OpenAI service for various AI tasks
    """
    
    def __init__(self):
        # Updated configuration to match Azure OpenAI documentation
        self.endpoint = settings.azure_openai_endpoint
        self.model_name = settings.azure_openai_model
        self.deployment = settings.azure_openai_deployment
        self.subscription_key = settings.azure_openai_api_key
        self.api_version = settings.azure_openai_api_version
        self.client = None
        
        # Validate configuration
        if not self.subscription_key:
            logging.warning("Azure OpenAI API key not found. Please set azure_openai_api_key environment variable.")
    
    def _get_client(self):
        """Lazy initialization of the Azure OpenAI client"""
        
        if self.client is None:
            try:
                http_client = httpx.Client()
                # Updated client initialization to match documentation
                self.client = AzureOpenAI(
                    api_version=self.api_version,
                    azure_endpoint=self.endpoint,
                    api_key=self.subscription_key,
                    http_client=http_client
                )
                logging.info(f"Azure OpenAI client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
                raise ValueError(f"Failed to initialize Azure OpenAI client: {str(e)}")
        
        return self.client
    
    async def call_llm(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 8192,
        temperature: float = 0.7,
        top_p: float = 0.95,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generic method to call Azure OpenAI LLM
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            dict: Response from Azure OpenAI
        """
        start_time = time.time()
        
        try:
            client = self._get_client()
            
            # Updated to use the correct model parameter (deployment name)
            response = client.chat.completions.create(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                model=self.deployment  # Use deployment name as model
            )
            
            generated_content = response.choices[0].message.content
            model_used = response.model
            processing_time = time.time() - start_time
            
            logging.info(f"Successfully called Azure OpenAI with model: {model_used}")
            
            # Track in Galileo if conversation_id is provided
            if conversation_id:
                galileo_service.track_conversation(
                    conversation_id=conversation_id,
                    messages=messages,
                    response=generated_content,
                    model_used=model_used,
                    metadata={
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "processing_time": processing_time
                    }
                )
            
            return {
                "status": "success",
                "message": "Successfully generated content",
                "model_used": model_used,
                "generated_content": generated_content,
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logging.error(f"Error calling Azure OpenAI: {str(e)}")
            return {
                "status": "error",
                "message": f"Exception occurred while calling Azure OpenAI: {str(e)}",
                "processing_time": processing_time
            }
    
    async def categorize_ticket(self, subject: str, description: str, ticket_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Categorize a ticket using Azure OpenAI
        
        Args:
            subject: Ticket subject
            description: Ticket description
            ticket_id: Optional ticket ID for tracking
            
        Returns:
            dict: Categorization result with category and confidence
        """
        start_time = time.time()
        
        candidate_labels = [
            "human_resources", "engineering", "it_support", "product", "design",
            "sales", "marketing", "finance", "legal", "customer_support", "operations", "executive"
        ]
        
        system_prompt = f"""You are a ticket categorization AI. Your task is to categorize Zendesk tickets into one of the following categories: {candidate_labels}

        Analyze the ticket subject and description, then respond with a JSON object containing:
        - category: the most appropriate category from the list above
        - confidence: a confidence score between 0 and 1
        - reasoning: brief explanation of why this category was chosen

        IMPORTANT: Return ONLY the raw JSON object. Do not wrap in markdown code blocks, do not add any formatting, just the pure JSON."""

        user_prompt = f"Subject: {subject}\nDescription: {description}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate conversation ID for tracking if ticket_id is provided
        conversation_id = f"categorization_{ticket_id}" if ticket_id else None
        
        response = await self.call_llm(messages, temperature=0.3, max_tokens=500, conversation_id=conversation_id)
        
        if response["status"] == "success":
            try:
                content = json.loads(response["generated_content"])
                processing_time = response.get("processing_time", 0)
                
                # Track categorization in Galileo
                if ticket_id:
                    galileo_service.track_ticket_categorization(
                        ticket_id=ticket_id,
                        subject=subject,
                        description=description,
                        category=content.get("category", ""),
                        confidence=content.get("confidence", 0.0),
                        model_used=response.get("model_used", "unknown"),
                        processing_time=processing_time
                    )
                
                return {
                    "status": "success",
                    "category": content.get("category", ""),
                    "confidence": content.get("confidence", 0.0),
                    "reasoning": content.get("reasoning", ""),
                    "model_used": response.get("model_used", "unknown"),
                    "processing_time": processing_time
                }
            except json.JSONDecodeError:
                logging.error(f"Failed to parse JSON response: {response['generated_content']}")
                return {
                    "status": "error",
                    "message": "Failed to parse categorization response"
                }
        else:
            return response
    
    async def analyze_ticket_comments(self, ticket_public_comments: List[Dict], ticket_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze ticket comments for support quality insights
        
        Args:
            ticket_public_comments: List of public comments from the ticket
            ticket_id: Optional ticket ID for tracking
            
        Returns:
            dict: Analysis result with insights and metrics
        """
        start_time = time.time()
        
        comments_json = json.dumps(ticket_public_comments, indent=2)
        
        system_prompt = """You are a support quality analyst AI. You will be given a list of Zendesk ticket comments, each with plain_body, created_at, and author_id.

        There are two participants: a Requester (customer) and a Support Engineer (agent). You must:
        1. Identify the role of each participant (Requester or Engineer) based on tone and context.
        2. Group and label messages by author.
        3. Analyze the customer experience and return a structured JSON response.

        Your output should include:
        - summary
        - sentiment (Positive, Neutral, Negative)
        - satisfaction_likelihood (High, Medium, Low)
        - pain_points
        - agent_empathy_score (1–5)
        - clarity_score (1–5)
        - resolution_confidence
        - frustration_signals
        - action_recommendations
        - message_content

        IMPORTANT: Return ONLY the raw JSON object. Do not wrap in markdown code blocks, do not add any formatting, just the pure JSON."""

        user_prompt = f"Here is the conversation data in json: {comments_json}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate conversation ID for tracking if ticket_id is provided
        conversation_id = f"analysis_{ticket_id}" if ticket_id else None
        
        response = await self.call_llm(messages, temperature=0.7, max_tokens=8192, conversation_id=conversation_id)
        
        if response["status"] == "success":
            processing_time = response.get("processing_time", 0)
            
            # Track analysis in Galileo
            if ticket_id:
                try:
                    content = json.loads(response["generated_content"])
                    galileo_service.track_comment_analysis(
                        ticket_id=ticket_id,
                        comments_count=len(ticket_public_comments),
                        analysis_result=content,
                        model_used=response.get("model_used", "unknown"),
                        processing_time=processing_time
                    )
                except json.JSONDecodeError:
                    logging.warning(f"Could not parse analysis result for Galileo tracking: {response['generated_content']}")
            
            return {
                "status": "success",
                "message": "Successfully generated insights from ticket comments",
                "model_used": response.get("model_used", "unknown"),
                "generated_content": response["generated_content"],
                "comments_analyzed": len(ticket_public_comments),
                "processing_time": processing_time
            }
        else:
            return response

# Create a singleton instance
azure_openai_service = AzureOpenAIService()

 