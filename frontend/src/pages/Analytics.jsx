import { useState, useEffect } from 'react';
import { getAnalytics, compareWeeks } from '../services/api';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsRes, compareRes] = await Promise.all([
          getAnalytics(),
          compareWeeks(),
        ]);
        setAnalytics(analyticsRes.data);
        setComparison(compareRes.data);
      } catch (err) {
        console.error('Failed to fetch analytics');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading analytics...</div>;
  }

  if (!analytics || analytics.total === 0) {
    return (
      <div className="space-y-6">
        <div className="border-b border-gray-200 pb-4">
          <h1 className="text-2xl font-semibold text-gray-900">Analytics</h1>
          <p className="text-gray-500 text-sm mt-1">Track your progress and performance</p>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 p-6 rounded-lg">
          <p className="text-yellow-700">No activity data yet. Mark some activities as done or missed to see analytics.</p>
        </div>
      </div>
    );
  }

  const rate = analytics.completion_rate;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-semibold text-gray-900">Analytics</h1>
        <p className="text-gray-500 text-sm mt-1">
          Week of {analytics.week_start} to {analytics.week_end}
        </p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="col-span-2 lg:col-span-1 bg-white p-5 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-500 mb-1">Completion Rate</p>
          <div className="flex items-end gap-2">
            <span className="text-3xl font-semibold text-gray-900">{rate}%</span>
            {comparison && (
              <span className={`flex items-center text-sm mb-1 ${comparison.improved ? 'text-green-600' : 'text-red-600'}`}>
                {comparison.improved ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {Math.abs(comparison.change)}%
              </span>
            )}
          </div>
          <div className="mt-3 bg-gray-100 rounded-full h-1.5">
            <div 
              className={`h-1.5 rounded-full ${rate >= 70 ? 'bg-green-500' : rate >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
              style={{ width: `${rate}%` }}
            />
          </div>
        </div>

        <div className="bg-white p-5 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-500 mb-1">Completed</p>
          <p className="text-3xl font-semibold text-green-600">{analytics.done}</p>
        </div>

        <div className="bg-white p-5 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-500 mb-1">Missed</p>
          <p className="text-3xl font-semibold text-red-600">{analytics.missed}</p>
        </div>

        <div className="bg-white p-5 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-500 mb-1">Partial</p>
          <p className="text-3xl font-semibold text-yellow-600">{analytics.partial}</p>
        </div>

        <div className="bg-white p-5 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-500 mb-1">Rescheduled</p>
          <p className="text-3xl font-semibold text-gray-600">{analytics.rescheduled}</p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Category */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-5 py-4 border-b border-gray-200">
            <h2 className="font-medium text-gray-900">By Category</h2>
          </div>
          <div className="p-5">
            {Object.entries(analytics.by_category).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(analytics.by_category)
                  .sort((a, b) => b[1].rate - a[1].rate)
                  .map(([category, data]) => (
                    <div key={category}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-700">{category}</span>
                        <span className="text-gray-500">{data.rate}%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full">
                        <div 
                          className={`h-2 rounded-full ${
                            data.rate >= 70 ? 'bg-green-500' : data.rate >= 50 ? 'bg-yellow-500' : 'bg-red-400'
                          }`}
                          style={{ width: `${data.rate}%` }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            ) : (
              <p className="text-gray-400 text-sm">No category data</p>
            )}
          </div>
        </div>

        {/* By Day */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-5 py-4 border-b border-gray-200">
            <h2 className="font-medium text-gray-900">By Day</h2>
          </div>
          <div className="p-5">
            {Object.entries(analytics.by_day).length > 0 ? (
              <div className="space-y-4">
                {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                  .filter(day => analytics.by_day[day])
                  .map((day) => {
                    const data = analytics.by_day[day];
                    return (
                      <div key={day}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-700">{day}</span>
                          <span className="text-gray-500">{data.rate}%</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full">
                          <div 
                            className={`h-2 rounded-full ${
                              data.rate >= 70 ? 'bg-green-500' : data.rate >= 50 ? 'bg-yellow-500' : 'bg-red-400'
                            }`}
                            style={{ width: `${data.rate}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
              </div>
            ) : (
              <p className="text-gray-400 text-sm">No daily data</p>
            )}
          </div>
        </div>
      </div>

      {/* Streaks & Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Streaks */}
        {analytics.streaks && analytics.streaks.filter(s => s.streak > 0).length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-5 py-4 border-b border-gray-200">
              <h2 className="font-medium text-gray-900">Active Streaks</h2>
            </div>
            <div className="p-5">
              <div className="space-y-3">
                {analytics.streaks.filter(s => s.streak > 0).map((streak, i) => (
                  <div key={i} className="flex items-center justify-between py-2">
                    <span className="text-gray-700">{streak.title}</span>
                    <span className="text-sm font-medium text-orange-600">{streak.streak} days</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Insights */}
        {analytics.insights && analytics.insights.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-5 py-4 border-b border-gray-200">
              <h2 className="font-medium text-gray-900">Insights</h2>
            </div>
            <div className="p-5">
              <ul className="space-y-3">
                {analytics.insights.map((insight, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                    <span className="text-gray-400 mt-0.5">•</span>
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}