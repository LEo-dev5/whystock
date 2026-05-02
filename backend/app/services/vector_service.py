# backend/app/services/vector_service.py
import chromadb
from sqlalchemy.orm import Session
from app.models.schema import NewsData

# ChromaDB 클라이언트 초기화
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="news")

def vectorize_news(db: Session, ticker_id: int):
    # is_vectorized=False 인 뉴스만 가져와서 벡터화
    news_list = db.query(NewsData).filter(
        NewsData.ticker_id == ticker_id,
        NewsData.is_vectorized == False
    ).all()

    if not news_list:
        return

    for news in news_list:
        content = f"{news.title}\n{news.content}"

        collection.add(
            documents=[content],
            metadatas=[{
                "ticker_id": str(news.ticker_id),
                "url": news.url or "",
                "published_at": str(news.published_at)
            }],
            ids=[str(news.id)]
        )

        news.is_vectorized = True

    db.commit()

def search_related_news(ticker_id: int, query: str, n_results: int = 5) -> list:
    # 질문과 관련된 뉴스 검색
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"ticker_id": str(ticker_id)}
    )

    if not results["documents"][0]:
        return []

    return results["documents"][0]