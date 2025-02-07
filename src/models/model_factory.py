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
    def __init__(self):
        self.models = {}
        self.initialized_models = []
        self.available_models = []
        
        print("\nCreating new ModelFactory instance...")
        
        # Load environment
        env_file = Path(__file__).parent.parent / ".env"
        print(f"\nLoading environment from: {env_file}")
        if env_file.exists():
            print("Environment loaded")
        
        print("\nModel Factory Initialization")
        print("═" * 50)
        
        # Initialize Ollama model
        try:
            ollama = OllamaModel()
            if ollama.initialize():
                self.models['ollama'] = ollama
                self.initialized_models.append('ollama')
                self.available_models.append('ollama')
        except Exception as e:
            print(f"Error initializing Ollama: {e}")
        
        print("\n" + "═" * 50)
        print("Initialization Summary:")
        print(f"  ├─ Models attempted: {len(self.models)}")
        print(f"  ├─ Models initialized: {len(self.initialized_models)}")
        print(f"  └─ Available models: {self.available_models}")
        
        print("\nAvailable AI Models:")
        for model_name in self.available_models:
            print(f"  ├─ {model_name}: {self.models[model_name].model_name}")
        print("  └─ Model Factory Ready!")

    def get_model(self, model_type='ollama'):
        """Get an initialized model instance"""
        if model_type not in self.models:
            print(f"Error: Model {model_type} not available")
            return None
        return self.models[model_type]
