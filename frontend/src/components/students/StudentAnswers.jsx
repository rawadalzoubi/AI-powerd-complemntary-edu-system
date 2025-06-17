import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import FeedbackForm from './FeedbackForm';
import { toast } from 'react-hot-toast';

const StudentAnswers = ({ studentId, onClose }) => {
  const [quizAttempts, setQuizAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedAttempts, setExpandedAttempts] = useState({});
  const [selectedAttempt, setSelectedAttempt] = useState(null);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackList, setFeedbackList] = useState({});
  const { currentUser } = useAuth();

  useEffect(() => {
    const fetchStudentAnswers = async () => {
      try {
        setLoading(true);
        
        const token = localStorage.getItem('accessToken');
        if (!token) {
          throw new Error('Authentication required');
        }
        
        const response = await axios.get(`http://localhost:8000/api/user/students/${studentId}/quiz-answers/`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        setQuizAttempts(response.data);
      } catch (err) {
        console.error('Error fetching student answers:', err);
        setError('Failed to load student answers. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    if (studentId) {
      fetchStudentAnswers();
    }
  }, [studentId]);
  
  useEffect(() => {
    const fetchFeedback = async () => {
      if (!studentId || currentUser.role !== 'teacher') return;
      
      try {
        const token = localStorage.getItem('accessToken');
        if (!token) return;
        
        const response = await axios.get(
          `http://localhost:8000/api/user/feedback/student/${studentId}/`,
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
        
        // Organize feedback by attempt ID for easy lookup
        const feedbackByAttempt = {};
        response.data.forEach(item => {
          feedbackByAttempt[item.quiz_attempt.id] = item;
        });
        
        setFeedbackList(feedbackByAttempt);
      } catch (err) {
        console.error('Error fetching feedback:', err);
      }
    };
    
    fetchFeedback();
  }, [studentId, currentUser]);

  const toggleExpand = (attemptId) => {
    setExpandedAttempts(prev => ({
      ...prev,
      [attemptId]: !prev[attemptId]
    }));
  };
  
  const handleOpenFeedbackForm = (attempt) => {
    setSelectedAttempt(attempt);
    setShowFeedbackForm(true);
  };
  
  const handleCloseFeedbackForm = () => {
    setShowFeedbackForm(false);
    setSelectedAttempt(null);
  };
  
  const handleFeedbackSent = async () => {
    // Refresh feedback list
    try {
      const token = localStorage.getItem('accessToken');
      const response = await axios.get(
        `http://localhost:8000/api/user/feedback/student/${studentId}/`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      const feedbackByAttempt = {};
      response.data.forEach(item => {
        feedbackByAttempt[item.quiz_attempt.id] = item;
      });
      
      setFeedbackList(feedbackByAttempt);
    } catch (err) {
      console.error('Error refreshing feedback:', err);
    }
    
    setShowFeedbackForm(false);
    setSelectedAttempt(null);
  };

  if (loading) {
    return (
      <div className="p-4 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
        <p className="mt-2">Loading answers...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  if (quizAttempts.length === 0) {
    return (
      <div className="p-8 text-center">
        <div className="text-gray-400 mb-4">
          <i className="fas fa-clipboard-list text-4xl"></i>
        </div>
        <h3 className="text-xl font-medium mb-2">No Quiz Attempts Found</h3>
        <p className="text-gray-500">This student hasn't attempted any quizzes yet.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold">Student Quiz Answers</h2>
        <button 
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          <i className="fas fa-times"></i>
        </button>
      </div>
      
      {showFeedbackForm && selectedAttempt ? (
        <div className="p-4 border-b border-gray-200">
          <FeedbackForm
            studentId={studentId}
            attemptId={selectedAttempt.attempt_id}
            attemptDetails={selectedAttempt}
            onFeedbackSent={handleFeedbackSent}
            onCancel={handleCloseFeedbackForm}
          />
        </div>
      ) : (
        <div className="p-4 max-h-[70vh] overflow-y-auto">
          {quizAttempts.map(attempt => (
            <div 
              key={attempt.attempt_id} 
              className="mb-4 border border-gray-200 rounded-lg overflow-hidden"
            >
              <div 
                className="flex items-center justify-between p-4 bg-gray-50 cursor-pointer"
                onClick={() => toggleExpand(attempt.attempt_id)}
              >
                <div>
                  <h3 className="font-medium">{attempt.quiz_title}</h3>
                  <p className="text-sm text-gray-500">{attempt.lesson_name}</p>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <span className={`font-semibold ${attempt.passed ? 'text-green-600' : 'text-red-600'}`}>
                      {attempt.score}%
                    </span>
                    <p className="text-xs text-gray-500">
                      {new Date(attempt.start_time).toLocaleString()}
                    </p>
                  </div>
                  <span>
                    <i className={`fas ${expandedAttempts[attempt.attempt_id] ? 'fa-chevron-up' : 'fa-chevron-down'}`}></i>
                  </span>
                </div>
              </div>
              
              {expandedAttempts[attempt.attempt_id] && (
                <div className="p-4 bg-white">
                  {/* Display existing feedback if available */}
                  {feedbackList[attempt.attempt_id] && (
                    <div className="mb-4 p-3 bg-blue-50 border border-blue-100 rounded-md">
                      <div className="flex justify-between items-center mb-2">
                        <h4 className="text-sm font-semibold text-blue-800">Your Feedback</h4>
                        <span className="text-xs text-gray-500">
                          {new Date(feedbackList[attempt.attempt_id].created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-blue-800">{feedbackList[attempt.attempt_id].feedback_text}</p>
                    </div>
                  )}
                
                  {/* List of answers */}
                  {attempt.answers.map((answer, index) => (
                    <div 
                      key={index}
                      className="mb-4 pb-4 border-b border-gray-100 last:border-b-0"
                    >
                      <p className="font-medium mb-2">{index + 1}. {answer.question_text}</p>
                      
                      <div className="flex items-start mb-1 pl-4">
                        <div className="flex-shrink-0 mr-2">
                          <i className={`fas ${answer.is_correct ? 'fa-check-circle text-green-500' : 'fa-times-circle text-red-500'}`}></i>
                        </div>
                        <div>
                          <p className={answer.is_correct ? 'text-green-700' : 'text-red-700'}>
                            {answer.selected_answer}
                          </p>
                          <p className="text-xs text-gray-500">Student's answer</p>
                        </div>
                      </div>
                      
                      {!answer.is_correct && (
                        <div className="flex items-start mt-2 pl-4">
                          <div className="flex-shrink-0 mr-2">
                            <i className="fas fa-info-circle text-blue-500"></i>
                          </div>
                          <div>
                            <p className="text-blue-700">{answer.correct_answer}</p>
                            <p className="text-xs text-gray-500">Correct answer</p>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {/* Feedback button */}
                  {currentUser.role === 'teacher' && (
                    <div className="mt-4 flex justify-end">
                      <button 
                        className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700"
                        onClick={() => handleOpenFeedbackForm(attempt)}
                      >
                        {feedbackList[attempt.attempt_id] ? 'Update Feedback' : 'Provide Feedback'}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default StudentAnswers; 