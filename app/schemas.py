from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List



class BloggerBase(BaseModel):
    platform: str
    external_id: str
    handle: str
    name: Optional[str] = None


class BloggerCreate(BloggerBase):
    pass


class BloggerRead(BloggerBase):
    id: int

    class Config:
        from_attributes = True


class PostRead(BaseModel):
    id: int
    blogger_id: int
    platform: str
    external_id: str
    published_at: datetime
    text: str
    links: List[str] = Field(default_factory=list)
    media: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class IntegrationRead(BaseModel):
    id: int
    brand: str
    is_ad: bool
    confidence: int
    promo_codes: List[str] = Field(default_factory=list)
    has_logo: bool
    has_ad_label: bool
    detected_at: datetime
    post: PostRead

    class Config:
        from_attributes = True

class BriefCheckRequest(BaseModel):
    transcript: str
    description: Optional[str] = ""
    duration_seconds: Optional[int] = None
    integration_start: Optional[int] = None
    integration_end: Optional[int] = None
    first_description_line: Optional[str] = None


class BriefCheckResponse(BaseModel):
    overall_status: str
    summary: str
    checks: Dict[str, Dict[str, Any]]
    recommended_edits: List[str]
    raw: Dict[str, Any]
    
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