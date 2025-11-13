"""
Configuration and API Client Initialization
Handles environment variables and API client setup
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tavily import TavilyClient

# Load environment variables
load_dotenv()


def initialize_clients():
    """Initialize Groq LLM and Tavily API clients"""
    groq_api_key = os.getenv("GROQ_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not groq_api_key or not tavily_api_key:
        return None, None, "Missing API keys"
    
    try:
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            groq_api_key=groq_api_key,
            temperature=0.3
        )
        
        tavily_client = TavilyClient(api_key=tavily_api_key)
        
        return llm, tavily_client, None
    except Exception as e:
        return None, None, str(e)


def get_api_keys():
    """Get API keys from environment"""
    return os.getenv("GROQ_API_KEY"), os.getenv("TAVILY_API_KEY")

