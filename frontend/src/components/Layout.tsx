import { Outlet, Link, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { healthService } from '../services/api';

export default function Layout() {
  const location = useLocation();
  const { data: healthData } = useQuery({
    queryKey: ['health'],
    queryFn: healthService.checkHealth,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const navItems = [
    { path: '/', label: 'Dashboard', icon: 'fa-house-medical' },
    { path: '/clinical-trials', label: 'Clinical Trials', icon: 'fa-flask' },
    { path: '/disease-info', label: 'Disease Info', icon: 'fa-disease' },
    { path: '/literature', label: 'Literature', icon: 'fa-book-medical' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b-4 border-blue-600">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center space-x-4">
              <div className="bg-blue-600 p-3 rounded-xl">
                <i className="fas fa-user-nurse text-white text-2xl"></i>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">AI Nurse Florence</h1>
                <p className="text-sm text-blue-600 font-medium">Clinical Decision Support System</p>
              </div>
            </Link>

            {/* Connection Status */}
            <div className="flex items-center space-x-2 bg-gray-50 px-3 py-2 rounded-lg">
              <div className={`w-3 h-3 rounded-full ${healthData ? 'bg-green-500' : 'bg-gray-400'} animate-pulse`}></div>
              <span className="text-sm text-gray-600 font-medium">
                {healthData ? 'Connected' : 'Connecting...'}
              </span>
              {healthData && (
                <span className="text-xs text-gray-500">v{healthData.version}</span>
              )}
            </div>
          </div>

          {/* Navigation */}
          <nav className="mt-4 flex space-x-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  location.pathname === item.path
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <i className={`fas ${item.icon}`}></i>
                <span className="font-medium">{item.label}</span>
              </Link>
            ))}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-sm text-gray-600">
          <p className="font-semibold text-blue-600 mb-1">Clinical Decision Support Tool - Educational Purposes Only</p>
          <p>Draft for clinician review — not medical advice. No PHI stored.</p>
        </div>
      </footer>
    </div>
  );
}