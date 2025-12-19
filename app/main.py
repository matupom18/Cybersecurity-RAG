import uvicorn
from fastapi import FastAPI, HTTPException
from app.rag.loader import DocumentLoader
from app.rag.vectorstore import VectorDB
from app.rag.graph import app_graph
from app.rag.schemas import QueryRequest, QueryResponse, Citation

app = FastAPI(title="Cybersecurity RAG CLI")

@app.post("/ingest")
async def ingest_documents():
    try:
        loader = DocumentLoader()
        docs = loader.load_documents()
        vector_db = VectorDB()
        vector_db.add_documents(docs)
        
        return {"message": "Ingestion successful", "num_documents": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_db():
    try:
        vector_db = VectorDB()
        vector_db.clear()
        return {"message": "Embeddings reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    try:
        result = app_graph.invoke({"question": request.query})
        answer = result.get("answer", "No answer generated.")
        context = result.get("context", [])
        citations = []
        for doc in context:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page")
            citations.append(Citation(
                source=source, 
                page=page,
                text_snippet=doc.page_content[:100] + "..."
            ))
            
        unique_citations = {}
        for c in citations:
            key = f"{c.source}:{c.page}"
            unique_citations[key] = c
            
        return QueryResponse(answer=answer, citations=list(unique_citations.values()))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
