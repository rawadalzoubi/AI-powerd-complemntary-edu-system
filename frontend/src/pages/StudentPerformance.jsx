import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DashboardLayout from '../components/layout/DashboardLayout';
import advisorService from '../services/advisorService';
import StudentQuizResults from '../components/advisor/StudentQuizResults';

const StudentPerformance = () => {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const [student, setStudent] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);

  useEffect(() => {
    const fetchStudentPerformance = async () => {
      if (!studentId) {
        navigate('/advisor/students');
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // Get student performance data
        const performanceData = await advisorService.getStudentPerformance(studentId);
        setPerformance(performanceData);
        setStudent(performanceData.student);
      } catch (err) {
        console.error('Error fetching student performance:', err);
        setError('Failed to load student performance data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchStudentPerformance();
  }, [studentId, navigate]);

  const handleLessonSelect = (lesson) => {
    setSelectedLesson(lesson.lesson_id === selectedLesson?.lesson_id ? null : lesson);
  };

  const handleBackClick = () => {
    navigate('/advisor/students');
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-6">
          <p>{error}</p>
        </div>
        <button
          onClick={handleBackClick}
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
        >
          Back to Students
        </button>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="mb-6 flex justify-between items-center">
        <div>
          <button
            onClick={handleBackClick}
            className="mb-4 flex items-center text-indigo-600 hover:text-indigo-800"
          >
            <i className="fas fa-arrow-left mr-2"></i> Back to Students
          </button>
          
          <h1 className="text-2xl font-bold text-gray-900">
            Student Performance
          </h1>
          {student && (
            <p className="text-gray-600">
              {student.name} - Grade {student.grade}
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800">Enrolled Lessons</h3>
            </div>
            
            <div className="overflow-y-auto max-h-96">
              {performance?.enrollments && performance.enrollments.length > 0 ? (
                <ul className="divide-y divide-gray-200">
                  {performance.enrollments.map((enrollment) => (
                    <li 
                      key={enrollment.lesson_id}
                      className={`px-6 py-4 hover:bg-gray-50 cursor-pointer ${
                        selectedLesson?.lesson_id === enrollment.lesson_id ? 'bg-indigo-50' : ''
                      }`}
                      onClick={() => handleLessonSelect(enrollment)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">{enrollment.lesson_name}</h4>
                          <p className="text-sm text-gray-500">{enrollment.subject} - Grade {enrollment.grade_level}</p>
                        </div>
                        <div className="text-right">
                          <div className="w-16 h-16 rounded-full flex items-center justify-center bg-blue-100">
                            <span className="text-blue-800 font-semibold">{enrollment.progress}%</span>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="px-6 py-8 text-center">
                  <p className="text-gray-500">No lessons enrolled</p>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-2">
          {selectedLesson ? (
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-800">Lesson Progress</h3>
                </div>
                <div className="p-6">
                  <h4 className="font-medium text-gray-900 mb-4">{selectedLesson.lesson_name}</h4>
                  
                  <div className="mb-6">
                    <div className="flex justify-between text-sm mb-2">
                      <span>Progress</span>
                      <span>{selectedLesson.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div 
                        className="bg-blue-600 h-2.5 rounded-full" 
                        style={{ width: `${selectedLesson.progress}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-sm text-gray-500">Enrollment Date</p>
                      <p className="font-medium">
                        {new Date(selectedLesson.enrollment_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-sm text-gray-500">Last Activity</p>
                      <p className="font-medium">
                        {selectedLesson.last_activity ? 
                          new Date(selectedLesson.last_activity).toLocaleDateString() : 
                          'No activity yet'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              
              <StudentQuizResults 
                studentId={studentId} 
                lessonId={selectedLesson.lesson_id} 
              />
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <div className="text-gray-400 mb-4">
                <i className="fas fa-chart-bar text-5xl"></i>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Lesson</h3>
              <p className="text-gray-500">
                Please select a lesson from the list to view detailed performance and quiz results.
              </p>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default StudentPerformance; 