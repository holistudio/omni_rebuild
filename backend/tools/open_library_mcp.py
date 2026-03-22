import os
import asyncio
import json
import time
import requests

from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

NODE_PATH = os.getenv(
    "NODE_PATH",
    os.path.expanduser("usr/bin/node")
)

MCP_SERVER_PATH = os.getenv(
    "MCP_OPEN_LIBRARY_PATH",
    os.path.expanduser("~/mcp-open-library/build/index.js")
)

HEADERS = {
    "User-Agent": f"ProjectOmnibot/1.0 ({os.environ.get('CONTACT_EMAIL', 'contact@example.com')})"
}

def _author_match(llm_author: str, library_authors: list[str]) -> bool:
    if not library_authors:
        return False
    
    # use the last name / surname as basis for detecting the match
    last_name = llm_author.strip().split()[-1].lower()
    return any(last_name in a.lower() for a in library_authors)

def _fetch_work_data(work_key: str) -> dict:
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
    except Exception as e:
        print(f"   [OpenLib] Works API error for {work_key}: {e}")
        return empty

async def _get_books_async(suggestions: list[dict]):
    server_params = StdioServerParameters(
        command=NODE_PATH,
        args=[MCP_SERVER_PATH]
    )

    books = []

    # start one node.js process for entire batch of books
    async with stdio_client(server_params) as (read, write):
        # wrap into MCP
        async with ClientSession(read, write) as session:
            # MCP handshake
            await session.initialize()

            print("\nSearching...\n")
            for suggestion in suggestions:
                title = suggestion["title"]
                author = suggestion["author"]
                
                try:
                    print(f"   [MCP] Looking up {title}, {author}...\n")
                    # MCP returns CallToolResult
                    result = await session.call_tool(
                        "get_book_by_title", {"title": title}
                    )
                    # print(f"   {result}\n")

                    raw = result.content[0].text if result.content else "[]"
                    hits = json.loads(raw)

                    if not hits:
                        print(f"   [MCP] No results for {title}")
                        continue

                    top = hits[0]

                    # validate author matches
                    returned_authors = top.get("authors", [])
                    if not _author_match(author, returned_authors):
                        print(
                            f"   [MCP] Author mismatch — '{title} by {author}' vs '{top.get("title","no_title")}': "
                            f"expected '{author}', got {returned_authors}"
                        )
                        continue

                    # look up work for book description
                    work_key = top.get("open_library_work_key", "")
                    if not work_key:
                        print(f"   [MCP] No work key returned for: '{title}'")
                        continue

                    work_data = _fetch_work_data(work_key)
                    if not work_data["description"]:
                        print(f"   [OpenLib] No description for: '{title}' ({work_key})")
                        continue

                    subjects = work_data.get("subjects",[])[:5]
                    genre = subjects[0] if subjects else "N/A"

                    books.append({
                        "title": top.get("title", title),
                        "author": ", ".join(returned_authors) if returned_authors else author,
                        "year": top.get("first_publish_year", "N/A"),
                        "genre": genre,
                        "summary": work_data["description"],
                        "open_library_key": work_key,
                    })

                    print(f"   [OK]  {top.get('title', title)} collected!")

                    time.sleep(0.35)
                except json.JSONDecodeError as e:
                    print(f"   [ERR] JSON parse error for '{title}': {e}")
                    continue
                except Exception as e:
                    print(f"   [ERR] Unexpected error for '{title}': {e}")
                    continue
    return books

def search_books_mcp(suggestions: list[dict]) -> list[dict]:
    return asyncio.run(_get_books_async(suggestions))