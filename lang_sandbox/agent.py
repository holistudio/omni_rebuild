import getpass
import os
import ast
import random

from langchain.chat_models import init_chat_model

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage, trim_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

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



# New State dictionary class
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
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
        self.workflow = StateGraph(state_schema=MessagesState)

        # Define the (single) node in the graph
        self.workflow.add_edge(START, "model")
        self.workflow.add_node("model", self.call_model)

        # Add memory
        memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=memory)

        self.config = {"configurable": {"thread_id": "abc123"}}
        
        self.q_count = 0

        self.sys_intro = "The user is open to suggestions for new books to read. For now, only ask the user one question for their name."

        self.sys_generic = "The user is open to suggestions for new books to read. Try to get to know who they are, their general interest in stories, and specific tastes in books. ALWAYS ask ONE and ONLY ONE question at a time."

        self.sys_specific = "The user is open to suggestions for new books to read. Try to understand their specific tastes in books. Ask them if they have read a specific book by a specific author. ALWAYS ask ONE and ONLY ONE question at a time."

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "The user is open to suggestions for new books to read. Try to get to know who they are, their general interest in stories, and specific tastes in books. ALWAYS ask ONE and ONLY ONE question at a time.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        pass

    # Define the function that calls the model
    def call_model(self, state: State):
        trimmed_messages = self.trimmer.invoke(state["messages"])
        prompt = self.prompt_template.invoke(
            {"messages": trimmed_messages}
        )
        response = self.model.invoke(prompt)
        return {"messages": [response]}
    
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
        if self.q_count > 0:
            if self.q_count < 7:
                sys_message = self.sys_generic
            else:
                flip = random.random()
                # print(flip)
                if flip > 0.5:
                    sys_message = self.sys_specific
                else:
                    sys_message = self.sys_generic
        else:
            sys_message = self.sys_intro
        self.set_sys_message(sys_message)

        input_messages = [HumanMessage(query)]
        output = self.app.invoke({"messages": input_messages}, self.config)
        response = output["messages"][-1].content
        # response_pretty = ast.literal_eval(response)
        # response_pretty = response.encode().decode('unicode_escape')
        self.q_count += 1
        return response, output["messages"]