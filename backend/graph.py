from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, START, END

from nodes.chat_node import chat_node
from nodes.search_node import search_node
from nodes.recommend_node import recommend_node

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

def should_continue_chatting(state: OmnibotState) -> str:
    last_message = state["messages"][-1]
    if "[READY_TO_SEARCH]" in last_message.content:
        return "search"
    return "chat_with_user"

def build_graph():
    graph = StateGraph(OmnibotState)

    graph.add_node("chat", chat_node)
    graph.add_node("search", search_node)
    graph.add_node("recommend", recommend_node)

    graph.add_edge(START, "chat")

    graph.add_conditional_edges(
        "chat",
        should_continue_chatting,
        {
            "search": "search",
            "chat_with_user": END, # pause / loop back to START
        }
    )

    # TODO: search conditional edges

    graph.add_edge("recommend", END)

    return graph.compile()