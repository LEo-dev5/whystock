
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routers import stock, news, chat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="WhyStock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock.router)
app.include_router(news.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "WhyStock API is running"}