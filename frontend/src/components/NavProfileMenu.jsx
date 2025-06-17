import { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { resendVerificationEmail } from '../services/userService';
import { toast } from 'react-toastify';
import { useTranslation } from 'react-i18next';

const NavProfileMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const [isResending, setIsResending] = useState(false);
  const { t } = useTranslation();
  
  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };
  
  const handleClickOutside = (event) => {
    if (menuRef.current && !menuRef.current.contains(event.target)) {
      setIsOpen(false);
    }
  };
  
  useEffect(() => {
    // Add click event listener to close dropdown when clicking outside
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogout = () => {
    try {
      // Make sure to clear all user-related data
      localStorage.removeItem('userRole');
      logout();
      navigate('/login');
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setIsOpen(false);
    }
  };

  const handleResendVerification = async () => {
    if (!currentUser?.email || isResending) return;
    
    try {
      setIsResending(true);
      const response = await resendVerificationEmail(currentUser.email);
      toast.success(response.message || t('verification_resent'));
    } catch (error) {
      toast.error(error.message || t('verification_resend_failed'));
    } finally {
      setIsResending(false);
    }
  };

  // Extract initials from user's name
  const getInitials = () => {
    if (!currentUser) return '?';
    
    const firstName = currentUser.first_name || '';
    const lastName = currentUser.last_name || '';
    
    if (!firstName && !lastName) return '?';
    
    // Safely access first characters
    const firstInitial = firstName.length > 0 ? firstName.charAt(0) : '';
    const lastInitial = lastName.length > 0 ? lastName.charAt(0) : '';
    
    return `${firstInitial}${lastInitial}`.toUpperCase() || '?';
  };

  return (
    <div ref={menuRef} className="relative">
      <button
        onClick={toggleMenu}
        className="flex items-center justify-center w-10 h-10 rounded-full bg-indigo-600 text-white text-sm font-medium focus:outline-none shadow-md hover:bg-indigo-700 transition-colors"
        aria-expanded={isOpen}
      >
        {getInitials()}
      </button>
      
      {isOpen && currentUser && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10">
          <div className="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
            <div className="font-medium">
              {currentUser.first_name || ''} {currentUser.last_name || ''}
            </div>
            <div className="text-gray-500 truncate">{currentUser.email || t('no_email')}</div>
            <div className="mt-1 flex items-center">
              <span className={`h-2 w-2 rounded-full mr-1 ${currentUser?.is_email_verified ? 'bg-green-500' : 'bg-red-500'}`}></span>
              <span className="text-xs">
                {currentUser?.is_email_verified ? t('verified') : t('not_verified')}
                {!currentUser?.is_email_verified && (
                  <button 
                    onClick={handleResendVerification}
                    disabled={isResending}
                    className="ml-1 text-blue-500 hover:underline"
                  >
                    {isResending ? t('sending') : t('resend')}
                  </button>
                )}
              </span>
            </div>
          </div>
          <Link
            to="/profile"
            onClick={() => setIsOpen(false)}
            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            {t('profile')}
          </Link>
          <button
            onClick={handleLogout}
            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            {t('logout')}
          </button>
        </div>
      )}
    </div>
  );
};

export default NavProfileMenu; 