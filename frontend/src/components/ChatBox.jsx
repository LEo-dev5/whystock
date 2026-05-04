// src/components/ChatBox.jsx
import { useState } from 'react'
import ChatInput from './ChatInput'
import ChatOutput from './ChatOutput'
import { streamChat } from '../services/api'

function ChatBox({ ticker }) {
  const [answer, setAnswer] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)

  const handleAsk = (query) => {
    setAnswer('')
    setIsStreaming(true)

    streamChat(
      ticker,
      query,
      (text) => setAnswer(prev => prev + text),
      () => setIsStreaming(false)
    )
  }

  return (
    <div className="chat-box">
      <h3>AI 분석</h3>
      <ChatInput onAsk={handleAsk} isStreaming={isStreaming} />
      <ChatOutput answer={answer} isStreaming={isStreaming} />
    </div>
  )
}

export default ChatBox