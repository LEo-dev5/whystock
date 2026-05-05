# backend/app/services/news_service.py
from newsapi import NewsApiClient
from sqlalchemy.orm import Session
from app.models.schema import Ticker, NewsData
from app.core.config import settings
from datetime import datetime, timedelta

newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)

def is_news_outdated(db: Session, ticker_id: int) -> bool:
    # 가장 최근 뉴스 수집 시간 확인
    latest_news = db.query(NewsData).filter(
        NewsData.ticker_id == ticker_id
    ).order_by(NewsData.published_at.desc()).first()

    if not latest_news:
        return True  # 뉴스 없으면 수집 필요

    # 24시간 지났으면 갱신 필요
    now = datetime.utcnow()
    if latest_news.published_at is None:
        return True

    return (now - latest_news.published_at.replace(tzinfo=None)) > timedelta(hours=24)

def fetch_and_save_news(db: Session, ticker: str, ticker_id: int) -> list:
    # 24시간 이내 뉴스 있으면 스킵
    if not is_news_outdated(db, ticker_id):
        return []

    from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    response = newsapi.get_everything(
        q=ticker,
        from_param=from_date,
        language="en",
        sort_by="publishedAt",
        page_size=10
    )

    if response["status"] != "ok":
        return []

    saved_news = []

    for article in response["articles"]:
        existing = db.query(NewsData).filter(
            NewsData.url == article["url"]
        ).first()

        if existing:
            continue

        news = NewsData(
            ticker_id=ticker_id,
            title=article["title"] or "",
            content=article["content"] or article["description"] or "",
            url=article["url"],
            published_at=datetime.strptime(
                article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
            ),
            is_vectorized=False
        )
        db.add(news)
        saved_news.append(news)

    db.commit()
    return saved_news