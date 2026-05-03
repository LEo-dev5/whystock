from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.stock_service import get_or_create_ticker
from app.services.news_service import fetch_and_save_news
from app.services.vector_service import vectorize_news, search_related_news
from app.services.claude_service import generate_answer_stream
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    ticker: str
    query: str
@router.post("/")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    ticker = request.ticker.upper()
    query = request.query

    # 1. 티커 확인/생성
    db_ticker = get_or_create_ticker(db, ticker)

    # 2. 뉴스 수집
    fetch_and_save_news(db, ticker, db_ticker.id)

    # 3. 벡터화
    vectorize_news(db, db_ticker.id)

    # 4. 관련 뉴스 검색
    related_news = search_related_news(db_ticker.id, query)

    # 5. SSE 스트리밍 응답
    def stream():
        for text in generate_answer_stream(ticker, query, related_news):
            yield f"data: {text}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")