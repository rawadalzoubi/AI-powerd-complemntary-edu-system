import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';

const FeedbackList = () => {
  const [feedback, setFeedback] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { currentUser } = useAuth();

  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        setLoading(true);
        
        const token = localStorage.getItem('accessToken');
        if (!token) {
          throw new Error('Authentication required');
        }
        
        const response = await axios.get('http://localhost:8000/api/user/feedback/student/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        setFeedback(response.data);
      } catch (err) {
        console.error('Error fetching feedback:', err);
        setError('Failed to load feedback. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    if (currentUser?.role === 'student') {
      fetchFeedback();
    }
  }, [currentUser]);

  if (!currentUser || currentUser.role !== 'student') {
    return null;
  }

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
        <p className="mt-2 text-gray-500">Loading feedback...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md">
        {error}
      </div>
    );
  }

  if (feedback.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 p-6 rounded-md text-center">
        <div className="text-gray-400 mb-2">
          <i className="fas fa-comments text-3xl"></i>
        </div>
        <p className="text-gray-600">You don't have any feedback yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold mb-4">Teacher Feedback</h3>
      
      {feedback.map((item) => (
        <div 
          key={item.id}
          className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden"
        >
          <div className="bg-indigo-50 px-4 py-3 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h4 className="font-medium text-indigo-900">
                {item.quiz_attempt.quiz_title}
              </h4>
              <span className="text-sm text-gray-600">
                {new Date(item.created_at).toLocaleDateString()}
              </span>
            </div>
            <p className="text-xs text-gray-500">
              From: {item.teacher.name}
            </p>
          </div>
          
          <div className="p-4">
            <div className="flex items-center mb-3">
              <div className="flex-shrink-0 mr-2">
                <span className={`inline-block rounded-full w-3 h-3 ${
                  item.quiz_attempt.score >= 70 ? 'bg-green-500' : 'bg-red-500'
                }`}></span>
              </div>
              <p className="text-sm">
                Score: <span className="font-semibold">{item.quiz_attempt.score}%</span>
              </p>
            </div>
            
            <div className="border-t border-gray-100 pt-3">
              <p className="whitespace-pre-line text-gray-800">{item.feedback_text}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default FeedbackList; 