import { useState, useEffect } from 'react';
import { getActivities, createActivity, deleteActivity, toggleActivity } from '../services/api';
import { Plus, Trash2, Power, X } from 'lucide-react';

const CATEGORIES = ['Work', 'Personal', 'Health', 'Education', 'Errands', 'Social', 'Finance', 'Other'];
const RECURRENCE = ['once', 'daily', 'weekdays', 'weekends', 'weekly'];

export default function Activities() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [filter, setFilter] = useState('today');
  
  const [form, setForm] = useState({
    title: '',
    start_time: '09:00',
    category: 'Other',
    duration: '',
    recurrence: 'once',
    location: '',
    description: '',
    is_outdoor: false,
  });

  const fetchActivities = async () => {
    try {
      const params = {};
      if (filter === 'week') params.week = true;
      if (filter === 'all') params.all = true;
      
      const response = await getActivities(params);
      setActivities(response.data);
    } catch (err) {
      console.error('Failed to fetch activities');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();
  }, [filter]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createActivity({
        ...form,
        duration: form.duration ? parseInt(form.duration) : null,
      });
      setShowModal(false);
      setForm({
        title: '',
        start_time: '09:00',
        category: 'Other',
        duration: '',
        recurrence: 'once',
        location: '',
        description: '',
        is_outdoor: false,
      });
      fetchActivities();
    } catch (err) {
      console.error('Failed to create activity');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this activity?')) return;
    try {
      await deleteActivity(id);
      fetchActivities();
    } catch (err) {
      console.error('Failed to delete activity');
    }
  };

  const handleToggle = async (id) => {
    try {
      await toggleActivity(id);
      fetchActivities();
    } catch (err) {
      console.error('Failed to toggle activity');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Activities</h1>
        <button
          onClick={() => setShowModal(true)}
          style={{ backgroundColor: '#2563eb', color: '#ffffff' }}
          className="flex items-center gap-2 px-5 py-3 rounded-lg hover:opacity-90 transition-opacity shadow-lg font-semibold"
        >
          <Plus size={20} />
          Add Activity
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {['today', 'week', 'all'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={filter === f ? { backgroundColor: '#1e40af', color: '#ffffff' } : { backgroundColor: '#ffffff', color: '#374151' }}
            className="px-4 py-2 rounded-lg capitalize transition-colors font-medium shadow-sm border border-gray-200"
          >
            {f}
          </button>
        ))}
      </div>

      {/* Activities Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : activities.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No activities found. Add one to get started!
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-4 font-medium text-gray-600">Time</th>
                <th className="text-left p-4 font-medium text-gray-600">Title</th>
                <th className="text-left p-4 font-medium text-gray-600">Category</th>
                <th className="text-left p-4 font-medium text-gray-600">Duration</th>
                <th className="text-left p-4 font-medium text-gray-600">Recurs</th>
                <th className="text-left p-4 font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {activities.map((activity) => (
                <tr 
                  key={activity.id} 
                  className={`border-t ${!activity.is_active ? 'opacity-50' : ''}`}
                >
                  <td className="p-4 text-blue-600 font-medium">{activity.start_time}</td>
                  <td className="p-4 font-medium text-gray-800">{activity.title}</td>
                  <td className="p-4">
                    <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-sm">
                      {activity.category}
                    </span>
                  </td>
                  <td className="p-4 text-gray-600">{activity.duration_formatted}</td>
                  <td className="p-4 text-gray-600">{activity.recurrence}</td>
                  <td className="p-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleToggle(activity.id)}
                        className={`p-2 rounded transition-colors ${
                          activity.is_active 
                            ? 'text-green-600 hover:bg-green-50' 
                            : 'text-gray-400 hover:bg-gray-100'
                        }`}
                        title={activity.is_active ? 'Disable' : 'Enable'}
                      >
                        <Power size={18} />
                      </button>
                      <button
                        onClick={() => handleDelete(activity.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                        title="Delete"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Add Activity Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-800">Add Activity</h2>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                <X size={24} />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  type="text"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Time *</label>
                  <input
                    type="time"
                    value={form.start_time}
                    onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Duration (min)</label>
                  <input
                    type="number"
                    value={form.duration}
                    onChange={(e) => setForm({ ...form, duration: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="60"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select
                    value={form.category}
                    onChange={(e) => setForm({ ...form, category: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Recurrence</label>
                  <select
                    value={form.recurrence}
                    onChange={(e) => setForm({ ...form, recurrence: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {RECURRENCE.map((rec) => (
                      <option key={rec} value={rec}>{rec}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                <input
                  type="text"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Optional"
                />
              </div>
              
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="outdoor"
                  checked={form.is_outdoor}
                  onChange={(e) => setForm({ ...form, is_outdoor: e.target.checked })}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="outdoor" className="text-sm text-gray-700">Outdoor activity</label>
              </div>
              
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ backgroundColor: '#2563eb', color: '#ffffff' }}
                  className="flex-1 px-4 py-2 rounded-lg hover:opacity-90 font-medium"
                >
                  Add Activity
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}