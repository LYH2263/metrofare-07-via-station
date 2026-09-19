from fastapi import APIRouter, HTTPException

from app.engines.route_quote import QuoteError
from app.schemas.quote import QuoteRequest
from app.services.metro_service import MetroService

router = APIRouter(tags=["quote"])

_STATUS = {"same_station": 400, "via_not_found": 404}


@router.post("/quote")
def post_quote(body: QuoteRequest):
    try:
        with MetroService() as s:
            return s.quote(body.start, body.end, body.persist, body.via)
    except QuoteError as e:
        raise HTTPException(status_code=_STATUS[e.code], detail={"code": e.code, "message": str(e)})
