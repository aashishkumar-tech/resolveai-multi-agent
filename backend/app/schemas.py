from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Customer query")
    customer_name: str | None = Field(
        default=None,
        description="Customer name (used to personalize the response)",
        min_length=1,
    )
    mobile_number: str | None = Field(
        default=None,
        description="Customer mobile number (used for personalization/verification messaging)",
        min_length=5,
    )


class ChatResponse(BaseModel):
    final_response: str
    trace_id: str | None = None
    duration_s: float | None = None
    customer_name: str | None = None
    mobile_number: str | None = None
