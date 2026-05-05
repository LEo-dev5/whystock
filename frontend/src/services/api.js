import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

// 주가 데이터 가져오기
export const fetchStock = async (ticker) => {
    const response = await axios.get(`${BASE_URL}/stock/${ticker}`);
    return response.data;
};

// 뉴스 가져오기
export const fetchNews = async (ticker) => {
    const response = await axios.get(`${BASE_URL}/news/${ticker}`);
    return response.data;
};

// SSE 스트리밍 채팅
// src/services/api.js
export const streamChat = (ticker, query, onMessage, onDone) => {
    fetch(`${BASE_URL}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker, query })
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const read = () => {
            reader.read().then(({ done, value }) => {
                if (done) return;  // onDone 제거, 그냥 return만

                const text = decoder.decode(value);
                const lines = text.split('\n');

                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        const data = line.replace('data: ', '').trim();
                        if (data === '[DONE]') {
                            onDone();  // [DONE] 신호에서만 호출
                        } else if (data) {
                            onMessage(data);
                        }
                    }
                });
                read();
            });
        };
        read();
    });
};