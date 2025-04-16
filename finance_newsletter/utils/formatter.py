"""
Formatter Module

This module provides utilities for formatting the newsletter data into various output formats,
including JSON, Markdown, and HTML.
"""

import os
import glob
import json
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def safe_dict(value) -> Dict:
    """Ensure the value is a dict; otherwise, return an empty dict."""
    return value if isinstance(value, dict) else {}


class NewsletterFormatter:
    """Formatter for converting newsletter data to various output formats."""
    
    def __init__(self, output_dir: str = "../outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def format_json(self, data: Dict[str, Any], date_str: Optional[str] = None) -> str:
        try:
            date_str = date_str or datetime.now().strftime("%Y-%m-%d")
            filepath = os.path.join(self.output_dir, f"report_{date_str}.json")
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"JSON report saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error formatting JSON: {e}")
            return ""
    
    def format_markdown(self, data: Dict[str, Any], date_str: Optional[str] = None) -> str:
        try:
            date_str = date_str or datetime.now().strftime("%Y-%m-%d")
            filepath = os.path.join(self.output_dir, f"report_{date_str}.md")
            md_content = self._generate_markdown(data, date_str)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"Markdown report saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error formatting Markdown: {e}")
            return ""
    
    def format_html(self, data: Dict[str, Any], date_str: Optional[str] = None) -> str:
        try:
            date_str = date_str or datetime.now().strftime("%Y-%m-%d")
            filepath = os.path.join(self.output_dir, f"report_{date_str}.html")
            html_content = self._generate_html(data, date_str)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML report saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error formatting HTML: {e}")
            return ""
    
    def _generate_markdown(self, data: Dict[str, Any], date_str: str) -> str:
        md = []
        
        # Title
        md.append(f"# Financial Market Newsletter - {date_str}\n")
        
        # TL;DR Summary Section
        if "tldr_summary" in data:
            tldr_data = data["tldr_summary"]
            if isinstance(tldr_data, dict):
                tldr_text = tldr_data.get("summary", "No summary available")
            else:
                tldr_text = str(tldr_data)
            md.append("## TL;DR Summary\n")
            md.append(tldr_text + "\n\n")
        
        # Market News Section
        if "market_news" in data:
            md.append("## Top Market-Moving News\n")
            news_data = safe_dict(data["market_news"])
            if "error" in news_data:
                md.append(f"*Error retrieving market news: {news_data['error']}*\n")
            else:
                for item in news_data.get("news_items", []):
                    md.append(f"### {item.get('headline', 'Untitled')}\n")
                    md.append(f"{item.get('summary', 'No summary available')}\n")
                    md.append(f"**Market Impact:** {item.get('impact', 'Unknown')}\n")
                    md.append(f"**Source:** {item.get('source', 'Unknown')}\n\n")
        
        # Market Reaction Section
        if "market_reaction" in data:
            md.append("## Market Reaction Summary\n")
            reaction_data = safe_dict(safe_dict(data["market_reaction"]).get("data", {}))
            if "error" in safe_dict(data["market_reaction"]):
                md.append(f"*Error retrieving market reaction: {data['market_reaction']['error']}*\n")
            else:
                if "overall_summary" in reaction_data:
                    md.append(f"{reaction_data['overall_summary']}\n\n")
                for section, label in [("indices", "Indices"), ("commodities", "Commodities"), ("crypto", "Cryptocurrencies")]:
                    if section in reaction_data:
                        md.append(f"### {label}\n")
                        for item in reaction_data[section]:
                            md.append(f"**{item.get('name', 'Unknown')} ({item.get('ticker', '')}):** {item.get('performance', 'Unknown')} at {item.get('value', 'Unknown')}\n")
                            md.append(f"{item.get('summary', 'No summary available')}\n\n")
        
        # Macro-Economic Landscape Section
        if "macro_landscape" in data:
            md.append("## Macro-Economic Landscape\n")
            macro_data = safe_dict(safe_dict(data["macro_landscape"]).get("data", {}))
            if "error" in safe_dict(data["macro_landscape"]):
                md.append(f"*Error retrieving macro landscape: {data['macro_landscape']['error']}*\n")
            else:
                for region in macro_data.get("regions", []):
                    md.append(f"### {region.get('name', 'Unknown Region')}\n")
                    ec = safe_dict(region.get("economic_conditions", {}))
                    md.append("#### Economic Conditions\n")
                    md.append(f"- **Growth:** {ec.get('growth', 'No data')}\n")
                    md.append(f"- **Inflation:** {ec.get('inflation', 'No data')}\n")
                    md.append(f"- **Employment:** {ec.get('employment', 'No data')}\n\n")
                    cb = safe_dict(region.get("central_bank", {}))
                    md.append("#### Central Bank Policy\n")
                    md.append(f"- **Current Rate:** {cb.get('current_rate', 'No data')}\n")
                    md.append(f"- **Recent Decision:** {cb.get('recent_decision', 'No data')}\n")
                    md.append(f"- **Outlook:** {cb.get('outlook', 'No data')}\n\n")
                    indicators = region.get("recent_indicators", [])
                    if indicators:
                        md.append("#### Recent Economic Indicators\n")
                        for i in indicators:
                            md.append(f"- **{i.get('indicator', 'Unknown')}:** {i.get('value', '')} — {i.get('impact', '')}\n")
                        md.append("\n")
                    risks = region.get("risks_opportunities", [])
                    if risks:
                        md.append("#### Risks & Opportunities\n")
                        for item in risks:
                            md.append(f"- {item}\n")
                        md.append("\n")
                if "global_outlook" in macro_data:
                    md.append("### Global Outlook\n")
                    md.append(f"{macro_data['global_outlook']}\n\n")
        
        # Stock Watch Section
        if "stock_watch" in data:
            md.append("## Stock Watch\n")
            stock_data = safe_dict(safe_dict(data["stock_watch"]).get("data", {}))
            if "error" in safe_dict(data["stock_watch"]):
                md.append(f"*Error retrieving stock data: {data['stock_watch']['error']}*\n")
            else:
                sp = safe_dict(stock_data.get("sector_performance", {}))
                md.append("### Sector Performance\n")
                md.append(f"- **Best Performing:** {sp.get('best_performing', 'No data')}\n")
                md.append(f"- **Worst Performing:** {sp.get('worst_performing', 'No data')}\n\n")
                for stock in stock_data.get("stocks", []):
                    md.append(f"### {stock.get('company', 'Unknown')} ({stock.get('ticker', '')})\n")
                    md.append(f"**Price:** {stock.get('price', 'N/A')} ({stock.get('performance', 'N/A')})\n\n")
                    if "news" in stock:
                        md.append("#### Recent News\n")
                        for news in stock["news"]:
                            md.append(f"- {news}\n")
                        md.append("\n")
                    ta = safe_dict(stock.get("technical_analysis", {}))
                    md.append("#### Technical Analysis\n")
                    md.append(f"- **Trend:** {ta.get('trend', 'No data')}\n")
                    md.append(f"- **Support:** {ta.get('support', 'No data')}\n")
                    md.append(f"- **Resistance:** {ta.get('resistance', 'No data')}\n")
                    md.append(f"- **Moving Averages:** {ta.get('moving_averages', 'No data')}\n\n")
                    md.append("#### Fundamental Outlook\n")
                    md.append(f"{stock.get('fundamental_outlook', 'No data')}\n\n")
        
        # Upcoming Events Section
        if "upcoming_events" in data:
            md.append("## Upcoming Economic Events\n")
            events_data = safe_dict(safe_dict(data["upcoming_events"]).get("data", {}))
            if "error" in safe_dict(data["upcoming_events"]):
                md.append(f"*Error retrieving upcoming events: {data['upcoming_events']['error']}*\n")
            else:
                if "highlights" in events_data:
                    md.append("### Key Highlights\n")
                    for h in events_data["highlights"]:
                        md.append(f"- {h}\n")
                    md.append("\n")
                if "calendar" in events_data:
                    md.append("### Economic Calendar\n")
                    for day in events_data["calendar"]:
                        md.append(f"#### {day.get('date', 'Unknown')} ({day.get('day', '')})\n")
                        for e in day.get("events", []):
                            md.append(f"- **{e.get('time', '')} - {e.get('region', '')}: {e.get('event', 'Unknown Event')}**\n")
                            md.append(f"  Previous: {e.get('previous', 'N/A')} | Forecast: {e.get('forecast', 'N/A')} | Importance: {e.get('importance', 'N/A')}\n")
                        md.append("\n")
        
        md.append("---\n")
        md.append(f"*This newsletter was automatically generated on {date_str}*\n")
        return "\n".join(md)
    
    def _generate_html(self, data: Dict[str, Any], date_str: str) -> str:
        md = self._generate_markdown(data, date_str).replace("\n", "<br>\n")
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Financial Market Newsletter - {date_str}</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .footer {{ font-size: 0.8em; color: #999; margin-top: 40px; border-top: 1px solid #ccc; padding-top: 10px; }}
            </style>
        </head>
        <body>
            {md}
            <div class="footer">
                <p>This newsletter was automatically generated on {date_str}</p>
            </div>
        </body>
        </html>
        """


if __name__ == "__main__":
    # This main block finds the latest JSON report in the outputs folder,
    # loads it, and then generates Markdown and HTML reports from it.
    outputs_dir = os.path.join(os.getcwd(), "outputs")
    json_files = sorted(glob.glob(os.path.join(outputs_dir, "*.json")),
                        key=os.path.getmtime, reverse=True)
    if not json_files:
        logger.error("No JSON report found in outputs folder.")
        exit(1)
    
    latest_json = json_files[0]
    try:
        with open(latest_json, "r") as f:
            newsletter_data = json.load(f)
            logger.info(f"Loaded JSON report from {latest_json}")
    except Exception as e:
        logger.error(f"Error loading JSON report: {e}")
        exit(1)
    
    formatter = NewsletterFormatter(output_dir=outputs_dir)
    date_str = newsletter_data.get("date", datetime.now().strftime("%Y-%m-%d"))
    md_path = formatter.format_markdown(newsletter_data, date_str)
    html_path = formatter.format_html(newsletter_data, date_str)
    logger.info(f"Markdown report saved to {md_path}")
    logger.info(f"HTML report saved to {html_path}")
