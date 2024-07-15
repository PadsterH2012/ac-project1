import requests

def connect_to_ollama(url, model, prompt):
    try:
        response = requests.post(
            url,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        return None
