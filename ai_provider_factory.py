from ollama_connection import connect_to_ollama

class AIProviderFactory:
    @staticmethod
    def get_provider(provider_type, url, model, api_key=None):
        if provider_type == 'ollama':
            return OllamaProvider(url, model)
        # Add more providers here as needed
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

class AIProvider:
    def get_response(self, prompt):
        raise NotImplementedError

class OllamaProvider(AIProvider):
    def __init__(self, url, model):
        self.url = url
        self.model = model

    def get_response(self, prompt):
        response_data = connect_to_ollama(self.url, self.model, prompt)
        if response_data:
            return response_data.get('response', '')
        return None
