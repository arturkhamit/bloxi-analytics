import requests

class OllamaClient:
    def __init__(self, model="llama3.1", host="http://localhost:11434"):
        self.model = model
        self.url = f"{host}/api/generate"


    def generate(self, prompt: str, system: str = "", temperature: float = 0.2, num_ctx: int = 8192) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "options": {
                "temperature": temperature,
                "num_ctx": num_ctx
            },
            "stream": False
        }
        resp = requests.post(self.url, json=payload, timeout=6000)
        resp.raise_for_status()
        return resp.json()["response"]
