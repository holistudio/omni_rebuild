# 📚 omni_rebuild

An agent that makes book recommendations based on conversations with you about your nuanced preferences for stories. This is a rebuild of a [chatbot app](https://github.com/holistudio/project-omnibus) a friend and I made back before chatbots were cool, now with LLMs.

## 🛠️ Set Up

0. Prerequisites:
   - Claude API key OR Ollama/llama3.1
   - Node.js

    Create a `.env` file in `backend/`:

    ```env
    LLM_PROVIDER=anthropic
    ANTHROPIC_API_KEY=sk-ant-your-key-here

    # or

    LLM_PROVIDER=ollama
    OLLAMA_MODEL=llama3.1
    OLLAMA_BASE_URL=http://localhost:XXXX

    # Open Library API request header
    CONTACT_EMAIL=email@example.com
    ```

   Download *works, authors, ratings (txt.gz files)* [Open Library data dumps](https://openlibrary.org/developers/dumps) to `backend/data/dumps/` 

1. Start a virtual environment

    ```bash
    conda create -n omnibot python=3.12 -y
    conda activate omnibot
    ```

2. Install backend dependencies

    ```bash
    cd backend
    (uv) pip install -r requirements.txt
    ```
3. Create a local vector index of Open Library book summaries (in `backend/` directory)

    ```bash
    python scripts/process_dumps.py
    ```
    
    This will generate a `books_corpus.json` file in the `data` folder. To convert this corpus into a FAISS vector index, run:

    ```bash
    python indexer/build_index.py
    ```
    
    The FAISS index will then be saved to `data/vector_index/`.

4. Set up frontend

    ```bash
    cd frontend
    npm init -y
    npm install typescript esbuild --save-dev
    npx tsc --init
    ```

## 🧑‍💻 Usage

0. If using Ollama, make sure it is running in the background via `ollama serve` in separate terminal

1. Make sure you are in this directory (`omni_rebuild`) and activate the virtual environment in **two terminals**
   
   ```bash
   conda activate omnibot
   ```

2. Terminal 1: Start Flask server backend

    ```bash
    cd backend
    python app.py
    ```

   Flask starts on `http://localhost:5000`

3. Terminal 2: Start frontend

    ```bash
    cd frontend
    python -m http.server 3000
    ```

4. Open browser to `http://localhost:3000`
5. Start chatting with Omnibot!