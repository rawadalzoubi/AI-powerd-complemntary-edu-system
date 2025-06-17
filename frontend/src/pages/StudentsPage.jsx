import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../components/layout/DashboardLayout';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import StudentAnswers from '../components/students/StudentAnswers';

const StudentsPage = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGrade, setSelectedGrade] = useState('');
  const [showAnswersModal, setShowAnswersModal] = useState(false);
  const [selectedStudentId, setSelectedStudentId] = useState(null);
  const [selectedStudentName, setSelectedStudentName] = useState('');

  // Function to generate avatar initials from name
  const getInitials = (name) => {
    if (!name) return '';
    return name.split(' ')
      .map(part => part.charAt(0))
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  // Function to get avatar color based on name
  const getAvatarColor = (name) => {
    if (!name) return { bg: 'bg-gray-100', text: 'text-gray-800' };
    
    // Create a simple hash of the name for consistent colors
    const hash = name.split('').reduce((acc, char) => {
      return char.charCodeAt(0) + acc;
    }, 0);
    
    // List of color combinations
    const colors = [
      { bg: 'bg-indigo-100', text: 'text-indigo-800' },
      { bg: 'bg-pink-100', text: 'text-pink-800' },
      { bg: 'bg-green-100', text: 'text-green-800' },
      { bg: 'bg-purple-100', text: 'text-purple-800' },
      { bg: 'bg-blue-100', text: 'text-blue-800' },
      { bg: 'bg-yellow-100', text: 'text-yellow-800' },
      { bg: 'bg-red-100', text: 'text-red-800' },
      { bg: 'bg-teal-100', text: 'text-teal-800' }
    ];
    
    return colors[hash % colors.length];
  };

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setLoading(true);
        
        // Get auth token
        const token = localStorage.getItem('accessToken');
        if (!token) {
          throw new Error('Authentication required');
        }
        
        // Fetch students from backend API
        const response = await axios.get('http://localhost:8000/api/user/students/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        if (response.data) {
          // Transform API data to the format needed by the UI
          const formattedStudents = response.data.map(student => {
            const avatarColor = getAvatarColor(student.first_name + ' ' + student.last_name);
            
            return {
              id: student.id,
              name: `${student.first_name} ${student.last_name}`,
              email: student.email,
              grade: student.grade || 'N/A',
              enrolledLessons: student.enrolled_lessons || [],
              progress: student.progress || 0,
              lastActive: student.last_login || new Date().toISOString().split('T')[0],
              avatarInitials: getInitials(`${student.first_name} ${student.last_name}`),
              avatarColor: avatarColor.bg,
              textColor: avatarColor.text
            };
          });
          
          setStudents(formattedStudents);
        }
      } catch (err) {
        console.error('Error fetching students:', err);
        setError('Failed to load students. Please try again later.');
        
        // If unauthorized, redirect to login
        if (err.response && err.response.status === 401) {
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, [navigate]);

  // Filter students based on search term and selected grade
  const filteredStudents = students.filter(student => {
    const matchesSearch = student.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          student.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesGrade = selectedGrade === '' || student.grade === selectedGrade;
    
    return matchesSearch && matchesGrade;
  });

  const handleViewAnswers = (student) => {
    setSelectedStudentId(student.id);
    setSelectedStudentName(student.name);
    setShowAnswersModal(true);
  };

  const closeAnswersModal = () => {
    setShowAnswersModal(false);
    setSelectedStudentId(null);
  };

  return (
    <DashboardLayout>
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Students Management</h2>
        
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div className="w-full md:w-1/2">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <i className="fas fa-search text-gray-400"></i>
              </div>
              <input
                type="text"
                placeholder="Search students by name or email..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          
          <div className="flex gap-4">
            <select
              value={selectedGrade}
              onChange={(e) => setSelectedGrade(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Grades</option>
              <option value="9">Grade 9</option>
              <option value="10">Grade 10</option>
              <option value="11">Grade 11</option>
              <option value="12">Grade 12</option>
            </select>
            
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
              <i className="fas fa-plus mr-2"></i> Add Student
            </button>
          </div>
        </div>
        
        {loading ? (
          <div className="text-center py-10">
            <i className="fas fa-spinner fa-spin text-indigo-600 text-2xl"></i>
            <p className="mt-2 text-gray-600">Loading students...</p>
          </div>
        ) : error ? (
          <div className="bg-red-100 text-red-700 p-4 rounded-lg">
            {error}
          </div>
        ) : filteredStudents.length === 0 ? (
          <div className="text-center py-10 bg-gray-50 rounded-lg border border-dashed border-gray-300">
            <i className="fas fa-users text-gray-400 text-4xl mb-3"></i>
            <p className="text-gray-600">No students found matching your criteria.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Student
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Enrolled Lessons
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Active
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredStudents.map((student) => (
                  <tr key={student.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className={`flex-shrink-0 h-10 w-10 rounded-full ${student.avatarColor} flex items-center justify-center`}>
                          <span className={`${student.textColor} font-medium`}>{student.avatarInitials}</span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{student.name}</div>
                          <div className="text-sm text-gray-500">Grade {student.grade}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{student.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{student.enrolledLessons.length} Lessons</div>
                      <div className="text-xs text-gray-500">{student.enrolledLessons.join(', ')}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div 
                          className={`h-2.5 rounded-full ${
                            student.progress >= 80 ? 'bg-green-600' : 
                            student.progress >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                          }`} 
                          style={{ width: `${student.progress}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{student.progress}% Complete</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(student.lastActive).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-3">
                        <button 
                          className="text-indigo-600 hover:text-indigo-900"
                          onClick={() => handleViewAnswers(student)}
                          title="View Student Answers"
                        >
                          <i className="fas fa-clipboard-check"></i>
                        </button>
                        <button className="text-blue-600 hover:text-blue-900" title="Message Student">
                          <i className="fas fa-envelope"></i>
                        </button>
                        <button className="text-red-600 hover:text-red-900" title="Remove Student">
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

      {/* Student Answers Modal */}
      {showAnswersModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-lg max-w-4xl w-full">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-lg font-semibold">{selectedStudentName}'s Answers</h3>
              <button 
                onClick={closeAnswersModal}
                className="text-gray-500 hover:text-gray-700"
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div>
              <StudentAnswers studentId={selectedStudentId} onClose={closeAnswersModal} />
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
};

export default StudentsPage; 