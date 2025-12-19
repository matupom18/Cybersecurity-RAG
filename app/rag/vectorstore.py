import os
from typing import List
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import settings

class VectorDB:
    def __init__(self):
        import chromadb
        self.persist_directory = settings.VECTOR_DB_PATH
        self.embedding_function = self._get_embedding_function()
        
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.vector_store = Chroma(
            client=self.client,
            collection_name="cyber_rag_docs_bge_m3",
            embedding_function=self.embedding_function,
        )

    def clear(self):
        try:
            self.client.delete_collection("cyber_rag_docs_bge_m3")
        except ValueError:
            pass 

    def _get_embedding_function(self):
        print("Using multilingual HuggingFace embeddings (BAAI/bge-m3)...")
        return HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3"
        )

    def add_documents(self, documents: List[Document]):
        if not documents:
            return
        # reset_collection removed to prevent errors
        pass

        self.vector_store.add_documents(documents)
        print("Documents added to vector store.")

    def as_retriever(self, k: int = 4):
        return self.vector_store.as_retriever(search_kwargs={"k": k})
