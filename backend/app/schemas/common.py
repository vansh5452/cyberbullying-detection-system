"""
Shared response envelopes used across every endpoint, per the project's
consistent API error/success format.
"""
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
