import os
import asyncio
import json
import time

from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

MCP_SERVER_PATH = os.getenv(
    "MCP_OPEN_LIBRARY_PATH",
    os.path.expanduser("~/mcp-open-library/build/index.js")
)

HEADERS = {
    "User-Agent": f"ProjectOmnibot/1.0 ({os.environ.get('CONTACT_EMAIL', 'contact@example.com')})"
}

async def _get_books_async(suggestions: list[dict]):
    server_params = StdioServerParameters(
        command="node",
        args=[MCP_SERVER_PATH]
    )

    books = []

    # start one node.js process for entire batch of books
    async with stdio_client(server_params) as (read, write):
        # wrap into MCP
        async with ClientSession(read, write) as session:
            # MCP handshake
            await session.initialize()

            for suggestion in suggestions:
                title = suggestion["title"]
                author = suggestion["author"]
                
                try:
                    # MCP returns CallToolResult
                    result = await session.call_tool(
                        "get_book_by_title", {"title": title}
                    )

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
                            f"   [MCP] Author mismatch — '{title}': "
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