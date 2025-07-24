from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the OmniRebuild backend!"})

if __name__ == '__main__':
    app.run(debug=True) 