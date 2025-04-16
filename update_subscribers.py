import csv
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get the API key from environment variables (set in GitHub Secrets)
API_KEY = os.getenv("MAILERLITE_API_KEY")
# MailerLite API endpoint to get subscribers (refer to their API docs for exact details)
API_URL = "https://api.mailerlite.com/api/v2/subscribers"  # or https://api.mailerlite.com/api/v2/groups/{group_id}/subscribers

if not API_KEY:
    raise Exception("MAILERLITE_API_KEY environment variable is not set!")

headers = {
    "X-MailerLite-ApiKey": API_KEY,
    "Content-Type": "application/json"
}

def fetch_subscribers():
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()  # This should be a list of subscriber objects.
    else:
        raise Exception(f"Error fetching subscribers: {response.status_code} {response.text}")

def update_csv(subscribers, csv_path="subscribers.csv"):
    # Assuming each subscriber object contains an "email" field.
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for subscriber in subscribers:
            email = subscriber.get("email")
            if email:
                writer.writerow([email])
    print(f"Updated CSV with {len(subscribers)} subscribers.")

if __name__ == "__main__":
    subscribers = fetch_subscribers()
    update_csv(subscribers)
