from crewai import Agent
from langchain_groq import ChatGroq
import os

class DesignerAgent:
    def __init__(self, groq_llm: ChatGroq = None):
        self.llm = groq_llm or self._create_groq_llm()
    
    def _create_groq_llm(self) -> ChatGroq:
        return ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="groq/llama3-8b-8192"
        )
    
    def create_agent(self) -> Agent:
        return Agent(
            role="Graphic Designer",
            goal="Generate AI image prompts for social media",
            backstory="Expert in creating visual content prompts",
            llm=self.llm,
            verbose=True
        )