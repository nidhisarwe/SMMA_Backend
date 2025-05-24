# Backend/app/agents/designer.py - FIXED AND ENHANCED
from crewai import Agent, Task  # FIXED: Added Task import
from typing import Optional
from langchain_groq import ChatGroq
import os

class DesignerAgent:
    def __init__(self, groq_llm: Optional[ChatGroq] = None):
        self.llm = groq_llm or self._create_groq_llm()
    
    def _create_groq_llm(self) -> ChatGroq:
        """Create Groq LLM instance with proper configuration"""
        try:
            return ChatGroq(
                temperature=0.8,  # Higher creativity for design
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model="llama3-8b-8192",  # FIXED: Use 'model' not 'model_name'
                max_retries=3,
                request_timeout=60
            )
        except Exception as e:
            print(f"Error initializing Groq LLM: {e}")
            raise
    
    def create_agent(self) -> Agent:
        """Create designer agent"""
        return Agent(
            role="Expert Visual Content Designer",
            goal="Create detailed, professional AI image prompts for social media content that drive engagement",
            backstory="""You are a seasoned graphic designer and visual content strategist with 8+ years of experience. 
            You understand color theory, composition, typography, and how visual elements impact social media engagement.
            You excel at creating detailed prompts that generate stunning, on-brand visuals for different content types.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
    
    def create_design_task(self, content_planning_task: Task) -> Task:
        """Create visual design prompt generation task"""
        return Task(
            description="""
Based on the content calendar provided, create detailed AI image generation prompts for each post.

For each post, analyze the content type and create appropriate visual prompts:

**PROMPT REQUIREMENTS:**
- **Style**: Specify artistic style (modern, minimalist, corporate, playful, etc.)
- **Colors**: Define color palette that matches brand/theme
- **Composition**: Describe layout, focal points, and visual hierarchy  
- **Elements**: List specific visual elements needed (icons, text, people, objects)
- **Quality**: Include technical specifications (high-resolution, professional quality)
- **Platform**: Optimize dimensions and style for the target social platform

**CONTENT TYPE SPECIFIC GUIDELINES:**
- **Image Posts**: Single striking visual with clear focal point
- **Carousels**: Consistent design template across slides with slide-specific elements
- **Video/Reels**: Dynamic elements, motion-friendly design, attention-grabbing thumbnails
- **Stories**: Vertical format, bold text, interactive elements

**FORMAT FOR EACH POST:**
Post [NUMBER] - [TITLE]
Content Type: [Image Post/Carousel/Video/Story]
AI Prompt: [Detailed, specific prompt for image generation - 2-3 sentences minimum]
Design Notes: [Additional styling, branding, or technical requirements]
---

**EXAMPLE:**
Post 1 - Eco-Friendly Daily Swaps
Content Type: Carousel
AI Prompt: Create a modern, clean carousel design showing before/after comparisons of 5 eco-friendly swaps. Use a fresh green and white color scheme with subtle earth tones. Each slide should feature split-screen layout with wasteful item on left (faded/red tint) and eco-alternative on right (bright/green highlight). Include minimalist icons, sans-serif typography, and small environmental impact statistics in clean text boxes.
Design Notes: Maintain consistent template across all 5 slides, ensure text is readable on mobile, use sustainable/natural imagery style
---

Create detailed prompts for all posts that will result in professional, engaging visuals.
            """,
            expected_output="Detailed AI image generation prompts for each post in the content calendar, with specific design specifications and technical requirements",
            agent=self.create_agent(),
            context=[content_planning_task]
        )