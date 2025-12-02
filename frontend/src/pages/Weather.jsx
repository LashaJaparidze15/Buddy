import { useState, useEffect } from 'react';
import { getWeather, getWeatherForecast } from '../services/api';
import { Cloud, Droplets, Wind, Thermometer, RefreshCw } from 'lucide-react';

// Convert Celsius to Fahrenheit
const toFahrenheit = (celsius) => Math.round((celsius * 9/5) + 32);

const getTemp = (celsius, units) => {
  if (units === 'imperial') {
    return toFahrenheit(celsius);
  }
  return Math.round(celsius);
};

const getTempUnit = (units) => units === 'imperial' ? '°F' : '°C';

// Load settings from localStorage
const loadSettings = () => {
  const stored = localStorage.getItem('buddy_settings');
  if (stored) {
    return JSON.parse(stored);
  }
  return { location: 'London', units: 'metric' };
};

export default function Weather() {
  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState(loadSettings);  // Load immediately

  const fetchData = async (location) => {
    setLoading(true);
    try {
      const [weatherRes, forecastRes] = await Promise.all([
        getWeather(location),
        getWeatherForecast(location),
      ]);
      setWeather(weatherRes.data);
      setForecast(forecastRes.data);
    } catch (err) {
      console.error('Failed to fetch weather');
    } finally {
      setLoading(false);
    }
  };

  // Fetch weather on mount and when location changes
  useEffect(() => {
    fetchData(settings.location);
  }, [settings.location]);

  const handleRefresh = () => {
    const newSettings = loadSettings();
    setSettings(newSettings);
    fetchData(newSettings.location);
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading weather...</div>;
  }

  if (!weather || weather.error) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 p-6 rounded-xl">
        <h2 className="font-semibold text-yellow-800">Weather Unavailable</h2>
        <p className="text-yellow-700">Check your API key in the .env file.</p>
      </div>
    );
  }

  const displayTemp = getTemp(weather.temperature, settings.units);
  const feelsLikeTemp = getTemp(weather.feels_like, settings.units);
  const tempUnit = getTempUnit(settings.units);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Weather</h1>
        <button
          onClick={handleRefresh}
          className="flex items-center gap-2 text-gray-500 hover:text-gray-700"
        >
          <RefreshCw size={18} />
          Refresh
        </button>
      </div>

      {/* Current Weather */}
      <div className="bg-gradient-to-br from-blue-500 to-cyan-600 text-white p-8 rounded-2xl">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-blue-100 mb-1">{weather.location}</p>
            <div className="text-6xl font-bold">
              {displayTemp}{tempUnit}
            </div>
            <p className="text-xl capitalize mt-2">{weather.description}</p>
          </div>
          <Cloud size={100} className="text-white/50" />
        </div>

        <div className="grid grid-cols-3 gap-4 mt-8 pt-6 border-t border-white/20">
          <div className="flex items-center gap-3">
            <Thermometer size={24} className="text-blue-200" />
            <div>
              <p className="text-blue-200 text-sm">Feels like</p>
              <p className="font-semibold">{feelsLikeTemp}{tempUnit}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Droplets size={24} className="text-blue-200" />
            <div>
              <p className="text-blue-200 text-sm">Humidity</p>
              <p className="font-semibold">{weather.humidity}%</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Wind size={24} className="text-blue-200" />
            <div>
              <p className="text-blue-200 text-sm">Wind</p>
              <p className="font-semibold">{weather.wind_speed} {weather.wind_unit}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Forecast */}
      {forecast.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h2 className="font-semibold text-gray-700 mb-4">24-Hour Forecast</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
            {forecast.map((item, i) => (
              <div key={i} className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">
                  {new Date(item.datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
                <p className="text-xl font-bold text-gray-800 my-2">
                  {getTemp(item.temperature, settings.units)}{tempUnit}
                </p>
                <p className="text-xs text-gray-500 capitalize">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}