// src/components/ChatInput.jsx
import { useState } from 'react'

function ChatInput({ onAsk, isStreaming }) {
  const [query, setQuery] = useState('')

  const handleSubmit = () => {
    if (!query.trim() || isStreaming) return
    onAsk(query)
    setQuery('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSubmit()
  }

  return (
    <div className="chat-input">
      <input
        type="text"
        placeholder="예: 왜 올랐어? 왜 떨어졌어?"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isStreaming}
      />
      <button onClick={handleSubmit} disabled={isStreaming}>
        {isStreaming ? '분석 중...' : '질문'}
      </button>
    </div>
  )
}

export default ChatInput