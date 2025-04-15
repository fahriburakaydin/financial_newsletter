"""
README for Finance Newsletter Generator

A modular, configurable, AI-powered system that generates a daily financial newsletter using LangChain.
"""

# Finance Newsletter Generator

This system generates a comprehensive daily financial newsletter using LangChain for agent orchestration and Perplexity Sonar (or OpenAI) as the LLM provider.

## Features

- **Modular Design**: Each section of the newsletter is its own LangChain chain
- **Configurable**: Track specific stocks, indices, commodities, and macro focus via `config.yaml`
- **Multiple Output Formats**: JSON, Markdown, and HTML
- **Extensible Architecture**: Easy to add new sections or modify existing ones

## Newsletter Sections

1. **Top Market-Moving News**: Key news events affecting markets
2. **Market Reaction Summary**: Performance of indices, commodities, and cryptocurrencies
3. **Macro-Economic Landscape**: Overview of economic conditions in key regions
4. **Stock Watch**: Updates on user-defined tickers
5. **Upcoming Economic Events**: Calendar of important economic events

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -e .
   ```
3. Set up environment variables:
   ```
   export PERPLEXITY_API_KEY=your_key_here
   export OPENAI_API_KEY=your_key_here  # For fallback
   ```

## Configuration

Edit the `config.yaml` file to customize your newsletter:

```yaml
# Date settings (use "auto" for yesterday's date)
date: "auto"

# Region focus
region: "US"  # Options: US, EU, ASIA, GLOBAL

# Macro-economic focus areas
macro_focus:
  - "US"
  - "EU"
  - "China"

# Stock tickers to track
tickers:
  - "AAPL"  # Apple
  - "MSFT"  # Microsoft
  - "NVDA"  # NVIDIA
  - "TSLA"  # Tesla
  - "AMZN"  # Amazon

# Market indices to track
indices:
  - "^GSPC"  # S&P 500
  - "^DJI"   # Dow Jones
  - "^IXIC"  # NASDAQ
  - "^FTSE"  # FTSE 100

# Commodities to track
commodities:
  - "GC=F"   # Gold
  - "CL=F"   # Crude Oil
  - "SI=F"   # Silver

# Cryptocurrencies to track
crypto:
  - "BTC-USD"  # Bitcoin
  - "ETH-USD"  # Ethereum

# Output settings
output_format:
  - "json"     # Always output JSON
  - "markdown" # Also output markdown

# LLM settings
llm:
  provider: "sonar"  # Options: sonar, openai
  fallback: "openai" # Fallback provider if primary fails
  model: "sonar-medium-online"  # For Sonar
  openai_model: "gpt-3.5-turbo"  # For OpenAI fallback
```

## Usage

Run the newsletter generator:

```bash
python main.py
```

The generated newsletter will be saved in the `outputs` directory in the formats specified in your configuration.

## Project Structure

```
finance_newsletter/
├── config.yaml
├── main.py
├── chains/
│   ├── market_news.py
│   ├── market_reaction.py
│   ├── macro_landscape.py
│   ├── stock_watch.py
│   └── upcoming_events.py
├── utils/
│   ├── sonar_wrapper.py
│   └── formatter.py
└── outputs/
    └── report_<YYYY-MM-DD>.json
```

## Extending the System

To add a new section to the newsletter:

1. Create a new chain module in the `chains` directory
2. Update the `main.py` file to include your new chain
3. Update the formatter to handle the new section's data

## Scheduling

You can schedule the newsletter generation using cron:

```
0 6 * * * cd /path/to/finance_newsletter && python main.py
```

This will run the newsletter generator every day at 6:00 AM.

## License

MIT
