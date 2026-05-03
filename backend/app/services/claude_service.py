# backend/app/services/claude_service.py
import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def generate_answer_stream(ticker: str, query: str, related_news: list):
    # 검색된 뉴스를 컨텍스트로 만들기
    if related_news:
        news_context = "\n\n".join([
            f"뉴스 {i+1}:\n{news}" 
            for i, news in enumerate(related_news)
        ])
    else:
        news_context = "관련 뉴스를 찾을 수 없습니다."

    prompt = f"""
당신은 주식 시장 분석 AI입니다.
아래 최신 뉴스를 참고해서 사용자의 질문에 답변해주세요.
뉴스에 없는 내용은 지어내지 마세요.

[종목]
{ticker}

[최신 뉴스]
{news_context}

[사용자 질문]
{query}
"""

    # SSE 스트리밍으로 답변 생성
    with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield text