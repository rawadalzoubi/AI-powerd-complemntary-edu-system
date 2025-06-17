import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import QuestionForm from './QuestionForm';

const QuizModal = ({ isOpen, onClose, onSave, quiz = null, lessonId, temporaryMode = false }) => {
  console.log("QuizModal opened with lessonId:", lessonId, "temporaryMode:", temporaryMode);
  
  const [formData, setFormData] = useState({
    title: '',
    total_marks: 0,
    questions: []
  });
  const [errors, setErrors] = useState({});
  const [showQuestionForm, setShowQuestionForm] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (quiz) {
      setFormData({
        title: quiz.title || '',
        total_marks: quiz.total_marks || quiz.passing_score || 0,
        questions: quiz.questions || []
      });
    } else {
      setFormData({
        title: '',
        total_marks: 0,
        questions: []
      });
    }
  }, [quiz]);

  // Simulated progress function to provide visual feedback during quiz creation/update
  useEffect(() => {
    let interval;
    if (isSubmitting) {
      // Start at 15% to give immediate feedback
      setProgress(15);
      
      // Increment progress gradually up to 85% while waiting for server response
      interval = setInterval(() => {
        setProgress(prevProgress => {
          // Cap progress at 85% until we get the actual response
          if (prevProgress < 85) {
            return prevProgress + Math.random() * 15;
          }
          return prevProgress;
        });
      }, 500);
    } else {
      setProgress(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isSubmitting]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'total_marks' ? parseInt(value, 10) || 0 : value
    });

    // Clear validation error when field is modified
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: null
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Quiz title is required';
    }
    if (formData.total_marks <= 0) {
      newErrors.total_marks = 'Total marks must be greater than 0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Handle temporary mode (content-first approach)
      if (temporaryMode) {
        console.log("Creating quiz in temporary mode - returning data to parent without API call");
        
        // Create temporary quiz object with questions and answers
        const tempQuizData = {
          title: formData.title,
          total_marks: formData.total_marks,
          questions: formData.questions.map(q => ({
            question_text: q.question_text || q.text || '',
            points: q.points,
            question_type: q.question_type || 'SINGLE',
            answers: q.answers.map(a => ({
              answer_text: a.answer_text || a.text || '', 
              is_correct: a.is_correct
            }))
          })),
          // Add a unique temporary ID
          tempId: Date.now().toString()
        };
        
        // Return the temp quiz data to parent
        onSave(tempQuizData);
        setIsSubmitting(false);
        onClose();
        return;
      }
      
      // Regular mode - needs lessonId
      if (!lessonId) {
        setErrors({ general: "No lesson ID provided. Please try again." });
        setIsSubmitting(false);
        return;
      }
      
      await onSave(formData);
      // Complete the progress bar to 100%
      setProgress(100);
      
      // Small delay to show 100% completion before closing
      setTimeout(() => {
        setIsSubmitting(false);
        onClose();
      }, 500);
    } catch (error) {
      console.error('Failed to save quiz:', error);
      setIsSubmitting(false);
      
      // Display error message
      if (error.response?.data) {
        const backendErrors = error.response.data;
        const mappedErrors = {};
        
        Object.keys(backendErrors).forEach(key => {
          mappedErrors[key] = Array.isArray(backendErrors[key]) 
            ? backendErrors[key].join(', ') 
            : backendErrors[key];
        });
        
        setErrors({
          ...mappedErrors,
          general: 'Failed to save quiz. Please check the form and try again.'
        });
      } else {
        setErrors({
          general: 'Failed to save quiz. Please try again.'
        });
      }
    }
  };

  const handleAddQuestion = () => {
    setCurrentQuestion(null);
    setShowQuestionForm(true);
  };

  const handleEditQuestion = (question, index) => {
    setCurrentQuestion({ ...question, index });
    setShowQuestionForm(true);
  };

  const handleDeleteQuestion = (index) => {
    const updatedQuestions = [...formData.questions];
    updatedQuestions.splice(index, 1);
    setFormData({
      ...formData,
      questions: updatedQuestions
    });
  };

  const handleSaveQuestion = (question) => {
    let updatedQuestions = [...formData.questions];
    
    if (currentQuestion !== null) {
      // Update existing question
      updatedQuestions[currentQuestion.index] = question;
    } else {
      // Add new question
      updatedQuestions.push(question);
    }
    
    setFormData({
      ...formData,
      questions: updatedQuestions
    });
    
    setShowQuestionForm(false);
    setCurrentQuestion(null);
  };

  const handleCancelQuestion = () => {
    setShowQuestionForm(false);
    setCurrentQuestion(null);
  };

  // Calculate total points from questions
  const totalQuestionPoints = formData.questions.reduce(
    (total, question) => total + question.points,
    0
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-3xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-gray-800">
              {quiz ? 'Edit Quiz' : 'Create New Quiz'}
            </h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500" disabled={isSubmitting}>
              <i className="fas fa-times"></i>
            </button>
          </div>
          
          {errors.general && (
            <div className="mb-4 bg-red-50 p-3 rounded text-red-600 text-sm">
              {errors.general}
            </div>
          )}

          {showQuestionForm ? (
            <QuestionForm
              question={currentQuestion}
              onSave={handleSaveQuestion}
              onCancel={handleCancelQuestion}
            />
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                  Quiz Title
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border ${errors.title ? 'border-red-500' : 'border-gray-300'} rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500`}
                  placeholder="Enter quiz title"
                  disabled={isSubmitting}
                />
                {errors.title && (
                  <p className="mt-1 text-sm text-red-600">{errors.title}</p>
                )}
              </div>
              
              <div className="mb-4">
                <label htmlFor="total_marks" className="block text-sm font-medium text-gray-700 mb-1">
                  Total Marks
                </label>
                <input
                  type="number"
                  id="total_marks"
                  name="total_marks"
                  min="1"
                  value={formData.total_marks}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border ${errors.total_marks ? 'border-red-500' : 'border-gray-300'} rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500`}
                  disabled={isSubmitting}
                />
                {errors.total_marks && (
                  <p className="mt-1 text-sm text-red-600">{errors.total_marks}</p>
                )}
              </div>
              
              <div className="mb-6">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-medium text-gray-700">Questions</h4>
                  <button
                    type="button"
                    onClick={handleAddQuestion}
                    className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 flex items-center text-sm"
                    disabled={isSubmitting}
                  >
                    <i className="fas fa-plus mr-2"></i> Add Question
                  </button>
                </div>
                
                {formData.questions.length === 0 ? (
                  <div className="text-center py-8 border border-dashed border-gray-300 rounded-lg">
                    <i className="fas fa-question-circle text-gray-400 text-3xl mb-3"></i>
                    <p className="text-gray-500">No questions added yet. Add your first question!</p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-64 overflow-y-auto p-2">
                    {formData.questions.map((question, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex justify-between">
                          <div>
                            <h5 className="font-medium">{question.question_text || question.text || 'Untitled Question'}</h5>
                            <p className="text-sm text-gray-500">Points: {question.points}</p>
                            <p className="text-sm text-gray-500">
                              Answers: {question.answers ? question.answers.length : 0}
                            </p>
                          </div>
                          <div>
                            <button
                              type="button"
                              onClick={() => handleEditQuestion(question, index)}
                              className="text-indigo-600 hover:text-indigo-800 mr-2"
                              disabled={isSubmitting}
                            >
                              <i className="fas fa-edit"></i>
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDeleteQuestion(index)}
                              className="text-red-600 hover:text-red-800"
                              disabled={isSubmitting}
                            >
                              <i className="fas fa-trash"></i>
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                {formData.questions.length > 0 && (
                  <div className="mt-3 flex justify-between text-sm">
                    <span>Total Questions: {formData.questions.length}</span>
                    <span className={totalQuestionPoints !== formData.total_marks ? 'text-yellow-600' : 'text-green-600'}>
                      Total Points: {totalQuestionPoints} / {formData.total_marks}
                    </span>
                  </div>
                )}
                
                {totalQuestionPoints !== formData.total_marks && formData.questions.length > 0 && (
                  <p className="mt-1 text-sm text-yellow-600">
                    <i className="fas fa-exclamation-triangle mr-1"></i>
                    The sum of question points ({totalQuestionPoints}) doesn't match the total marks ({formData.total_marks}).
                  </p>
                )}
              </div>
              
              {isSubmitting && (
                <div className="mb-4">
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300 ease-in-out" 
                      style={{ width: `${Math.round(progress)}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600 mt-1 text-center">
                    {progress < 100 ? 'Processing...' : 'Completed!'}
                  </p>
                </div>
              )}
              
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      {quiz ? 'Updating...' : 'Creating...'}
                    </>
                  ) : (
                    quiz ? 'Update Quiz' : 'Create Quiz'
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

QuizModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired,
  quiz: PropTypes.object,
  lessonId: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  temporaryMode: PropTypes.bool
};

export default QuizModal; 