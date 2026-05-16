import { useState, useEffect } from 'react'
import ChatInput from './ChatInput'
import ChatOutput from './ChatOutput'
import { streamChat } from '../services/api'
import axios from 'axios'

function ChatBox({ ticker }) {
  const [answer, setAnswer] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [history, setHistory] = useState([])

  // 티커 바뀌면 히스토리 불러오기
  useEffect(() => {
    if (!ticker) return
    axios.get(`http://localhost:8000/chat/history/${ticker}`)
      .then(res => setHistory(res.data))
      .catch(err => console.error(err))
  }, [ticker])

  const handleAsk = (query) => {
    setAnswer('')
    setIsStreaming(true)

    streamChat(
      ticker,
      query,
      (text) => setAnswer(prev => prev + text),
      () => {
        setIsStreaming(false)
        // 스트리밍 완료 후 히스토리 다시 불러오기
        axios.get(`http://localhost:8000/chat/history/${ticker}`)
          .then(res => setHistory(res.data))
          .catch(err => console.error(err))
      }
    )
  }

  return (
    <div className="chat-box">
      <h3>AI 분석</h3>

      {/* 히스토리 표시 */}
      {history.length > 0 && (
        <div className="chat-history">
          {history.map((msg, index) => (
            <div key={index} className={`history-item ${msg.role}`}>
              <span className="role-label">{msg.role === 'user' ? '질문' : 'AI'}</span>
              <p>{msg.content}</p>
            </div>
          ))}
        </div>
      )}

      <ChatInput onAsk={handleAsk} isStreaming={isStreaming} />
      {isStreaming && (
        <ChatOutput answer={answer} isStreaming={isStreaming} />
      )}
    </div>
  )
}

export default ChatBox