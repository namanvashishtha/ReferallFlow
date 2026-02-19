import httpx
import json
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Any, Dict, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("hf_mcp_client")


class MCPClientError(Exception):
    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type((httpx.RequestError, MCPClientError)))
async def extract_entities_from_text(text: str, timeout: int = 60) -> Dict[str, Any]:
    """Send text to Hugging Face Inference API and return parsed JSON entities.
    
    Uses an LLM (Mistral/Llama) to extract structured data from resume text.
    """
    if not settings.HF_MCP_TOKEN:
        logger.error("HF_MCP_TOKEN is not configured")
        raise MCPClientError("Hugging Face API token not configured")

    model_url = settings.HF_MCP_URL
    headers = {"Authorization": f"Bearer {settings.HF_MCP_TOKEN}"}
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant that extracts structured data from resume text. Always return ONLY valid JSON."},
        {"role": "user", "content": f"Extract the following information from this resume text and return it ONLY as a valid JSON object:\n- candidate_name\n- top_skills (list of strings)\n- years_of_experience (as a number or string)\n- positions (list of job titles the candidate is qualified for)\n\nResume Text:\n{text[:3000]}"}
    ]

    payload = {
        "model": settings.HF_MODEL_ID,
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.1
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(model_url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.error("HF API error", status=resp.status_code, response=resp.text)
            resp.raise_for_status()
            
            result = resp.json()
            # New format for chat/completions
            generated_text = result['choices'][0]['message']['content']
            
            # Use regex to find the JSON block in case the model added chatter
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
                logger.info("Successfully extracted entities from HF")
                return extracted_data
            else:
                logger.error("Could not find JSON in model response", response=generated_text)
                raise MCPClientError("Invalid response format from model")

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        response_text = e.response.text
        logger.error("HF API returned bad status", status=status_code, text=response_text)
        
        if status_code == 503:
            raise MCPClientError("HF Model is currently loading, please try again in a few seconds")
        elif status_code == 401:
            raise MCPClientError("HF API token is invalid or expired")
        elif status_code == 429:
            raise MCPClientError("HF API rate limit exceeded")
        
        raise MCPClientError(f"HF API error: {status_code}")
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON from model output")
        raise MCPClientError("JSON parsing error")
    except Exception as e:
        logger.exception("Error communicating with Hugging Face API")
        raise
