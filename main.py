import os
import csv
import ajyal_donation_extractor

if __name__ == "__main__":
    service = ajyal_donation_extractor.connect_to_gmail('credentials.json')

    # Fetch emails from the same sender
    messages = ajyal_donation_extractor.fetch_emails(service, '(FROM "hayri.ardal@gmail.com")')

    if not os.path.exists("emails"):
        os.makedirs("emails")

    all_data = []
    for message in messages:  # Iterate through the downloaded messages
        filename = os.path.join("emails", message['id'] + ".eml")
        ajyal_donation_extractor.download_email(service, message, filename)

        # Extract order information
        data = ajyal_donation_extractor.extract_order_info(filename)
        if data:
            all_data.append(data)

    # Store the extracted data from all emails
    with open("email_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["order_number", "phone_number", "first_name", "last_name", "email_address", "quantity", "total"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_data:
            writer.writerow(row)