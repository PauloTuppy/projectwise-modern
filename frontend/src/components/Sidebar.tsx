import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };
  
  const linkClass = (path: string) => {
    return `flex items-center gap-2 px-3 py-2 rounded transition ${
      isActive(path) 
        ? 'bg-blue-600 text-white' 
        : 'hover:bg-gray-700 text-gray-300'
    }`;
  };
  
  return (
    <div className="w-64 bg-gray-800 text-white p-4">
      <h2 className="text-2xl font-bold mb-6 px-3">ProjectWise</h2>
      <nav>
        <ul className="space-y-2">
          <li>
            <Link to="/dashboard" className={linkClass('/dashboard')}>
              <span className="text-xl">📊</span>
              <span>Dashboard</span>
            </Link>
          </li>
          <li>
            <Link to="/projects" className={linkClass('/projects')}>
              <span className="text-xl">📁</span>
              <span>Projects</span>
            </Link>
          </li>
          <li>
            <Link to="/workflows" className={linkClass('/workflows')}>
              <span className="text-xl">🔄</span>
              <span>Workflows</span>
            </Link>
          </li>
          <li>
            <Link to="/upload" className={linkClass('/upload')}>
              <span className="text-xl">📤</span>
              <span>Upload</span>
            </Link>
          </li>
          <li>
            <Link to="/editor" className={linkClass('/editor')}>
              <span className="text-xl">✏️</span>
              <span>Editor</span>
            </Link>
          </li>
        </ul>
      </nav>
      
      {/* ISO 9001:2015 Badge */}
      <div className="mt-8 px-3">
        <div className="bg-green-700 text-white text-xs font-bold px-2 py-1 rounded text-center">
          ISO 9001:2015
        </div>
        <p className="text-xs text-gray-400 mt-2 text-center">
          Quality Management System
        </p>
      </div>
    </div>
  );
};

export default Sidebar;