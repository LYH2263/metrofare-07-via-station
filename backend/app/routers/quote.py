from fastapi import APIRouter, HTTPException
from app.engines.route_quote import QuoteError
from app.schemas.quote import QuoteRequest
from app.services.metro_service import MetroService

router = APIRouter(tags=["quote"])


@router.post("/quote")
def post_quote(body: QuoteRequest):
    with MetroService() as s:
        try:
            return s.quote(body.start, body.end, body.persist, via=body.via or None)
        except QuoteError as e:
            raise HTTPException(status_code=400, detail={"code": e.code, "message": e.message})
