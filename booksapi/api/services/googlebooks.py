import requests
from booksapi.api import app


def search_books(search_terms, max_results=20):
    r = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={search_terms}'
                     f'&maxResults={max_results}&key={app.config["GOOGLE_API_KEY"]}')
    if r.status_code not in [200, 201]:
        return {}

    return r.json()


def get_book(book_id):
    r = requests.get(f'https://www.googleapis.com/books/v1/volumes/{book_id}?&key={app.config["GOOGLE_API_KEY"]}')
    if r.status_code not in [200, 201]:
        return None

    return r.json()