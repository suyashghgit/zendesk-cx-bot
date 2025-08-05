# services/azure_openai.py

import os
import json
import logging
from openai import AzureOpenAI

async def call_azure_llm_with_comments(ticket_public_comments: list) -> dict:
    """
    Call Azure OpenAI LLM with ticket public comments to generate insights or summaries.
    
    Args:
        ticket_public_comments (list): List of public comments from the ticket
    
    Returns:
        dict: Response from Azure OpenAI with generated content
    """
    try:
        # Azure OpenAI configuration
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://zendesk-resource.cognitiveservices.azure.com/")
        model_name = os.getenv("AZURE_OPENAI_MODEL", "model-router")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "model-router")
        subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        if not subscription_key:
            return {
                "status": "error",
                "message": "Missing Azure OpenAI API key. Please set AZURE_OPENAI_API_KEY environment variable."
            }
        
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=subscription_key,
        )
        
        # Prepare the comments as JSON for the LLM
        comments_json = json.dumps(ticket_public_comments, indent=2)
        
        # Create the system and user messages with the specific support quality analysis prompt
        messages = [
            {
                "role": "system",
                "content": "You are a support quality analyst AI. You will be given a list of Zendesk ticket comments, each with plain_body, created_at, and author_id.\n\nThere are two participants: a Requester (customer) and a Support Engineer (agent). You must:\n1. Identify the role of each participant (Requester or Engineer) based on tone and context.\n2. Group and label messages by author.\n3. Analyze the customer experience and return a structured JSON response.\n\nYour output should include:\n- summary\n- sentiment (Positive, Neutral, Negative)\n- satisfaction_likelihood (High, Medium, Low)\n- pain_points\n- agent_empathy_score (1–5)\n- clarity_score (1–5)\n- resolution_confidence\n- frustration_signals\n - action_recommendations\n - message content"
            },
            {
                "role": "user",
                "content": f"Here is the conversation data in json {comments_json}"
            }
        ]
        
        # Call Azure OpenAI
        response = client.chat.completions.create(
            messages=messages,
            max_tokens=8192,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            model=deployment
        )
        
        # Extract the response content
        generated_content = response.choices[0].message.content
        model_used = response.model
        
        logging.info(f"Successfully called Azure OpenAI with model: {model_used}")
        
        return {
            "status": "success",
            "message": "Successfully generated insights from ticket comments",
            "model_used": model_used,
            "generated_content": generated_content,
            "comments_analyzed": len(ticket_public_comments)
        }
        
    except Exception as e:
        logging.error(f"Error calling Azure OpenAI: {str(e)}")
        return {
            "status": "error",
            "message": f"Exception occurred while calling Azure OpenAI: {str(e)}"
        } 