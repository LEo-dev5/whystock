from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.stock_service import get_or_create_ticker, fetch_earnings
from app.services.news_service import fetch_and_save_news
from app.services.vector_service import vectorize_news, search_related_news
from app.services.claude_service import generate_answer_stream
from app.models.schema import ChatHistory
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    ticker: str
    query: str

@router.get("/history/{ticker}")
def get_history(ticker: str, db: Session = Depends(get_db)):
    db_ticker = db.query(__import__('app.models.schema', fromlist=['Ticker']).Ticker).filter_by(ticker=ticker.upper()).first()
    if not db_ticker:
        return []

    history = db.query(ChatHistory).filter(
        ChatHistory.ticker_id == db_ticker.id
    ).order_by(ChatHistory.created_at.asc()).all()

    return [{"role": h.role, "content": h.content, "created_at": str(h.created_at)} for h in history]

@router.post("/")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    ticker = request.ticker.upper()
    query = request.query

    # 1. 티커 확인/생성
    db_ticker = get_or_create_ticker(db, ticker)

    # 2. 뉴스 수집
    fetch_and_save_news(db, ticker, db_ticker.id, db_ticker.name)

    # 3. 벡터화
    vectorize_news(db, db_ticker.id)

    # 4. 관련 뉴스 검색
    related_news = search_related_news(db_ticker.id, query)

    # 5. 실적 데이터 수집
    earnings = fetch_earnings(ticker)

    # 6. 이전 대화 히스토리 가져오기
    history = db.query(ChatHistory).filter(
        ChatHistory.ticker_id == db_ticker.id
    ).order_by(ChatHistory.created_at.asc()).all()

    chat_history = [{"role": h.role, "content": h.content} for h in history]

    # 7. 사용자 질문 저장
    user_msg = ChatHistory(
        ticker_id=db_ticker.id,
        role="user",
        content=query
    )
    db.add(user_msg)
    db.commit()

    # 8. SSE 스트리밍 + 답변 저장
    answer_buffer = []

    def stream():
        for text in generate_answer_stream(ticker, query, related_news, db_ticker.name, earnings, chat_history):
            answer_buffer.append(text)
            yield f"data: {text}\n\n"

        full_answer = "".join(answer_buffer)
        assistant_msg = ChatHistory(
            ticker_id=db_ticker.id,
            role="assistant",
            content=full_answer
        )
        db.add(assistant_msg)
        db.commit()

        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")