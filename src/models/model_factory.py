"""
🌙 Moon Dev's Model Factory
Built with love by Moon Dev 🚀

This module manages all available AI models and provides a unified interface.
"""

import os
from typing import Dict, Optional, Type
from termcolor import cprint
from dotenv import load_dotenv
from pathlib import Path
from .base_model import BaseModel
from .ollama_model import OllamaModel
import random
import time

class ModelFactory:
    """Factory for creating and managing AI models"""
    
    # Map model types to their implementations
    MODEL_IMPLEMENTATIONS = {
        "ollama": OllamaModel  # Using only Ollama for local model deployment
    }
    
    # Default models for each type
    DEFAULT_MODELS = {
        "ollama": "deepseek-r1:1.5b"  # DeepSeek R1 1.5B through Ollama
    }
    
    def __init__(self):
        cprint("\n🏗️ Creating new ModelFactory instance...", "cyan")
        
        # Load environment variables first
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / '.env'
        cprint(f"\n🔍 Loading environment from: {env_path}", "cyan")
        load_dotenv(dotenv_path=env_path)
        cprint("✨ Environment loaded", "green")
        
        self._models: Dict[str, BaseModel] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all available models"""
        initialized = False
        
        cprint("\n🏭 Moon Dev's Model Factory Initialization", "cyan")
        cprint("═" * 50, "cyan")
        
        # Initialize Ollama model
        try:
            model_class = self.MODEL_IMPLEMENTATIONS["ollama"]
            model_name = self.DEFAULT_MODELS["ollama"]
            if not model_name:
                raise ValueError("Model name cannot be empty")
            cprint(f"🔄 Initializing Ollama with model {model_name}...", "cyan")
            model_instance = model_class(api_key=None, model_name=model_name)
            if model_instance.is_available():
                self._models["ollama"] = model_instance
                initialized = True
                cprint(f"✨ Successfully initialized Ollama with model {model_name}", "green")
            else:
                cprint("⚠️ Ollama server not available - make sure 'ollama serve' is running", "yellow")
        except Exception as e:
            cprint(f"❌ Failed to initialize Ollama model: {str(e)}", "red")
            raise
        except Exception as e:
            cprint(f"❌ Failed to initialize Ollama: {str(e)}", "red")
        
        cprint("\n" + "═" * 50, "cyan")
        cprint(f"📊 Initialization Summary:", "cyan")
        cprint(f"  ├─ Models attempted: {len(self._get_api_key_mapping()) + 1}", "cyan")  # +1 for Ollama
        cprint(f"  ├─ Models initialized: {len(self._models)}", "cyan")
        cprint(f"  └─ Available models: {list(self._models.keys())}", "cyan")
        
        if not initialized:
            cprint("\n⚠️ No AI models available - check API keys and Ollama server", "yellow")
            cprint("Required environment variables:", "yellow")
            for model_type, key_name in self._get_api_key_mapping().items():
                cprint(f"  ├─ {key_name} (for {model_type})", "yellow")
            cprint("  └─ Add these to your .env file 🌙", "yellow")
            cprint("\nFor Ollama:", "yellow")
            cprint("  └─ Make sure 'ollama serve' is running", "yellow")
        else:
            # Print available models
            cprint("\n🤖 Available AI Models:", "cyan")
            for model_type, model in self._models.items():
                cprint(f"  ├─ {model_type}: {model.model_name}", "green")
            cprint("  └─ Moon Dev's Model Factory Ready! 🌙", "green")
    
    def get_model(self, model_type: str, model_name: Optional[str] = None) -> Optional[BaseModel]:
        """Get a specific model instance"""
        cprint(f"\n🔍 Requesting model: {model_type} ({model_name or 'default'})", "cyan")
        
        if model_type not in self.MODEL_IMPLEMENTATIONS:
            cprint(f"❌ Invalid model type: '{model_type}'", "red")
            cprint("Available types:", "yellow")
            for available_type in self.MODEL_IMPLEMENTATIONS.keys():
                cprint(f"  ├─ {available_type}", "yellow")
            return None
        
        try:
            if model_type == "ollama":
                model_name = model_name or self.DEFAULT_MODELS["ollama"]
                if not model_name:
                    raise ValueError("Model name cannot be empty")
                cprint(f"🔄 Initializing Ollama with model {model_name}...", "cyan")
                try:
                    model = self.MODEL_IMPLEMENTATIONS[model_type](
                        api_key=None,
                        model_name=model_name
                    )
                    if model and model.is_available():
                        self._models[model_type] = model
                        cprint(f"✨ Successfully initialized Ollama with model {model_name}", "green")
                        return model
                    else:
                        cprint(f"⚠️ Model {model_name} not available", "yellow")
                except Exception as e:
                    cprint(f"❌ Error initializing model: {str(e)}", "red")
                    return None
            else:
                if model_type not in self._models:
                    key_name = self._get_api_key_mapping().get(model_type)
                    if key_name:
                        cprint(f"❌ Model type '{model_type}' not available - check {key_name} in .env", "red")
                    else:
                        cprint(f"❌ Model type '{model_type}' not available", "red")
                    return None
                
                model = self._models[model_type]
                if model_name and model.model_name != model_name:
                    if api_key := os.getenv(self._get_api_key_mapping()[model_type]):
                        model = self.MODEL_IMPLEMENTATIONS[model_type](api_key, model_name=model_name)
                        self._models[model_type] = model
                        cprint(f"✨ Successfully reinitialized with new model", "green")
                    else:
                        cprint(f"❌ API key not found for {model_type}", "red")
                        return None
                
                return model
                
        except Exception as e:
            cprint(f"❌ Failed to initialize {model_type} with model {model_name}", "red")
            cprint(f"❌ Error type: {type(e).__name__}", "red")
            cprint(f"❌ Error: {str(e)}", "red")
            return None
            
        return model
    
    def _get_api_key_mapping(self) -> Dict[str, str]:
        """Get mapping of model types to their API key environment variable names"""
        return {}
    
    @property
    def available_models(self) -> Dict[str, list]:
        """Get all available models and their configurations"""
        models = {}
        for model_type, model in self._models.items():
            if hasattr(model, 'AVAILABLE_MODELS'):
                models[model_type] = model.AVAILABLE_MODELS
            else:
                models[model_type] = []
        return models
    
    def is_model_available(self, model_type: str) -> bool:
        """Check if a specific model type is available"""
        return model_type in self._models and self._models[model_type].is_available()

    def generate_response(self, system_prompt, user_content, temperature=0.7, max_tokens=None):
        """Generate a response using the selected model"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self._models:
                    self._initialize_models()
                
                model_name = self.DEFAULT_MODELS["ollama"]
                if not model_name:
                    raise ValueError("Model name cannot be empty")
                
                if "ollama" not in self._models:
                    model = self.get_model("ollama", model_name)
                    if not model:
                        raise ValueError(f"Could not initialize Ollama model {model_name}")
                    self._models["ollama"] = model
                
                if not self._models["ollama"]:
                    raise ValueError("Model not properly initialized")
                
                response = self._models["ollama"].generate_response(system_prompt, user_content, temperature)
                if response:
                    return response
                    
                raise ValueError("Model returned empty response")
                
            except Exception as e:
                cprint(f"❌ Model error (attempt {retry_count + 1}/{max_retries}): {str(e)}", "red")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(1)  # Wait before retrying
                    # Try to reinitialize the model
                    if "ollama" in self._models:
                        del self._models["ollama"]
                        self._models = {}  # Clear all models to force reinitialization
                
        return None

# Create a singleton instance
model_factory = ModelFactory()                                              