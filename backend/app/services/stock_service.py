# backend/app/services/stock_service.py
import yfinance as yf
from sqlalchemy.orm import Session
from app.models.schema import Ticker, PriceData
from datetime import date
from fastapi import HTTPException

def get_or_create_ticker(db: Session, ticker: str) -> Ticker:
    db_ticker = db.query(Ticker).filter(Ticker.ticker == ticker).first()

    if not db_ticker:
        stock = yf.Ticker(ticker)
        info = stock.info

        # 유효하지 않은 티커 체크
        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            raise HTTPException(status_code=404, detail=f"{ticker} 티커를 찾을 수 없습니다.")

        name = info.get("longName") or info.get("shortName") or ticker

        db_ticker = Ticker(ticker=ticker, name=name)
        db.add(db_ticker)
        db.commit()
        db.refresh(db_ticker)

    return db_ticker

def fetch_and_save_price(db: Session, ticker: str) -> dict:
    db_ticker = get_or_create_ticker(db, ticker)

    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")

    if hist.empty:
        raise HTTPException(status_code=404, detail=f"{ticker} 주가 데이터를 가져올 수 없습니다.")

    latest = hist.iloc[-1]
    open_price = round(float(latest["Open"]), 2)
    close_price = round(float(latest["Close"]), 2)
    change_rate = round((close_price - open_price) / open_price * 100, 2)

    price = PriceData(
        ticker_id=db_ticker.id,
        date=date.today(),
        open=open_price,
        close=close_price,
        change_rate=change_rate
    )
    db.add(price)
    db.commit()

    return {
        "ticker": ticker,
        "name": db_ticker.name,
        "open": open_price,
        "close": close_price,
        "change_rate": change_rate
    }

def fetch_earnings(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        earnings = stock.earnings_dates
        
        if earnings is None or earnings.empty:
            return ""
        
        # 최근 4분기만 가져오기
        recent = earnings.head(2)
        
        result = "최근 실적 데이터:\n"
        for date, row in recent.iterrows():
            date_str = date.strftime("%Y-%m-%d")
            eps_est = row.get("EPS Estimate", "N/A")
            surprise = row.get("Surprise(%)", "N/A")
            
            if surprise != "N/A" and not isinstance(surprise, str):
                surprise_str = f"{surprise:+.2f}%"
            else:
                surprise_str = "미발표"
                
            result += f"- {date_str}: EPS 예상 {eps_est}, 서프라이즈 {surprise_str}\n"
        
        return result
    except Exception as e:
        print(f"실적 데이터 수집 실패: {e}")
        return ""