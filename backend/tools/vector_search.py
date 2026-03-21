import os
import faiss # required by LlamaIndex

from llama_index.core import VectorStoreIndex, Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore

INDEX_DIR =  os.path.join("data", "vector_index")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# module level cache to load index only once
_index = None


def _load_index() -> VectorStoreIndex:
    print("Loading vector index...")
    # load the FAISS index if it hasn't been loaded yet in cache
    global _index
    if _index is not None:
        return _index
    
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
    Settings.llm = None
    vector_store = FaissVectorStore.from_persist_dir(INDEX_DIR)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=INDEX_DIR,
    )
    _index = load_index_from_storage(storage_context=storage_context)
    print("Vector index loaded.")
    return _index

def vector_search_books(query: str, top_k: int = 20) -> list[dict]:
    index = _load_index()
    docstore = index.storage_context.docstore # original documents
    
    retriever = index.as_retriever(similarity_top_k=top_k)

    # get back closest nodes based on L2 similarity with query vector
    results = retriever.retrieve(query)

    # convert nodes into book records
    books = []
    for node in results:
        metadata = node.metadata
        # get node's associated full document
        node_doc = docstore.get_document(node.node_id)

        # document full text format: "Title by Author. Summary: xyz. Subjects: ..."
        full_text = node_doc.text
        summary_start = full_text.find("Summary: ") + len("Summary: ")
        summary_end = full_text.rfind(" Subjects:")
        if summary_start < summary_end:
            summary = full_text[summary_start:summary_end] # "xyz."
        else:
            summary = full_text

        books.append({
            "title": metadata.get("title", "Unknown"),
            "author": metadata.get("author", "Unknown"),
            "year": metadata.get("year", "N/A"),
            "genre": metadata.get("genre", "General"),
            "summary": summary,
            "open_library_key": metadata.get("open_library_key", ""),
        })
    return books