import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  CalendarDays, 
  Cloud, 
  Newspaper, 
  TrendingUp, 
  BarChart3, 
  Settings 
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/activities', icon: CalendarDays, label: 'Activities' },
  { to: '/weather', icon: Cloud, label: 'Weather' },
  { to: '/news', icon: Newspaper, label: 'News' },
  { to: '/stocks', icon: TrendingUp, label: 'Stocks' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export default function Sidebar() {
  return (
    <aside className="w-56 bg-slate-900 text-white min-h-screen p-4 flex flex-col">
      <div className="mb-8 px-3 py-4 border-b border-slate-700">
        <h1 className="text-xl font-bold text-white">Buddy</h1>
        <p className="text-slate-400 text-xs mt-1">Daily Planner</p>
      </div>
      
      <nav className="flex-1 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors text-sm ${
                isActive 
                  ? 'bg-white text-slate-900 font-medium' 
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto pt-4 border-t border-slate-700 px-3">
        <p className="text-slate-500 text-xs">v1.0.0</p>
      </div>
    </aside>
  );
}