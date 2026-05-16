import finnhub
from sqlalchemy.orm import Session
from app.models.schema import NewsData
from app.core.config import settings
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time

finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)

def crawl_article_content(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

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

def fetch_and_save_news(db: Session, ticker: str, ticker_id: int, company_name: str = None) -> list:
    if not is_news_outdated(db, ticker_id):
        return []

    # Finnhub는 티커로 직접 뉴스 검색
    from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    to_date = datetime.now().strftime("%Y-%m-%d")

    # 일본 종목은 .T 제거 후 검색
    search_ticker = ticker.replace(".T", "")

    try:
        news_list = finnhub_client.company_news(search_ticker, _from=from_date, to=to_date)
    except Exception as e:
        print(f"Finnhub 뉴스 수집 실패: {e}")
        return []

    if not news_list:
        return []

    saved_news = []

    for article in news_list[:10]:  # 최대 10개
        existing = db.query(NewsData).filter(
            NewsData.url == article.get("url", "")
        ).first()

        if existing:
            continue

        # URL로 본문 직접 크롤링
        full_content = crawl_article_content(article.get("url", ""))
        content = full_content or article.get("summary") or ""

        published_at = datetime.fromtimestamp(article.get("datetime", 0))

        news = NewsData(
            ticker_id=ticker_id,
            title=article.get("headline") or "",
            content=content,
            url=article.get("url") or "",
            published_at=published_at,
            is_vectorized=False
        )
        db.add(news)
        saved_news.append(news)

    db.commit()
    return saved_news