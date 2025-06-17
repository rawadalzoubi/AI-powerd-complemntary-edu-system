import React, { useMemo } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from 'react-i18next';

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser, logout } = useAuth();
  const userRole = currentUser?.role?.toLowerCase() || '';
  const { t } = useTranslation();
  
  // Define navigation items based on user role
  const navItems = useMemo(() => {
    // Common items for all roles
    const commonItems = [
      { path: '/profile', icon: 'fa-user', label: t('profile') },
    ];
    
    // Role-specific items
    switch(userRole) {
      case 'teacher':
        return [
          { path: '/dashboard', icon: 'fa-tachometer-alt', label: t('dashboard') },
          { path: '/lessons', icon: 'fa-book', label: t('lessons') },
          { path: '/students', icon: 'fa-users', label: t('students') },
          { path: '/analytics', icon: 'fa-chart-line', label: t('analytics') },
          { path: '/messages', icon: 'fa-envelope', label: t('messages') },
          ...commonItems
        ];
      case 'advisor':
        return [
          { path: '/advisor/dashboard', icon: 'fa-tachometer-alt', label: t('dashboard') },
          { path: '/advisor/students', icon: 'fa-users', label: t('students') },
          { path: '/advisor/lessons', icon: 'fa-book', label: t('lessons') },
          { path: '/advisor/analytics', icon: 'fa-chart-line', label: t('analytics') },
          ...commonItems
        ];
      case 'student':
        return [
          { path: '/student/dashboard', icon: 'fa-tachometer-alt', label: t('dashboard') },
          { path: '/student/courses', icon: 'fa-graduation-cap', label: t('courses') },
          { path: '/student/assignments', icon: 'fa-tasks', label: t('assignments') },
          { path: '/student/progress', icon: 'fa-chart-line', label: t('progress') },
          ...commonItems
        ];
      default:
        return commonItems;
    }
  }, [userRole, t]);

  // Check if path is active
  const isActive = (path) => {
    return location.pathname === path || 
           (path !== '/dashboard' && path !== '/advisor/dashboard' && path !== '/student/dashboard' && location.pathname.startsWith(path));
  };

  return (
    <div className="w-64 h-screen bg-indigo-700 text-white flex flex-col">
      {/* Logo Header */}
      <div className="p-4 border-b border-indigo-600">
        <Link to="/home" className="flex items-center space-x-2 text-xl font-bold">
          <i className="fas fa-graduation-cap"></i>
          <span>{t('app_name')}</span>
        </Link>
      </div>
      
      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 text-sm ${
                  isActive(item.path)
                    ? 'bg-indigo-800 font-medium'
                    : 'hover:bg-indigo-600'
                }`}
              >
                <i className={`fas ${item.icon} w-5 text-center`}></i>
                <span>{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      
      {/* User Profile */}
      {currentUser && (
        <>
          <div
            className="p-4 border-t border-indigo-600 flex items-center space-x-3 cursor-pointer hover:bg-indigo-600 transition"
            onClick={() => navigate('/profile')}
            aria-label={t('profile')}
            tabIndex={0}
            onKeyPress={e => { if (e.key === 'Enter' || e.key === ' ') navigate('/profile'); }}
          >
            <div className="w-9 h-9 rounded-full bg-indigo-500 flex items-center justify-center text-white font-medium">
              {currentUser.first_name?.charAt(0)}{currentUser.last_name?.charAt(0)}
            </div>
            <div className="text-sm">
              <div className="font-medium">{currentUser.first_name} {currentUser.last_name}</div>
              <div className="text-indigo-300 text-xs">{currentUser.role ? currentUser.role.charAt(0).toUpperCase() + currentUser.role.slice(1) : 'User'}</div>
            </div>
          </div>
          <button
            onClick={logout}
            className="m-4 py-2 px-4 w-[calc(100%-2rem)] bg-red-500 text-white rounded hover:bg-red-600 transition focus:outline-none focus:ring-2 focus:ring-red-400"
            aria-label={t('logout')}
          >
            {t('logout')}
          </button>
        </>
      )}
    </div>
  );
};

export default Sidebar; 