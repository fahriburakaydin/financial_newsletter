"""
Formatter Module

This module provides utilities for formatting the newsletter data into various output formats,
including JSON, Markdown, and HTML.
"""

import os
import glob
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import markdown
from dotenv import load_dotenv

load_dotenv()

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
    
    def __init__(self, output_dir: str = "..docs/outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def format_json(self, data: Dict[str, Any], date_str: Optional[str] = None) -> str:
        try:
            date_str = date_str or datetime.now().strftime("%Y-%m-%d")
            filepath = os.path.join(self.output_dir, f"report_{date_str}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
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
    
    def update_index(self, index_path: Optional[str] = None) -> str:
        """
        Updates (or creates) an index.html file with links to all HTML reports in the outputs folder.
        The reports are sorted by modification time (newest first).
        """
        if index_path is None:
            index_path = os.path.join(os.getcwd(),"docs", "index.html")
        
        # Find all report HTML files matching the pattern in the output_dir.
        html_files = sorted(
            glob.glob(os.path.join(self.output_dir, "report_*.html")),
            key=lambda x: os.path.getmtime(x),
            reverse=True
        )
        
        list_items = []
        for file in html_files:
            base = os.path.basename(file)
            # Assuming filename format: report_YYYY-MM-DD.html
            if base.startswith("report_") and base.endswith(".html"):
                date_part = base[len("report_"):-len(".html")]
                # Construct the relative URL for GitHub Pages.
                # Adjust the href if needed (here we assume outputs folder is visible in your GitHub Pages deployment)
                list_items.append(f'<li><a href="financial_newsletter/outputs/{base}">Newsletter {date_part}</a></li>\n')
        
        index_html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Newsletter Reports Archive</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      font-family: Arial, sans-serif;
      background-color: #f9f9f9;
    }}
    .container {{
      max-width: 850px;
      margin: 40px auto;
      background: #fff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    header {{
      text-align: center;
      padding-bottom: 20px;
      border-bottom: 1px solid #ddd;
      margin-bottom: 20px;
    }}
    header img {{
      width: 200px;
      height: auto;
      display: block;
      margin: 0 auto 10px;
    }}
    header h1 {{
      font-size: 32px;
      color: #333;
      margin: 0;
    }}
    ul {{
      list-style-type: none;
      padding: 0;
      margin: 0;
    }}
    li {{
      margin: 10px 0;
      border-bottom: 1px solid #eee;
      padding: 10px 0;
    }}
    li a {{
      text-decoration: none;
      color: #005ecc;
      font-size: 18px;
    }}
    li a:hover {{
      text-decoration: underline;
    }}
    @media only screen and (max-width: 600px) {{
      .container {{
        margin: 20px auto;
        padding: 10px;
      }}
      header h1 {{
        font-size: 24px;
      }}
      header img {{
        width: 150px;
      }}
      li a {{
        font-size: 16px;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <img src="{os.getenv('LOGO_URL', 'https://yourusername.github.io/yourrepository/logo.png')}" alt="Logo">
      <h1>Newsletter Reports Archive</h1>
    </header>
    <ul>
      {''.join(list_items)}
    </ul>
  </div>
</body>
</html>
"""
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_html)
        logger.info(f"Index report saved to {index_path}")
        return index_path

    def _generate_markdown(self, data: Dict[str, Any], date_str: str) -> str:
        # Build a Markdown representation of the newsletter.
        md = []
        
        # Title
        md.append(f"# Financial Market Newsletter - {date_str}\n")
        
        # Market News Section
        if "market_news" in data:
            md.append("## Top Market-Moving News 🗞️\n")
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
            md.append("## Market Reaction Summary 🔍\n")
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
            md.append("## Macro-Economic Landscape 🏦\n")
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
            md.append("## Stock Watch 📈\n")
            stock_data = safe_dict(data["stock_watch"].get("data", {}))
            stocks = stock_data.get("stocks", [])
            if stocks:
                for stock in stocks:
                    md.append(f"### {stock.get('company', 'Unknown')} ({stock.get('ticker', '')})\n")
                    md.append(f"{stock.get('overall_summary', 'No summary available')}\n\n")
            else:
                md.append("*No stock watch data available*\n\n")
        
        # Upcoming Events Section
        if "upcoming_events" in data:
            md.append("## Upcoming Economic Events 📢 📅\n")
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
        # md.append(f"*This newsletter was automatically generated on {date_str}*\n")
        return "\n".join(md)
    
    def _generate_html(self, data: Dict[str, Any], date_str: str) -> str:
        # Generate Markdown content
        md_content = self._generate_markdown(data, date_str)
        # Convert Markdown to HTML using the markdown library with the "extra" extension.
        md_html = markdown.markdown(md_content, extensions=['extra'])
        # Get the full URL for the logo from the environment variable.
        logo_url = os.getenv('LOGO_URL', 'https://fahriburakaydin.github.io/financial_newsletter/logo.png')
        # Build the full HTML report using the designed template
        html_content = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Minutes by Burki - Daily Financial Report ({date_str})</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    /* Global styling */
    body {{ 
      margin: 0; 
      padding: 0; 
      font-family: Arial, sans-serif; 
      background-color: #f9f9f9; 
      color: #333;
      line-height: 1.7;
    }}
    .container {{ 
      width: 850px; 
      max-width: 100%; 
      background-color: #ffffff; 
      border-radius: 8px; 
      overflow: hidden; 
      margin: 20px auto; 
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .header {{ 
      background-color: #fcf6eb; 
      padding: 20px; 
      text-align: center; 
    }}
    .header img {{ 
      width: 350px; 
      height: auto;
      display: block;
      margin: 0 auto;
    }}
    .section {{ 
      padding: 20px; 
      border-bottom: 1px solid #ddd; 
    }}
    .section:last-child {{ 
      border-bottom: none; 
    }}
    .section h2 {{ 
      font-size: 24px; 
      color: #333; 
      margin-top: 0; 
      margin-bottom: 10px; 
    }}
    .section p {{ 
      font-size: 16px; 
      margin-bottom: 10px; 
    }}
    .cta {{
      text-align: center; 
      padding: 20px; 
    }}
    .cta a {{
      display: inline-block; 
      text-decoration: none; 
      background-color: #28a745; 
      color: #ffffff; 
      padding: 14px 28px; 
      border-radius: 5px; 
      font-size: 18px; 
      font-weight: bold; 
    }}
    .footer {{ 
      padding: 15px; 
      background-color: #f0f0f0; 
      border-top: 1px solid #ddd; 
      text-align: center; 
      font-size: 14px; 
      color: #555; 
    }}
    .footer p {{ 
      margin: 10px 0 0; 
      font-size: 12px; 
      color: #777; 
    }}
    /* Responsive adjustments */
    @media only screen and (max-width: 950px) {{
      .container {{ 
        width: 100% !important; 
        padding: 5px; 
      }}
      .header {{ 
        padding: 10px; 
      }}
      .header img {{ 
        width: 250px !important; 
      }}
      .section {{ 
        padding: 10px; 
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <img src="{logo_url}" alt="Logo">
    </div>
    <!-- Content Section -->
    <div class="section">
      {md_html}
    </div>
    <!-- Call-to-Action Button for full archive -->
    <div class="cta">
      <a href="https://fahriburakaydin.github.io/financial_newsletter/index.html">View Full Report Archive</a>
    </div>
    <!-- Footer -->
    <div class="footer">
      <p>This newsletter was generated on {date_str}</p>
      <p><em>All data is provided "as is". NOT FINANCIAL ADVICE.</em></p>
      <p>Follow us on: 
        <a href="https://twitter.com/YourHandle" style="text-decoration:none; color:#1DA1F2;">Twitter</a> | 
        <a href="https://linkedin.com/in/YourProfile" style="text-decoration:none; color:#0077B5;">LinkedIn</a>
      </p>
    </div>
  </div>
</body>
</html>
"""
        return html_content


if __name__ == "__main__":
    # This main block finds the latest JSON report in the outputs folder,
    # loads it, and then generates Markdown and HTML reports from it.
    outputs_dir = os.path.join(os.getcwd(),"docs", "outputs")
    json_files = sorted(glob.glob(os.path.join(outputs_dir, "*.json")),
                        key=os.path.getmtime, reverse=True)
    if not json_files:
        logger.error("No JSON report found in outputs folder.")
        exit(1)
    
    latest_json = json_files[0]
    try:
        with open(latest_json, "r", encoding="utf-8") as f:
            newsletter_data = json.load(f)
            logger.info(f"Loaded JSON report from {latest_json}")
    except Exception as e:
        logger.error(f"Error loading JSON report: {e}")
        exit(1)
    
    formatter = NewsletterFormatter(output_dir=outputs_dir)
    date_str = newsletter_data.get("date", datetime.now().strftime("%Y-%m-%d"))
    md_path = formatter.format_markdown(newsletter_data, date_str)
    html_path = formatter.format_html(newsletter_data, date_str)
    # Update index.html with links to all HTML reports in the outputs folder.
    index_path = formatter.update_index()
    logger.info(f"Markdown report saved to {md_path}")
    logger.info(f"HTML report saved to {html_path}")
    logger.info(f"Index page updated at {index_path}")
