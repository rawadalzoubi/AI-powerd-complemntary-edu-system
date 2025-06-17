import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import axios from 'axios';
import StudentDetails from '../components/students/StudentDetails';
import AssignLessonsModal from '../components/lessons/AssignLessonsModal';

const AdvisorStudents = () => {
  const { currentUser } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [gradeFilter, setGradeFilter] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showAssignLessonsModal, setShowAssignLessonsModal] = useState(false);

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

  // Check for URL parameters on component mount
  useEffect(() => {
    const handleUrlParams = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const view = urlParams.get('view');
      const studentId = urlParams.get('studentId');
      
      if (studentId) {
        try {
          const token = localStorage.getItem('accessToken');
          const response = await axios.get(`http://localhost:8000/api/user/advisor/students/`, {
            headers: {
              Authorization: `Bearer ${token}`
            }
          });
          
          if (response.data) {
            const student = response.data.find(s => s.id === parseInt(studentId));
            if (student) {
              setSelectedStudent(student);
              
              if (view === 'details') {
                setShowDetailsModal(true);
              } else if (view === 'assign') {
                setShowAssignLessonsModal(true);
              }
            }
          }
        } catch (err) {
          console.error('Error fetching student details from URL params:', err);
        }
      }
      
      // Clean up the URL after handling parameters
      if (view || studentId) {
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
      }
    };
    
    handleUrlParams();
  }, []);

  // Fetch students
    const fetchStudents = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('accessToken');
        let url = 'http://localhost:8000/api/user/advisor/students/';
        
        // Add query parameters if filters are set
        if (gradeFilter) {
          url += `?grade=${gradeFilter}`;
        }
        
        const response = await axios.get(url, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        if (response.data) {
          setStudents(response.data);
        }
      } catch (err) {
        setError('Failed to fetch students. Please try again later.');
        console.error('Error fetching students:', err);
      } finally {
        setLoading(false);
      }
    };

  useEffect(() => {
    fetchStudents();
  }, [gradeFilter]);

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

  // Handle view details button click
  const handleViewDetails = (student) => {
    setSelectedStudent(student);
    setShowDetailsModal(true);
  };

  // Handle assign lessons button click
  const handleAssignLessons = (student) => {
    setSelectedStudent(student);
    setShowAssignLessonsModal(true);
  };

  // Handle closing details modal
  const handleCloseDetailsModal = (action) => {
    setShowDetailsModal(false);
    // If the user was trying to assign lessons from the details view,
    // we'll open the assign lessons modal
    if (action === 'assign' && selectedStudent) {
      setShowAssignLessonsModal(true);
    }
  };

  // Handle closing assign lessons modal
  const handleCloseAssignLessonsModal = () => {
    setShowAssignLessonsModal(false);
  };

  // Handle after lessons assigned
  const handleLessonsAssigned = () => {
    // Refresh the student data after assigning lessons
    fetchStudents();
  };

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Students</h1>
        <p className="text-gray-600">View and manage students</p>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-4">
            <div>
              <label htmlFor="grade-filter" className="mr-2 text-gray-700">Filter by Grade:</label>
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
          </div>
        </div>

        {loading ? (
          <div className="text-center py-6">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading students...</p>
          </div>
        ) : error ? (
          <div className="bg-red-100 text-red-700 p-4 m-6 rounded-lg">
            {error}
          </div>
        ) : students.length === 0 ? (
          <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg text-center py-10 m-6">
            <i className="fas fa-users text-gray-400 text-4xl mb-3"></i>
            <p className="text-gray-600">No students found for the selected grade.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Student Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {students.map((student) => (
                  <tr key={student.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 flex-shrink-0">
                          {student.profile_image ? (
                            <img 
                              className="h-10 w-10 rounded-full" 
                              src={student.profile_image} 
                              alt={`${student.first_name} ${student.last_name}`} 
                            />
                          ) : (
                            <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                              <span className="text-indigo-700 font-medium">
                                {student.first_name?.charAt(0)}{student.last_name?.charAt(0)}
                              </span>
                            </div>
                          )}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {student.first_name} {student.last_name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {student.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {student.grade ? `Grade ${student.grade}` : 'Not set'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(student.date_joined)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleViewDetails(student)}
                        className="text-indigo-600 hover:text-indigo-900 mr-3"
                      >
                        View Details
                      </button>
                      <button
                        onClick={() => handleAssignLessons(student)}
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

      {/* Student Details Modal */}
      {showDetailsModal && selectedStudent && (
        <StudentDetails 
          student={selectedStudent}
          onClose={handleCloseDetailsModal}
        />
      )}

      {/* Assign Lessons Modal */}
      {showAssignLessonsModal && selectedStudent && (
        <AssignLessonsModal 
          student={selectedStudent}
          onClose={handleCloseAssignLessonsModal}
          onAssigned={handleLessonsAssigned}
        />
      )}
    </DashboardLayout>
  );
};

export default AdvisorStudents; 