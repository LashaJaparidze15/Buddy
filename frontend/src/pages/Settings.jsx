import { useState, useEffect } from 'react';
import { Save, Check } from 'lucide-react';

const CITIES = [
  { name: 'Dublin', country: 'Ireland' },
  { name: 'London', country: 'UK' },
  { name: 'New York', country: 'USA' },
  { name: 'Paris', country: 'France' },
  { name: 'Tokyo', country: 'Japan' },
  { name: 'Sydney', country: 'Australia' },
];

export default function Settings() {
  const [settings, setSettings] = useState({
    location: 'London',
    units: 'metric',
    report_time: '06:00',
    review_time: '21:00',
  });
  
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('buddy_settings');
    if (stored) {
      setSettings(JSON.parse(stored));
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem('buddy_settings', JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
        <p className="text-gray-500 text-sm mt-1">Configure your preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* General Settings */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-5 py-4 border-b border-gray-200">
            <h2 className="font-medium text-gray-900">General</h2>
          </div>
          <div className="p-5 space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Location</label>
              <select
                value={settings.location}
                onChange={(e) => setSettings({ ...settings, location: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {CITIES.map((city) => (
                  <option key={city.name} value={city.name}>
                    {city.name}, {city.country}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-400 mt-1">Used for weather data</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Temperature Units</label>
              <select
                value={settings.units}
                onChange={(e) => setSettings({ ...settings, units: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="metric">Celsius (°C)</option>
                <option value="imperial">Fahrenheit (°F)</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Morning Report</label>
                <input
                  type="time"
                  value={settings.report_time}
                  onChange={(e) => setSettings({ ...settings, report_time: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Evening Review</label>
                <input
                  type="time"
                  value={settings.review_time}
                  onChange={(e) => setSettings({ ...settings, review_time: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <button
              onClick={handleSave}
              style={{ backgroundColor: '#2563eb', color: '#ffffff' }}
              className="flex items-center gap-2 px-4 py-2 rounded-md hover:opacity-90 transition-opacity text-sm font-medium"
            >
              {saved ? <Check size={16} /> : <Save size={16} />}
              {saved ? 'Saved' : 'Save Settings'}
            </button>
          </div>
        </div>

        {/* API Status */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-5 py-4 border-b border-gray-200">
            <h2 className="font-medium text-gray-900">API Status</h2>
          </div>
          <div className="p-5">
            <p className="text-sm text-gray-500 mb-4">
              API keys are configured in the server's .env file.
            </p>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">Weather API</span>
                <span className="text-xs font-medium text-green-600">Connected</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-100">
                <span className="text-sm text-gray-700">News API</span>
                <span className="text-xs font-medium text-green-600">Connected</span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-gray-700">Stocks API</span>
                <span className="text-xs font-medium text-green-600">Connected</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}