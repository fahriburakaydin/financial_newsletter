"""
Test script for the financial newsletter system

This script tests the basic functionality of the newsletter system
without requiring actual API keys by mocking the LLM responses.
"""

import os
import sys
import json
import logging
from unittest.mock import patch
from dotenv import load_dotenv

# Import Runnable from LangChain
from langchain_core.runnables import Runnable

# Load environment variables
load_dotenv()

# Add the project directory to the path to allow relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define mock responses as Python objects
MOCK_MARKET_NEWS_RESPONSE = [
    {
        "headline": "Fed Signals Potential Rate Cut",
        "summary": "Federal Reserve officials indicated they may be ready to cut interest rates in the coming months if inflation continues to moderate. Chair Powell emphasized data dependency in the decision-making process.",
        "impact": "Markets rallied on the news, with the S&P 500 gaining 1.2% and Treasury yields falling.",
        "source": "Federal Reserve Press Release"
    }
]

MOCK_MARKET_REACTION_RESPONSE = {
    "indices": [
        {
            "name": "S&P 500",
            "ticker": "^GSPC",
            "performance": "+0.85%",
            "value": "5,234.18",
            "summary": "The S&P 500 rose on positive Fed comments and strong tech earnings."
        }
    ],
    "commodities": [
    {
      "name": "Gold",
      "performance": "-0.2%",
      "summary": "Gold prices dropped as bond yields rose."
    }
    ],
  "crypto": [
    {
      "name": "Bitcoin",
      "performance": "+3.0%",
      "summary": "Bitcoin surged after positive regulatory news."
    }
  ],
    "overall_summary": "Markets were broadly positive."
}

MOCK_MACRO_RESPONSE = {
    "regions": [
        {
            "name": "US",
            "economic_conditions": {"growth": "2.0%", "inflation": "3.0%", "employment": "3.5%"},
            "central_bank": {"current_rate": "5.00%", "recent_decision": "No change", "outlook": "Stable"},
            "recent_indicators": [{"indicator": "Retail Sales", "value": "+0.5%", "impact": "Moderate"}],
            "risks_opportunities": ["Global uncertainties"]
        },
        {
            "name": "EU",
            "economic_conditions": {"growth": "1.5%", "inflation": "2.5%", "employment": "4.0%"},
            "central_bank": {"current_rate": "4.50%", "recent_decision": "No change", "outlook": "Cautious"},
            "recent_indicators": [{"indicator": "CPI", "value": "2.8%", "impact": "Stable"}],
            "risks_opportunities": ["Political risks"]
        }
    ],
    "global_outlook": "Overall, cautious optimism."
}

MOCK_STOCK_WATCH_RESPONSE = {
    "stocks": [
        {
            "ticker": "AAPL",
            "company": "Apple Inc.",
            "price": "150.00",
            "performance": "+1.0%",
            "news": ["Apple releases new product"],
            "technical_analysis": {
                "trend": "Bullish",
                "support": "148.00",
                "resistance": "155.00",
                "moving_averages": "Above both 50-day and 200-day MA"
            },
            "fundamental_outlook": "Solid growth expected."
        }
    ],
    "sector_performance": {
        "best_performing": "Technology",
        "worst_performing": "Utilities"
    }
}

MOCK_UPCOMING_EVENTS_RESPONSE = {
    "calendar": [
        {
            "date": "2025-04-09",
            "day": "Wednesday",
            "events": [
                {
                    "time": "08:30 ET",
                    "region": "US",
                    "event": "US CPI",
                    "previous": "3.0%",
                    "forecast": "3.1%",
                    "importance": "High"
                }
            ]
        }
    ],
    "highlights": ["Fed chair's speech on Thursday"]
}

# Updated FakeRunnable: accepts two arguments and returns JSON strings for different chains based on the prompt text.
class FakeRunnable(Runnable):
    def invoke(self, inputs, config=None):
        # If inputs is a dict and contains a "text" key (common in PromptTemplate outputs), use it
        if isinstance(inputs, dict) and "text" in inputs:
            prompt_text = inputs["text"]
        else:
            prompt_text = str(inputs)
        print("FakeRunnable invoked with prompt text (first 200 chars):", prompt_text[:200])
        
        # Choose response branch by checking for key phrases in the prompt text
        if "summarizing the most important market-moving news" in prompt_text:
            return json.dumps(MOCK_MARKET_NEWS_RESPONSE)
        elif "summarizing market reactions" in prompt_text:
            return json.dumps(MOCK_MARKET_REACTION_RESPONSE)
        elif "macro-economic" in prompt_text or "current macro-economic landscape" in prompt_text:
            return json.dumps(MOCK_MACRO_RESPONSE)
        elif "Stock Watch" in prompt_text or "analyzing the following tickers" in prompt_text or "specific stocks" in prompt_text:
            return json.dumps(MOCK_STOCK_WATCH_RESPONSE)
        elif "upcoming economic events" in prompt_text or "upcoming events" in prompt_text:
            return json.dumps(MOCK_UPCOMING_EVENTS_RESPONSE)
        else:
            return json.dumps({})

def test_newsletter_generation():
    """Test the newsletter generation process with mocked LLM responses"""
    try:
        from main import load_config, run_newsletter_generation
        from finance_newsletter.utils.formatter import NewsletterFormatter

        # Load configuration from config.yaml
        config = load_config()
        if not config:
            logger.error("Failed to load configuration")
            return False

        # Create a test output directory
        os.makedirs("test_outputs", exist_ok=True)

        # Use our custom FakeRunnable instance as the mock LLM
        mock_llm = FakeRunnable()

        # Patch the LLMProvider.get_llm method to return our FakeRunnable
        with patch('finance_newsletter.utils.sonar_wrapper.LLMProvider.get_llm', return_value=mock_llm):
            # Run newsletter generation process
            newsletter = run_newsletter_generation(config)
            if "error" in newsletter:
                logger.error(f"Newsletter generation failed: {newsletter['error']}")
                return False

            formatter = NewsletterFormatter(output_dir="test_outputs")
            date_str = newsletter.get("date", "2025-04-07")
            json_path = formatter.format_json(newsletter, date_str)
            if not os.path.exists(json_path):
                logger.error(f"JSON file was not created at {json_path}")
                return False

            # Save additional output formats if configured
            output_formats = config.get("output_format", [])
            if "markdown" in output_formats:
                md_path = formatter.format_markdown(newsletter, date_str)
                if not os.path.exists(md_path):
                    logger.error(f"Markdown file was not created at {md_path}")
                    return False
            if "html" in output_formats:
                html_path = formatter.format_html(newsletter, date_str)
                if not os.path.exists(html_path):
                    logger.error(f"HTML file was not created at {html_path}")
                    return False

            logger.info(f"Test successful! Newsletter generated and saved to {json_path}")
            return True

    except Exception as e:
        logger.error(f"Error in test: {e}")
        return False

if __name__ == "__main__":
    success = test_newsletter_generation()
    print(f"Test {'passed' if success else 'failed'}")
    sys.exit(0 if success else 1)
