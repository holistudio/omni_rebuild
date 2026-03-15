from typing import TypedDict, Annotated
import operator

class OmnibotState(TypedDict):
    # conversation history
    messages: Annotated[list, operator.add] # nodes can append new messages

    # books from Open Library API
    search_results: list[dict]

    # final 5 book recs with LLM explanations
    recommendations: list[dict]

    # track number of search query attempts to API
    search_queries_tried: int

    # books found from queries
    num_books_found: int

    # phase of agent in user story: "chat", "search", or "recommend"
    phase: str