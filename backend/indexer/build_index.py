import json
import os
import faiss

from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore

# assumes pwd = "./backend" NOT "./backend/indexer"
CORPUS_PATH = os.path.join("data", "books_corpus.json")
INDEX_DIR =  os.path.join("data", "vector_index")

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def build_documents(corpus: list[dict]) -> list[Document]:
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
    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
    Settings.embed_model = embed_model
    Settings.llm = None

    documents = build_documents(corpus) 

    # get embedding dimension of model
    EMBED_DIM = len(embed_model.get_text_embedding("hello"))

    # use L2 distance for index search
    faiss_index = faiss.IndexFlatL2(EMBED_DIM)
    
    # construct FAISS index
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents=documents,
        storage_context=storage_context,
        show_progress=True,
    )

    # save locally
    os.makedirs(INDEX_DIR, exist_ok=True)
    index.storage_context.persist(persist_dir=INDEX_DIR)