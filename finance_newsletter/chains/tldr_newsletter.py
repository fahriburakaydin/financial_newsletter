"""
TLDR Chain for generating summary of the total newsleter.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta, date
import json
import re

from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import Runnable



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TLDRChain:
    """Chain for generating TL;DR summaries of newsletters."""
    
    def __init__(self, llm: BaseLanguageModel):
        """
        Initialize the TLDR Chain.
        
        Args:
            llm: LangChain language model
        """
        self.llm = llm
        self.prompt = self._create_prompt()
        self.chain: Runnable = self.prompt | self.llm
    
    def _create_prompt(self) -> PromptTemplate:
        """
        Create the prompt template for tldr summary.
        
        Returns:
            PromptTemplate for tldr summary
        """
        template = """
        You are a financial journalist and an experienced editor, who is best at summarizing reports. Your task is to generate a tldr summary of the daily newsletter.
        Read the follwoing {newsletter} and provide a concise summary of the most important points.
        Make it easy to read and understand for a general audience.
        Use bullet points or numbered lists where appropriate.
        Focus on the key takeaways and insights from the newsletter.
        Please do not include any unnecessary details or jargon.
        Make it as informative and engaging as possible. Evoke curiosity and interest in the reader.


        """
        return PromptTemplate(
            input_variables=["newsletter"],
            template=template
        )
    
    def run(self, newsletter) -> Dict[str, Any]:
        """
        Run the tldr chain.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict containing tldr data
        """
        max_attempts = 3
        attempt = 0
        last_error = None
        
        inputs = {"newsletter": newsletter}
        
        while attempt < max_attempts:
            try:
                result = self.chain.invoke(inputs)
                logger.info(f"LLM response (attempt {attempt+1}): {result}")

                
                # Ensure we have a string to work with
                if not isinstance(result, str):
                    result_str = result.content if hasattr(result, "content") else str(result)
                else:
                    result_str = result

                json_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", result_str, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(1)
                else:
                    # Fallback: try to locate just the first top-level JSON array
                    array_match = re.search(r"(\[\s*{.*?}\s*\])", result_str, re.DOTALL)
                    cleaned_response = array_match.group(1) if array_match else result_str.strip()
                
                
                # Strip <think> block if present
                cleaned_response = re.sub(r"<think>.*?</think>", "", result_str, flags=re.DOTALL).strip()

                # Check if the cleaned response appears to be an error (e.g., it contains "401 Authorization Required")
                if "401 Authorization Required" in cleaned_response:
                    raise ValueError("Authorization error encountered in TLDR response.")

                logger.info(f"Cleaned response: {cleaned_response}")


                return {
                    "section": "tldr_summary",
                    "summary": cleaned_response
                }
            except Exception as e:
                logger.error(f"Error in TLDR summary chain: {e}")
                return {
                    "section": "tldr_summary",
                    "error": str(e)
                }
        return {
        "section": "tldr_summary",
        "summary": f"Error generating TLDR summary after {max_attempts} attempts: {last_error}"
    }


