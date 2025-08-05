# app/services/huggingface.py

import os, logging, requests
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

async def send_to_huggingface(rendered_template: str) -> dict:
    try:
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }

        candidate_labels = [
            "human_resources", "engineering", "it_support", "product", "design",
            "sales", "marketing", "finance", "legal", "customer_support", "operations", "executive"
        ]

        payload = {
            "inputs": rendered_template,
            "parameters": {
                "candidate_labels": candidate_labels
            }
        }

        response = requests.post(
            HUGGINGFACE_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "status": "success",
                "category": result.get("labels", [""])[0],
                "confidence": result.get("scores", [])[0],
                "model_used": "facebook/bart-large-mnli"
            }
        else:
            logging.error(f"HF API error: {response.status_code} - {response.text}")
            return {"status": "error", "error": response.text}

    except Exception as e:
        logging.error(f"HF API error: {str(e)}")
        return {"status": "error", "error": str(e)}
