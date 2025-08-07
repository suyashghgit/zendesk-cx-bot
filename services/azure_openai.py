import os
import json
import logging
from typing import Dict, List, Optional, Any
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AzureOpenAIService:
    """
    Generic Azure OpenAI service for various AI tasks
    """
    
    def __init__(self):
        # Updated configuration to match Azure OpenAI documentation
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://zendesk-resource.cognitiveservices.azure.com/")
        self.model_name = os.getenv("AZURE_OPENAI_MODEL", "model-router")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "model-router")
        self.subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.client = None
        
        # Validate configuration
        if not self.subscription_key:
            logging.warning("Azure OpenAI API key not found. Please set azure_openai_api_key environment variable.")
    
    def _get_client(self):
        """Lazy initialization of the Azure OpenAI client"""
        
        if self.client is None:
            try:
                # Updated client initialization to match documentation
                self.client = AzureOpenAI(
                    api_version=self.api_version,
                    azure_endpoint=self.endpoint,
                    api_key=self.subscription_key,
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
        presence_penalty: float = 0.0
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
            
        Returns:
            dict: Response from Azure OpenAI
        """
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
            
            logging.info(f"Successfully called Azure OpenAI with model: {model_used}")
            
            return {
                "status": "success",
                "message": "Successfully generated content",
                "model_used": model_used,
                "generated_content": generated_content
            }
            
        except Exception as e:
            logging.error(f"Error calling Azure OpenAI: {str(e)}")
            return {
                "status": "error",
                "message": f"Exception occurred while calling Azure OpenAI: {str(e)}"
            }
    
    async def categorize_ticket(self, subject: str, description: str) -> Dict[str, Any]:
        """
        Categorize a ticket using Azure OpenAI
        
        Args:
            subject: Ticket subject
            description: Ticket description
            
        Returns:
            dict: Categorization result with category and confidence
        """
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
        
        response = await self.call_llm(messages, temperature=0.3, max_tokens=500)
        
        if response["status"] == "success":
            try:
                content = json.loads(response["generated_content"])
                return {
                    "status": "success",
                    "category": content.get("category", ""),
                    "confidence": content.get("confidence", 0.0),
                    "reasoning": content.get("reasoning", ""),
                    "model_used": response.get("model_used", "unknown")
                }
            except json.JSONDecodeError:
                logging.error(f"Failed to parse JSON response: {response['generated_content']}")
                return {
                    "status": "error",
                    "message": "Failed to parse categorization response"
                }
        else:
            return response
    
    async def analyze_ticket_comments(self, ticket_public_comments: List[Dict]) -> Dict[str, Any]:
        """
        Analyze ticket comments for support quality insights
        
        Args:
            ticket_public_comments: List of public comments from the ticket
            
        Returns:
            dict: Analysis result with insights and metrics
        """
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
        
        response = await self.call_llm(messages, temperature=0.7, max_tokens=8192)
        
        if response["status"] == "success":
            return {
                "status": "success",
                "message": "Successfully generated insights from ticket comments",
                "model_used": response.get("model_used", "unknown"),
                "generated_content": response["generated_content"],
                "comments_analyzed": len(ticket_public_comments)
            }
        else:
            return response

# Create a singleton instance
azure_openai_service = AzureOpenAIService()

 