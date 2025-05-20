from crewai import Agent, Task
from typing import Optional
from langchain_groq import ChatGroq
import os

class CopywriterAgent:
    def __init__(self, groq_llm: Optional[ChatGroq] = None):
        self.llm = groq_llm or self._create_groq_llm()
        
    def _create_groq_llm(self) -> ChatGroq:
        """Create Groq LLM instance with retries"""
        try:
            return ChatGroq(
                temperature=0,
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model_name="groq/llama3-8b-8192",
                max_retries=5
            )
        except Exception as e:
            print(f"Error initializing Groq LLM: {e}")
            raise
    
    def create_agent(self) -> Agent:
        """Create copywriter agent"""
        return Agent(
            role="Copywriter",
            goal="Write compelling captions and hashtags for social media posts",
            backstory="A creative writer specializing in high-conversion social media content.",
            llm=self.llm,
            verbose=True
        )
    
    def create_caption_task(self, content_planning_task: Task) -> Task:
        """Create caption generation task"""
        return Task(
            description=(
                "Create engaging captions and hashtags for each post in the content calendar.\n"
                "Each caption should:\n"
                "- Be 150-300 characters long\n"
                "- Start with a strong hook\n"
                "- Include relevant emojis\n"
                "- End with a clear CTA\n\n"
                "Hashtags should:\n"
                "- Include 8-12 relevant tags\n"
                "- Mix popular and niche hashtags\n"
                "- Be properly categorized\n\n"
                "Adapt your writing style for each content type (Image, Carousel, Video/Reel, Story)."
            ),
            expected_output="Complete captions and hashtag sets for all scheduled posts.",
            agent=self.create_agent(),
            context=[content_planning_task],
            output_file="output/captions_hashtags.md"
        )