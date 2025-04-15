"""
Market Reaction Chain Module

This module provides a LangChain pipeline for generating the market reaction section
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

class MarketReactionChain:
    """Chain for generating market reaction summaries."""
    
    def __init__(self, llm: BaseLanguageModel):
        """
        Initialize the Market Reaction Chain.
        
        Args:
            llm: LangChain language model
        """
        self.llm = llm
        self.prompt = self._create_prompt()
        self.chain: Runnable = self.prompt | self.llm
        
    def _create_prompt(self) -> PromptTemplate:
        """
        Create the prompt template for market reaction.
        
        Returns:
            PromptTemplate for market reaction
        """
        template = """
        You are an expeirence professional financial analyst, who is specielized in stock-market analysis, financial journalism, commodities and crypto-markets.
        tasked with summarizing market reactions from previous active market day until the current time.
        Use the latest available data and news available online. MAKE SURE YOU SHARE CORRECT and RELIABLE DATA, DO NOT MAKE UP ANY DATA.
        
        Do your and extended research and provide a detailed summary of how the following categories performed on from {date} until current time:
        DO NOT USE ANY RESOURCES THAT ARE OLDER THAN {date}.

        - Indices: Including {indices}
        - Commodities: including {commodities}
        - Cryptocurrencies: including {crypto}
        
        For each category, include:
        1. Performance summary (up/down percentage last active market day)
        2. Latest value of the market (Make sure this is correct and up to date)
        3.Latest price of the market (Make sure this is correct and up to date)
        4. Key drivers of performance
        5. Notable outliers or exceptions
        6. Comparison to recent trends
        7.Sentiment Analysis

        
        If the market was closed then it is fine to say that market was closed an no updates are available. Just mention if there is any sentiment to share in that case.
        ENSURE that you spend enough time for each categoty to provide a detailed summary for each.
        If certain data points are missing, look for further resources to adress everything.
        Format your response as a structured object that can be parsed into JSON. Do not include any introductory or concluding text.
        
        Example format:
        {{
            "indices": [
                {{
                    "name": "xxx",
                    "ticker": "xxx",
                    "performance": "+x.x%",
                    "value": "xxx",
                    "summary": "xxxxx"
                }},
                ...
            ],
            "commodities": [
                {{
                    "name": "xxx",
                    "ticker": "xxx",
                    "performance": "-x.x%",
                    "value": "1,876.50",
                    "summary": "xxx"
                }},
                ...
            ],
            "crypto": [
                {{
                    "name": "xxx",
                    "ticker": "xxx",
                    "performance": "+x.x%",
                    "value": "xxx",
                    "summary": "xxxxxx"
                }},
                ...
            ],
            "overall_summary": " A concise commentative summary over eveyrthing."
        }}
        """
        return PromptTemplate(
            input_variables=["date", "indices", "commodities", "crypto"],
            template=template
        )
    
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the market reaction chain.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict containing market reaction data
        """
        try:
            # Get date from config or use yesterday's date
            date_str = config.get("date", "auto")
            if date_str == "auto":
                yesterday = datetime.now() - timedelta(days=1)
                date_str = yesterday.strftime("%Y-%m-%d")
            
            # Get market components from config
            indices = ", ".join(config.get("indices", ["^GSPC", "^DJI", "^IXIC"]))
            commodities = ", ".join(config.get("commodities", ["GC=F", "CL=F"]))
            crypto = ", ".join(config.get("crypto", ["BTC-USD", "ETH-USD"]))
            
            # Run the chain
            logger.info(f"Generating market reaction for {date_str}")
            logger.debug(f"Indices: {indices}, /nCommodities: {commodities}, /nCrypto: {crypto}")
            result = self.chain.invoke({
                "date": date_str,
                "indices": indices,
                "commodities": commodities,
                "crypto": crypto
                })
            
            logger.info("Market reaction generation completed.")
            logger.info(f"Result from LLM: {result}")
            
            if not isinstance(result, str):
                if hasattr(result, "content"):
                    result_str = result.content
                else:
                    result_str = str(result)
            else:
                result_str = result
            
            # Step 1: Skip everything before the first JSON block (which may come after </think>)
            json_start = result_str.find('{')
            if json_start == -1:
                logger.error("No JSON object start found in LLM output")
                return {
                    "section": "market_reaction",
                    "date": date_str,
                    "error": "No JSON object found"
                }

            # Step 2: Try to load the JSON from the first `{` onward
            cleaned_response = result_str[json_start:].strip()

            # Remove citation footnotes like [1][5][10] from inside strings
            cleaned_response = re.sub(r'\s*\[\d+(?:\]\[\d+)*\]', '', cleaned_response)

            logger.info(f"Cleaned response: {cleaned_response}")

            try:
                # Now attempt to parse the extracted text as JSON
                parsed = json.loads(cleaned_response)
                logger.debug(f"Parsed news items: {parsed}")
                return {
                    "section": "market_reaction",
                    "date": date_str,
                    "data": parsed
                }
            except json.JSONDecodeError as e:
                # Sometimes there's trailing text or citation metadata that breaks JSON
                match = re.search(r"(\{.*?\})\s*(?=\n?[a-zA-Z0-9_-]+:|\Z)", cleaned_response, re.DOTALL)
                if match:
                    try:
                        parsed = json.loads(match.group(1))
                    except Exception as e2:
                        logger.error(f"Still failed to parse cleaned JSON: {e2}")
                return {
                    "section": "market_reaction",
                    "date": date_str,
                    "data": {},
                    "error": "Failed to parse response"
                }
                
        except Exception as e:
            logger.error(f"Error in market reaction chain: {e}")
            return {
                "section": "market_reaction",
                "error": str(e)
            }
