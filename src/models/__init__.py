"""
Model System
Manages AI model initialization and configuration
"""

from .base_model import BaseModel, ModelResponse
from .ollama_model import OllamaModel
from .model_factory import ModelFactory

__all__ = [
    'BaseModel',
    'ModelResponse',
    'OllamaModel',
    'ModelFactory'
]
