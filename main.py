"""
Main Script for Financial Newsletter Generation

This script orchestrates the entire newsletter generation process by:
1. Loading the configuration
2. Initializing the LLM
3. Running each chain module
4. Formatting and saving the results
"""

import os
import sys
import yaml
import json
import logging
from datetime import datetime, timedelta, date 
from typing import Dict, Any, List, Optional

# Add the project directory to the path to allow relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import chain modules
from finance_newsletter.chains.market_news import MarketNewsChain
from finance_newsletter.chains.market_reaction import MarketReactionChain
from finance_newsletter.chains.macro_landscape import MacroLandscapeChain
from finance_newsletter.chains.stock_watch import StockWatchChain
from finance_newsletter.chains.upcoming_events import UpcomingEventsChain
from finance_newsletter.chains.tldr_newsletter import TLDRChain

# Import utility modules
from finance_newsletter.utils.sonar_wrapper import LLMProvider
from finance_newsletter.utils.formatter import NewsletterFormatter

from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("finance_newsletter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict containing configuration
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {config_path}")
            return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}

def process_date(config: Dict[str, Any]) -> str:
    """
    Process the date from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Processed date string
    """
    date_str = config.get("date", "auto")
    if date_str == "auto":
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
        logger.info(f"Using yesterday's date: {date_str}")
    return date_str

def run_newsletter_generation(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the complete newsletter generation process.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dict containing the complete newsletter data
    """
    try:
        # Process date
        date_str = process_date(config)
        
        # Initialize LLM provider
        llm_provider = LLMProvider(config_path="config.yaml")
        llm = llm_provider.get_llm()
        
        if not llm:
            logger.error("Failed to initialize LLM. Exiting.")
            return {"error": "Failed to initialize LLM"}
        
        # Initialize chain modules
        market_news_chain = MarketNewsChain(llm)
        market_reaction_chain = MarketReactionChain(llm)
        macro_landscape_chain = MacroLandscapeChain(llm)
        stock_watch_chain = StockWatchChain(llm)
        upcoming_events_chain = UpcomingEventsChain(llm)
        tldr_chain = TLDRChain(llm)
        
        # Run each chain and collect results
        logger.info("Running market news chain...")
        market_news_result = market_news_chain.run(config)
        
        logger.info("Running market reaction chain...")
        market_reaction_result = market_reaction_chain.run(config)
        
        logger.info("Running macro landscape chain...")
        macro_landscape_result = macro_landscape_chain.run(config)
        
        logger.info("Running stock watch chain...")
        stock_watch_result = stock_watch_chain.run(config)
        
        logger.info("Running upcoming events chain...")
        upcoming_events_result = upcoming_events_chain.run(config)
        
        # Combine results into a single newsletter
        newsletter = {
            "date": date_str,
            "region": config.get("region", "US"),
            "market_news": market_news_result,
            "market_reaction": market_reaction_result,
            "macro_landscape": macro_landscape_result,
            "stock_watch": stock_watch_result,
            "upcoming_events": upcoming_events_result
        }
        logger.info("Running TL;DR summary chain...")
        tldr_result = tldr_chain.run(newsletter)

        # Finalize the newsletter
        final_newsletter = {
            "date": date_str,
            "tldr_summary": tldr_result,
            "region": config.get("region"),
            "market_news": market_news_result,
            "market_reaction": market_reaction_result,
            "macro_landscape": macro_landscape_result,
            "stock_watch": stock_watch_result,
            "upcoming_events": upcoming_events_result
        }
        
        logger.info("Newsletter generation completed successfully")
        print(f"Final newsletter: {json.dumps(final_newsletter, indent=2)}")

        return final_newsletter
        
    except Exception as e:
        logger.error(f"Error in newsletter generation: {e}")
        return {"error": str(e)}

def main():
    """Main function to run the newsletter generation process."""
    try:
        # Load configuration
        config = load_config()
        if not config:
            logger.error("Failed to load configuration. Exiting.")
            return
        
        # Run newsletter generation
        newsletter = run_newsletter_generation(config)
        
        # Check for errors
        if "error" in newsletter:
            logger.error(f"Newsletter generation failed: {newsletter['error']}")
            return
        
        # Initialize formatter
        formatter = NewsletterFormatter(output_dir="outputs")
        
        # Get date string
        date_str = newsletter.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        # Format and save outputs based on configuration
        output_formats = config.get("output_format", ["json"])
        
        # Always save JSON
        json_path = formatter.format_json(newsletter, date_str)
        logger.info(f"JSON report saved to {json_path}")
        
        # Save markdown if configured
        if "markdown" in output_formats:
            md_path = formatter.format_markdown(newsletter, date_str)
            logger.info(f"Markdown report saved to {md_path}")
        
        # Save HTML if configured
        if "html" in output_formats:
            html_path = formatter.format_html(newsletter, date_str)
            logger.info(f"HTML report saved to {html_path}")
        
        logger.info("Newsletter generation and formatting completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
