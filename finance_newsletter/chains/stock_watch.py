"""
Stock Watch Chain Module

This module provides a LangChain pipeline for generating the stock watch section
of the financial newsletter, focusing on user-defined tickers.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta, date
import json
import re

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.language_models import BaseLanguageModel


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockWatchChain:
    """Chain for generating stock watch analysis for user-defined tickers."""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.prompt = self._create_prompt()
        self.chain: Runnable = self.prompt | self.llm

    
    def _create_prompt(self) -> PromptTemplate:
        """
        Create the prompt template for stock watch analysis.
        
        Returns:
            PromptTemplate for stock watch
        """
        template = """
        You are a professional stock analyst, who is also a financial journalist. You also have great technical analysis skills.
        You are tasked with providing a detailed stock watch analysis for the following tickers as of {date}.
        USE the latest available data and news available online. DO NOT MAKE UP ANY DATA.
        
        Please analyze the following tickers: {tickers}.
        Please analyze ONLY the following tickers: {tickers}. MAke sure you cover all the tickers provided.
        DO NOT INCLUDE any other tickers or stocks in your analysis.
        
        For each ticker, provide an overall summary that includes the following:
        1. Company name and ticker symbol
        2. Current price and daily performance (percentage change)
        3. Recent news or developments affecting the stock
        4. Brief technical analysis (trend)
        5. Brief fundamental outlook. Sentiment analysis.

        If certain data points are missing, look for further resources.
        Format your response as a structured object that can be parsed into JSON. Do not include any introductory or concluding text.
        
        Example format:
        {{
            "stocks": [
                {{
                    "ticker": "AAPL",
                    "company": "Apple Inc.",
                    "overall_summary": "Forexample: Fundamental outlook: Bullish. Technical analysis: Uptrend. Recent news: Apple announces new product launch.",
                }},
                ...
            ]
        }}
        """
        return PromptTemplate(
            input_variables=["date", "tickers"],
            template=template
        )
    
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the stock watch chain.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict containing stock watch data
        """
        try:
            # Get date from config or use yesterday's date
            date_str = config.get("date", "auto")
            if date_str == "auto":
                yesterday = datetime.now() - timedelta(days=1)
                date_str = yesterday.strftime("%Y-%m-%d")
            
            # Get tickers from config
            tickers = ", ".join(config.get("tickers", ["AAPL", "MSFT", "AMZN", "GOOGL", "META"]))
            
            # Run the chain
            logger.info(f"Generating stock watch analysis for {date_str} on tickers: {tickers}")
            result = self.chain.invoke({    
                "date": date_str,
                "tickers": tickers
            })
            logger.info(f"LLM response: {result}")

            # Ensure the result is a string; if not, try to extract content
            if not isinstance(result, str):
                if hasattr(result, "content"):
                    result_str = result.content
                else:
                    result_str = str(result)
            else:
                result_str = result
            
            # Step 1: Remove <think>...</think> blocks
            result_str = re.sub(r"<think>.*?</think>", "", result_str, flags=re.DOTALL).strip()

            # Step 2: Extract first JSON object using regex
            match = re.search(r"(\{.*\})", result_str, re.DOTALL)
            if match:
                cleaned_response = match.group(1).strip()
            else:
                cleaned_response = result_str.strip()

            logger.info(f"Cleaned response: {cleaned_response}")

            try:
                # Now attempt to parse the extracted text as JSON
                stock_data = json.loads(cleaned_response)
                logger.info(f"Parsed news items: {stock_data}")

                return {
                    "section": "stock_watch",
                    "date": date_str,
                    "data": stock_data
                }
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON")
                return {
                    "section": "stock_watch",
                    "date": date_str,
                    "data": {},
                    "error": "Failed to parse response"
                }
                
        except Exception as e:
            logger.error(f"Error in stock watch chain: {e}")
            return {
                "section": "stock_watch",
                "error": str(e)
            }
