from crewai import Agent, Task
from typing import Dict
import os
from langchain_groq import ChatGroq


class ContentPlannerAgent:
    def __init__(self, groq_llm: ChatGroq = None):
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
        """Create content planner agent"""
        return Agent(
            role="Content Strategist",
            goal="Create engaging content calendars for social media campaigns with varied content types",
            backstory="An expert in social media strategy with years of experience planning viral content across different formats.",
            llm=self.llm,
            verbose=True
        )

    def create_planning_task(self, campaign_name: str, content_theme: str, num_content_pieces: int) -> Task:
        """Create content planning task"""
        return Task(
            description=(
                f"Create a detailed content calendar for '{campaign_name}' campaign.\n"
                f"Theme: {content_theme}\n"
                f"Number of posts: {num_content_pieces}\n\n"
                "Include a mix of content types:\n"
                "- Regular image posts\n"
                "- Carousel posts (2-5 slides)\n"
                "- Video/Reel ideas\n"
                "- Stories\n\n"
                "For each post, provide:\n"
                "1. What to Post (specific topic)\n"
                "2. Type of Post (Image, Carousel, Video/Reel, Story)\n"
                "3. Posting Schedule (ideal date/time)\n"
                "4. Detailed description (visual style, key points to highlight)\n"
                "5. Suggested Call-to-Action\n\n"
                "For Carousels, specify the theme and content of each slide.\n"
                "Format output as clear markdown with Post numbers."
            ),
            expected_output="A structured content calendar with various content types.",
            agent=self.create_agent(),
            output_file="output/content_calendar.md"
        )