# # backend/app/services/content_planner_engine.py
#
# from ..agents.content_planner import ContentPlannerAgent
# from crewai import Crew  # ✅ Import Crew
#
# def generate_content_plan(campaign_name: str, theme: str, count: int):
#     planner_agent = ContentPlannerAgent()
#     task = planner_agent.create_planning_task(campaign_name, theme, count)
#
#     # ✅ Wrap the agent and task in a Crew
#     crew = Crew(
#         agents=[task.agent],  # or [planner_agent.create_agent()]
#         tasks=[task],
#         verbose=True
#     )
#     result = crew.kickoff()
#
#     if isinstance(result, (list, dict)):
#         result = str(result)
#     print("CREW RESULT:", result)
#     return result
#
#     # result = crew.kickoff()
#
#     # return result


from ..agents.content_planner import ContentPlannerAgent
from crewai import Crew
from datetime import datetime, timedelta

# 🔧 Best recommended times for posting
RECOMMENDED_TIMES = ["10:00 AM", "12:00 PM", "3:00 PM", "6:00 PM"]

def generate_post_schedule(start_date_str: str, end_date_str: str, count: int):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    if start_date > end_date:
        raise ValueError("Start date must be before end date.")

    delta = (end_date - start_date).days + 1
    if count > delta:
        raise ValueError("Cannot generate more posts than available days.")

    step = max(1, delta // count)
    scheduled_dates = [start_date + timedelta(days=i * step) for i in range(count)]

    # Rotate through best times
    scheduled_datetime = [
        f"{dt.strftime('%B %d')} at {RECOMMENDED_TIMES[i % len(RECOMMENDED_TIMES)]}"
        for i, dt in enumerate(scheduled_dates)
    ]
    return scheduled_datetime


def generate_content_plan(campaign_name: str, theme: str, count: int, start_date: str, end_date: str):
    planner_agent = ContentPlannerAgent()
    post_schedule = generate_post_schedule(start_date, end_date, count)

    markdown_posts = []
    for i in range(count):
        markdown_posts.append(f"""
### Post {i+1}
1. **What to Post**: Content related to **{theme}** #{i+1}
2. **Type of Post**: (Agent will fill this)
3. **Posting Schedule**: {post_schedule[i]}
4. **Description**: (To be filled by strategist agent)
5. **Call-to-Action**: (To be filled by strategist agent)
""")

    full_description = (
        f"📅 Campaign: **{campaign_name}**\n"
        f"🗓 Duration: {start_date} to {end_date}\n\n"
        f"**Theme**: {theme}\n"
        f"**Total Posts**: {count}\n\n"
        f"Here is the post plan outline:\n\n" +
        "\n".join(markdown_posts)
    )

    task = planner_agent.create_planning_task(
        campaign_name=campaign_name,
        content_theme=theme,
        num_content_pieces=count
    )

    task.description = full_description + "\n\n" + task.description

    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()

    if isinstance(result, (list, dict)):
        result = str(result)

    raw_output = result
    dates = post_schedule

    return {
        "postCount": count,
        "raw": raw_output,
        "dates": dates,
        "name": campaign_name,  # Add this line
        "theme": theme,  # Add this line
        "startDate": start_date,  # Add this line
        "endDate": end_date  # Add this line
    }
