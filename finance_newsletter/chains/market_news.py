"""
Market News Chain Module

This module provides a LangChain pipeline for generating the market news section
of the financial newsletter.
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

class MarketNewsChain:
    """Chain for generating market-moving news summaries."""
    
    def __init__(self, llm: BaseLanguageModel):
        """
        Initialize the Market News Chain.
        
        Args:
            llm: LangChain language model
        """
        self.llm = llm
        self.prompt = self._create_prompt()
        self.chain: Runnable = self.prompt | self.llm
    
    def _create_prompt(self) -> PromptTemplate:
        """
        Create the prompt template for market news.
        
        Returns:
            PromptTemplate for market news
        """
        template = """
        You are a professional financial analyst tasked with summarizing the most important market-moving news from {{date}} till now.
        
        Focus on news related to the {{region}} market and include global events that had significant market impact.
        
        Please provide the top 3-5 market-moving news stories from {{date}} with the following information for each:
        1. Headline
        2. Brief summary (2-3 sentences)
        3. Market impact (how markets reacted to this news)
        4. Source
        
        Return only a JSON array of news items, like this:
        
        Example format:
        [
            {{
                "headline": "Fed Raises Interest Rates by 25 Basis Points",
                "summary": "The Federal Reserve raised its benchmark interest rate by 25 basis points to a range of 5.25% to 5.50%. This marks the 11th rate hike in the current tightening cycle.",
                "impact": "Markets initially dipped on the news but recovered by close as Powell's comments suggested a potential pause in rate hikes.",
                "source": "Federal Reserve Press Release"
            }},
            ...
        ]
        """
        return PromptTemplate(
            input_variables=["date", "region"],
            template=template
        )
    
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the market news chain.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict containing market news data
        """
        try:
            # Get date from config or use yesterday's date
            date_str = config.get("date", "auto")
            if date_str == "auto":
                yesterday = datetime.now() - timedelta(days=1)
                date_str = yesterday.strftime("%Y-%m-%d")
            
            # Get region from config
            region = config.get("region", "US")
            
            # Run the chain
            logger.info(f"Generating market news for {date_str} in {region}")

            inputs = {"date": date_str, "region": region}
            result = self.chain.invoke(inputs)   
            logger.info(f"LLM response: {result}")        
    
             # Ensure the result is a string; if not, try to extract content
            if not isinstance(result, str):
                if hasattr(result, "content"):
                    result_str = result.content
                else:
                    result_str = str(result)
            else:
                result_str = result

            json_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", result_str, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(1)
            else:
                # Fallback: try to locate just the first top-level JSON array
                array_match = re.search(r"(\[\s*{.*?}\s*\])", result_str, re.DOTALL)
                cleaned_response = array_match.group(1) if array_match else result_str.strip()
            logger.info(f"Cleaned response: {cleaned_response}")
            

            try:
                # Now attempt to parse the extracted text as JSON
                parsed = json.loads(cleaned_response)
                logger.debug(f"Parsed news items: {parsed}")
                            
                
                return {
                    "section": "market_news",
                    "date": date_str,
                    "region": region,
                    "news_items": parsed
                }
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON")
                return {
                    "section": "market_news",
                    "date": date_str,
                    "region": region,
                    "news_items": [],
                    "error": "Failed to parse response"
                }
                
        except Exception as e:
            logger.error(f"Error in market news chain: {e}")
            return {
                "section": "market_news",
                "error": str(e)
            }