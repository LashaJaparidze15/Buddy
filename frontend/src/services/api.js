import axios from 'axios';

const API_BASE = (import.meta.env.VITE_API_URL || 'https://web-production-6e4cd.up.railway.app') + '/api';
const api = axios.create({
  baseURL: API_BASE,
});

// Dashboard
export const getDashboard = (location) => api.get('/dashboard', { params: { location } });

// Activities
export const getActivities = (params) => api.get('/activities', { params });
export const getActivity = (id) => api.get(`/activities/${id}`);
export const createActivity = (data) => api.post('/activities', data);
export const updateActivity = (id, data) => api.put(`/activities/${id}`, data);
export const deleteActivity = (id) => api.delete(`/activities/${id}`);
export const toggleActivity = (id) => api.post(`/activities/${id}/toggle`);
export const markActivity = (id, data) => api.post(`/activities/${id}/mark`, data);
export const getActivityHistory = (id) => api.get(`/activities/${id}/history`);

// Weather
export const getWeather = (location) => api.get('/weather', { params: { location } });
export const getWeatherForecast = (location) => api.get('/weather/forecast', { params: { location } });

// News
export const getNews = (category = 'general') => api.get('/news', { params: { category } });
export const getNewsCategories = () => api.get('/news/categories');

// Stocks
export const getStocks = () => api.get('/stocks');
export const getMarketSummary = () => api.get('/stocks/market');

// Analytics
export const getAnalytics = () => api.get('/analytics');
export const compareWeeks = () => api.get('/analytics/compare');

export default api;
