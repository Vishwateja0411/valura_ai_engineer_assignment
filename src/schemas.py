from pydantic import BaseModel


class SafetyVerdict(BaseModel):
    blocked: bool
    category: str = "safe"
    message: str = ""
