"""
Upcoming Events Chain Module

This module provides a LangChain pipeline for generating the upcoming economic events
section of the financial newsletter.
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

class UpcomingEventsChain:
    """Chain for generating upcoming economic events calendar."""
    
    def __init__(self, llm: BaseLanguageModel):
        """
        Initialize the Upcoming Events Chain.
        
        Args:
            llm: LangChain language model
        """
        self.llm = llm
        self.prompt = self._create_prompt()
        self.chain: Runnable = self.prompt | self.llm
    
    def _create_prompt(self) -> PromptTemplate:
        """
        Create the prompt template for upcoming events.
        
        Returns:
            PromptTemplate for upcoming events
        """
        template = """
        You are a professional financial analyst tasked with providing a calendar of upcoming economic events for the next week starting from {{date}} until the end of week.
        Use the latest available data and news available online. DO NOT MAKE UP ANY DATA.
        
        Focus on the following regions: {{macro_focus}}
        
        Please provide:
        1. Key economic data releases (e.g., GDP, CPI, employment reports)
        2. Central bank meetings and announcements
        3. Treasury auctions
        4. Important earnings releases for major companies
        5. Other significant events that could impact markets
        
        Organize events by date for the next 7 days.
        
        Format your response as a structured object that can be parsed into JSON. Do not include any introductory or concluding text.
        
        Example format:
        {{
            "calendar": [
                {{
                    "date": "2023-10-16",
                    "day": "Monday",
                    "events": [
                        {{
                            "time": "08:30 ET",
                            "region": "US",
                            "event": "Empire State Manufacturing Index",
                            "previous": "-2.1",
                            "forecast": "0.0",
                            "importance": "Medium"
                        }},
                        {{
                            "time": "All Day",
                            "region": "US",
                            "event": "Bank of America Q3 Earnings",
                            "previous": "EPS $0.88",
                            "forecast": "EPS $0.82",
                            "importance": "High"
                        }}
                    ]
                }},
                ...
            ],
            "highlights": [
                "Fed Chair Powell speech on Wednesday",
                "US CPI data on Thursday",
                "Multiple Fed officials speaking throughout the week"
            ]
        }}
        """
        return PromptTemplate(
            input_variables=["date", "macro_focus"],
            template=template
        )
    
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the upcoming events chain.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict containing upcoming events data
        """
        try:
            # Get date from config or use yesterday's date
            date_str = config.get("date", "auto")
            if date_str == "auto":
                today = datetime.now()
                date_str = today.strftime("%Y-%m-%d")
            
            # Get macro focus regions from config
            macro_focus = ", ".join(config.get("macro_focus", ["US", "EU", "China"]))
            
            # Run the chain
            logger.info(f"Generating upcoming events calendar starting from {date_str} for regions: {macro_focus}")
            result = self.chain.invoke( 
                {"date": date_str},
                {"macro_focus": macro_focus}
            )
            
            logger.info(f"LLM response: {result}")
            
            # Ensure we have a string to parse: if not a string, extract content or cast to string
            if not isinstance(result, str):
                if hasattr(result, "content"):
                    result_str = result.content
                else:
                    result_str = str(result)
            else:
                result_str = result

            
           # Step 1: Remove <think>...</think> blocks
            result_str = re.sub(r"<think>.*?</think>", "", result_str, flags=re.DOTALL).strip()

            # Step 2: Try to extract a top-level JSON object
            match = re.search(r"(\{.*\})", result_str, re.DOTALL)
            if match:
                cleaned_response = match.group(1).strip()
            else:
                cleaned_response = result_str.strip()

            logger.debug(f"Cleaned response: {cleaned_response}")
            try:
                # Now attempt to parse the extracted text as JSON
                events_data = json.loads(cleaned_response)
                logger.debug(f"Parsed news items: {events_data}")
                return {
                    "section": "upcoming_events",
                    "date": date_str,
                    "data": events_data
                }
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON")
                return {
                    "section": "upcoming_events",
                    "date": date_str,
                    "data": {},
                    "error": "Failed to parse response"
                }
                
        except Exception as e:
            logger.error(f"Error in upcoming events chain: {e}")
            return {
                "section": "upcoming_events",
                "error": str(e)
            }
