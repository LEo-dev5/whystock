// src/components/ChatOutput.jsx
function ChatOutput({ answer, isStreaming }) {
  if (!answer && !isStreaming) return null

  return (
    <div className="chat-output">
      <p>{answer}</p>
      {isStreaming && <span className="cursor">▋</span>}
    </div>
  )
}

export default ChatOutput