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
    뉴스에 주가 상승/하락의 직접적인 원인이 없더라도,
    관련 뉴스 내용을 바탕으로 가능한 영향 요인을 분석해주세요.

    [종목]
    {ticker}

    [최신 뉴스]
    {news_context}

    [사용자 질문]
    {query}

    반드시 다음 규칙을 지켜주세요:
    - 마크다운 문법 사용 금지 (**, #, *, - 등)
    - 이모지 사용 금지
    - 자연스러운 문장으로만 답변
    - 뉴스 내용을 근거로 구체적으로 분석
    - 각 문단 사이에 빈 줄을 넣어서 읽기 쉽게 작성
    """

    # SSE 스트리밍으로 답변 생성
    with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield text