import os
import pickle
import base64
import email
import re
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
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # Correct redirect URI
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
    """Fetches emails based on the given search criteria.  Handles pagination."""
    messages = []
    page_token = None
    while True:
        results = service.users().messages().list(
            userId='me',
            q=search_criteria,
            maxResults=500,  # Fetch 500 at a time
            pageToken=page_token
        ).execute()

        if 'messages' in results:
            messages.extend(results['messages'])
        page_token = results.get('nextPageToken')
        if not page_token or len(messages) >= 500:  # Stop if no more pages OR we have >= 500
            break
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
        A dictionary containing the extracted order information, or None if extraction fails.
    """
    try:
        with open(eml_file, 'rb') as f:
            msg = email.message_from_binary_file(f)

        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True).decode()
                soup = BeautifulSoup(html_content, "html.parser")

                # Find the <div> with class "body"  -- Use regex for robustness
                body_div = soup.find("div", style=re.compile(r"font-size:\s*16px;\s*width:\s*100%!important;"))

                if body_div:
                    # Extract order number  -- Use regex
                    order_number_match = re.search(r"Order No\.\s*(\S+)", body_div.get_text())
                    order_number = order_number_match.group(1) if order_number_match else None

                    # --- IMPROVED CUSTOMER INFO EXTRACTION ---
                    all_text_nodes = body_div.find_all(string=True)
                    all_text = "\n".join(node.strip() for node in all_text_nodes if node.strip())
                    customer_info_match = re.search(r"Customer Information\n(.*?)\nOrder Summary", all_text, re.DOTALL)

                    if customer_info_match:
                        customer_info = customer_info_match.group(1).strip()

                        # --- Corrected Name, Email, and Phone Extraction ---
                        # 1. Find the email address.  This seems *most* reliable in your examples.
                        email_match = re.search(r"([\w\.-]+@[\w\.-]+)", customer_info)
                        email_address = email_match.group(1) if email_match else ""

                        # 2. Find the phone number. Allow for variations in formatting
                        phone_match = re.search(r"(\+?\d[\d\s\(\)-]*)", customer_info) # More flexible phone
                        phone_number = phone_match.group(1).strip() if phone_match else ""


                        # 3. Extract the name, handling different orderings.
                        if email_address:
                            parts = customer_info.split(email_address)
                            if len(parts) > 1:  # email is in the middle or end
                                name_part = parts[0].strip(", \n")
                                if phone_number: #phone number exists
                                    name_part = name_part.split(phone_number)[-1].strip(", \n")
                            else: #email is at the begining
                                name_part = ""
                        else:
                             name_part = ""


                        names = name_part.strip().split()
                        first_name = names[0] if names else ""
                        last_name = names[-1] if len(names) > 1 else ""
                        # --- End of Corrected Extraction ---

                    else:  # No Customer Information section found
                        phone_number = ""
                        first_name = ""
                        last_name = ""
                        email_address = ""

                    # --- IMPROVED ORDER SUMMARY EXTRACTION ---
                    order_summary_match = re.search(r"Order Summary\n(.*?)(?:\nCustomer Information|\nThank you|\Z)", all_text, re.DOTALL) #Added \Z
                    if order_summary_match:
                        order_summary = order_summary_match.group(1).strip()

                        # --- Corrected Quantity and Total Extraction ---
                        # Use find_all to find ALL quantity and total lines, then get the LAST one
                        quantity_lines = re.findall(r"Quantity:\s*(\d+)", order_summary)
                        quantity = quantity_lines[-1] if quantity_lines else None

                        total_lines = re.findall(r"Total:\s*[^\d]*(\d+\.\d+)", order_summary)
                        total = total_lines[-1] if total_lines else None

                        #If it's not found in the normal order summary, search the whole thing.
                        if not quantity:
                            quantity_lines = re.findall(r"Quantity:\s*(\d+)", all_text)
                            quantity = quantity_lines[-1] if quantity_lines else None
                        if not total:
                            total_lines = re.findall(r"Total:\s*[^\d]*(\d+\.\d+)", all_text)
                            total = total_lines[-1] if total_lines else None
                        # --- End of Corrected Extraction ---

                    else:
                        quantity = None
                        total = None

                    return {
                        "order_number": order_number,
                        "phone_number": phone_number,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email_address": email_address,
                        "quantity": quantity,
                        "total": total,
                    }

    except Exception as e:
        print(f"Error processing {eml_file}: {e}")  # Log the specific error
        return None

    return None