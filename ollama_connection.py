import requests

def connect_to_ollama(url, model, prompt):
    try:
        print(f"Sending request to Ollama. URL: {url}, Model: {model}")
        print(f"Prompt (truncated): {prompt[:100]}...")
        response = requests.post(
            url,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
        json_response = response.json()
        print(f"JSON response (truncated): {str(json_response)[:200]}...")
        return json_response
    except requests.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        print(f"Response content: {response.content if 'response' in locals() else 'No response'}")
        return None
