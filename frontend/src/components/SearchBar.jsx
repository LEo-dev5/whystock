// src/components/SearchBar.jsx
import { useState } from 'react'

function SearchBar({ onSearch, loading }) {
  const [input, setInput] = useState('')

  const handleSubmit = () => {
    if (!input.trim()) return
    onSearch(input.toUpperCase())
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSubmit()
  }

  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="티커 입력 (예: TSLA, MHI)"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={loading}
      />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? '검색 중...' : '검색'}
      </button>
    </div>
  )
}

export default SearchBar