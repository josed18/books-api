import requests


def search_books(search_terms, max_results=20):
    r = requests.get(f'http://openlibrary.org/search.json?q={search_terms}')
    if r.status_code not in [200, 201]:
        return {}

    return r.json()


def get_authors_name(authors):
    authors_name = []

    for author in authors:
        author_key = author.get("key") if "key" in author else author.get("author", {}).author.get("key")
        if author_key is None:
            continue
        r = requests.get(f"https://openlibrary.org{author_key}.json")
        if r.status_code not in [200, 201]:
            continue
        authors_name.append(r.json().get("name"))

    return authors_name


def get_subjects(works_key):
    if works_key is None:
        return []
    r = requests.get(f"https://openlibrary.org{works_key}.json")
    if r.status_code not in [200, 201]:
        return []

    return r.json().get("subjects", [])


def get_book(book_id):
    r = requests.get(f"https://openlibrary.org/books/{book_id}.json")
    if r.status_code not in [200, 201]:
        return None

    data = r.json()

    data["author_name"] = get_authors_name(data.get("authors", []))
    data["subjects"] = get_subjects(data.get("works", [{}])[0].get("key"))

    return data
