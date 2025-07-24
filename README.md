# omni_rebuild

a rebuild of project-omnibus using LangChain and RAG

## Getting Started

### Backend (Flask)
1. Navigate to `omni_rebuild/backend`.
2. Create a virtual environment and activate it:
   ```
   python -m venv omni-test
   source venv/bin/activate  # On Windows: omni-test\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the Flask server:
   ```
   flask run
   ```

### Frontend (Vue.js)
1. Navigate to `omni_rebuild/frontend`.
2. Install dependencies:
   ```
   npm install
   ```
3. Run the development server:
   ```
   npm run dev
   ```

The frontend will be available at `http://localhost:5173` (default Vite port), and the backend at `http://localhost:5000`.
