import requests
from django.conf import settings


def fetch_book_data_from_google_books(title):
    api_key = settings.GOOGLE_BOOKS_API_KEY
    base_url = 'https://www.googleapis.com/books/v1/volumes'
    params = {
        'q': title,
        'key': api_key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    # Check if there are items in the response
    if 'items' in data:
        book_data = data['items'][0]['volumeInfo']
        return book_data
    else:
        return None
