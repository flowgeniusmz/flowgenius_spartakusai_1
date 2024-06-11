import streamlit as st
from openai import OpenAI
from tavily import TavilyClient


class Tools:
    @staticmethod
    def internet_search(query: str):
        client = TavilyClient(api_key=st.secrets.tavily.api_key)
        response = client.search(query=query, search_depth="advanced", include_answer=True, include_raw_content=True, max_results=7)
        return response
    
    