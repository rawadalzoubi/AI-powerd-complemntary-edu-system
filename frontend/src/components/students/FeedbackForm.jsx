import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const FeedbackForm = ({ studentId, attemptId, attemptDetails, onFeedbackSent, onCancel }) => {
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!feedback.trim()) {
      toast.error('Please enter feedback text');
      return;
    }
    
    setLoading(true);
    
    try {
      const token = localStorage.getItem('accessToken');
      
      const response = await axios.post(
        'http://localhost:8000/api/user/feedback/send/',
        {
          student_id: studentId,
          attempt_id: attemptId,
          feedback_text: feedback
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      if (response.data.status === 'success') {
        toast.success('Feedback sent successfully');
        setFeedback('');
        if (onFeedbackSent) onFeedbackSent();
      }
    } catch (error) {
      console.error('Error sending feedback:', error);
      toast.error(error.response?.data?.message || 'Failed to send feedback');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg p-4 shadow">
      <div className="mb-4">
        <h3 className="text-lg font-medium">Send Feedback</h3>
        {attemptDetails && (
          <div className="mt-2 text-sm text-gray-600">
            <p><span className="font-medium">Quiz:</span> {attemptDetails.quiz_title}</p>
            <p><span className="font-medium">Score:</span> {attemptDetails.score}%</p>
            <p><span className="font-medium">Date:</span> {new Date(attemptDetails.start_time).toLocaleString()}</p>
          </div>
        )}
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="feedback" className="block text-sm font-medium text-gray-700 mb-1">
            Your Feedback
          </label>
          <textarea
            id="feedback"
            rows={5}
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Enter your feedback to the student..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            disabled={loading}
          />
        </div>
        
        <div className="flex justify-end space-x-2">
          <button
            type="button"
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-70"
            disabled={loading}
          >
            {loading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending...
              </span>
            ) : (
              'Send Feedback'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FeedbackForm; 