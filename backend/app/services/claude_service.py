import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def generate_answer_stream(ticker: str, query: str, related_news: list, company_name: str = "", earnings: str = "", chat_history: list = []):
    if related_news:
        news_context = "\n\n".join([
            f"뉴스 {i+1}:\n{news}"
            for i, news in enumerate(related_news)
        ])
    else:
        news_context = "관련 뉴스를 찾을 수 없습니다."

    system_prompt = f"""
당신은 주식 시장 분석 AI입니다.
아래 최신 뉴스와 실적 데이터를 참고해서 사용자의 질문에 답변해주세요.
뉴스에 주가 상승/하락의 직접적인 원인이 없더라도,
관련 뉴스 내용을 바탕으로 가능한 영향 요인을 분석해주세요.

[종목 정보]
티커: {ticker}
회사명: {company_name}

[최신 뉴스]
{news_context}

[실적 데이터]
{earnings if earnings else "실적 데이터를 찾을 수 없습니다."}

반드시 다음 규칙을 지켜주세요:
- 마크다운 문법 사용 금지 (**, #, *, - 등)
- 이모지 사용 금지
- 자연스러운 문장으로만 답변
- 뉴스 내용과 실적 데이터를 근거로 구체적으로 분석
- 각 문단 사이에 빈 줄을 넣어서 읽기 쉽게 작성
- 종목명을 잘못 인식하지 말 것: 이 종목은 반드시 {company_name} 입니다
- 제공된 뉴스 내용을 직접 인용하지 말고 반드시 자신의 말로 재해석해서 작성
"""

    # 이전 대화 히스토리를 messages 배열로 변환
    messages = []
    for msg in chat_history[-6:]:  # 최근 6개만 (3턴)
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # 현재 질문 추가
    messages.append({"role": "user", "content": query})

    with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=1000,
        system=system_prompt,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            yield text