# backend/app/routers/news.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.news_service import fetch_and_save_news
from app.services.stock_service import get_or_create_ticker

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/{ticker}")
def get_news(ticker: str, db: Session = Depends(get_db)):
    db_ticker = get_or_create_ticker(db, ticker.upper())
    news_list = fetch_and_save_news(db, ticker.upper(), db_ticker.id)
    
    return {
        "ticker": ticker.upper(),
        "count": len(news_list),
        "message": f"{len(news_list)}개 뉴스 저장 완료"
    }