from langchain_core.messages import SystemMessage
from config import get_llm
from tools.vector_search import vector_search_books

RAG_SYSTEM_PROMPT = """Based on the conversation history below, construct a 
natural language description of what kind of book the user wants.

Return ONLY the description string, nothing else.
Be specific about themes, mood, style, and any authors or genres mentioned.
Examples:
- "dark atmospheric gothic fiction with unreliable narrators"
- "uplifting science fiction about first contact with aliens"
- "literary fiction exploring grief and family dynamics"

If previous searches haven't found enough books, try a DIFFERENT angle
based on other preferences mentioned in the conversation."""

def search_node(state: dict) -> dict:
    llm = get_llm()

    context = f"Previous search attempts: {state['search_attempts_tried']}\n"
    context += f"Number of books found so far: {state['num_books_found']}"
    rag_msg = SystemMessage(content=RAG_SYSTEM_PROMPT + "\n" + context)
    
    messages = [rag_msg] + state["messages"]

    query_response = llm.invoke(messages)
    query_text = query_response.content.strip().strip('"')
    print(f"\nLLM search query:\n{query_text}\n")

    # search FAISS Index for books
    print("\nSearching...")
    new_books = vector_search_books(query=query_text)
    print("...Done!")

    # TODO: supplement with Open Library Search API

    # only add new book titles
    existing_titles = {b["title"] for b in state["search_results"]}
    unique_new = [b for b in new_books if b["title"] not in existing_titles]
    all_results = state["search_results"] + unique_new
    print(f"\n Vector Search Results:\n{[(b["title"], b["author"]) for b in all_results]}")

    return {
        "search_results": all_results,
        "search_attempts_tried": state["search_attempts_tried"] + 1,
        "num_books_found": len(all_results),
        "messages": [],
    }