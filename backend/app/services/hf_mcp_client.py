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

    model_url = f"{settings.HF_MCP_URL.rstrip('/')}/{settings.HF_MODEL_ID}"
    headers = {"Authorization": f"Bearer {settings.HF_MCP_TOKEN}"}
    
    prompt = f"""<s>[INST] Extract the following information from this resume text and return it ONLY as a valid JSON object:
- candidate_name
- top_skills (list of strings)
- years_of_experience (as a number or string)
- positions (list of job titles the candidate is qualified for)

Resume Text:
{text[:3000]} [/INST]</s>"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "return_full_text": False
        },
        "options": {
            "wait_for_model": True
        }
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(model_url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.error("HF API error", status=resp.status_code, response=resp.text)
            resp.raise_for_status()
            
            # The API usually returns a list with the generated text
            result = resp.json()
            generated_text = result[0]['generated_text'] if isinstance(result, list) else result.get('generated_text', '')
            
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
