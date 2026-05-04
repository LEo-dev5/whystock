// src/App.jsx
import { useState } from 'react'
import SearchBar from './components/SearchBar'
import StockInfo from './components/StockInfo'
import ChatBox from './components/ChatBox'
import { fetchStock, fetchNews } from './services/api'

function App() {
  const [ticker, setTicker] = useState('')
  const [stockData, setStockData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (inputTicker) => {
    setLoading(true)
    setError(null)
    setStockData(null)

    try {
      // 주가 + 뉴스 동시 요청
      const [stock] = await Promise.all([
        fetchStock(inputTicker),
        fetchNews(inputTicker)
      ])
      setTicker(inputTicker)
      setStockData(stock)
    } catch (err) {
      setError('종목을 찾을 수 없어요. 티커를 확인해주세요.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <h1>WhyStock</h1>
      <SearchBar onSearch={handleSearch} loading={loading} />
      {error && <p className="error">{error}</p>}
      {stockData && (
        <>
          <StockInfo stockData={stockData} />
          <ChatBox ticker={ticker} />
        </>
      )}
    </div>
  )
}

export default App