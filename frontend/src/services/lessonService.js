import axios from 'axios';
import { refreshToken } from './authService';

const API_URL = 'http://localhost:8000/api/content/';
const STUDENT_API_URL = 'http://localhost:8000/api/student/';

// Add auth token to requests
const authHeader = () => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    console.log('Adding auth header with token:', token.substring(0, 15) + '...');
    return { Authorization: `Bearer ${token}` };
  } else {
    console.warn('No access token found in localStorage');
    return {};
  }
};

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL
});

// Create student axios instance
const studentApiClient = axios.create({
  baseURL: STUDENT_API_URL
});

// Add request interceptor to always include auth token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      console.log('Request interceptor added auth header');
    } else {
      console.warn('Request interceptor: No token available');
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add same interceptor for student API client
studentApiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      console.log('Student API: Request interceptor added auth header');
    } else {
      console.warn('Student API: Request interceptor: No token available');
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh for both clients
const addResponseInterceptor = (client) => {
  client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't tried refreshing token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Attempt to refresh the token
        const newToken = await refreshToken();
        
        // Update the authorization header with new token
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
        console.log('Token refreshed, retrying request with new token');
        
        // Retry the original request with new token
          return client(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Redirect to login if refresh fails
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
};

// Add response interceptors to both clients
addResponseInterceptor(apiClient);
addResponseInterceptor(studentApiClient);

// Lesson APIs
const getLessons = async () => {
  try {
    const response = await apiClient.get('lessons/', { 
      headers: authHeader() 
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

const getLessonById = async (lessonId) => {
  try {
    // Check if we're in a student route to use the student API
    const inStudentRoute = window.location.pathname.includes('/student/');
    console.log(`Current path: ${window.location.pathname}`);
    console.log(`Using ${inStudentRoute ? 'student' : 'content'} API for lesson ${lessonId}`);
    
    if (inStudentRoute) {
      console.log(`Calling student API endpoint: ${API_URL}../student/lessons/${lessonId}/`);
      console.log('Auth headers:', authHeader());
      const response = await axios.get(`http://localhost:8000/api/student/lessons/${lessonId}/`, { 
        headers: authHeader() 
      });
      console.log('Student API response:', response.data);
      return response.data;
    } else {
      console.log(`Calling content API endpoint: ${API_URL}lessons/${lessonId}/`);
    const response = await apiClient.get(`lessons/${lessonId}/`, { 
      headers: authHeader() 
    });
      console.log('Content API response:', response.data);
    return response.data;
    }
  } catch (error) {
    console.error('Error getting lesson by ID:', error);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
      console.error('Request URL:', error.config?.url);
      console.error('Request method:', error.config?.method);
      
      // Check if this is an authentication issue
      if (error.response.status === 401) {
        console.error('Authentication error - token may be expired');
      }
      // Check if this is an access issue
      else if (error.response.status === 403) {
        console.error('Authorization error - user may not have permission');
      }
      // Check if this is a not found issue
      else if (error.response.status === 404) {
        console.error('Resource not found - check if lesson exists or user is enrolled');
      }
    }
    throw error;
  }
};

const createLesson = async (lessonData) => {
  try {
    console.log("Creating lesson with data:", lessonData);
    const response = await apiClient.post('lessons/', lessonData, { 
      headers: authHeader() 
    });
    console.log("Lesson created successfully:", response.data);
    console.log("Lesson ID:", response.data.id, "Type:", typeof response.data.id);
    return response.data;
  } catch (error) {
    console.error("Error creating lesson:", error.response?.data || error.message);
    throw error;
  }
};

const updateLesson = async (lessonId, lessonData) => {
  try {
    const response = await apiClient.put(`lessons/${lessonId}/`, lessonData, { 
      headers: authHeader() 
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

const deleteLesson = async (lessonId) => {
  try {
    await apiClient.delete(`lessons/${lessonId}/`, { 
      headers: authHeader() 
    });
    return true;
  } catch (error) {
    throw error;
  }
};

// Lesson Content APIs
const getLessonContents = async (lessonId) => {
  try {
    console.log(`Fetching lesson contents for lessonId: ${lessonId}`);
    
    // Check if we're in a student route to use the student API
    const inStudentRoute = window.location.pathname.includes('/student/');
    console.log(`Current path: ${window.location.pathname}`);
    console.log(`Using ${inStudentRoute ? 'student' : 'content'} API for content of lesson ${lessonId}`);
    
    // Try multiple URL options for content, similar to getLessonById
    const urlOptions = [
      `http://localhost:8000/api/student/lessons/${lessonId}/contents/`,
      `http://localhost:8000/api/content/lessons/${lessonId}/contents/`,
      `/api/student/lessons/${lessonId}/contents/`,
      `/api/content/lessons/${lessonId}/contents/`
    ];
    
    console.log("%c ATTEMPTING MULTIPLE CONTENT URLs", "background:orange; color:white", urlOptions);
    
    let contentsData = null;
    let successUrl = null;
    
    for (const url of urlOptions) {
      try {
        console.log(`Trying content URL: ${url}`);
        const token = localStorage.getItem('accessToken');
        const response = await axios.get(url, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          withCredentials: true
        });
        
        // If we get here, the request succeeded
        console.log(`%c SUCCESS with URL: ${url}`, "background:green; color:white", response.data);
        contentsData = response.data;
        successUrl = url;
        break;
      } catch (err) {
        console.error(`Failed with URL: ${url}`, err.response || err.message);
      }
    }
    
    if (!contentsData) {
      // Fall back to original approach if all new approaches fail
      console.log("All new approaches failed, trying original approach");
    const response = await apiClient.get(`lessons/${lessonId}/contents/`, { 
      headers: authHeader() 
    });
      contentsData = response.data;
    }
    
    return contentsData || [];
  } catch (error) {
    console.error("Error fetching lesson contents:", error.response?.data || error.message);
    // Return empty array instead of throwing to avoid breaking the UI
    return [];
  }
};

const uploadLessonContent = async (lessonId, contentData) => {
  try {
    const formData = new FormData();
    formData.append('title', contentData.title);
    formData.append('content_type', contentData.content_type);
    formData.append('file', contentData.file);

    const response = await apiClient.post(`lessons/${lessonId}/contents/`, formData, { 
      headers: {
        ...authHeader(),
        'Content-Type': 'multipart/form-data',
      }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

const deleteLessonContent = async (contentId) => {
  try {
    await apiClient.delete(`contents/${contentId}/`, { 
      headers: authHeader() 
    });
    return true;
  } catch (error) {
    throw error;
  }
};

// Quiz APIs
const getLessonQuizzes = async (lessonId) => {
  try {
    console.log(`Fetching lesson quizzes for lessonId: ${lessonId}`);
    
    // Check if we're in a student route to use the student API
    const inStudentRoute = window.location.pathname.includes('/student/');
    console.log(`Current path: ${window.location.pathname}`);
    console.log(`Using ${inStudentRoute ? 'student' : 'content'} API for quizzes of lesson ${lessonId}`);
    
    // Try multiple URL options for quizzes, similar to getLessonById
    const urlOptions = [
      `http://localhost:8000/api/student/lessons/${lessonId}/quizzes/`,
      `http://localhost:8000/api/content/lessons/${lessonId}/quizzes/`,
      `/api/student/lessons/${lessonId}/quizzes/`,
      `/api/content/lessons/${lessonId}/quizzes/`
    ];
    
    console.log("%c ATTEMPTING MULTIPLE QUIZ URLs", "background:orange; color:white", urlOptions);
    
    let quizzesData = null;
    let successUrl = null;
    
    for (const url of urlOptions) {
      try {
        console.log(`Trying quiz URL: ${url}`);
        const token = localStorage.getItem('accessToken');
        const response = await axios.get(url, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          withCredentials: true
        });
        
        // If we get here, the request succeeded
        console.log(`%c SUCCESS with URL: ${url}`, "background:green; color:white", response.data);
        quizzesData = response.data;
        successUrl = url;
        break;
      } catch (err) {
        console.error(`Failed with URL: ${url}`, err.response || err.message);
      }
    }
    
    if (!quizzesData) {
      // Fall back to original approach if all new approaches fail
      console.log("All new approaches failed, trying original approach");
    const response = await apiClient.get(`lessons/${lessonId}/quizzes/`, { 
      headers: authHeader() 
    });
      quizzesData = response.data;
    }
    
    return quizzesData || [];
  } catch (error) {
    console.error("Error fetching lesson quizzes:", error.response?.data || error.message);
    // Return empty array instead of throwing to avoid breaking the UI
    return [];
  }
};

const getQuizById = async (quizId) => {
  try {
    const response = await apiClient.get(`quizzes/${quizId}/`, { 
      headers: authHeader() 
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

const createQuiz = async (lessonId, quizData) => {
  try {
    const response = await apiClient.post(`lessons/${lessonId}/quizzes/`, quizData, { 
      headers: authHeader() 
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

const updateQuiz = async (quizId, quizData) => {
  try {
    const headers = authHeader();
    console.log('Updating quiz with ID:', quizId, 'Headers:', headers, 'Data:', quizData);
    const response = await apiClient.put(`quizzes/${quizId}/`, quizData, { 
      headers: headers
    });
    console.log('Quiz update response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error updating quiz:', error.response?.data || error.message);
    throw error;
  }
};

const deleteQuiz = async (quizId) => {
  try {
    await apiClient.delete(`quizzes/${quizId}/`, { 
      headers: authHeader() 
    });
    return true;
  } catch (error) {
    throw error;
  }
};

// Question APIs
const createQuestion = async (quizId, questionData) => {
  try {
    const response = await apiClient.post(`quizzes/${quizId}/questions/`, questionData, { 
      headers: authHeader() 
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

const updateQuestion = async (questionId, questionData) => {
  try {
    const response = await apiClient.put(`questions/${questionId}/`, questionData, { 
      headers: authHeader() 
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

const deleteQuestion = async (questionId) => {
  try {
    await apiClient.delete(`questions/${questionId}/`, { 
      headers: authHeader() 
    });
    return true;
  } catch (error) {
    throw error;
  }
};

// Answer APIs
const createAnswer = async (questionId, answerData) => {
  try {
    const response = await apiClient.post(`questions/${questionId}/answers/`, answerData, { 
      headers: authHeader() 
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

const updateAnswer = async (answerId, answerData) => {
  try {
    const response = await apiClient.put(`answers/${answerId}/`, answerData, { 
      headers: authHeader() 
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

const deleteAnswer = async (answerId) => {
  try {
    await apiClient.delete(`answers/${answerId}/`, { 
      headers: authHeader() 
    });
    return true;
  } catch (error) {
    throw error;
  }
};

const lessonService = {
  getLessons,
  getLessonById,
  createLesson,
  updateLesson,
  deleteLesson,
  getLessonContents,
  uploadLessonContent,
  deleteLessonContent,
  getLessonQuizzes,
  getQuizById,
  createQuiz,
  updateQuiz,
  deleteQuiz,
  createQuestion,
  updateQuestion,
  deleteQuestion,
  createAnswer,
  updateAnswer,
  deleteAnswer
};

export default lessonService; 