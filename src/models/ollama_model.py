"""
Ollama Model Integration
Handles interaction with local Ollama API
"""

import os
import json
import requests
from .base_model import BaseModel, ModelResponse

class OllamaModel(BaseModel):
    def __init__(self, model_name="deepseek-r1:1.5b"):
        super().__init__()
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"
        self.headers = {"Content-Type": "application/json"}
        
    def initialize(self):
        """Initialize connection to Ollama API"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            response.raise_for_status()
            models = [model['name'] for model in response.json()['models']]
            print("✨ Successfully connected to Ollama API")
            print(f"📚 Available Ollama models: {models}")
            return True
        except Exception as e:
            print(f"Error connecting to Ollama API: {e}")
            return False
            
    def generate_response(self, system_prompt, user_content, temperature=0.7):
        """Generate response from Ollama model"""
        try:
            data = {
                "model": self.model_name,
                "prompt": f"{system_prompt}\n\n{user_content}",
                "temperature": temperature
            }
            
            response = requests.post(self.api_url, json=data, headers=self.headers)
            response.raise_for_status()
            
            return ModelResponse(
                content=response.json().get('response', ''),
                raw_response=response.json()
            )
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
