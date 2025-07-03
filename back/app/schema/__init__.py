from pydantic import BaseModel


class BaseOutput(BaseModel):
    status: int = 0
    info: str = "ok"
    data: BaseModel
