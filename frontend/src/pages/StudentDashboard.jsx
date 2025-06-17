import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import axios from 'axios';
import { Link } from 'react-router-dom';
import FeedbackList from '../components/students/FeedbackList';
import { FaBook, FaCheckCircle, FaHourglassHalf, FaRobot } from 'react-icons/fa';

const StudentDashboard = () => {
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [assignedLessons, setAssignedLessons] = useState([]);
  const [stats, setStats] = useState({
    completedLessons: 0,
    inProgressLessons: 0,
    averageProgress: 0
  });

  useEffect(() => {
    const fetchAssignedLessons = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('accessToken');
        
        const response = await axios.get(
          'http://localhost:8000/api/student/dashboard/lessons/',
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        
        if (response.data) {
          setAssignedLessons(response.data);
          
          // Calculate dashboard stats
          const completed = response.data.filter(lesson => lesson.progress === 100).length;
          const inProgress = response.data.filter(lesson => lesson.progress > 0 && lesson.progress < 100).length;
          const avgProgress = response.data.length > 0 
            ? Math.round(response.data.reduce((sum, lesson) => sum + lesson.progress, 0) / response.data.length) 
            : 0;
          
          setStats({
            completedLessons: completed,
            inProgressLessons: inProgress,
            averageProgress: avgProgress
          });
        }
      } catch (err) {
        console.error('Error fetching assigned lessons:', err);
        setError('Failed to load your assigned lessons. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchAssignedLessons();
  }, []);

  // Helper function to format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }).format(date);
  };
  
  // Calculate lesson status color
  const getLessonStatusColor = (progress) => {
    if (progress === 100) return 'bg-green-100 text-green-800'; // Completed
    if (progress > 0) return 'bg-blue-100 text-blue-800'; // In progress
    return 'bg-gray-100 text-gray-800'; // Not started
  };
  
  // Get lesson status text
  const getLessonStatusText = (progress) => {
    if (progress === 100) return 'Completed';
    if (progress > 0) return 'In Progress';
    return 'Not Started';
  };

  // Helper function to get the proper URL for lesson details
  const viewLessonDetails = (lessonId) => {
    return `/student/lessons/${lessonId}`;
  };

  return (
    <div className="student-dashboard-container">
      <DashboardLayout>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Student Dashboard</h1>
          <p className="text-gray-600">View your assigned lessons and track your progress</p>
        </div>
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Total Lessons Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-indigo-100 mr-4">
                <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Total Lessons</p>
                <p className="text-2xl font-bold text-gray-900">{assignedLessons.length}</p>
              </div>
            </div>
          </div>
          
          {/* Completed Lessons Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100 mr-4">
                <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-gray-900">{stats.completedLessons}</p>
              </div>
            </div>
          </div>
          
          {/* Progress Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-blue-100 mr-4">
                <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Average Progress</p>
                <p className="text-2xl font-bold text-gray-900">{stats.averageProgress}%</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            {/* Assigned Lessons Section */}
            <div className="bg-white rounded-lg shadow mb-8">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">My Assigned Lessons</h2>
              </div>
              
              <div className="p-6">
                {loading ? (
                  <div className="text-center py-6">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
                    <p className="mt-2 text-gray-600">Loading lessons...</p>
                  </div>
                ) : error ? (
                  <div className="bg-red-100 text-red-700 p-4 rounded-lg">
                    {error}
                  </div>
                ) : assignedLessons.length === 0 ? (
                  <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg text-center py-10">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    <p className="mt-2 text-gray-600">You don't have any assigned lessons yet.</p>
                    <p className="text-gray-500">Your advisor will assign lessons to you soon.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {assignedLessons.map(lesson => (
                      <div key={lesson.id} className="border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                        <div className="h-40 bg-indigo-100 flex items-center justify-center">
                          {lesson.cover_image ? (
                            <img 
                              src={lesson.cover_image} 
                              alt={lesson.name} 
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="text-indigo-500">
                              <svg className="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                              </svg>
                            </div>
                          )}
                        </div>
                        
                        <div className="p-4">
                          <div className="flex justify-between items-start mb-2">
                            <h3 className="text-lg font-medium text-gray-900">{lesson.name}</h3>
                            <span className={`px-2 py-1 text-xs rounded-full ${getLessonStatusColor(lesson.progress)}`}>
                              {getLessonStatusText(lesson.progress)}
                            </span>
                          </div>
                          
                          <p className="text-sm text-gray-600 mb-1">
                            <span className="font-medium">Subject:</span> {lesson.subject}
                          </p>
                          
                          <p className="text-sm text-gray-600 mb-3">
                            <span className="font-medium">Assigned:</span> {formatDate(lesson.assigned_date)}
                          </p>
                          
                          <div className="mb-3">
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-indigo-600 h-2 rounded-full" 
                                style={{ width: `${lesson.progress}%` }}
                              ></div>
                            </div>
                            <div className="text-xs text-gray-500 mt-1 text-right">{lesson.progress}% complete</div>
                          </div>
                          
                          <Link 
                            to={viewLessonDetails(lesson.id)}
                            className="block w-full text-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                          >
                            {lesson.progress > 0 ? 'Continue Learning' : 'Start Learning'}
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-1">
            {/* Teacher Feedback Section */}
            <div className="bg-white rounded-lg shadow mb-8">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Teacher Feedback</h2>
              </div>
              
              <div className="p-6">
                <FeedbackList />
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>

      {/* Homework Helper FAB */}
      <Link
        to="/homework-helper"
        className="fixed bottom-8 right-8 bg-indigo-600 text-white p-4 rounded-full shadow-lg hover:bg-indigo-700 transition-transform transform hover:scale-110 z-50"
        title="AI Homework Helper"
      >
        <FaRobot size={24} />
      </Link>
    </div>
  );
};

export default StudentDashboard; 