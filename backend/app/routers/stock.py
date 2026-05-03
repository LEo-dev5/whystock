# backend/app/routers/stock.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.stock_service import fetch_and_save_price

router = APIRouter(prefix="/stock", tags=["stock"])

@router.get("/{ticker}")
def get_stock(ticker: str, db: Session = Depends(get_db)):
    return fetch_and_save_price(db, ticker.upper())