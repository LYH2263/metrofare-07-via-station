from pydantic import BaseModel, field_validator


class QuoteRequest(BaseModel):
    start: str
    end: str
    via: str | None = None
    persist: bool = True

    @field_validator("via")
    @classmethod
    def _empty_via_is_none(cls, v):
        if v is not None and not v.strip():
            return None
        return v
