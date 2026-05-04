// src/components/ChatOutput.jsx
import ReactMarkdown from 'react-markdown'

function ChatOutput({ answer, isStreaming }) {
  if (!answer && !isStreaming) return null

  return (
    <div className="chat-output">
      {isStreaming ? (
        <p>{answer}<span className="cursor">▋</span></p>
      ) : (
        <ReactMarkdown>{answer}</ReactMarkdown>
      )}
    </div>
  )
}

export default ChatOutput