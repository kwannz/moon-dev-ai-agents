"""
🌙 Moon Dev's Model Interface
Built with love by Moon Dev 🚀

This module defines the base interface for all AI models.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import random
import time
from termcolor import cprint

@dataclass
class ModelResponse:
    """Standardized response format for all models"""
    content: str
    raw_response: Any  # Original response object
    model_name: str
    usage: Optional[Dict] = None
    
class BaseModel(ABC):
    """Base interface for all AI models"""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.client = None
        self.initialize_client(**kwargs)
    
    @abstractmethod
    def initialize_client(self, **kwargs) -> None:
        """Initialize the model's client"""
        pass
    
    @abstractmethod
    def generate_response(self, system_prompt, user_content, temperature=0.7, max_tokens=None):
        """Generate a response from the model"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available and properly configured"""
        pass
    
    @property
    @abstractmethod
    def model_type(self) -> str:
        """Return the type/name of the model"""
        pass  