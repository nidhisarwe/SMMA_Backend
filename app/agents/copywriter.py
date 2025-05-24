# Backend/app/agents/copywriter.py - FIXED
from crewai import Agent, Task
from typing import Optional
from langchain_groq import ChatGroq
import os

class CopywriterAgent:
    def __init__(self, groq_llm: Optional[ChatGroq] = None):
        self.llm = groq_llm or self._create_groq_llm()
        
    def _create_groq_llm(self) -> ChatGroq:
        """Create Groq LLM instance with proper configuration"""
        try:
            return ChatGroq(
                temperature=0.7,
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model="llama3-8b-8192",  # FIXED: Use 'model' not 'model_name'
                max_retries=3,
                request_timeout=60
            )
        except Exception as e:
            print(f"Error initializing Groq LLM: {e}")
            raise
    
    def create_agent(self) -> Agent:
        """Create copywriter agent"""
        return Agent(
            role="Expert Social Media Copywriter",
            goal="Write compelling, engaging captions and strategic hashtags for social media posts",
            backstory="""You are a creative copywriter with expertise in social media marketing. 
            You know how to craft captions that hook readers, drive engagement, and convert followers into customers.
            You understand platform-specific best practices and current social media trends.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
    
    def create_caption_task(self, content_planning_task: Task) -> Task:
        """Create caption generation task"""
        return Task(
            description="""
Based on the content calendar provided, create engaging captions and strategic hashtags for each post.

For each post, provide:

**CAPTION REQUIREMENTS:**
- Hook: Start with an attention-grabbing first line
- Body: 2-3 sentences that provide value or tell a story
- Length: 150-300 characters (optimal for engagement)
- Include relevant emojis naturally (2-4 per caption)
- End with a clear, specific call-to-action
- Match the tone to the content type (professional for carousels, casual for stories, etc.)

**HASHTAG REQUIREMENTS:**
- Provide 8-12 relevant hashtags per post
- Mix of popular (#entrepreneurship), medium (#startuplife), and niche (#b2bsaas) hashtags
- Include branded hashtags if applicable
- Research-based tags that your target audience actually follows

**FORMAT FOR EACH POST:**
Post [NUMBER] - [TITLE]
Caption: [Your engaging caption with emojis]
Hashtags: #hashtag1 #hashtag2 #hashtag3 [etc.]
---

Ensure each caption is unique, platform-appropriate, and designed to maximize engagement.
            """,
            expected_output="Complete captions with strategic hashtags for all posts in the content calendar, formatted clearly with post numbers and titles",
            agent=self.create_agent(),
            context=[content_planning_task]
        )