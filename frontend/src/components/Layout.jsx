import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 p-8 w-full overflow-auto"h>
        <div className="w-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
