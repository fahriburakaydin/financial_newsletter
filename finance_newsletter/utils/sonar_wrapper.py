"""
Sonar Wrapper Module

This module provides a wrapper for the Perplexity Sonar LLM and OpenAI GPT models
using LangChain, with fallback functionality.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_perplexity import ChatPerplexity
from langchain_core.language_models import BaseLanguageModel
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMProvider:
    """A wrapper class for LLM providers with fallback functionality."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.llm_config = self.config.get("llm", {})
        self.primary_provider = self.llm_config.get("provider", "sonar")
        self.fallback_provider = self.llm_config.get("fallback", "openai")
        self.primary_llm = None
        self.fallback_llm = None
        self._initialize_llms()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _initialize_llms(self) -> None:
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

        # Init primary
        if self.primary_provider == "sonar":
            self.primary_llm = self._init_perplexity(callback_manager)
        elif self.primary_provider == "openai":
            self.primary_llm = self._init_openai(callback_manager)
        
        # Init fallback
        if self.fallback_provider != self.primary_provider:
            if self.fallback_provider == "sonar":
                self.fallback_llm = self._init_perplexity(callback_manager)
            elif self.fallback_provider == "openai":
                self.fallback_llm = self._init_openai(callback_manager)
    
    def _init_perplexity(self, callback_manager) -> Optional[BaseLanguageModel]:
        try:
            api_key = os.getenv("PERPLEXITY_API_KEY")
            if not api_key:
                logger.warning("PERPLEXITY_API_KEY not found in environment variables")
            model = self.llm_config.get("model", "sonar-medium-online")

            logger.info(f"Initializing Perplexity Sonar: {model}")
            return ChatPerplexity(model=model, api_key=api_key, callback_manager=callback_manager)
        except Exception as e:
            logger.error(f"Failed to initialize Perplexity: {e}")
            return None
    
    def _init_openai(self, callback_manager) -> Optional[BaseLanguageModel]:
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not found in environment variables")
            model = self.llm_config.get("openai_model", "gpt-3.5-turbo")

            logger.info(f"Initializing OpenAI model: {model}")
            return ChatOpenAI(model_name=model, temperature=0.1, api_key=api_key, callback_manager=callback_manager)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            return None

    def get_llm(self) -> Optional[BaseLanguageModel]:
        if self.primary_llm:
            logger.info(f"Using primary LLM: {self.primary_provider}")
            return self.primary_llm
        elif self.fallback_llm:
            logger.warning("Using fallback LLM as primary is unavailable")
            return self.fallback_llm
        else:
            logger.error("No available LLM (primary or fallback)")
            return None

    def get_config(self) -> Dict[str, Any]:
        return self.config
