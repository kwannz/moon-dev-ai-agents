"""
Base Model
Abstract base class for AI model implementations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ModelResponse:
    content: str
    raw_response: dict

class BaseModel(ABC):
    @property
    @abstractmethod
    def AVAILABLE_MODELS(self):
        """List of available models for this provider"""
        pass
        
    @abstractmethod
    def initialize_client(self):
        """Initialize the model client"""
        pass
        
    @abstractmethod
    def is_available(self):
        """Check if model is available"""
        pass
        
    @property
    @abstractmethod
    def model_type(self):
        """Get model type"""
        pass
        
    @abstractmethod
    def generate_response(self, system_prompt, user_content, temperature=0.7):
        """Generate response from model"""
        pass
