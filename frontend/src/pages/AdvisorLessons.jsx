import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import axios from 'axios';

const AdvisorLessons = () => {
  const { currentUser } = useAuth();
  const [lessons, setLessons] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [gradeFilter, setGradeFilter] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [assigningLesson, setAssigningLesson] = useState(null);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [assignmentMessage, setAssignmentMessage] = useState({ text: '', type: '' });

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

  // Subject options for filtering
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

  // Fetch lessons
  useEffect(() => {
    const fetchLessons = async () => {
      try {
        setLoading(true);
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
        setError('Failed to fetch lessons. Please try again later.');
        console.error('Error fetching lessons:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLessons();
  }, [gradeFilter, subjectFilter]);

  // Fetch students (for assignment dropdown)
  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await axios.get('http://localhost:8000/api/user/advisor/students/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        if (response.data) {
          setStudents(response.data);
        }
      } catch (err) {
        console.error('Error fetching students:', err);
      }
    };

    // Only fetch students when the assign modal is shown
    if (showAssignModal) {
      fetchStudents();
    }
  }, [showAssignModal]);

  // Handle assigning a lesson to a student
  const assignLessonToStudent = async () => {
    if (!selectedStudent || !assigningLesson) {
      return;
    }

    // Clear any previous messages
    setAssignmentMessage({ text: '', type: '' });

    try {
      setLoading(true);
      const token = localStorage.getItem('accessToken');
      const response = await axios.post('http://localhost:8000/api/content/advisor/lessons/assign/', 
        { 
          lesson_id: assigningLesson.id,
          student_id: selectedStudent
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.data && response.data.status === 'success') {
        setAssignmentMessage({ 
          text: response.data.message, 
          type: 'success' 
        });
        
        // Close modal after short delay on success
        setTimeout(() => {
          setShowAssignModal(false);
          setSelectedStudent(null);
          setAssigningLesson(null);
          setAssignmentMessage({ text: '', type: '' });
        }, 1500);
      }
    } catch (err) {
      console.error('Error assigning lesson:', err);
      
      // Check if the error response contains a message
      if (err.response && err.response.data) {
        // Handle the specific case of student already enrolled
        if (err.response.data.message && err.response.data.message.includes('already enrolled')) {
          setAssignmentMessage({ 
            text: err.response.data.message, 
            type: 'warning' 
          });
        } else if (err.response.data.message) {
          setAssignmentMessage({ 
            text: err.response.data.message, 
            type: 'error' 
          });
        } else {
          setAssignmentMessage({ 
            text: 'Failed to assign lesson. Please try again later.', 
            type: 'error' 
          });
        }
      } else {
        setAssignmentMessage({ 
          text: 'Failed to assign lesson. Please try again later.', 
          type: 'error' 
        });
      }
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
        <h1 className="text-2xl font-bold text-gray-900">Lessons</h1>
        <p className="text-gray-600">Browse and assign lessons to students</p>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-wrap items-center gap-4">
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
            <div>
              <label htmlFor="subject-filter" className="mr-2 text-gray-700">Filter by Subject:</label>
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
        </div>

        {loading && !showAssignModal ? (
          <div className="text-center py-6">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading lessons...</p>
          </div>
        ) : error ? (
          <div className="bg-red-100 text-red-700 p-4 m-6 rounded-lg">
            {error}
          </div>
        ) : lessons.length === 0 ? (
          <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg text-center py-10 m-6">
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
                          setAssigningLesson(lesson);
                          setShowAssignModal(true);
                          setAssignmentMessage({ text: '', type: '' });
                        }}
                        className="text-indigo-600 hover:text-indigo-900"
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

      {/* Assign Lesson Modal */}
      {showAssignModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-medium">Assign Lesson to Student</h3>
            </div>
            <div className="p-4">
              <p className="mb-4">
                <span className="font-medium">Lesson:</span> {assigningLesson?.name}
              </p>
              <div className="mb-4">
                <label htmlFor="student-select" className="block mb-2 text-sm font-medium text-gray-700">
                  Select Student
                </label>
                <select
                  id="student-select"
                  value={selectedStudent || ''}
                  onChange={(e) => setSelectedStudent(e.target.value)}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">-- Select a student --</option>
                  {students.map(student => (
                    <option key={student.id} value={student.id}>
                      {student.first_name} {student.last_name} - {student.grade ? `Grade ${student.grade}` : 'No grade'}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Assignment Message */}
              {assignmentMessage.text && (
                <div className={`mb-4 p-3 rounded ${
                  assignmentMessage.type === 'success' 
                    ? 'bg-green-100 text-green-700' 
                    : assignmentMessage.type === 'warning'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-red-100 text-red-700'
                }`}>
                  {assignmentMessage.text}
                </div>
              )}
            </div>
            <div className="px-4 py-3 bg-gray-50 flex justify-end space-x-2 rounded-b-lg">
              <button
                type="button"
                onClick={() => {
                  setShowAssignModal(false);
                  setSelectedStudent(null);
                  setAssigningLesson(null);
                  setAssignmentMessage({ text: '', type: '' });
                }}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={assignLessonToStudent}
                disabled={!selectedStudent || loading}
                className={`px-4 py-2 rounded-md text-sm font-medium text-white ${
                  selectedStudent && !loading
                    ? 'bg-indigo-600 hover:bg-indigo-700'
                    : 'bg-indigo-400 cursor-not-allowed'
                }`}
              >
                {loading ? (
                  <>
                    <span className="inline-block animate-spin mr-2">⟳</span>
                    Assigning...
                  </>
                ) : (
                  'Assign Lesson'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
};

export default AdvisorLessons; 