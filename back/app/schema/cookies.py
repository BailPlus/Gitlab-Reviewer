from pydantic import BaseModel, Field


class CookiesSchema(BaseModel):
    """Cookie"""
    token: str = Field(description="gitlab token")
