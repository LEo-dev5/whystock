import re
import chromadb
from chromadb.utils import embedding_functions
from sqlalchemy.orm import Session
from app.models.schema import NewsData

# 다국어 임베딩 모델 설정
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

# ChromaDB 클라이언트 초기화
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="news",
    embedding_function=sentence_transformer_ef
)

def clean_text(text: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\[\+\d+ chars\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def vectorize_news(db: Session, ticker_id: int):
    news_list = db.query(NewsData).filter(
        NewsData.ticker_id == ticker_id,
        NewsData.is_vectorized == False
    ).all()

    if not news_list:
        return

    for news in news_list:
        raw_text = f"{news.title}\n{news.content}"
        cleaned_text = clean_text(raw_text)

        if not cleaned_text:
            news.is_vectorized = True
            continue

        chunks = chunk_text(cleaned_text)
        chunk_ids = [f"{news.id}_{i}" for i in range(len(chunks))]

        existing = collection.get(ids=chunk_ids)
        existing_ids = set(existing["ids"])

        for i, chunk in enumerate(chunks):
            chunk_id = f"{news.id}_{i}"
            if chunk_id in existing_ids:
                continue

            collection.add(
                documents=[chunk],
                metadatas=[{
                    "ticker_id": str(news.ticker_id),
                    "news_id": str(news.id),
                    "url": news.url or "",
                    "published_at": str(news.published_at),
                    "chunk_index": str(i)
                }],
                ids=[chunk_id]
            )

        news.is_vectorized = True

    db.commit()

def search_related_news(ticker_id: int, query: str, n_results: int = 5) -> list:
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"ticker_id": str(ticker_id)}
    )

    if not results["documents"][0]:
        return []

    return results["documents"][0]