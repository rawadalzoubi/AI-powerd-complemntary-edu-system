import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import advisorService from '../../services/advisorService';

const StudentQuizResults = ({ studentId, lessonId }) => {
  const [quizAttempts, setQuizAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAttempt, setSelectedAttempt] = useState(null);

  useEffect(() => {
    const fetchQuizAttempts = async () => {
      try {
        setLoading(true);
        setError(null);
        const params = {};
        if (lessonId) params.lessonId = lessonId;
        
        const data = await advisorService.getStudentQuizAttempts(studentId, lessonId);
        setQuizAttempts(data);
      } catch (err) {
        console.error('Error fetching quiz attempts:', err);
        setError('Failed to load quiz attempts. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    if (studentId) {
      fetchQuizAttempts();
    }
  }, [studentId, lessonId]);

  const handleViewAttemptDetails = (attempt) => {
    setSelectedAttempt(attempt);
  };

  const closeAttemptDetails = () => {
    setSelectedAttempt(null);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-4 rounded-lg">
        <p>{error}</p>
      </div>
    );
  }

  if (quizAttempts.length === 0) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg text-center">
        <p className="text-gray-500">No quiz attempts found for this student.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">Quiz Results</h3>
      </div>
      
      {selectedAttempt ? (
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h4 className="text-md font-medium text-gray-700">
              {selectedAttempt.quiz_title} - Details
            </h4>
            <button
              onClick={closeAttemptDetails}
              className="text-gray-400 hover:text-gray-500"
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
          
          <div className="mb-4 grid grid-cols-2 gap-4">
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-sm text-gray-500">Score</p>
              <p className="text-lg font-semibold">
                {selectedAttempt.score}%
              </p>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-sm text-gray-500">Status</p>
              <p className={`text-lg font-semibold ${selectedAttempt.passed ? 'text-green-600' : 'text-red-600'}`}>
                {selectedAttempt.passed ? 'Passed' : 'Failed'}
              </p>
            </div>
            <div className="bg-gray-50 p-3 rounded">
              <p className="text-sm text-gray-500">Started</p>
              <p className="text-md">{new Date(selectedAttempt.start_time).toLocaleString()}</p>
            </div>
            {selectedAttempt.end_time && (
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-sm text-gray-500">Completed</p>
                <p className="text-md">{new Date(selectedAttempt.end_time).toLocaleString()}</p>
              </div>
            )}
          </div>
          
          <h5 className="text-md font-medium text-gray-700 mb-3">Answers</h5>
          
          {selectedAttempt.quiz_answers && selectedAttempt.quiz_answers.length > 0 ? (
            <div className="space-y-3">
              {selectedAttempt.quiz_answers.map((answer, index) => (
                <div 
                  key={answer.id || index}
                  className={`p-3 rounded-lg border ${answer.is_correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}
                >
                  <p className="font-medium mb-1">{answer.question_text}</p>
                  <p className="text-sm">
                    <span className={`${answer.is_correct ? 'text-green-600' : 'text-red-600'} font-medium`}>
                      {answer.is_correct ? '✓ Correct' : '✗ Incorrect'}
                    </span> - {answer.selected_answer_text}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No detailed answers available for this attempt.</p>
          )}
          
          <div className="mt-4 flex justify-end">
            <button
              onClick={closeAttemptDetails}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
            >
              Back to List
            </button>
          </div>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quiz</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {quizAttempts.map((attempt) => (
                <tr key={attempt.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{attempt.quiz_title}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(attempt.start_time).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-sm leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {attempt.score}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {attempt.passed ? (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        Passed
                      </span>
                    ) : (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                        Failed
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleViewAttemptDetails(attempt)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

StudentQuizResults.propTypes = {
  studentId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  lessonId: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
};

export default StudentQuizResults; 