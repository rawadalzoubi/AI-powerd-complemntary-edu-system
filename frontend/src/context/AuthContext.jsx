import { createContext, useState, useEffect, useContext } from 'react';
import { getCurrentUser, logout } from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load user from localStorage on component mount
    try {
      const user = getCurrentUser();
      setCurrentUser(user);
    } catch (err) {
      setError('Failed to restore session');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleLogout = () => {
    logout();
    setCurrentUser(null);
  };

  // Force re-login to refresh tokens when they are invalid
  const forceRelogin = (redirectPath = '/login') => {
    console.log('Session expired, redirecting to login...');
    handleLogout();
    // Use window.location for a full page refresh to clear any state
    window.location.href = redirectPath;
  };

  const updateUser = (user) => {
    if (user) {
      // Update in state
      setCurrentUser(user);
      
      // Persist to localStorage
      try {
        localStorage.setItem('user', JSON.stringify(user));
        
        // Also update userRole for easy access
        if (user.role) {
          localStorage.setItem('userRole', user.role);
        }
        
        console.log('User data updated in localStorage:', user);
      } catch (err) {
        console.error('Failed to update user data in localStorage:', err);
      }
    }
  };

  const value = {
    currentUser,
    loading,
    error,
    logout: handleLogout,
    updateUser,
    forceRelogin
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext; 