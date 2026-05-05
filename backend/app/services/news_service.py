# backend/app/services/news_service.py
from newsapi import NewsApiClient
from sqlalchemy.orm import Session
from app.models.schema import NewsData
from app.core.config import settings
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)

def crawl_article_content(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # 불필요한 태그 제거
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # 본문 추출 (p 태그 기준)
        paragraphs = soup.find_all("p")
        content = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

        return content[:3000] if content else ""
    except:
        return ""

def is_news_outdated(db: Session, ticker_id: int) -> bool:
    latest_news = db.query(NewsData).filter(
        NewsData.ticker_id == ticker_id
    ).order_by(NewsData.published_at.desc()).first()

    if not latest_news:
        return True

    now = datetime.utcnow()
    if latest_news.published_at is None:
        return True

    return (now - latest_news.published_at.replace(tzinfo=None)) > timedelta(hours=24)

def fetch_and_save_news(db: Session, ticker: str, ticker_id: int) -> list:
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

        # URL로 본문 직접 크롤링
        full_content = crawl_article_content(article["url"])

        # 크롤링 실패시 NewsAPI 본문으로 fallback
        content = full_content or article.get("content") or article.get("description") or ""

        news = NewsData(
            ticker_id=ticker_id,
            title=article["title"] or "",
            content=content,
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