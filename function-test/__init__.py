import logging
import requests
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Fetch a random word from the API
    word = fetch_random_word()

    # Process the response
    if word:
        return func.HttpResponse(f"Random Word: {word}", status_code=200)
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
