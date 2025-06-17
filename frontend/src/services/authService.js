import axios from 'axios';

const API_URL = 'http://localhost:8000/api/user';

// Create an axios instance with default configs
const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Important for CORS with credentials
  headers: {
    'Content-Type': 'application/json'
  }
});

// Create a public API client that doesn't send auth headers for registration and other public endpoints
const publicApiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const register = async (userData) => {
  console.log('Attempting registration with data:', userData);
  try {
    const response = await publicApiClient.post('/register/', userData);
    console.log('Registration successful:', response.data);
    return response.data;
  } catch (error) {
    console.error('Registration error:', error);
    
    // Check for network errors
    if (!error.response) {
      console.error('Network error - no response from server');
      throw new Error('Network error. Please check your connection and try again.');
    }
    
    // Check for specific error about existing email
    if (error.response.data && error.response.data.errors && error.response.data.errors.email) {
      const emailError = error.response.data.errors.email[0];
      console.error('Email error:', emailError);
      throw new Error(emailError);
    }
    
    // General error handling
    const errorMessage = error.response.data?.message || 'Registration failed';
    console.error('Error message:', errorMessage);
    throw new Error(errorMessage);
  }
};

export const verifyEmail = async (email, verificationCode) => {
  try {
    const response = await publicApiClient.post('/verify-email/', {
      email,
      verification_code: verificationCode
    });
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : new Error('Verification failed');
  }
};

export const login = async (email, password) => {
  try {
    const response = await publicApiClient.post('/login/', {
      email,
      password
    });
    
    // Store tokens in local storage
    if (response.data.tokens) {
      localStorage.setItem('user', JSON.stringify(response.data.user));
      localStorage.setItem('accessToken', response.data.tokens.access);
      localStorage.setItem('refreshToken', response.data.tokens.refresh);
      
      // Store user role for easy access
      if (response.data.user && response.data.user.role) {
        localStorage.setItem('userRole', response.data.user.role);
      }
      
      // Set the token in axios default headers for authenticated requests
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${response.data.tokens.access}`;
    }
    
    return response.data;
  } catch (error) {
    console.error('Login error:', error);
    
    // Check if this is a verification error
    if (error.response && error.response.data && error.response.status === 401) {
      // For verification errors, pass along the requires_verification flag and email
      if (error.response.data.requires_verification) {
        throw {
          ...error.response.data,
          message: error.response.data.message
        };
      }
    }
    
    throw error.response ? error.response.data : new Error('Login failed');
  }
};

export const logout = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  
  // Remove auth header
  delete apiClient.defaults.headers.common['Authorization'];
};

export const getCurrentUser = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

// Password reset request
export const requestPasswordReset = async (email) => {
  console.log(`Sending password reset request for: ${email}`);
  try {
    const response = await publicApiClient.post('/password-reset/request/', {
      email
    });
    
    console.log('Password reset request successful:', response.data);
    return response.data;
  } catch (error) {
    console.error('Password reset request error:', error);
    
    if (!error.response) {
      console.error('Network error during password reset request');
      throw new Error('Network error. Please check your connection and try again.');
    }
    
    if (error.response.status === 404) {
      console.error('Password reset endpoint not found (404)');
      throw new Error('Password reset service is unavailable. Please try again later.');
    }
    
    throw new Error(
      error.response?.data?.message || 
      'Failed to send password reset email'
    );
  }
};

// Validate reset token
export const validateResetToken = async (token) => {
  try {
    const response = await publicApiClient.get(`/password-reset/validate/${token}/`);
    
    return response.data;
  } catch (error) {
    console.error('Token validation error:', error);
    throw new Error(
      error.response?.data?.message || 
      'Invalid or expired reset link'
    );
  }
};

// Reset password
export const resetPassword = async (token, password, password_confirm) => {
  try {
    const response = await publicApiClient.post('/password-reset/confirm/', {
      token,
      password,
      password_confirm
    });
    
    return response.data;
  } catch (error) {
    console.error('Password reset error:', error);
    throw new Error(
      error.response?.data?.errors?.password || 
      error.response?.data?.errors?.password_confirm || 
      error.response?.data?.message || 
      'Failed to reset password'
    );
  }
};

// Refresh token
export const refreshToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refreshToken');
    
    if (!refreshToken) {
      console.error('No refresh token available');
      throw new Error('No refresh token available');
    }
    
    console.log('Attempting to refresh token...');
    
    const response = await publicApiClient.post('/token/refresh/', {
      refresh: refreshToken
    });
    
    if (response.data && response.data.access) {
      // Update the access token in localStorage
      localStorage.setItem('accessToken', response.data.access);
      
      // Update the axios default headers
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
      
      return response.data.access;
    } else {
      console.error('Invalid refresh response:', response.data);
      throw new Error('Failed to refresh token - invalid response');
    }
  } catch (error) {
    console.error('Token refresh error details:', error.response?.data || error.message);
    
    // Clear tokens if refresh fails
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      console.log('Refresh token expired or invalid. Logging out...');
      logout();
    }
    
    throw error;
  }
};

// Setup token on initial load if it exists
const token = localStorage.getItem('accessToken');
if (token) {
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
} 