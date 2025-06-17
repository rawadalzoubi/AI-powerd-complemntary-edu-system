import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
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

const AdvisorDashboard = () => {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('students');
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [gradeFilter, setGradeFilter] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [studentPerformance, setStudentPerformance] = useState(null);

  // Grade levels for filtering
  const gradeOptions = [
    { value: '1', label: '1st Grade' },
    { value: '2', label: '2nd Grade' },
    { value: '3', label: '3rd Grade' },
    { value: '4', label: '4th Grade' },
    { value: '5', label: '5th Grade' },
    { value: '6', label: '6th Grade' },
    { value: '7', label: '7th Grade' },
    { value: '8', label: '8th Grade' },
    { value: '9', label: '9th Grade' },
    { value: '10', label: '10th Grade' },
    { value: '11', label: '11th Grade' },
    { value: '12', label: '12th Grade' },
  ];

  // Subject options for filtering (example - adjust based on your system's subjects)
  const subjectOptions = [
    'Mathematics',
    'Science',
    'English',
    'History',
    'Geography',
    'Art',
    'Music',
    'Physical Education'
  ];

  // Fetch students
  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('accessToken');
        let url = 'http://localhost:8000/api/user/advisor/students/';
        
        if (gradeFilter) {
          url = `http://localhost:8000/api/user/advisor/students/grade/${gradeFilter}/`;
        }
        
        const response = await axios.get(url, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        if (response.data) {
          setStudents(response.data);
          setFilteredStudents(response.data);
        }
      } catch (err) {
        setError('Failed to fetch students. Please try again later.');
        console.error('Error fetching students:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, [gradeFilter]);

  // Fetch lessons for filtering
  useEffect(() => {
    const fetchLessons = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        let url = 'http://localhost:8000/api/content/advisor/lessons/filter/';
        
        // Add query parameters if filters are set
        const params = new URLSearchParams();
        if (subjectFilter) params.append('subject', subjectFilter);
        if (gradeFilter) params.append('grade_level', gradeFilter);
        
        if (params.toString()) {
          url += `?${params.toString()}`;
        }
        
        const response = await axios.get(url, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        if (response.data) {
          setLessons(response.data);
        }
      } catch (err) {
        console.error('Error fetching filtered lessons:', err);
      }
    };

    if (activeTab === 'lessons') {
      fetchLessons();
    }
  }, [activeTab, subjectFilter, gradeFilter]);

  // Fetch student performance data
  const fetchStudentPerformance = async (studentId) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('accessToken');
      const response = await axios.get(`http://localhost:8000/api/user/advisor/students/${studentId}/performance/`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (response.data) {
        setStudentPerformance(response.data);
        setActiveTab('performance');
      }
    } catch (err) {
      setError('Failed to fetch student performance. Please try again later.');
      console.error('Error fetching student performance:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle assigning a lesson to a student
  const assignLessonToStudent = async (lessonId, studentId) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('accessToken');
      const response = await axios.post(`http://localhost:8000/api/content/advisor/lessons/assign/`, 
        { 
          lesson_id: lessonId,
          student_id: studentId
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.data && response.data.status === 'success') {
        alert(response.data.message);
        
        // If we're viewing the student's performance, refresh it
        if (selectedStudent && selectedStudent.id === studentId) {
          fetchStudentPerformance(studentId);
        }
      }
    } catch (err) {
      setError('Failed to assign lesson. Please try again later.');
      console.error('Error assigning lesson:', err);
    } finally {
      setLoading(false);
    }
  };

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

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Advisor Dashboard</h1>
        <p className="text-gray-600">Manage students, track performance, and assign lessons</p>
      </div>

      {/* Tabs Navigation */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button 
              onClick={() => setActiveTab('students')}
              className={`relative px-4 py-3 flex items-center text-sm font-medium ${
                activeTab === 'students' 
                  ? 'text-blue-600 border-b-2 border-blue-500' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <i className="fas fa-users mr-2"></i> Students
            </button>
            <button 
              onClick={() => setActiveTab('lessons')}
              className={`relative px-4 py-3 flex items-center text-sm font-medium ${
                activeTab === 'lessons' 
                  ? 'text-blue-600 border-b-2 border-blue-500' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <i className="fas fa-book mr-2"></i> Lessons
            </button>
            {selectedStudent && (
              <button
                onClick={() => setActiveTab('performance')}
                className={`relative px-4 py-3 flex items-center text-sm font-medium ${
                  activeTab === 'performance' 
                    ? 'text-blue-600 border-b-2 border-blue-500' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <i className="fas fa-chart-line mr-2"></i> Student Performance
              </button>
            )}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Students Tab */}
          {activeTab === 'students' && (
            <div>
              <div className="mb-6 flex items-center">
                <label htmlFor="grade-filter" className="mr-2">Filter by Grade:</label>
                <select 
                  id="grade-filter" 
                  value={gradeFilter} 
                  onChange={(e) => setGradeFilter(e.target.value)}
                  className="border border-gray-300 rounded-md shadow-sm p-2"
                >
                  <option value="">All Grades</option>
                  {gradeOptions.map(grade => (
                    <option key={grade.value} value={grade.value}>{grade.label}</option>
                  ))}
                </select>
              </div>

              {loading ? (
                <div className="text-center py-6">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
                  <p className="mt-2 text-gray-600">Loading students...</p>
                </div>
              ) : error ? (
                <div className="bg-red-100 text-red-700 p-4 rounded-lg">
                  {error}
                </div>
              ) : filteredStudents.length === 0 ? (
                <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg text-center py-10">
                  <i className="fas fa-users text-gray-400 text-4xl mb-3"></i>
                  <p className="text-gray-600">No students found for the selected grade.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Login</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {filteredStudents.map((student) => (
                        <tr key={student.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              {student.first_name} {student.last_name}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-500">{student.email}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-500">
                              {student.grade ? 
                                gradeOptions.find(g => g.value === student.grade)?.label || `Grade ${student.grade}` 
                                : 'Not specified'}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {student.last_login ? formatDate(student.last_login) : 'Never'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button
                              onClick={() => {
                                setSelectedStudent(student);
                                fetchStudentPerformance(student.id);
                              }}
                              className="text-blue-600 hover:text-blue-900 mr-4"
                            >
                              View Performance
                            </button>
                            <button
                              onClick={() => window.location.href = `/advisor/students?view=details&studentId=${student.id}`}
                              className="text-indigo-600 hover:text-indigo-900 mr-4"
                            >
                              View Details
                            </button>
                            <button
                              onClick={() => window.location.href = `/advisor/students?view=assign&studentId=${student.id}`}
                              className="text-green-600 hover:text-green-900"
                            >
                              Assign Lessons
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Lessons Tab */}
          {activeTab === 'lessons' && (
            <div>
              <div className="mb-6 flex flex-wrap gap-4">
                <div>
                  <label htmlFor="grade-filter-lessons" className="mr-2">Filter by Grade:</label>
                  <select 
                    id="grade-filter-lessons" 
                    value={gradeFilter} 
                    onChange={(e) => setGradeFilter(e.target.value)}
                    className="border border-gray-300 rounded-md shadow-sm p-2"
                  >
                    <option value="">All Grades</option>
                    {gradeOptions.map(grade => (
                      <option key={grade.value} value={grade.value}>{grade.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="subject-filter" className="mr-2">Filter by Subject:</label>
                  <select 
                    id="subject-filter" 
                    value={subjectFilter} 
                    onChange={(e) => setSubjectFilter(e.target.value)}
                    className="border border-gray-300 rounded-md shadow-sm p-2"
                  >
                    <option value="">All Subjects</option>
                    {subjectOptions.map(subject => (
                      <option key={subject} value={subject}>{subject}</option>
                    ))}
                  </select>
                </div>
              </div>

              {loading ? (
                <div className="text-center py-6">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
                  <p className="mt-2 text-gray-600">Loading lessons...</p>
                </div>
              ) : error ? (
                <div className="bg-red-100 text-red-700 p-4 rounded-lg">
                  {error}
                </div>
              ) : lessons.length === 0 ? (
                <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg text-center py-10">
                  <i className="fas fa-book text-gray-400 text-4xl mb-3"></i>
                  <p className="text-gray-600">No lessons found for the selected filters.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lesson Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subject</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade Level</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {lessons.map((lesson) => (
                        <tr key={lesson.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{lesson.name}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {lesson.subject}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {lesson.level_display || `Grade ${lesson.level}`}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(lesson.created_at)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button
                              onClick={() => {
                                if (selectedStudent) {
                                  assignLessonToStudent(lesson.id, selectedStudent.id);
                                } else {
                                  alert("Please select a student first to assign this lesson.");
                                  setActiveTab('students');
                                }
                              }}
                              className="text-blue-600 hover:text-blue-900"
                              disabled={!selectedStudent}
                            >
                              Assign to Student
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Performance Tab */}
          {activeTab === 'performance' && selectedStudent && (
            <div>
              <div className="bg-blue-50 rounded-lg p-4 mb-6">
                <h2 className="text-lg font-medium text-blue-800">Student: {selectedStudent.first_name} {selectedStudent.last_name}</h2>
                <p className="text-blue-600">Grade: {selectedStudent.grade ? 
                  gradeOptions.find(g => g.value === selectedStudent.grade)?.label || `Grade ${selectedStudent.grade}` 
                  : 'Not specified'}</p>
              </div>

              {loading ? (
                <div className="text-center py-6">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
                  <p className="mt-2 text-gray-600">Loading performance data...</p>
                </div>
              ) : error ? (
                <div className="bg-red-100 text-red-700 p-4 rounded-lg">
                  {error}
                </div>
              ) : !studentPerformance || studentPerformance.enrollments.length === 0 ? (
                <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg text-center py-10">
                  <i className="fas fa-chart-line text-gray-400 text-4xl mb-3"></i>
                  <p className="text-gray-600">No lessons assigned to this student yet.</p>
                  <button 
                    onClick={() => setActiveTab('lessons')}
                    className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Assign Lessons
                  </button>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <h3 className="text-lg font-medium mb-4">Enrolled Lessons</h3>
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lesson Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subject</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade Level</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Activity</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {studentPerformance.enrollments.map((enrollment) => (
                        <tr key={enrollment.lesson_id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{enrollment.lesson_name}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {enrollment.subject}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {enrollment.grade_level ? 
                              gradeOptions.find(g => g.value === enrollment.grade_level)?.label || `Grade ${enrollment.grade_level}` 
                              : 'Not specified'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                              <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${enrollment.progress}%` }}></div>
                            </div>
                            <span className="text-xs text-gray-500">{enrollment.progress}% completed</span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(enrollment.last_activity)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdvisorDashboard; 