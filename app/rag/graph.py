from typing import List, Dict, Any, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.documents import Document

from app.config import settings
from app.rag.vectorstore import VectorDB

class GraphState(TypedDict):
    question: str
    context: List[Document]
    answer: str

vector_db = VectorDB()

def get_llm():
    if settings.LLM_PROVIDER == "openrouter" and settings.OPENROUTER_API_KEY:
        return ChatOpenAI(
            model=settings.OPENROUTER_MODEL,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            temperature=0.1
        )
    else:
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.1
        )

llm = get_llm()

system_prompt = """You are a Cybersecurity Assistant.
You must answer the user's question using ONLY the context provided below.
If the answer is not in the context, state that you do not have enough information in the provided dataset.
Do NOT use outside knowledge.
CITE YOUR SOURCES. For every statement, reference the source document name and page number.
Format citations in the text as [Source: filename, Page: page_number].

Context:
{context}
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{question}")
])

# Nodes
def retrieve(state: GraphState):
    question = state["question"]
    retriever = vector_db.as_retriever(k=5)
    docs = retriever.invoke(question)
    return {"context": docs}

def generate(state: GraphState):
    question = state["question"]
    context = state["context"]
    
    formatted_context = "\n\n".join([f"Source: {doc.metadata.get('source', 'Unknown')}, Page: {doc.metadata.get('page', 'Unknown')}\nContent: {doc.page_content}" for doc in context])
    
    chain = prompt_template | llm | StrOutputParser()
    response = chain.invoke({"context": formatted_context, "question": question})
    
    return {"answer": response}

workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app_graph = workflow.compile()
