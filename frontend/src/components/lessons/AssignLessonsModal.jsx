import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AssignLessonsModal = ({ student, onClose, onAssigned }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lessons, setLessons] = useState([]);
  const [selectedLessons, setSelectedLessons] = useState([]);
  const [success, setSuccess] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('');
  const [gradeFilter, setGradeFilter] = useState('');

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

  useEffect(() => {
    const fetchLessons = async () => {
      try {
        setLoading(true);
        setError('');
        const token = localStorage.getItem('accessToken');
        
        let url = 'http://localhost:8000/api/user/advisor/lessons/';
        
        // Add query parameters if filters are set
        const params = [];
        if (subjectFilter) params.push(`subject=${subjectFilter}`);
        if (gradeFilter) params.push(`level=${gradeFilter}`);
        
        if (params.length > 0) {
          url += `?${params.join('&')}`;
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
  }, [subjectFilter, gradeFilter]);

  const handleLessonSelection = (lessonId) => {
    if (selectedLessons.includes(lessonId)) {
      setSelectedLessons(selectedLessons.filter(id => id !== lessonId));
    } else {
      setSelectedLessons([...selectedLessons, lessonId]);
    }
  };

  const handleAssignLessons = async () => {
    if (selectedLessons.length === 0) {
      setError('Please select at least one lesson to assign.');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('accessToken');
      
      const response = await axios.post(
        `http://localhost:8000/api/user/advisor/students/${student.id}/assign-lessons/`,
        { lesson_ids: selectedLessons },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      setSuccess('Lessons successfully assigned to the student.');
      setTimeout(() => {
        if (onAssigned) onAssigned(response.data);
        onClose();
      }, 1500);
    } catch (err) {
      setError('Failed to assign lessons. Please try again later.');
      console.error('Error assigning lessons:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!student) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">
              Assign Lessons to {student.first_name} {student.last_name}
            </h2>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <div className="p-6">
          {success && (
            <div className="mb-4 bg-green-100 text-green-700 p-3 rounded-md">
              {success}
            </div>
          )}
          
          {error && (
            <div className="mb-4 bg-red-100 text-red-700 p-3 rounded-md">
              {error}
            </div>
          )}
          
          <div className="mb-6 flex flex-wrap gap-4">
            <div>
              <label htmlFor="subject-filter" className="block text-sm font-medium text-gray-700 mb-1">
                Filter by Subject:
              </label>
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
            
            <div>
              <label htmlFor="grade-filter" className="block text-sm font-medium text-gray-700 mb-1">
                Filter by Grade Level:
              </label>
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
          
          {loading ? (
            <div className="text-center py-6">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading lessons...</p>
            </div>
          ) : lessons.length === 0 ? (
            <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg text-center py-8">
              <p className="text-gray-600">No lessons found matching the selected filters.</p>
            </div>
          ) : (
            <div>
              <div className="mb-4">
                <p className="text-sm text-gray-600">
                  Select lessons to assign to this student:
                </p>
              </div>
              
              <div className="bg-white shadow-md rounded-lg">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Select
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Lesson Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Subject
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Grade Level
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {lessons.map((lesson) => (
                      <tr key={lesson.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <input
                            type="checkbox"
                            checked={selectedLessons.includes(lesson.id)}
                            onChange={() => handleLessonSelection(lesson.id)}
                            className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                          />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{lesson.name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {lesson.subject}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {lesson.level_display || `Grade ${lesson.level}`}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div className="mt-6 flex justify-end">
                <button
                  onClick={onClose}
                  className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 mr-3"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAssignLessons}
                  disabled={selectedLessons.length === 0 || loading}
                  className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white 
                    ${selectedLessons.length === 0 || loading 
                      ? 'bg-indigo-300 cursor-not-allowed' 
                      : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'}`}
                >
                  {loading ? 'Assigning...' : 'Assign Selected Lessons'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AssignLessonsModal; 