from typing import Optional, List, Any, Dict
from pydantic import BaseModel
from datetime import datetime

class BloggerCreate(BaseModel):
    platform: str
    external_id: str
    handle: Optional[str] = None
    name: Optional[str] = None

class BloggerOut(BaseModel):
    id: int
    platform: str
    external_id: str
    handle: Optional[str]
    name: Optional[str]
    class Config:
        from_attributes = True

class PostOut(BaseModel):
    id: int
    blogger_id: int
    platform: str
    external_id: str
    text: str
    published_at: Optional[datetime]
    class Config:
        from_attributes = True

class KupikodIntegrationOut(BaseModel):
    id: int
    post: PostOut
    is_ad: bool
    confidence: float
    promo_codes: List[str]
    detected_at: Optional[datetime]
    class Config:
        from_attributes = True

class LinkCheckRequest(BaseModel):
    url: str
    transcript: Optional[str] = ""
    description: Optional[str] = ""
    duration_seconds: Optional[int] = None
    integration_start: Optional[int] = None
    integration_end: Optional[int] = None
    first_description_line: Optional[str] = None

class LinkCheckResponse(BaseModel):
    platform: Optional[str] = None
    external_id: Optional[str] = None
    has_kupikod_integration: bool
    brief: Optional[Dict[str, Any]] = None

class PostRead(BaseModel):
    id: int
    blogger_id: int
    platform: str
    external_id: str
    text: str
    published_at: Optional[datetime]

    class Config:
        from_attributes = True