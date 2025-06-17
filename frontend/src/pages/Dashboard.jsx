import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import lessonService from '../services/lessonService';
import LessonModal from '../components/lessons/LessonModal';
import axios from 'axios';

const StatCard = ({ title, value, icon, trend, trendText, color }) => (
  <div className="bg-white rounded-lg shadow p-6 flex items-start">
    <div className="flex-1">
      <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      <p className="text-4xl font-bold mt-2">{value}</p>
      {trend && (
        <p className={`text-xs mt-2 ${trend > 0 ? 'text-green-500' : 'text-red-500'}`}>
          <span>{trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%</span> {trendText}
        </p>
      )}
    </div>
    <div className={`rounded-full p-3 bg-${color}-100`}>
      <i className={`fas ${icon} text-${color}-500 text-xl`}></i>
    </div>
  </div>
);

const Dashboard = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('lessons');
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showNewLessonModal, setShowNewLessonModal] = useState(false);
  const [stats, setStats] = useState({
    students: 0,
    studentsTrend: 0,
    lessons: 0,
    lessonsTrend: 0,
    assignments: 0,
    pendingAssignments: 0
  });

  // Redirect logic for different user roles
  useEffect(() => {
    if (currentUser && currentUser.role) {
      const role = currentUser.role.toLowerCase();
      
      // Redirect students to student dashboard
      if (role === 'student') {
        navigate('/student/dashboard');
      }
      // Redirect advisors to advisor dashboard
      else if (role === 'advisor') {
        navigate('/advisor/dashboard');
      }
      // Teachers stay on this dashboard
    }
  }, [currentUser, navigate]);

  // Fetch lessons and statistics
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Get lessons
        const lessonsData = await lessonService.getLessons();
        setLessons(lessonsData);
        
        // Get dashboard statistics from the backend
        try {
          const token = localStorage.getItem('accessToken');
          // This endpoint should be created in your backend to provide dashboard stats
          const response = await axios.get('http://localhost:8000/api/content/dashboard-stats/', {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          
          if (response.data) {
            setStats({
              students: response.data.total_students || 0,
              studentsTrend: response.data.students_trend || 0,
              lessons: response.data.total_lessons || lessonsData.length,
              lessonsTrend: response.data.lessons_trend || 0,
              assignments: response.data.graded_assignments || 0,
              pendingAssignments: response.data.pending_assignments || 0
            });
          } else {
            // Fallback to counting actual lessons if stats endpoint not available
            setStats(prev => ({
              ...prev,
              lessons: lessonsData.length
            }));
          }
        } catch (statsError) {
          console.error('Failed to fetch dashboard statistics:', statsError);
          // Fallback: Use real lessons count at minimum
          setStats(prev => ({
            ...prev,
            lessons: lessonsData.length
          }));
        }
      } catch (err) {
        setError('Failed to load data. Please try again later.');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Helper function to format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }).format(date);
  };

  // Content type indicator component
  const ContentTypeIndicator = ({ type }) => {
    const types = {
      video: { icon: 'fa-video', bg: 'bg-blue-100', text: 'text-blue-500' },
      pdf: { icon: 'fa-file-pdf', bg: 'bg-red-100', text: 'text-red-500' },
      exercise: { icon: 'fa-tasks', bg: 'bg-green-100', text: 'text-green-500' }
    };
    
    const style = types[type.toLowerCase()] || { icon: 'fa-file', bg: 'bg-gray-100', text: 'text-gray-500' };
    
    return (
      <span className={`inline-flex items-center ${style.bg} ${style.text} px-2 py-1 rounded-md mr-2`}>
        <i className={`fas ${style.icon} mr-1`}></i> {type}
      </span>
    );
  };

  return (
    <DashboardLayout>
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard 
          title="Total Students" 
          value={stats.students} 
          icon="fa-users" 
          trend={stats.studentsTrend} 
          trendText="from last month" 
          color="indigo" 
        />
        <StatCard 
          title="Lessons Uploaded" 
          value={stats.lessons} 
          icon="fa-book" 
          trend={stats.lessonsTrend} 
          trendText="new this week" 
          color="blue" 
        />
        <StatCard 
          title="Assignments Graded" 
          value={stats.assignments} 
          icon="fa-check-circle" 
          color="green" 
        />
      </div>

      {/* Render the LessonModal conditionally */}
      <LessonModal
        isOpen={showNewLessonModal}
        onClose={() => setShowNewLessonModal(false)}
        onSave={async (lessonData, callback) => {
          try {
            const createdLesson = await lessonService.createLesson(lessonData);
            if (callback && typeof callback === 'function') {
              callback(createdLesson.id);
            }
            setShowNewLessonModal(false);
            // Refresh lessons list
            const data = await lessonService.getLessons();
            setLessons(data);
          } catch (err) {
            console.error('Error creating lesson:', err);
            setError('Failed to create lesson. Please try again.');
          }
        }}
      />

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button 
              onClick={() => setActiveTab('lessons')}
              className={`relative px-4 py-3 flex items-center text-sm font-medium ${
                activeTab === 'lessons' 
                  ? 'text-indigo-600 border-b-2 border-indigo-500' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <i className="fas fa-book mr-2"></i> Lessons
            </button>
            <button 
              onClick={() => setActiveTab('students')}
              className={`relative px-4 py-3 flex items-center text-sm font-medium ${
                activeTab === 'students' 
                  ? 'text-indigo-600 border-b-2 border-indigo-500' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <i className="fas fa-users mr-2"></i> Students
            </button>
          <button
              onClick={() => setActiveTab('performance')}
              className={`relative px-4 py-3 flex items-center text-sm font-medium ${
                activeTab === 'performance' 
                  ? 'text-indigo-600 border-b-2 border-indigo-500' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
          >
              <i className="fas fa-chart-line mr-2"></i> Performance
          </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'lessons' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-medium">Upload New Lesson</h2>
              </div>

              <h2 className="text-lg font-medium mb-4">Recent Lessons</h2>
              
              {loading ? (
                <div className="text-center py-6">
                  <i className="fas fa-spinner fa-spin text-indigo-600 text-2xl"></i>
                  <p className="mt-2 text-gray-600">Loading lessons...</p>
                </div>
              ) : error ? (
                <div className="bg-red-100 text-red-700 p-4 rounded-lg">
                  {error}
                </div>
              ) : lessons.length === 0 ? (
                <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg text-center py-10">
                  <i className="fas fa-book text-gray-400 text-4xl mb-3"></i>
                  <p className="text-gray-600">No lessons found. Create your first lesson!</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade & Subject</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Content</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {lessons.slice(0, 5).map((lesson) => (
                        <tr key={lesson.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="font-medium text-gray-900">{lesson.name}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="px-2 py-1 text-xs rounded-full bg-indigo-100 text-indigo-800">
                              Grade {lesson.level} - {lesson.subject}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex">
                              {lesson.contents && lesson.contents.length > 0 ? (
                                <>
                                  {lesson.contents.some(c => c.content_type === 'VIDEO') && (
                                    <ContentTypeIndicator type="Video" />
                                  )}
                                  {lesson.contents.some(c => c.content_type === 'PDF') && (
                                    <ContentTypeIndicator type="PDF" />
                                  )}
                                  {lesson.quizzes && lesson.quizzes.length > 0 && (
                                    <ContentTypeIndicator type="Exercise" />
                                  )}
                                </>
                              ) : (
                                <span className="text-gray-400 text-sm">No content</span>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(lesson.created_at)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <div className="flex space-x-3">
                              <Link to={`/lessons/${lesson.id}`} className="text-indigo-600 hover:text-indigo-900">
                                <i className="fas fa-edit"></i>
                              </Link>
                              <button className="text-red-600 hover:text-red-900">
                                <i className="fas fa-trash-alt"></i>
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === 'students' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-medium">Students Management</h2>
                <Link 
                  to="/students"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center"
                >
                  <i className="fas fa-users mr-2"></i> All Students
                </Link>
              </div>

              <h2 className="text-lg font-medium mb-4">Students in Your Lessons</h2>
              
              {loading ? (
                <div className="text-center py-6">
                  <i className="fas fa-spinner fa-spin text-indigo-600 text-2xl"></i>
                  <p className="mt-2 text-gray-600">Loading students...</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Enrolled Lessons</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {/* Sample student data - replace with actual data */}
                      <tr>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                              <span className="text-indigo-800 font-medium">JD</span>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">John Doe</div>
                              <div className="text-sm text-gray-500">Grade 9</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">john.doe@example.com</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">3 Lessons</div>
                          <div className="text-xs text-gray-500">Math, Science, History</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="w-full bg-gray-200 rounded-full h-2.5">
                            <div className="bg-green-600 h-2.5 rounded-full" style={{ width: '85%' }}></div>
                          </div>
                          <div className="text-xs text-gray-500 mt-1">85% Complete</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="flex space-x-3">
                            <button className="text-indigo-600 hover:text-indigo-900">
                              <i className="fas fa-eye"></i>
                            </button>
                            <button className="text-blue-600 hover:text-blue-900">
                              <i className="fas fa-envelope"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                      <tr>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="h-10 w-10 rounded-full bg-pink-100 flex items-center justify-center">
                              <span className="text-pink-800 font-medium">JS</span>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">Jane Smith</div>
                              <div className="text-sm text-gray-500">Grade 10</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">jane.smith@example.com</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">2 Lessons</div>
                          <div className="text-xs text-gray-500">Science, Art</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="w-full bg-gray-200 rounded-full h-2.5">
                            <div className="bg-green-600 h-2.5 rounded-full" style={{ width: '65%' }}></div>
                          </div>
                          <div className="text-xs text-gray-500 mt-1">65% Complete</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="flex space-x-3">
                            <button className="text-indigo-600 hover:text-indigo-900">
                              <i className="fas fa-eye"></i>
                            </button>
                            <button className="text-blue-600 hover:text-blue-900">
                              <i className="fas fa-envelope"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
              </div>
              )}
            </div>
          )}

          {activeTab === 'performance' && (
            <div className="text-center py-10 text-gray-500">
              Performance metrics and analytics will be displayed here.
          </div>
          )}
        </div>
    </div>
    </DashboardLayout>
  );
};

export default Dashboard; 