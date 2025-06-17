import React from 'react';
import Sidebar from './Sidebar';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../LanguageSwitcher';

const DashboardLayout = ({ children }) => {
  const { currentUser } = useAuth();
  const userRole = currentUser?.role || '';
  const { t } = useTranslation();
  
  // Get dashboard title based on user role
  const getDashboardTitle = () => {
    switch(userRole.toLowerCase()) {
      case 'teacher':
        return t('dashboard') + ' - ' + t('teachers');
      case 'advisor':
        return t('dashboard') + ' - ' + t('advisor');
      case 'student':
        return t('dashboard') + ' - ' + t('students');
      default:
        return t('dashboard');
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 overflow-auto">
        <div className="h-16 bg-white shadow flex items-center justify-between px-6">
          <h1 className="text-xl font-semibold text-gray-800">{getDashboardTitle()}</h1>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <input
                type="text"
                className="w-64 pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder={t('search')}
              />
              <div className="absolute left-3 top-2.5 text-gray-400">
                <i className="fas fa-search"></i>
              </div>
            </div>
            <LanguageSwitcher />
            <div className="text-gray-600 hover:text-gray-800 cursor-pointer">
              <i className="fas fa-bell text-xl"></i>
            </div>
          </div>
        </div>
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout; 