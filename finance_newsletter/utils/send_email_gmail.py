# send_email_gmail.py
import os
import csv
import sys
import json
import glob
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, date 
import markdown

from dotenv import load_dotenv

load_dotenv()

#TODO: make the email html pretty


def load_subscribers(csv_file_path='subscribers.csv'):
    subscribers = []
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            email = row[0].strip()
            if email:
                subscribers.append(email)
    return subscribers

def get_latest_newsletter_json():
    # Use glob to find all JSON files that match your report pattern in the outputs folder
    json_files = glob.glob("outputs/report_*.json")
    if not json_files:
        return None
    # Get the latest file by modification time
    latest_file = max(json_files, key=os.path.getmtime)
    return latest_file

def extract_tldr_from_newsletter(json_file_path):
    try:
        with open(json_file_path, 'r') as f:
            newsletter = json.load(f)
        # Assuming the TLDR summary is stored under the "tldr_summary" key.
        # Depending on how your TLDRChain outputs the summary,
        # you might need to adjust this (e.g., if it’s nested or stored under another key).
        tldr =  newsletter["tldr_summary"]["summary"]
        print(f"Extracted TLDR: {tldr}")
        return tldr
    except Exception as e:
        print(f"Error extracting TLDR: {e}")
        return "TLDR summary not available"

def markdown_to_html(md_text: str) -> str:
    """
    Convert Markdown text to HTML using the python-markdown library.
    """
    # You can enable or configure various markdown extensions if you like.
    return markdown.markdown(md_text)

def send_email_gmail(to_emails, subject, html_content):
    smtp_server = "smtp.gmail.com"
    port = 587  # TLS
    sender_email = os.getenv("SENDER_EMAIL", "burkilabs60@gmail.com")  # Use your Gmail address or secret
    password = os.getenv("GMAIL_APP_PASSWORD")
    if not password:
        print("GMAIL_APP_PASSWORD not set!")
        sys.exit(1)
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(to_emails)

    # Attach both plain text and HTML content parts
    #message.attach(MIMEText(plain_text_content, "plain"))  -- removed from the mail assuming that email clients can support html emails. Otherwise they wont see anything in the mail
    message.attach(MIMEText(html_content, "html"))
    
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.sendmail(sender_email, to_emails, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)

if __name__ == '__main__':
    # Locate the latest newsletter JSON file
    latest_json = get_latest_newsletter_json()
    if latest_json:
        tldr = extract_tldr_from_newsletter(latest_json)
        # Optionally, log or print the filename if needed:
        print(f"Using newsletter file: {latest_json}")
    else:
        tldr = "TLDR summary not available."

    
    #Get yesterdays date for the report pulling
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")


    # Full newsletter URL (the GitHub Pages site where reports are hosted)
    full_newsletter_url = os.getenv('FULL_NEWSLETTER_URL', f'https://fahriburakaydin.github.io/financial_newsletter/outputs/report_{date_str}.html')
    
    #plain_text = f"{tldr}\n\nRead the full newsletter here: {full_newsletter_url}"
    #html_content = f"<p>{tldr}</p><p>Read the full newsletter <a href='{full_newsletter_url}'>here</a>.</p>"
    
    #Convert the markdown TLDR to HTML
    tldr_html = markdown_to_html(tldr)

    logo_url = os.getenv('LOGO_URL', f'{full_newsletter_url}/logo.png')
    html_email = f"""\
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>📝Daily Financial Newsletter TLDR</title>
  <style>
    /* Global styling for a modern look */
    body {{ margin:0; padding:0; background-color:#f9f9f9; font-family:Arial, sans-serif; }}
    .container {{ width:850px; max-width:100%; background-color:#ffffff; border-radius:8px; overflow:hidden; }}
    .header {{ background: linear-gradient(90deg, #fcf6eb); padding:20px; text-align:center; }}
    .content {{ padding:20px; color:#333333; font-size:16px; line-height:1.8; }}
    .cta {{ text-align:center; padding:20px; }}
    .cta a {{ display:inline-block; text-decoration:none; background-color:#28a745; color:#ffffff; padding:14px 28px; border-radius:5px; font-size:18px; font-weight:bold; }}
    .footer {{ padding:15px; background-color:#f0f0f0; border-top:1px solid #ddd; text-align:center; font-size:14px; color:#555555; }}
    .footer p {{ margin:10px 0 0; font-size:12px; color:#777777; }}
  
    /* Responsive adjustments for mobile devices */
    @media only screen and (max-width: 950px) {{
      .container {{ width: 100% !important; padding: 5px !important; }}
      .header {{ padding:0x !important; background-color:#fcf6eb !important; }}
      .hero-image {{ width:150px; background-color:#fcf6eb !important; }}
      .content {{ padding:5px !important; }}
      .cta a {{ padding:5px 5px !important; font-size:16px !important; }}
    }}
  </style>
</head>
<body>
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#f9f9f9;">
    <tr>
      <td align="center" style="padding:20px;">
        <table class="container" border="0" cellspacing="0" cellpadding="0">
          <!-- Header: Only the logo -->
          <tr>
            <td class="header">
              <img src="{logo_url}" alt="Logo" class="hero-image" style="display:block; margin-bottom:0; width:350px; height:auto;">
            </td>
          </tr>
          <!-- Main Content -->
          <tr>
            <td class="content">
              {tldr_html}
            </td>
          </tr>
          <!-- CTA Button -->
          <tr>
            <td class="cta">
              <a href="{full_newsletter_url}">Read Full Newsletter</a>
            </td>
          </tr>
          <!-- Footer with social media links -->
          <tr>
            <td class="footer">
              <p>Follow us on: 
                <a href="https://twitter.com/YourHandle" style="text-decoration:none; color:#1DA1F2; margin:0 5px;">Twitter</a> | 
                <a href="https://linkedin.com/in/YourProfile" style="text-decoration:none; color:#0077B5; margin:0 5px;">LinkedIn</a>
              </p>
              <p>Sent via Minutes by Burki<br><em>All data is provided "as is". Not financial advice.</em></p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    subscribers = load_subscribers()
    subject = "Your Daily Financial Newsletter TLDR"
    send_email_gmail(subscribers, subject, html_email)