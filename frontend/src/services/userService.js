import axios from 'axios';

const API_URL = 'http://localhost:8000/api/user';
const SERVER_URL = 'http://localhost:8000';

// Create an axios instance with default configs
const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Set up request interceptor to add the auth token to every request
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Ensure content type is set appropriately based on data type
    if (config.data instanceof FormData) {
      // For FormData, remove Content-Type so that the browser can set it with the boundary
      delete config.headers['Content-Type'];
    } else if (!config.headers['Content-Type']) {
      // Default to JSON if not specified
      config.headers['Content-Type'] = 'application/json';
    }
    
    // Add additional headers for better debugging
    config.headers['X-Requested-With'] = 'XMLHttpRequest';
    
    console.log('Request config:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
    });
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token expiration
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Log detailed error information for debugging
    if (error.response) {
      console.error('Response Error:', {
        status: error.response.status,
        data: error.response.data,
        url: originalRequest.url
      });
    } else {
      console.error('Request Error:', error.message);
    }
    
    // Check if this is a token expiration error
    const isExpiredToken = 
      error.response?.data?.detail?.includes('expired') || 
      error.response?.data?.code === 'token_not_valid' ||
      error.response?.data?.message?.includes('expired') ||
      (error.response?.data?.detail === 'Given token not valid for any token type');
    
    if (error.response && error.response.status === 401 && isExpiredToken) {
      console.log('Access token expired, clearing tokens and redirecting to login');
      
      // Clear tokens from localStorage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      
      // Redirect to login page
      window.location.href = '/login?expired=true';
      
      // Don't attempt refresh, just redirect
      return Promise.reject(error);
    }
    
    // For other errors, just reject the promise
    return Promise.reject(error);
  }
);

// Helper function to format image URLs
export const formatImageUrl = (relativeUrl) => {
  if (!relativeUrl) return null;
  
  // If the URL already starts with http, return it as is
  if (relativeUrl.startsWith('http')) {
    return relativeUrl;
  }
  
  // Otherwise, prepend the server URL
  return `${SERVER_URL}${relativeUrl}`;
};

export const getUserProfile = async () => {
  try {
    // Use the correct endpoint /api/user/profile/ not /api/profile/
    const response = await axios.get('http://localhost:8000/api/user/profile/', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`
      }
    });
    
    console.log('Profile response:', response);
    
    // Format image URLs
    if (response.data.profile_image) {
      response.data.profile_image = formatImageUrl(response.data.profile_image);
    }
    if (response.data.cover_image) {
      response.data.cover_image = formatImageUrl(response.data.cover_image);
    }
    
    return response.data;
  } catch (error) {
    console.error('Profile fetch error details:', error.response || error);
    throw error.response ? error.response.data : new Error('Failed to fetch profile');
  }
};

export const updateUserProfile = async (profileData) => {
  // Define a function to try an endpoint
  const tryEndpoint = async (endpoint) => {
    try {
      console.log(`Attempting to update profile with endpoint: ${endpoint}`);
      // Use axios directly with full URL to bypass apiClient's base URL
      const response = await axios.put(`http://localhost:8000${endpoint}`, profileData, {
        headers: {
          // Let browser set the multipart boundary
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`
        },
        // Add timeout to prevent hanging requests
        timeout: 10000
      });
      console.log('Profile update successful:', response);
      
      // Validate response to ensure it's what we expect
      if (!response || !response.data) {
        console.error('Empty response received from server');
        throw new Error('Invalid response from server');
      }
      
      return response;
    } catch (error) {
      console.error(`Error with endpoint ${endpoint}:`, error.response || error);
      
      // Check for specific error types for better error handling
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Server responded with error:', error.response.status, error.response.data);
        if (error.response.status === 401) {
          throw new Error('Authentication error. Please log in again.');
        }
        throw error.response.data || 'Server error';
      } else if (error.request) {
        // The request was made but no response was received
        console.error('No response received from server:', error.request);
        throw new Error('No response from server. Please check your connection.');
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Error setting up request:', error.message);
        throw error;
      }
    }
  };

  try {
    // Based on the user's role and URL patterns from Django, determine endpoints to try
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    const role = currentUser.role || '';
    
    let endpoints = [];
    
    // Choose appropriate endpoint based on user role
    if (role.toLowerCase() === 'teacher') {
      endpoints = ['/api/user/teacher/profile/', '/api/user/profile/'];
    } else if (role.toLowerCase() === 'student') {
      endpoints = ['/api/user/student/profile/', '/api/user/profile/'];
    } else {
      endpoints = ['/api/user/profile/'];
    }
    
    let lastError = null;
    let response = null;
    
    // Try each endpoint until one works
    for (const endpoint of endpoints) {
      try {
        response = await tryEndpoint(endpoint);
        
        // If we got a response, no need to try other endpoints
        if (response) {
          break;
        }
      } catch (error) {
        lastError = error;
        // Continue to the next endpoint
      }
    }
    
    // If no response was received after trying all endpoints
    if (!response) {
      throw lastError || new Error('Failed to update profile');
    }
    
    // Format image URLs in the response
    const userData = response.data;
    if (userData.profile_image) {
      userData.profile_image = formatImageUrl(userData.profile_image);
    }
    if (userData.cover_image) {
      userData.cover_image = formatImageUrl(userData.cover_image);
    }
    
    // Make sure to update userRole in localStorage
    if (userData.role) {
      localStorage.setItem('userRole', userData.role);
    }
    
    return userData;
  } catch (error) {
    console.error('All profile update attempts failed:', error);
    if (typeof error === 'object' && error.message) {
      throw error.message;
    }
    throw error.response ? error.response.data : 'Failed to update profile';
  }
};

// Resend verification email
export const resendVerificationEmail = async (email) => {
  try {
    console.log('Attempting to resend verification email to:', email);
    
    // The correct URL path matches what's defined in user_urls.py
    const response = await axios.post('http://localhost:8000/api/user/resend-verification/', {
      email
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Resend verification response:', response.data);
    
    if (response.data && response.data.status === 'success') {
      return response.data;
    } else {
      throw new Error(response.data?.message || 'Failed to resend verification email');
    }
  } catch (error) {
    console.error('Error resending verification email:', error);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
      
      if (error.response.status === 404) {
        throw new Error('Verification endpoint not found. Please contact support.');
      }
    }
    throw error.response?.data || error;
  }
};

// Handle response from API
// ... existing code ... 