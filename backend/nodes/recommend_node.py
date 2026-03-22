import json
import re
import os

from langchain_core.messages import HumanMessage, SystemMessage

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

Your response should consist of ONLY one valid JSON array. No markdown, no code fences, just the array."""

def extract_recommendations(raw_content: str) -> list:
    recommendations = []
    # Match balanced-ish JSON objects by finding { ... } blocks
    # that contain "title"
    pattern = r'\{[^{}]*"title"[^{}]*\}'
    matches = re.findall(pattern, raw_content, re.DOTALL)
    
    for match in matches:
        try:
            obj = json.loads(match)
            recommendations.append(obj)
        except json.JSONDecodeError:
            # Try minor repairs: trailing commas, unescaped quotes
            cleaned = match.rstrip().rstrip(',')
            try:
                obj = json.loads(cleaned)
                recommendations.append(obj)
            except json.JSONDecodeError:
                continue

    # Deduplicate by title
    seen = set()
    unique = []
    for rec in recommendations:
        title = rec.get("title", "")
        if title not in seen:
            seen.add(title)
            unique.append(rec)

    return unique[:5]

def recommend_node(state: dict) -> dict:
    llm = get_llm()

    # use search results from Open Library API
    if state.get("search_results"):
        search_data = json.dumps(state["search_results"], indent=2)
        search_context = (
            "Use the following search results as your primary source for recommendations. "
            "Pick the 5 best matches from these results:\n"
            f"{search_data}"
        )
    else:
        search_context = (
            "No search results are available. Use your own knowledge of books to recommend 5 books based on the conversation history."
        )

    # insert search results into context window
    prompt = RECOMMEND_SYSTEM_PROMPT.format(search_context=search_context)
    print(f"\nFinal Recommendation Prompt:\n{prompt}")

    # append system message
    messages = [SystemMessage(content=prompt)] + state["messages"]
    # serialized_messages = [
    #     {
    #         "role": "human" if isinstance(m, HumanMessage) else "ai",
    #         "content": m.content
    #     } for m in state["messages"]
    # ]
    # print(f"Final LLM message:\n{prompt}\n{serialized_messages}")

    # get LLM response
    response = llm.invoke(messages)
    content = response.content.strip()
    print(f"\nFinal LLM response:\n{content}")

    # parse the LLM response as a JSON
    try:
        # Extract JSON array from anywhere in the response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
        recommendations = json.loads(content)
    except json.JSONDecodeError:
        if os.getenv("LLM_PROVIDER") == 'ollama':
            recommendations = extract_recommendations(content)
        else:
            recommendations = [{"title": "Error", "recommendation": response.content}]

    return {
        "recommendations": recommendations,
        "phase": "done",
        "messages": []
    }