# Ajyal Donation Extractor

This project helps you extract donation information from your Ajyal emails and save it to a CSV file.

## Requirements

* Python 3.6 or higher
* Gmail account
* Enabled Gmail API
* `credentials.json` file (downloaded from Google Cloud Console)

## Setup

1. **Install Python:**

    * Download the latest version of Python from [python.org](https://www.python.org/downloads/).
    * Run the installer and follow the instructions.

2. **Install required libraries:**

    * Open a terminal or command prompt.
    * Run the following command:
        ```bash
        pip install -r requirements.txt
        ```

3. **Enable Gmail API:**

    * Go to the [Google Cloud Console](https://console.cloud.google.com/).
    * Create a new project or select an existing one.
    * Enable the Gmail API.
    * Create credentials for a desktop application and download the `credentials.json` file.

## Usage

1. **Clone the repository:**

    ```bash
    git clone [https://github.com/aydintd/ajyal-donation-extractor.git](https://github.com/aydintd/ajyal-donation-extractor.git)
    cd ajyal-donation-extractor
    ```

2. **Run the script:**

    ```bash
    python main.py
    ```

3. **Authorize the application:**

    * The script will prompt you to visit an authorization URL in your web browser.
    * Copy the URL and paste it into your browser.
    * Authorize the application to access your Gmail account.
    * Copy the authorization code from the browser.
    * Paste the authorization code back into the script's prompt.

4. **Wait for the script to finish:**

    * The script will download the emails and extract the donation information.
    * The extracted data will be saved in a CSV file named `email_data.csv`.

## Customization

* **Email search criteria:**
    * Modify the `fetch_emails` function in `ajyal_donation_extractor.py` to change the criteria for selecting emails (e.g., sender, subject, date range).
* **Data extraction:**
    * Update the `extract_order_info` function in `ajyal_donation_extractor.py` to extract additional or different data from the emails.

## Security

* **Keep your `credentials.json` file secure.** Do not share it publicly or commit it to version control.
* The `.gitignore` file is included to prevent sensitive files from being accidentally committed to the repository.