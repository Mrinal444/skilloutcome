from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response envelope matching the documented contract."""
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None
