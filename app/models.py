from bson import ObjectId
from datetime import datetime
from typing import List, Dict

class Draft:
    def __init__(self, caption: str, platform: str, image_url: str = None, prompt: str = None, _id: ObjectId = None):
        self._id = _id or ObjectId()
        self.caption = caption
        self.platform = platform
        self.image_url = image_url
        self.prompt = prompt

    def to_dict(self):
        return {
            "_id": str(self._id),
            "caption": self.caption,
            "platform": self.platform,
            "image_url": self.image_url,
            "prompt": self.prompt,
        }

class CampaignSchedule:
    def __init__(
        self,
        campaign_name: str,
        theme: str,
        posts: List[Dict],
        start_date: str,
        end_date: str,
        created_at: datetime = None,
        _id: ObjectId = None
    ):
        self._id = _id or ObjectId()
        self.campaign_name = campaign_name
        self.theme = theme
        self.posts = posts
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            "_id": str(self._id),
            "campaign_name": self.campaign_name,
            "theme": self.theme,
            "posts": self.posts,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "created_at": self.created_at.isoformat(),
        }