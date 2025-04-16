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
from dotenv import load_dotenv

load_dotenv()

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

def send_email_gmail(to_emails, subject, plain_text_content, html_content):
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
    message.attach(MIMEText(plain_text_content, "plain"))
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
    
    # Full newsletter URL (the GitHub Pages site where reports are hosted)
    full_newsletter_url = os.getenv('FULL_NEWSLETTER_URL', 'https://fahriburakaydin.github.io/financial_newsletter/reports/report_2025-04-14.html')
    
    subject = "Your Daily Financial Newsletter TLDR"
    plain_text = f"{tldr}\n\nRead the full newsletter here: {full_newsletter_url}"
    html_content = f"<p>{tldr}</p><p>Read the full newsletter <a href='{full_newsletter_url}'>here</a>.</p>"
    
    subscribers = load_subscribers()
    send_email_gmail(subscribers, subject, plain_text, html_content)
