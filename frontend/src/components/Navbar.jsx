import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import NavProfileMenu from './NavProfileMenu';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';

const Navbar = () => {
  const { currentUser } = useAuth();
  const [userRole, setUserRole] = useState('');
  const { t } = useTranslation();
  
  // Get the role from localStorage or currentUser
  useEffect(() => {
    if (currentUser && currentUser.role) {
      setUserRole(currentUser.role);
    } else {
      // Fallback to localStorage
      const storedRole = localStorage.getItem('userRole');
      if (storedRole) {
        setUserRole(storedRole);
      }
    }
  }, [currentUser]);

  // Display the role in a user-friendly format
  const formatRole = (role) => {
    if (!role) return t('user');
    // Ensure role is a string and handle case
    const roleStr = String(role).toLowerCase();
    return roleStr.charAt(0).toUpperCase() + roleStr.slice(1);
  };
  
  // Check if user is verified
  const isVerified = currentUser?.is_email_verified || false;

  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/home" className="flex-shrink-0 flex items-center">
              <span className="text-xl font-bold text-indigo-600">{t('home')}</span>
            </Link>
            
            {currentUser && userRole.toLowerCase() === 'student' && (
              <Link 
                to="/student/dashboard" 
                className="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                  <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
                </svg>
                {t('dashboard')}
              </Link>
            )}
            
            {currentUser && userRole.toLowerCase() === 'teacher' && (
              <Link 
                to="/dashboard" 
                className="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                </svg>
                {t('lessons')}
              </Link>
            )}
            
            {currentUser && userRole.toLowerCase() === 'advisor' && (
              <Link 
                to="/advisor/dashboard" 
                className="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                  <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
                </svg>
                {t('dashboard')}
              </Link>
            )}
          </div>
          
          <div className="flex items-center">
            {currentUser && (
              <>
                <LanguageSwitcher className="mr-4" />
                <div className="flex flex-col items-end mr-4">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${userRole.toLowerCase() === 'teacher' ? 'bg-indigo-100 text-indigo-800' : userRole.toLowerCase() === 'advisor' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'}`}>
                    {(userRole || '').toLowerCase() === 'teacher' ? 
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
                      </svg> : 
                      (userRole || '').toLowerCase() === 'advisor' ?
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                      </svg> :
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                      </svg>
                    }
                    {formatRole(userRole)}
                  </span>
                  <span className={`text-xs ${isVerified ? 'text-green-600' : 'text-red-600'}`}>
                    {isVerified ? t('verified') : t('not_verified')}
                  </span>
                </div>
                <NavProfileMenu />
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 