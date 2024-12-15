# ajyal_donation_extractor.py

import os
import pickle
import base64
import email
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup


def connect_to_gmail(credentials_file):
    """Connects to the Gmail server using credentials from a JSON file."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, ['https://www.googleapis.com/auth/gmail.readonly'])
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            auth_url, _ = flow.authorization_url(prompt='consent')
            print("Please visit this URL in your browser: " + auth_url)
            code = input("Enter the authorization code: ")
            flow.fetch_token(code=code)
            creds = flow.credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def fetch_emails(service, search_criteria):
    """Fetches emails based on the given search criteria."""
    results = service.users().messages().list(userId='me', q=search_criteria).execute()
    messages = results.get('messages', [])
    return messages


def download_email(service, message_id, filename):
    """Downloads the email and saves it as an .eml file."""
    msg = service.users().messages().get(userId='me', id=message_id['id'], format='raw').execute()
    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))

    with open(filename, 'wb') as f:
        f.write(msg_str)

def extract_order_info(eml_file):
    """
    Extracts order information from the downloaded .eml file.

    Args:
        eml_file: Path to the .eml file.

    Returns:
        A dictionary containing the extracted order information.
    """
    with open(eml_file, 'rb') as f:
        msg = email.message_from_binary_file(f)

    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_content = part.get_payload(decode=True).decode()
            soup = BeautifulSoup(html_content, "html.parser")

            # Find the <div> with class "body"
            body_div = soup.find("div", style="font-size:16px;width:100%!important;height:100%!important;margin:0!important;padding:0!important;background:#f8f8f8")

            if body_div:
                # Extract order number
                order_number = body_div.find(text=lambda value: value and "Order No." in value).strip().split("Order No. ")[1].split(" ")[0]

                # Extract customer information directly from the <div>
                customer_info = body_div.find(text=lambda value: value and "Customer Information" in value).strip()
                phone_number = customer_info.split(" ")[0]
                first_name = customer_info.split(" ")[3]
                last_name = customer_info.split(" ")[4]

                email_tag = body_div.find("a", href=lambda value: value and "mailto:" in value)
                if email_tag:
                    email_address = email_tag["href"].split("mailto:")[1]
                else:
                    email_address = None

                # Extract order summary directly from the <div>
                order_summary = body_div.find(text=lambda value: value and "Order Summary" in value).strip()
                quantity = order_summary.split("Quantity: ")[1].split(" ")[0]
                total = order_summary.split("Total: $")[1].split(" ")[0]

                return {
                    "order_number": order_number,
                    "phone_number": phone_number,
                    "last_name": last_name,
                    "email_address": email_address,
                    "first_name": first_name,
                    "quantity": quantity,
                    "total": total,
                }

    return None
