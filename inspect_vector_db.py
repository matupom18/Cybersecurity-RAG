import chromadb
from app.config import settings
from langchain_chroma import Chroma
from app.rag.vectorstore import VectorDB

def inspect_chunks():
    print(f"Inspecting Vector DB at: {settings.VECTOR_DB_PATH}")
    
    # Initialize VectorDB to get the client and embedding function configuration correctly
    vdb = VectorDB()
    
    # Access the collection directly
    collection = vdb.client.get_collection("cyber_rag_docs")
    
    # Get all items
    count = collection.count()
    print(f"Total Chunks: {count}")
    
    if count == 0:
        print("Database is empty.")
        return

    # Retrieve a sample of items to show structure
    # getting first 10 items
    result = collection.get(limit=10, include=["documents", "metadatas"])
    
    ids = result["ids"]
    documents = result["documents"]
    metadatas = result["metadatas"]
    
    print("\n--- Sample Chunks (First 10) ---")
    for i in range(len(ids)):
        print(f"\nChunk ID: {ids[i]}")
        print(f"Source: {metadatas[i].get('source', 'Unknown')}")
        print(f"Metadata: {metadatas[i]}")
        print(f"Metadata: {metadatas[i]}")
        print(f"Content:\n{documents[i]}")
        print("-" * 50)

    # Calculate some stats about chunk sizes
    all_docs = collection.get(include=["documents"])["documents"]
    lengths = [len(d) for d in all_docs]
    avg_len = sum(lengths) / len(lengths)
    print(f"\n--- Statistics ---")
    print(f"Average Chunk Length: {avg_len:.2f} characters")
    print(f"Max Chunk Length: {max(lengths)} characters")
    print(f"Min Chunk Length: {min(lengths)} characters")

    # Export all to JSON
    print("\n--- Exporting All Data ---")
    all_data = collection.get(include=["documents", "metadatas"])
    
    export_data = []
    for i in range(len(all_data["ids"])):
        export_data.append({
            "id": all_data["ids"][i],
            "metadata": all_data["metadatas"][i],
            "content": all_data["documents"][i]
        })
    
    import json
    with open("vector_db_dump.json", "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"Exported {len(export_data)} chunks to 'vector_db_dump.json'")

if __name__ == "__main__":
    inspect_chunks()
