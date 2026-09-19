from pydantic import BaseModel


class QuoteRequest(BaseModel):
    start: str
    end: str
    via: str | None = None
    persist: bool = True
