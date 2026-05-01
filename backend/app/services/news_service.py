from newsapi import NewsApiClient
from sqlalchemy.orm import Session
from app.models.schema import Ticker, NewsData
from app.core.config import settings
from datetime import datetime, timedelta

newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)

def fetch_and_save_news(db: Session, ticker: str, ticker_id: int) -> list:
    # 최근 7일 뉴스 수집
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
        # 이미 저장된 뉴스는 스킵
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