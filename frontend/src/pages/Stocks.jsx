import { useState, useEffect } from 'react';
import { getStocks, getMarketSummary } from '../services/api';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function Stocks() {
  const [stocks, setStocks] = useState([]);
  const [market, setMarket] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stocksRes, marketRes] = await Promise.all([
          getStocks(),
          getMarketSummary(),
        ]);
        setStocks(stocksRes.data);
        setMarket(marketRes.data);
      } catch (err) {
        console.error('Failed to fetch stocks');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const getDirectionIcon = (direction) => {
    if (direction === '🟢') return <TrendingUp className="text-green-500" size={20} />;
    if (direction === '🔴') return <TrendingDown className="text-red-500" size={20} />;
    return <Minus className="text-gray-400" size={20} />;
  };

  const getChangeColor = (change) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading stocks...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Stocks</h1>

      {/* Market Summary */}
      {Object.keys(market).length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(market).map(([name, data]) => (
            <div key={name} className="bg-white p-5 rounded-xl shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600 font-medium">{name}</span>
                {getDirectionIcon(data.direction)}
              </div>
              <div className="text-2xl font-bold text-gray-800">
                ${data.price?.toFixed(2)}
              </div>
              <div className={`text-sm ${getChangeColor(data.change)}`}>
                {data.change >= 0 ? '+' : ''}{data.change?.toFixed(2)} ({data.change_percent?.toFixed(2)}%)
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Watchlist */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="p-5 border-b">
          <h2 className="font-semibold text-gray-700">Watchlist</h2>
        </div>
        
        {stocks.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No stock data available. Check your API key.
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-4 font-medium text-gray-600">Symbol</th>
                <th className="text-right p-4 font-medium text-gray-600">Price</th>
                <th className="text-right p-4 font-medium text-gray-600">Change</th>
                <th className="text-right p-4 font-medium text-gray-600">Change %</th>
                <th className="text-right p-4 font-medium text-gray-600">High</th>
                <th className="text-right p-4 font-medium text-gray-600">Low</th>
                <th className="text-right p-4 font-medium text-gray-600">Volume</th>
              </tr>
            </thead>
            <tbody>
              {stocks.map((stock) => (
                <tr key={stock.symbol} className="border-t hover:bg-gray-50">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      {getDirectionIcon(stock.direction)}
                      <span className="font-semibold text-gray-800">{stock.symbol}</span>
                    </div>
                  </td>
                  <td className="p-4 text-right font-medium">${stock.price?.toFixed(2)}</td>
                  <td className={`p-4 text-right ${getChangeColor(stock.change)}`}>
                    {stock.change >= 0 ? '+' : ''}{stock.change?.toFixed(2)}
                  </td>
                  <td className={`p-4 text-right ${getChangeColor(stock.change_percent)}`}>
                    {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent?.toFixed(2)}%
                  </td>
                  <td className="p-4 text-right text-gray-600">${stock.high?.toFixed(2)}</td>
                  <td className="p-4 text-right text-gray-600">${stock.low?.toFixed(2)}</td>
                  <td className="p-4 text-right text-gray-600">{stock.volume?.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}