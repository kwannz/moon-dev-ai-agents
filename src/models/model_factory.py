"""
Model Factory
Manages AI model initialization and configuration
"""

import os
import sys
import time
from pathlib import Path
from termcolor import cprint
from .ollama_model import OllamaModel

class ModelFactory:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelFactory, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
        
    def __init__(self):
        if self.initialized:
            return
            
        self.models = {}
        self.initialized_models = []
        self.available_models = []
        
        # Load environment
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            print("Environment loaded")
        
        # Initialize Ollama model
        try:
            ollama = OllamaModel()
            if ollama.initialize_client():
                self.models['ollama'] = ollama
                self.initialized_models.append('ollama')
                self.available_models.append('ollama')
        except Exception as e:
            print(f"Error initializing Ollama: {e}")
        
        print("Model Factory Ready!")
        self.initialized = True

    def get_model(self, model_type='ollama'):
        """Get an initialized model instance"""
        if model_type not in self.models:
            print(f"Error: Model {model_type} not available")
            return None
        return self.models[model_type]    