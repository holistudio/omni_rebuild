import json
import re

from langchain_core.messages import SystemMessage

from config import get_llm

RECOMMEND_SYSTEM_PROMPT = """Among the book search results below, recommend 
exactly 5 books to the user based on the conversation history below

{search_context}

For each book, provide a JSON array with objects containing:
- "title": the book title
- "author": the author name
- "year": publication year (use your best knowledge)
- "genre": primary genre
- "summary": a 2-3 sentence summary of the book
- "recommendation": a 2-3 sentence personalized explanation of WHY this book 
  is a good fit, referencing SPECIFIC things the user said in the conversation below.

Return ONLY valid JSON. No markdown, no code fences, just the array."""

def recommend_node(state: dict) -> dict:
    llm = get_llm()

    # TODO: use search results from Open Library API
    search_context = (
        "No search results are available. Use your own knowledge of books to recommend 5 books based on the conversation history."
    )

    # insert search results into context window
    prompt = RECOMMEND_SYSTEM_PROMPT.format(search_context=search_context)

    # append system message
    messages = [SystemMessage(content=prompt)] + state["messages"]

    # get LLM response
    response = llm.invoke(messages)

    # parse the LLM response as a JSON
    try:
        content = response.content.strip()
        # Extract JSON array from anywhere in the response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
        recommendations = json.loads(content)
    except json.JSONDecodeError:
        recommendations = [{"title": "Error", "recommendation": response.content}]

    return {
        "recommendations": recommendations,
        "phase": "done",
        "messages": []
    }