
from sqlalchemy import Column, Integer, String, Float, Date, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from app.core.database import Base

class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)

    price_data = relationship("PriceData", back_populates="ticker")
    news_data = relationship("NewsData", back_populates="ticker")

class PriceData(Base):
    __tablename__ = "price_data"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"))
    date = Column(Date, nullable=False)
    open = Column(Float)
    close = Column(Float)
    change_rate = Column(Float)

    ticker = relationship("Ticker", back_populates="price_data")

class NewsData(Base):
    __tablename__ = "news_data"

    id = Column(Integer, primary_key=True, index=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"))
    title = Column(Text, nullable=False)
    content = Column(Text)
    url = Column(Text)
    published_at = Column(TIMESTAMP)
    is_vectorized = Column(Boolean, default=False)

    ticker = relationship("Ticker", back_populates="news_data")