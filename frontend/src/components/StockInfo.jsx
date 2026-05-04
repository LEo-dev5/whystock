// src/components/StockInfo.jsx
function StockInfo({ stockData }) {
  const { ticker, name, open, close, change_rate } = stockData
  const isPositive = change_rate >= 0

  return (
    <div className="stock-info">
      <div className="stock-header">
        <h2>{ticker}</h2>
        <span className="stock-name">{name}</span>
      </div>
      <div className="stock-prices">
        <div className="price-item">
          <span className="label">시가</span>
          <span className="value">${open}</span>
        </div>
        <div className="price-item">
          <span className="label">종가</span>
          <span className="value">${close}</span>
        </div>
        <div className="price-item">
          <span className="label">등락률</span>
          <span className={`change-rate ${isPositive ? 'positive' : 'negative'}`}>
            {isPositive ? '+' : ''}{change_rate}%
          </span>
        </div>
      </div>
    </div>
  )
}

export default StockInfo