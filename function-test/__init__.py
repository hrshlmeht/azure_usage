import logging
import requests
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import csv 
from io import StringIO
import csv
from io import StringIO

# Azure Blob Storage settings
STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=myfirstblob0803;AccountKey=jx4woBiN1hnSnP7p5ZhLcUTrdy1C6kKjPDFy/lbnDXipjsY37fDl0mM0f14faWZ5hpt1BZGJE26r+AStvEqTTQ==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "firstcontainer"
BLOB_NAME = "random_words.txt"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    word = fetch_random_word()

    if word:
        store_word_in_blob(word)
        html_content = generate_html_content(word)
        return func.HttpResponse(html_content, status_code=200, mimetype="text/html")
    else:
        return func.HttpResponse("Failed to fetch a random word from the API.", status_code=500)

def fetch_random_word():
    """Fetch a random word from an API endpoint."""
    url = "https://random-word-api.herokuapp.com/word?number=1"
    response = requests.get(url)
    if response.status_code == 200:
        words = response.json()
        return words[0] if words else None
    return None

def generate_html_content(word):
    """Generate an HTML content to display the word beautifully."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Random Word</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: #f5f5f5;
            }}
            .word-container {{
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                font-size: 24px;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <div class="word-container">
            Random Word: <strong>{word}</strong>
        </div>
    </body>
    </html>
    """

# def store_word_in_blob(word):
#     """Store the fetched word in Azure Blob Storage."""
#     blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
#     blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)
    
#     if blob_client.exists():
#         existing_content = blob_client.download_blob().readall().decode('utf-8')
#         new_content = existing_content + "\n" + word
#     else:
#         new_content = word
    

#     blob_client.upload_blob(new_content, overwrite=True)




BLOB_NAME = 'words.csv'

def store_word_in_blob(word):
    """Store the fetched word in Azure Blob Storage with CSV format."""
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)
    
    counters = {}
    total_words = 0

    # Check if the blob exists
    if blob_client.exists():
        existing_content = blob_client.download_blob().readall().decode('utf-8')
        csv_reader = csv.reader(StringIO(existing_content))
        for row in csv_reader:
            letter, count = row
            counters[letter] = int(count)
            total_words += int(count)

    first_letter = word[0].upper()  # get the first letter and convert to uppercase
    counters[first_letter] = counters.get(first_letter, 0) + 1
    total_words += 1

    # Check if we reached the 200 words threshold
    if total_words >= 200:
        s = StringIO()
        csv_writer = csv.writer(s)
        for key, value in counters.items():
            csv_writer.writerow([key, value])
        blob_client.upload_blob(s.getvalue(), overwrite=True)