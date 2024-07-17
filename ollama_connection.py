import requests
import logging

logger = logging.getLogger(__name__)

class OllamaConnectionError(Exception):
    pass

def connect_to_ollama(url, model, prompt):
    try:
        logger.info(f"Sending request to Ollama. URL: {url}, Model: {model}")
        logger.debug(f"Prompt (truncated): {prompt[:100]}...")
        response = requests.post(
            url,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=30  # Add a timeout
        )
        response.raise_for_status()
        json_response = response.json()
        logger.debug(f"JSON response (truncated): {str(json_response)[:200]}...")
        return json_response
    except requests.RequestException as e:
        logger.error(f"Error connecting to Ollama: {e}")
        if 'response' in locals():
            logger.error(f"Response content: {response.content}")
        raise OllamaConnectionError(f"Failed to connect to Ollama: {str(e)}")
