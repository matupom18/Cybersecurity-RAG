import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATASET_PATH: str = "dataset"
    VECTOR_DB_PATH: str = "chroma_db"
    
    # Model Configuration
    # Options: "ollama", "openrouter"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter" if os.getenv("OPENROUTER_API_KEY") else "ollama") 
    
    # OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "google/gemini-2.0-flash-lite-001"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "scb10x/llama3.1-typhoon2-8b-instruct:latest"

    class Config:
        env_file = ".env"

settings = Settings()
