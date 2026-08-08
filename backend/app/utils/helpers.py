"""
Small shared helpers: consistent error envelope builder + pagination math.
"""
from fastapi import HTTPException
from fastapi.responses import JSONResponse


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": {"code": code, "message": message}},
    )


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    """Raise-able version, carries the same structured payload via `detail`."""
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def paginate_params(page: int, limit: int) -> tuple:
    page = max(page, 1)
    limit = max(min(limit, 100), 1)
    offset = (page - 1) * limit
    return page, limit, offset
