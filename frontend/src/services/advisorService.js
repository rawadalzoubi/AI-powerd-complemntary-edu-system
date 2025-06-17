import axios from 'axios';

const API_URL = 'http://localhost:8000/api/user/advisor/';

// Add auth token to requests
const authHeader = () => {
  const token = localStorage.getItem('accessToken');
  if (token) {
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

// Add request interceptor to always include auth token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response && error.response.status === 401) {
      console.log('Unauthorized access, redirecting to login');
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Get students by grade
const getStudentsByGrade = async (gradeLevel = null) => {
  try {
    const url = gradeLevel ? `students/grade/${gradeLevel}/` : 'students/';
    const response = await apiClient.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching students:', error);
    throw error;
  }
};

// Get student performance data
const getStudentPerformance = async (studentId) => {
  try {
    const response = await apiClient.get(`students/${studentId}/performance/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching student performance:', error);
    throw error;
  }
};

// Get student lessons
const getStudentLessons = async (studentId) => {
  try {
    const response = await apiClient.get(`students/${studentId}/lessons/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching student lessons:', error);
    throw error;
  }
};

// Get student quiz attempts
const getStudentQuizAttempts = async (studentId, lessonId = null, quizId = null) => {
  try {
    let url = `students/${studentId}/quiz-attempts/`;
    
    // Add query parameters if provided
    const params = {};
    if (lessonId) params.lesson_id = lessonId;
    if (quizId) params.quiz_id = quizId;
    
    const response = await apiClient.get(url, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching student quiz attempts:', error);
    throw error;
  }
};

// Assign lessons to student
const assignLessonsToStudent = async (studentId, lessonIds) => {
  try {
    const response = await apiClient.post(`students/${studentId}/assign-lessons/`, {
      lesson_ids: lessonIds
    });
    return response.data;
  } catch (error) {
    console.error('Error assigning lessons to student:', error);
    throw error;
  }
};

// Get lessons available to advisor (for assignment)
const getAvailableLessons = async () => {
  try {
    const response = await apiClient.get('lessons/');
    return response.data;
  } catch (error) {
    console.error('Error fetching available lessons:', error);
    throw error;
  }
};

// Delete lesson assigned to a student
const deleteStudentLesson = async (studentId, lessonId) => {
  try {
    const response = await apiClient.delete(`students/${studentId}/lessons/${lessonId}/`);
    return response.data;
  } catch (error) {
    console.error('Error deleting student lesson:', error);
    throw error;
  }
};

const advisorService = {
  getStudentsByGrade,
  getStudentPerformance,
  getStudentLessons,
  getStudentQuizAttempts,
  assignLessonsToStudent,
  getAvailableLessons,
  deleteStudentLesson
};

export default advisorService; 