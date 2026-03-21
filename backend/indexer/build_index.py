import json
import os

from llama_index.core import Document, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# assumes pwd = "./backend" NOT "./backend/indexer"
CORPUS_PATH = os.path.join("data", "books_corpus.json")
INDEX_DIR =  os.path.join("data", "vector_index")

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def build_document(corpus: list[dict]) -> list[Document]:
    documents = []
    for book in corpus:
        subjects_str = ", ".join(book.get("subjects",[]))
        text = f"{book["title"]} by {book["author"]}. Summary: {book.get("summary","")} Subjects: {subjects_str}"

        metadata = {
            "title": book["title"],
            "author": book["author"],
            "year": str(book.get("year", "N/A")),
            "genre": book.get("genre", "General"),
            "open_library_key": book.get("open_library_key", ""),
        }

        doc = Document(text=text, metadata=metadata)
        documents.append(doc)
    return documents

if __name__=="__main__":
    with open(CORPUS_PATH) as f:
        corpus = json.load(f)
    
    # set LlamaIndex global settings for embedding model and indexing
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
    Settings.llm = None