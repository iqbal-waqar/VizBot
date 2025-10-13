from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: Optional[str] = None
