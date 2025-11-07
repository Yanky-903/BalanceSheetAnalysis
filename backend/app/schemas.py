# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class LoginIn(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UploadResponse(BaseModel):
    company: str
    period: Optional[str]
    numeric_context: Dict[str, Optional[float]]

class LLMAnalysis(BaseModel):
    tldr: Optional[str]
    highlights: Optional[List[str]] = []
    risks: Optional[List[str]] = []
    actions: Optional[List[str]] = []
