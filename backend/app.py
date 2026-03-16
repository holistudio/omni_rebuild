import uuid

from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from graph import build_graph, OmnibotState

app = Flask(__name__)
CORS(app)

# compile LangGraph at startup
omnibot_graph = build_graph()

# conversation storage, keys=session_id, vals=states
sessions: dict[str, OmnibotState] = {}

INTRO_SYSTEM_PROMPT = """You are Omnibot. Imagine you are a warm and welcoming librarian 
who works at the world's largest library and are eager to share your love and excitement 
about books of all genres. Introduce yourself briefly and ask an open-ended question
to kick off the conversation about their reading preferences.
Keep your overall message to 3 sentences MAX. Do not use any markdown formatting. 
Do not use em-dashes ('-'), use commas instead!"""

def get_or_create_session(session_id: str | None) -> tuple[str, OmnibotState]:
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]
    
    new_id = session_id or str(uuid.uuid4())

    state: OmnibotState = {
        "messages": [],
        "search_results": [],
        "recommendations": [],
        "search_attempts_tried": 0,
        "num_books_found": 0,
        "phase": "chatting",
    }
    sessions[new_id] = state
    return new_id, state

@app.route("/api/intro", methods=["POST"])
def intro():
    # data: { "session_id": "optional", "message": "user text" }
    data = request.get_json() 
    session_id = data.get("session_id") or str(uuid.uuid4())
    
    # create new session
    _ , state = get_or_create_session(session_id)

    # add system prompt to the "top" of the blank conversation history
    messages = [SystemMessage(content=INTRO_SYSTEM_PROMPT), HumanMessage(content="...")]

    # call the LLM with "intro" message
    from config import get_llm
    llm = get_llm() 
    response = llm.invoke(messages)

    # add response to state
    state["messages"].append(response)
    sessions[session_id] = state

    return jsonify({
        "session_id": session_id,
        "response": response.content
    })

@app.route("/api/chat", methods=["POST"])
def chat():

    # data: { "session_id": "optional", "message": "user text" }
    data = request.get_json() 
    user_message = data.get("message", "")

    # load session and state
    session_id, state = get_or_create_session(data.get("session_id"))
    
    # add user message
    state["messages"].append(HumanMessage(content=user_message))

    # call the LLM via running the graph with the entire state
    result = omnibot_graph.invoke(state)

    # update session state
    sessions[session_id] = result

    # extract last AIMessage
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    last_response = ai_messages[-1].content if ai_messages else ""

    # clean out the [READY_TO_SEARCH] marker from response display to user
    display_response = last_response.replace("[READY_TO_SEARCH]","").strip()

    # determine the current phase
    phase = result.get("phase", "chatting")
    
    # compose response
    recommendations_url = None

    # if the recommendations list is populated
    if result.get("recommendations"):
        phase = "done"
        recommendations_url = f"recommendations.html?session_id={session_id}"
        display_response = f'Great, <a href="{recommendations_url}">here</a> are my recommendations for you!'
    elif "[READY_TO_SEARCH]" in last_response:
        phase = "searching"
        display_response = "Great, I understand what you're into, let me look up some books..."
    
    # TODO: save JSON files

    print({
        "session_id": session_id,
        "last_response": last_response,
        "display_response": display_response,
        "phase": phase,
        "recommendations_url": recommendations_url,
    })
    return jsonify({
        "session_id": session_id,
        "response": display_response,
        "phase": phase,
        "recommendations_url": recommendations_url,
    })

@app.route("/api/recommendations/<session_id>", methods=["GET"])
def get_recommendations(session_id: str):
    # fetch saved recommendations in memory
    if session_id in sessions:
        return jsonify({
            "recommendations": sessions[session_id].get("recommendations", [])
        })
    return jsonify({"error": "Session not found"}), 404

if __name__ == "__main__":
    # enable Flask auto-reloader 
    # and error pages during development
    app.run(debug=True, port=5000)