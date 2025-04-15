"""
Macro Landscape Chain Module

This module provides a LangChain pipeline for generating the macro-economic landscape
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

class MacroLandscapeChain:
    """Chain for generating macro-economic landscape analysis."""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.prompt = self._create_prompt()
        self.chain: Runnable = self.prompt | self.llm

    def _create_prompt(self) -> PromptTemplate:
        """
        Create the prompt template for macro landscape analysis.
        
        Returns:
            PromptTemplate for macro landscape
        """
        # Use single braces (not double) for variable substitution.
        template = """
        You are a professional macro-economic analyst tasked with providing an overview of the current macro-economic landscape as of {date}.
        
        Use the latest available data and news available online. DO NOT MAKE UP ANY DATA.
        Focus on the most recent macroeconomic data available online for the following regions: {macro_focus}
        DO NOT INCLUDE ANY OTHER REGIONS OR COUNTRIES.

        For each region, please provide:
        1. Current economic conditions (growth, inflation, employment)
        2. Central bank policies and recent decisions
        3. Key economic indicators released recently
        4. Major economic risks or opportunities
        
        Also include a brief global outlook section that ties these regions together.

        Only include the most relevant and impactful information. DO NOT MAKE UP ANY DATA.
        USE THE MOST RECENT AND REAL DATA ONLY. 
        Only include data for the following regions exactly as provided: {macro_focus}. Do not include any data for any other regions.

        Format your response as a structured object that can be parsed into JSON. Do not include any introductory or concluding text.
        
        Example format:
        {{
            "regions": [
                {{
                    "name": "US",
                    "economic_conditions": {{
                        "growth": "GDP grew at 2.1% annualized rate in Q2 2023",
                        "inflation": "CPI at 3.1% year-over-year, down from 3.3% previous month",
                        "employment": "Unemployment rate at 3.8%, with 175,000 jobs added last month"
                    }},
                    "central_bank": {{
                        "current_rate": "5.25-5.50%",
                        "recent_decision": "Held rates steady at September meeting",
                        "outlook": "Signaling potential rate cut in December if inflation continues to moderate"
                    }},
                    "recent_indicators": [
                        {{
                            "indicator": "Retail Sales",
                            "value": "+0.6% month-over-month",
                            "impact": "Stronger than expected, suggesting resilient consumer spending"
                        }},
                        {{
                            "indicator": "ISM Manufacturing",
                            "value": "48.5",
                            "impact": "Still in contraction territory but improving from previous month"
                        }}
                    ],
                    "risks_opportunities": [
                        "Risk: Persistent core services inflation could delay rate cuts",
                        "Opportunity: Strong labor market supporting consumer spending"
                    ]
                }},
                ...
            ],
            "global_outlook": "The global economy continues to show resilience despite high interest rates, with inflation gradually moderating in most major economies. Central banks are approaching the end of tightening cycles, with some beginning to signal potential easing in 2024. Key risks remain geopolitical tensions and potential energy price volatility."
        }}
        """
        return PromptTemplate(input_variables=["date", "macro_focus"], template=template)
    
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the macro landscape chain.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict containing macro landscape data
        """
        try:
            # Get date from config or use yesterday's date
            date_str = config.get("date", "auto")
            if date_str == "auto":
                yesterday = datetime.now() - timedelta(days=1)
                date_str = yesterday.strftime("%Y-%m-%d")
            
            # Get macro focus regions from config and join them into a comma-separated string
            macro_focus = ", ".join(config.get("macro_focus", ["US", "EU", "China"]))
            
            # Combine inputs into a single dictionary
            inputs = {"date": date_str, "macro_focus": macro_focus}
            
            logger.info(f"Generating macro landscape analysis for {date_str} focusing on {macro_focus}")
            result = self.chain.invoke(inputs)
            logger.info(f"LLM response: {result}")
            
            # Ensure we have a string to parse: if not a string, extract content or cast to string
            if not isinstance(result, str):
                if hasattr(result, "content"):
                    result_str = result.content
                else:
                    result_str = str(result)
            else:
                result_str = result

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

            # Remove citation footnotes like [1][5][10] from inside strings
            cleaned_response = re.sub(r'\s*\[\d+(?:\]\[\d+)*\]', '', cleaned_response)

            logger.info(f"Cleaned response: {cleaned_response}")
            try:
                macro_data = json.loads(cleaned_response)
                return {
                    "section": "macro_landscape",
                    "date": date_str,
                    "data": macro_data
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                return {
                    "section": "macro_landscape",
                    "date": date_str,
                    "data": {},
                    "error": "Failed to parse response"
                }
                
        except Exception as e:
            logger.error(f"Error in macro landscape chain: {e}")
            return {
                "section": "macro_landscape",
                "error": str(e)
            }
