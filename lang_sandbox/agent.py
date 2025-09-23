import getpass
import os
import ast
import random
import json

import requests

from langchain.chat_models import init_chat_model

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage, trim_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph, END

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from typing import Sequence

from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict


try:
    # load environment variables from .env file (requires `python-dotenv`)
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=os.path.join('..','backend','.env'))
except ImportError:
    pass

# os.environ["LANGSMITH_TRACING"] = "true"
os.getenv("LANGSMITH_TRACING")

if not os.getenv("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = getpass.getpass(
        prompt="Enter your LangSmith API key (optional): "
    )
if not os.getenv("LANGSMITH_PROJECT"):
    os.environ["LANGSMITH_PROJECT"] = getpass.getpass(
        prompt='Enter your LangSmith Project Name (default = "default"): '
    )
    if not os.environ.get("LANGSMITH_PROJECT"):
        os.environ["LANGSMITH_PROJECT"] = "default"

if not os.getenv("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

if not os.getenv("GOOGLE_BOOKS_API_KEY"):
  os.environ["GOOGLE_BOOKS_API_KEY"] = getpass.getpass("Enter API key for Google Books: ")



# New State dictionary class
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    search_query: str
    language: str

class ChatAgent(object):
    def __init__(self):
        self.model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

        # Message trimmer
        self.trimmer = trim_messages(
            max_tokens=1500,
            strategy="last",
            token_counter=self.model,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )

        # Define a new graph
        # self.workflow = StateGraph(state_schema=MessagesState)
        self.workflow = StateGraph(State)

        # Define the (single) node in the graph
        self.workflow.add_edge(START, "chat_node")
        self.workflow.add_node("chat_node", self.call_chatbot)
        self.workflow.add_node("search_node", self.make_search_query)
        self.workflow.add_node("rec_node", self.rec_books)


        self.workflow.add_edge("chat_node","search_node")
        self.workflow.add_edge("search_node", "rec_node")
        self.workflow.add_edge("rec_node", END)

        # Add memory
        memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=memory)

        self.config = {"configurable": {"thread_id": "abc123"}}
        
        self.q_count = 0

        self.sys_intro = "The user is open to suggestions for new books to read. For now, only ask the user one question for their name."

        self.sys_generic = "Imagine you are a librarian in the world's biggest library and love to read all kinds of books. The user is open to suggestions for new books to read. Try to get to know who they are, their general interest in stories, and specific tastes in books. Ask natural flowing questions that invite them to describe their interests at great length. ALWAYS ask ONE and ONLY ONE question at a time. Avoid sounding robotic."

        self.sys_specific = "The user is open to suggestions for new books to read. Try to understand their specific tastes in books. Ask them if they have read a specific book by a specific author. ALWAYS ask ONE and ONLY ONE question at a time."
        
        self.sys_end = "Based on the previous conversation, summarize the user's taste for books in a long-form paragraph back to the user and see if there's anything misunderstood. Avoid using bullet points and references to titles, authors, or genres. Focus on the essence of their interests."

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "The user is open to suggestions for new books to read. Try to get to know who they are, their general interest in stories, and specific tastes in books. ALWAYS ask ONE and ONLY ONE question at a time.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        self.query_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system", 
                    "You are a query generator. Given the conversation history with the user, produce a concise search query for the Google Books search engine API to find the books that the user will most likely want to read. Conversation: {chat_history}"
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        self.rec_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system", 
                    "You are a bibliophile and librarian who wants everyone to enjoy reading books. Given the conversation history with the user, generate a list of book titles and authors that the user will most likely want to read. Conversation: {chat_history}"
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        pass

    # Define the function that calls the model
    def call_chatbot(self, state: State):
        # print("# call_chatbot()")
        trimmed_messages = self.trimmer.invoke(state["messages"])
        prompt = self.prompt_template.invoke(
            {"messages": trimmed_messages}
        )
        response = self.model.invoke(prompt)
        # return {"messages": [response]}
        state["messages"].append(AIMessage(content=response.content))
        return state
    
    def set_sys_message(self, message):
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    message,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        return self.prompt_template

    def respond(self, query):
        # print("# respond()")
        # depending on how many human query messages have been made
        # set the system message to tweak out the chatbot responds
        if self.q_count > 0:
            if self.q_count < 7:
                sys_message = self.sys_generic
            else:
                if self.q_count < 10:
                    flip = random.random()
                    # print(flip)
                    if flip > 0.5:
                        sys_message = self.sys_specific
                    else:
                        sys_message = self.sys_generic
                else:
                    sys_message = self.sys_end
        else:
            sys_message = self.sys_intro

        # set the system message in prompt_template
        self.set_sys_message(sys_message)

        # wrap the human query in a HumanMessage
        input_messages = [HumanMessage(query)]

        # invoke the app with the HumanMessage
        output = self.app.invoke({"messages": input_messages}, self.config)

        # print(output.keys())

        # get back the chatbot response
        response = output["messages"][-1].content
        # response_pretty = ast.literal_eval(response)
        # response_pretty = response.encode().decode('unicode_escape')

        print(self.q_count)
        # if the chatbot has asked 10 questions, write latest search query to Google Books
        if self.q_count > 10:
            with open('search_prompt.txt', 'w', encoding='utf-8') as pf:
                pf.write(output["search_query"])
            # override response with the rec_node
            response = output["book_recs"]
            # self.search_books()
        # increment query counter
        self.q_count += 1
        return response, output["messages"], output["search_query"]
    
    def make_search_query(self, state: State):
        # print("# make_search_query()")
        trimmed_messages = self.trimmer.invoke(state["messages"])
        # get conversation history
        chat_history = "\n".join(
            f"{m.type.capitalize()}: {m.content}" for m in trimmed_messages
        )
        prompt = self.query_prompt.invoke(
            {"chat_history": chat_history,
             "messages": [HumanMessage(
                 """
                 What: Based on the entire conversation so far, generate search terms for the Google Books search engine to find the books that I will most likely want to read.
                 Bounds:
                  - Do NOT use search operators (e.g., '-' or exact phrase quotes "")
                  - Keep the list of search terms within 10 keywords
                  - Focus on what I want rather than what I might not like.
                 Success:
                  - Finding at least 10 books I might like with your generated search terms.
                 """
             )]}
        )
        # print(prompt)
        response = self.model.invoke(prompt)
        # print(response)
        state["search_query"] = response.content
        # return {"search_query": [response.content]}
        return state
    
    def rec_books(self, state: State):
        # print("# make_search_query()")
        trimmed_messages = self.trimmer.invoke(state["messages"])
        # get conversation history
        chat_history = "\n".join(
            f"{m.type.capitalize()}: {m.content}" for m in trimmed_messages
        )
        prompt = self.rec_prompt.invoke(
            {"chat_history": chat_history,
             "messages": [HumanMessage(
                 """
                 What: Based on the entire conversation, recommend me 12 books in the format `{"title": "string1", "author": "string2"}`
                 Bounds:
                  - Stick to books that you are confident exist in the real world (classic novels, modern best sellers)
                 Success:
                  - Finding at least 12 books I might like with your generated search terms.
                 """
             )]}
        )
        # print(prompt)
        response = self.model.invoke(prompt)
        # print(response)
        state["book_recs"] = response.content
        # return {"search_query": [response.content]}
        return state
    
    def search_books(self):
        # read search query from text file
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(backend_dir, 'search_prompt.txt')
        if not os.path.exists(prompt_path):
            return {'error': 'search_prompt.txt not found'}, 404
        with open(prompt_path, 'r', encoding='utf-8') as f:
            query = f.read().strip()
            query = query.replace('"','')

        # post request to the Google Books API
        if not query:
            return {'error': 'Empty search prompt'}, 400
        if not os.environ["GOOGLE_BOOKS_API_KEY"]:
            return {'error': 'Google Books API key not set'}, 500
        url = 'https://www.googleapis.com/books/v1/volumes'
        params = {
            'q': query,
            'key': os.environ["GOOGLE_BOOKS_API_KEY"],
            'maxResults': 12
        }

        try:
            print(f"[Google Books API] GET {url}")
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            books = []
            for item in data.get('items', []):
                volume = item.get('volumeInfo', {})
                books.append({
                    'title': volume.get('title'),
                    'authors': volume.get('authors'),
                    'description': volume.get('description'),
                    'thumbnail': volume.get('imageLinks', {}).get('thumbnail'),
                    'infoLink': volume.get('infoLink')
                })
            
            # get back a list of book titles, author, description
            # Print the first book result for debugging
            if books:
                print(f"[Google Books API] First result: {books[0]}")
            else:
                print("[Google Books API] No results found.")
            # Write results to search_results.json
            results_path = os.path.join(backend_dir, 'search_results.json')
            with open(results_path, 'w', encoding='utf-8') as rf:
                json.dump(books, rf, ensure_ascii=False, indent=2)

            # TODO: add an explanation for each book
            return {'books': books}
        except Exception as e:
            print(f"[Google Books API] ERROR: {e}")
            return {'error': str(e)}, 500