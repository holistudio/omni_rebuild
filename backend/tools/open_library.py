import requests
import time
import os

from dotenv import load_dotenv

load_dotenv()

SEARCH_URL = "https://openlibrary.org/search.json" # Search API endpoint returning JSON

# include header to 3 req/sec limit
HEADERS = {
    "User-Agent": f"ProjectOmnibot/1.0 ({os.environ.get('CONTACT_EMAIL', 'contact@example.com')})"
}

def fetch_work_data(work_key: str) -> dict:
    empty = {"description": None, "subjects": []}

    if not work_key:
        return empty
    
    url = f"https://openlibrary.org/{work_key}.json"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        print(resp.url + "\n")
        
        resp.raise_for_status() # raise exception immediately on HTTP error

        data = resp.json()

        # ensure description returned as string
        description = data.get("description")
        if isinstance(description, dict):
            description = description.get("value", None)
        
        # get full list of subjects
        subjects = data.get("subjects", [])
        return {"description": description, "subjects": subjects}
    except Exception:
        return empty


def search_books(query: str, author: str, limit: int = 10) -> list[dict]:
    """
    query: search query
    limit: max number of search results to get back
    """
    # get request
    params = {
        "q": query,
        "limit": limit,
        "fields": "key,title,author_name,first_publish_year"
    }
    resp = requests.get(SEARCH_URL, params=params, headers=HEADERS)
    print(resp.url + "\n") # uncomment for debugging
    
    resp.raise_for_status() # raise exception immediately on HTTP error

    raw_docs = resp.json().get("docs", []) # results are in "docs" key

    time.sleep(0.35) # stay with 3 req/sec rate limit

    books = []
    for doc in raw_docs:
        work_key = doc.get("key", "") # example: "/works/OL27448W"
        title = doc.get("title", "Unknown")
        authors = doc.get("author_name", ["Unknown"]) # list!
        year = doc.get("first_publish_year", "N/A")
        
        # additional info is fetched with Works API using work_key
        work_data = fetch_work_data(work_key)
        summary = work_data.get("description")
        subjects = work_data.get("subjects",[])[:5]
        genre = subjects[0] if subjects else "N/A"

        # only include books that have summaries and match authors
        if summary and author in authors:
            books.append({
                "title": title,
                "author": ", ".join(authors) if isinstance(authors, list) else authors,
                "year": year,
                "genre": genre,
                "summary": summary,
                "open_library_key": work_key,
            })

        time.sleep(0.35) # stay with 3 req/sec rate limit

    return books


def lookup_single_book(title: str, author: str) -> dict | None:
    # search for a single book by title and author
    query = f"{title} {author}"
    results = search_books(query, author, limit=3) 
    time.sleep(0.35) # stay with 3 req/sec rate limit
    return results[0] if results else None