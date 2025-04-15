"""
Formatter Module

This module provides utilities for formatting the newsletter data into various output formats
including JSON, Markdown, and HTML.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
            with open(filepath, 'w') as f:
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
            with open(filepath, 'w') as f:
                f.write(html_content)
            logger.info(f"HTML report saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error formatting HTML: {e}")
            return ""

    def _generate_markdown(self, data: Dict[str, Any], date_str: str) -> str:
        md = [f"# Financial Market Newsletter - {date_str}\n"]

        if "market_news" in data:
            md.append("## Top Market-Moving News\n")
            news_data = data["market_news"]
            if "error" in news_data:
                md.append(f"*Error retrieving market news: {news_data['error']}*\n")
            else:
                for item in news_data.get("news_items", []):
                    md.append(f"### {item.get('headline', 'Untitled')}\n")
                    md.append(f"{item.get('summary', 'No summary available')}\n")
                    md.append(f"**Market Impact:** {item.get('impact', 'Unknown')}\n")
                    md.append(f"**Source:** {item.get('source', 'Unknown')}\n\n")

        if "market_reaction" in data:
            md.append("## Market Reaction Summary\n")
            reaction_data = data["market_reaction"].get("data", {})
            if "error" in data["market_reaction"]:
                md.append(f"*Error retrieving market reaction: {data['market_reaction']['error']}*\n")
            else:
                if "overall_summary" in reaction_data:
                    md.append(f"{reaction_data['overall_summary']}\n\n")

                for section, label in [("indices", "Indices"), ("commodities", "Commodities"), ("crypto", "Cryptocurrencies")]:
                    if section in reaction_data:
                        md.append(f"### {label}\n")
                        for item in reaction_data[section]:
                            md.append(f"**{item.get('name')} ({item.get('ticker')}):** {item.get('performance')} at {item.get('value')}\n")
                            md.append(f"{item.get('summary')}\n\n")

        if "macro_landscape" in data:
            md.append("## Macro-Economic Landscape\n")
            macro_data = data["macro_landscape"].get("data", {})
            if "error" in data["macro_landscape"]:
                md.append(f"*Error retrieving macro landscape: {data['macro_landscape']['error']}*\n")
            else:
                for region in macro_data.get("regions", []):
                    md.append(f"### {region.get('name')}\n")

                    ec = region.get("economic_conditions", {})
                    md.append("#### Economic Conditions\n")
                    md.append(f"- **Growth:** {ec.get('growth')}\n")
                    md.append(f"- **Inflation:** {ec.get('inflation')}\n")
                    md.append(f"- **Employment:** {ec.get('employment')}\n\n")

                    cb = region.get("central_bank", {})
                    md.append("#### Central Bank Policy\n")
                    md.append(f"- **Current Rate:** {cb.get('current_rate')}\n")
                    md.append(f"- **Recent Decision:** {cb.get('recent_decision')}\n")
                    md.append(f"- **Outlook:** {cb.get('outlook')}\n\n")

                    indicators = region.get("recent_indicators", [])
                    if indicators:
                        md.append("#### Recent Economic Indicators\n")
                        for i in indicators:
                            md.append(f"- **{i.get('indicator')}**: {i.get('value')} — {i.get('impact')}\n")
                        md.append("\n")

                    for label, section in [("#### Risks & Opportunities", "risks_opportunities")]:
                        items = region.get(section, [])
                        if items:
                            md.append(f"{label}\n")
                            for item in items:
                                md.append(f"- {item}\n")
                            md.append("\n")

                if "global_outlook" in macro_data:
                    md.append("### Global Outlook\n")
                    md.append(f"{macro_data['global_outlook']}\n\n")

        if "stock_watch" in data:
            md.append("## Stock Watch\n")
            stock_data = data["stock_watch"].get("data", {})
            if "error" in data["stock_watch"]:
                md.append(f"*Error retrieving stock data: {data['stock_watch']['error']}*\n")
            else:
                sp = stock_data.get("sector_performance", {})
                md.append("### Sector Performance\n")
                md.append(f"- **Best Performing:** {sp.get('best_performing')}\n")
                md.append(f"- **Worst Performing:** {sp.get('worst_performing')}\n\n")

                for stock in stock_data.get("stocks", []):
                    md.append(f"### {stock.get('company')} ({stock.get('ticker')})\n")
                    md.append(f"**Price:** {stock.get('price')} ({stock.get('performance')})\n\n")
                    if "news" in stock:
                        md.append("#### Recent News\n")
                        for news in stock["news"]:
                            md.append(f"- {news}\n")
                        md.append("\n")
                    ta = stock.get("technical_analysis", {})
                    md.append("#### Technical Analysis\n")
                    md.append(f"- **Trend:** {ta.get('trend')}\n")
                    md.append(f"- **Support:** {ta.get('support')}\n")
                    md.append(f"- **Resistance:** {ta.get('resistance')}\n")
                    md.append(f"- **Moving Averages:** {ta.get('moving_averages')}\n\n")
                    md.append("#### Fundamental Outlook\n")
                    md.append(f"{stock.get('fundamental_outlook')}\n\n")

        if "upcoming_events" in data:
            md.append("## Upcoming Economic Events\n")
            events_data = data["upcoming_events"].get("data", {})
            if "error" in data["upcoming_events"]:
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
                        md.append(f"#### {day.get('date')} ({day.get('day')})\n")
                        for e in day.get("events", []):
                            md.append(f"- **{e.get('time')} - {e.get('region')}: {e.get('event')}**\n")
                            md.append(f"  Previous: {e.get('previous')} | Forecast: {e.get('forecast')} | Importance: {e.get('importance')}\n")
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
