from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: int
    name: str
    score: int
    progress: int
    trend: str
    avatar: str
    rank: int

    class Config:
        from_attributes = True

class LeaderboardResponse(BaseModel):
    data: List[User]
    totalCount: int
    page: int
    pageSize: int
    totalPages: int