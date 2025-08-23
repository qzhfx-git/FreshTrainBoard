from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    score: int
    progress: int
    trend: str
    avatar: str
    rank: Optional[int] = None
    last_updated: Optional[datetime] = None

class LeaderboardResponse(BaseModel):
    data: List[User]
    totalCount: int
    page: int
    pageSize: int
    totalPages: int

class UserCreate(BaseModel):
    name: str
    score: int
    progress: int
    trend: str = "neutral"
    avatar: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    score: Optional[int] = None
    progress: Optional[int] = None
    trend: Optional[str] = None
    avatar: Optional[str] = None