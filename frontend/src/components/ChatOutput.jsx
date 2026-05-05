// src/components/ChatOutput.jsx
import ReactMarkdown from 'react-markdown'

// src/components/ChatOutput.jsx
function ChatOutput({ answer, isStreaming }) {
  if (!answer && !isStreaming) return null

  const renderAnswer = (text) => {
    return text.split('\n').map((line, index) => (
      <p key={index} style={{marginBottom: '8px', fontSize: '0.95rem', lineHeight: '1.8'}}>
        {line}
      </p>
    ))
  }

  return (
    <div className="chat-output">
      {isStreaming ? (
        <p style={{fontSize: '0.95rem', lineHeight: '1.8'}}>
          {answer}
          <span className="cursor">▋</span>
        </p>
      ) : (
        renderAnswer(answer)
      )}
    </div>
  )
}

export default ChatOutput

