from pydantic import BaseModel


class CookiesSchema(BaseModel):
    """Cookie"""
    token: str
