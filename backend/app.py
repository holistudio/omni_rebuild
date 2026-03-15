from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import SystemMessage, HumanMessage

from config import get_llm
from graph import build_graph, OmniBotState

app = Flask(__name__)
CORS(app)

# compile LangGraph at startup
omnibot_graph = build_graph()

# conversation storage, keys=session_id, vals=states
sessions: dict[str, OmniBotState] = {}

INTRO_SYSTEM_PROMPT = """You are Omnibot. Imagine you are a warm and welcoming librarian 
who works at the world's largest library and are eager to share your love and excitement 
about books of all genres. Generate a warm, inviting opening message to greet a new user who has just
opened the chat. Introduce yourself briefly and ask an open-ended question
to kick off the conversation about their reading preferences.
Keep it to 2-3 sentences. Do not use any markdown formatting. 
Do not use em-dashes ('-'), use commas instead!"""

SYSTEM_PROMPT = """You are Omnibot. Imagine you are a warm and welcoming librarian 
who works at the world's largest library and are eager to share your love and excitement 
about books of all genres. But you also know that everyone has their own specific 
tastes in stories, writing style, and themes, so ask questions help you understand
the user's reading preferences and why. Once you feel like you understand the user's 
preferences, start probing their reading history with specific titles. Overall, 
chat with the user as if you two are sitting in a cafe: keep your responses concise, 
yet also warm and thoughtful. Keep it to 2-3 sentences. 
Most importantly, DO NOT ask more than one question per
response. Do not use em-dashes ('-'), use commas instead!"""

@app.route("/api/intro", methods=["POST"])
def intro():
    # data: { "session_id": "optional", "message": "user text" }
    data = request.get_json() 
    session_id = data.get("session_id", "default")
    sessions[session_id] = []

    # load conversation history
    history = sessions[session_id]
    history.append(HumanMessage(content="..."))

    # add system prompt to the "top" of the conversation history
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + history

    # call the LLM with "wrapped" message (System/Human/AIMessage)
    llm = get_llm() 
    response = llm.invoke(messages)

    # store LLM response (AIMessage) in history
    history.append(response)

    return jsonify({
        "session_id": session_id,
        "response": response.content
    })

@app.route("/api/chat", methods=["POST"])
def chat():

    # data: { "session_id": "optional", "message": "user text" }
    data = request.get_json() 
    session_id = data.get("session_id", "default")
    user_message = data.get("message", "")
    
    # create new conversation history if new session
    if session_id not in sessions:
        sessions[session_id] = []
    
    # load conversation history
    history = sessions[session_id]

    # add user message
    history.append(HumanMessage(user_message))

    # add system prompt to the "top" of the conversation history
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + history

    # call the LLM with "wrapped" message (System/Human/AIMessage)
    llm = get_llm() 
    response = llm.invoke(messages)

    # store LLM response (AIMessage) in history
    history.append(response)

    return jsonify({
        "session_id": session_id,
        "response": response.content
    })

if __name__ == "__main__":
    # enable Flask auto-reloader 
    # and error pages during development
    app.run(debug=True, port=5000)