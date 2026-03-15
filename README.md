# 📚 omni_rebuild

An agent that makes book recommendations based on conversations with you about your nuanced preferences for stories. This is a rebuild of a [chatbot app](https://github.com/holistudio/project-omnibus) a friend and I made back before chatbots were cool, now with LLMs.

## 🛠️ Set Up

0. Prerequisites:
   - Claude API key
   - Node.js

1. Start a virtual environment

    ```bash
    conda create -n omnibot python=3.12 -y
    conda activate omnibot
    ```

2. Install backend dependencies

    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3. Set up frontend

    ```bash
    cd frontend
    npm init -y
    npm install typescript esbuild --save-dev
    npx tsc --init
    ```

## 🧑‍💻 Usage

0. Make sure you are in this directory (`omni_rebuild`) and activate the virtual environment in **two terminals**
   
   ```bash
   conda activate omnibot
   ```

1. Terminal 1: Start Flask server backend

    ```bash
    cd backend
    python app.py
    ```

   Flask starts on `http://localhost:5000`

2. Terminal 2: Start frontend

    ```bash
    cd frontend
    npx esbuild --serve=localhost:3000 --servedir=.
    ```

3. Open browser to `http://localhost:3000`