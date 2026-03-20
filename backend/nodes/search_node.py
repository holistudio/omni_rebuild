import json

from langchain_core.messages import SystemMessage
from config import get_llm
from tools.open_library import lookup_single_book

SEARCH_SYSTEM_PROMPT = """Based on the conversation history below, suggest exactly 10 
real books the user might enjoy. Choose well-known, published books that are likely 
to exist in the Open Library catalog.
 
Return ONLY one JSON array of objects, each with "title" and "author" keys.
No markdown, no code fences, no commentary — just the raw JSON array.
 
Example response:
[
  {{"title": "Piranesi", "author": "Susanna Clarke"}},
  {{"title": "The Left Hand of Darkness", "author": "Ursula K. Le Guin"}}
]
 
Rules:
- Return ONLY one valid JSON array.
- Suggest exactly 10 books.
- Every book must be a real, published work.
- Vary your picks across sub-genres, time periods, and styles.
- Do NOT repeat any book from the "already tried" list below.
{previous_context}"""

def _generate_book_suggestions(llm, state: dict, titles_already_tried: list[str]) -> list[dict]:
    if titles_already_tried:
        previous_context = (
            "\n\nAlready tried (do NOT suggest these again):\n"
            + "\n".join(f"- {t}" for t in titles_already_tried)
        )
    else:
        previous_context = ""
    
    # insert previously tried titles if any into system prompt
    prompt = SEARCH_SYSTEM_PROMPT.format(previous_context=previous_context)

    # append system message
    messages = [SystemMessage(content=prompt)] + state["messages"]

    # get LLM response
    response = llm.invoke(messages)

    content = response.content.strip()
    print(f"Before parsing:\n {content}")

    # if the LLM responds with a JSON code snippet wrapper,
    # ex: ```json\n[{"title": "Piranesi", "author": "Susanna Clarke"}]\n```
    if content.startswith("```"):
        # remove so that only the list is kept ex: [{"title": "Piranesi", "author": "Susanna Clarke"}]
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    print(f"Pass 1:\n {content}")

    try:
        suggestions = json.loads(content)
    except json.JSONDecodeError:
        # if it still doesn't work, try just finding the list brackets
        start = content.find("[")
        end = content.find("]") + 1
        if start != -1 and end > start:
            try:
                print(f"Pass 2:\n {content}")
                suggestions = json.loads(content[start:end])
            except json.JSONDecodeError:
                return []
        else:
            return []
    
    valid = []
    for item in suggestions:
        if isinstance(item, dict) and "title" in item and "author" in item:
            valid.append(item)
    
    return valid[:10]

def search_node(state: dict) -> dict:
    llm = get_llm()

    existing_results= {b["title"] for b in state["search_results"]}
    titles_already_tried = list(state.get("_titles_tried", []))

    # ask LLM for book suggestions
    suggestions = _generate_book_suggestions(llm, state, titles_already_tried)

    # Search Open Library for books
    print("\nSearching...\n")
    new_books = []
    for suggestion in suggestions:
        title = suggestion["title"]
        author = suggestion["author"]

        titles_already_tried.append(title)

        if title in existing_results:
            continue

        print(f"Looking up {title}, {author}...\n")
        book = lookup_single_book(title, author)
        if book and book["title"] not in existing_results:
            print(f"Found!\n {book}")
            new_books.append(book)
            existing_results.add(book["title"])
    
    all_results = state["search_results"] + new_books

    return {
        "search_results": all_results,
        "search_attempts_tried": state["search_attempts_tried"] + 1,
        "num_books_found": len(all_results),
        "_titles_tried": titles_already_tried,
        "messages": [],
    }