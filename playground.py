#!/usr/bin/env python
"""
Playground Script for Testing Individual Finance Newsletter Chains

This script allows testing individual chain modules from the finance newsletter
project without running the entire pipeline. It's useful for development and debugging.

Usage:
    python playground.py --chain [chain_name]

Example:
    python playground.py --chain macro_landscape
"""

import os
import sys
import yaml
import json
import logging
import argparse
from datetime import datetime, timedelta

# Add the project directory to the path to allow relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import chain modules
from finance_newsletter.chains.market_news import MarketNewsChain
from finance_newsletter.chains.market_reaction import MarketReactionChain
from finance_newsletter.chains.macro_landscape import MacroLandscapeChain
from finance_newsletter.chains.stock_watch import StockWatchChain
from finance_newsletter.chains.upcoming_events import UpcomingEventsChain

# Import utility modules
from finance_newsletter.utils.sonar_wrapper import LLMProvider

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("playground.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path: str = "config.yaml"):
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

def process_date(config):
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

def initialize_llm(config):
    """
    Initialize the LLM provider.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Initialized LLM instance
    """
    try:
        llm_provider = LLMProvider(config_path="config.yaml")
        llm = llm_provider.get_llm()
        
        if not llm:
            logger.error("Failed to initialize LLM.")
            return None
            
        logger.info("LLM initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")
        return None

def run_chain(chain_name, config, llm):
    """
    Run a specific chain module.
    
    Args:
        chain_name: Name of the chain to run
        config: Configuration dictionary
        llm: Initialized LLM instance
        
    Returns:
        Result from the chain
    """
    try:
        # Initialize the specified chain
        if chain_name == "market_news":
            chain = MarketNewsChain(llm)
        elif chain_name == "market_reaction":
            chain = MarketReactionChain(llm)
        elif chain_name == "macro_landscape":
            chain = MacroLandscapeChain(llm)
        elif chain_name == "stock_watch":
            chain = StockWatchChain(llm)
        elif chain_name == "upcoming_events":
            chain = UpcomingEventsChain(llm)
        else:
            logger.error(f"Unknown chain: {chain_name}")
            return {"error": f"Unknown chain: {chain_name}"}
        
        # Run the chain
        logger.info(f"Running {chain_name} chain...")
        result = chain.run(config)
        
        return result
    except Exception as e:
        logger.error(f"Error running {chain_name} chain: {e}")
        return {"error": str(e)}

def save_result(result, chain_name):
    """
    Save the chain result to a JSON file.
    
    Args:
        result: Result from the chain
        chain_name: Name of the chain
    """
    try:
        # Create outputs directory if it doesn't exist
        os.makedirs(os.path.join("docs", "outputs"), exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"docs/outputs/{chain_name}_{timestamp}.json"
        
        # Save result to file
        with open(filename, 'w') as file:
            json.dump(result, file, indent=2)
            
        logger.info(f"Result saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving result: {e}")
        return None

def main():
    """Main function to run the playground."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test individual finance newsletter chains")
    parser.add_argument("--chain", type=str, required=True, 
                        choices=["market_news", "market_reaction", "macro_landscape", 
                                "stock_watch", "upcoming_events"],
                        help="Name of the chain to run")
    parser.add_argument("--config", type=str, default="config.yaml",
                        help="Path to configuration file")
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        if not config:
            logger.error("Failed to load configuration. Exiting.")
            return
        
        # Initialize LLM
        llm = initialize_llm(config)
        if not llm:
            logger.error("Failed to initialize LLM. Exiting.")
            return
        
        # Run the specified chain
        result = run_chain(args.chain, config, llm)
        
        # Check for errors
        if "error" in result:
            logger.error(f"Chain execution failed: {result['error']}")
            return
        
        # Save the result
        save_result(result, args.chain)
        
        # Print result summary
        print("\n" + "="*50)
        print(f"Chain '{args.chain}' executed successfully")
        print("="*50 + "\n")
        
        # Print the result in a readable format
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        logger.error(f"Error in playground: {e}")

if __name__ == "__main__":
    main()
