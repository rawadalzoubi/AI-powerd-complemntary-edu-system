import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import advisorService from '../../services/advisorService';

const StudentDetails = ({ student, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [assignedLessons, setAssignedLessons] = useState([]);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  const fetchStudentLessons = async () => {
    if (!student || !student.id) return;
    
    try {
      setLoading(true);
      const data = await advisorService.getStudentLessons(student.id);
      setAssignedLessons(data || []);
      setError('');
    } catch (err) {
      console.error('Error fetching student details:', err);
      setError('Failed to fetch lessons. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudentLessons();
  }, [student]);

  // Handle deleting a lesson from the student
  const handleDeleteLesson = async (lessonId) => {
    if (!window.confirm('Are you sure you want to remove this lesson from the student?')) {
      return;
    }
    
    try {
      setDeleteLoading(true);
      await advisorService.deleteStudentLesson(student.id, lessonId);
      
      // Update the lessons list after deletion
      setAssignedLessons(prevLessons => prevLessons.filter(lesson => lesson.id !== lessonId));
      
    } catch (err) {
      console.error('Error deleting student lesson:', err);
      setError('Failed to delete lesson. Please try again.');
    } finally {
      setDeleteLoading(false);
    }
  };

  if (!student) {
    return null;
  }

  // Format date helper
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Handle view performance button click
  const handleViewPerformance = () => {
    onClose(); // Close the modal
    navigate(`/advisor/students/${student.id}/performance`); // Navigate to performance page
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">Student Details</h2>
            <button 
              onClick={() => onClose()}
              className="text-gray-400 hover:text-gray-500"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <div className="p-6">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="md:w-1/3">
              <div className="bg-gray-50 rounded-lg p-4 shadow-sm">
                <div className="flex justify-center mb-4">
                  {student.profile_image ? (
                    <img 
                      src={student.profile_image} 
                      alt={`${student.first_name} ${student.last_name}`}
                      className="h-32 w-32 rounded-full object-cover" 
                    />
                  ) : (
                    <div className="h-32 w-32 rounded-full bg-indigo-100 flex items-center justify-center">
                      <span className="text-indigo-700 text-3xl font-medium">
                        {student.first_name?.charAt(0)}{student.last_name?.charAt(0)}
                      </span>
                    </div>
                  )}
                </div>
                
                <h3 className="text-xl font-semibold text-center text-gray-900 mb-2">
                  {student.first_name} {student.last_name}
                </h3>
                
                <div className="space-y-2 mt-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Email:</span>
                    <span className="text-gray-900 font-medium">{student.email}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Grade:</span>
                    <span className="text-gray-900 font-medium">{student.grade ? `Grade ${student.grade}` : 'Not set'}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Joined:</span>
                    <span className="text-gray-900 font-medium">
                      {formatDate(student.date_joined)}
                    </span>
                  </div>

                  {student.last_login && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Active:</span>
                      <span className="text-gray-900 font-medium">
                        {formatDate(student.last_login)}
                      </span>
                    </div>
                  )}
                </div>

                <div className="mt-6">
                  <button
                    onClick={handleViewPerformance}
                    className="w-full py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    View Performance & Quiz Results
                  </button>
                </div>
              </div>
            </div>
            
            <div className="md:w-2/3">
              <div className="mb-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold">Assigned Lessons</h3>
                  <button 
                    onClick={() => onClose('assign')}
                    className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 flex items-center"
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                    </svg>
                    Assign New Lessons
                  </button>
                </div>
                
                {loading ? (
                  <div className="mt-4 flex items-center text-gray-500">
                    <div className="animate-spin mr-2 h-5 w-5 border-t-2 border-b-2 border-indigo-500 rounded-full"></div>
                    <p>Loading lessons...</p>
                  </div>
                ) : error ? (
                  <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm">
                    {error}
                  </div>
                ) : (
                  <div>
                    {assignedLessons.length === 0 ? (
                      <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg text-center py-6 px-4">
                        <p className="text-gray-600">No lessons assigned to this student yet.</p>
                      </div>
                    ) : (
                      <div className="bg-white rounded-lg shadow">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lesson Name</th>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subject</th>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assigned Date</th>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {assignedLessons.map((lesson) => (
                              <tr key={lesson.id}>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="text-sm font-medium text-gray-900">{lesson.name}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {lesson.subject}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {formatDate(lesson.assigned_date)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                    ${lesson.completed ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}`}>
                                    {lesson.completed ? 'Completed' : 'In Progress'}
                                  </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                  <button
                                    onClick={() => handleDeleteLesson(lesson.id)}
                                    className="text-red-600 hover:text-red-900 flex items-center"
                                    disabled={deleteLoading}
                                  >
                                    {deleteLoading ? (
                                      <span className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Removing...
                                      </span>
                                    ) : (
                                      <>
                                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                        </svg>
                                        Delete
                                      </>
                                    )}
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
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDetails; 