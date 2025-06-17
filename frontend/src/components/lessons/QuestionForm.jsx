import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const QuestionForm = ({ question, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    question_text: '',
    points: 1,
    answers: [
      { answer_text: '', is_correct: true },
      { answer_text: '', is_correct: false }
    ]
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (question) {
      // If we're editing an existing question, populate the form
      setFormData({
        question_text: question.question_text || question.text || '',
        points: question.points || 1,
        answers: question.answers && question.answers.length > 0 
          ? [...question.answers.map(a => ({
              answer_text: a.answer_text || a.text || '',
              is_correct: a.is_correct || false
            }))] 
          : [
              { answer_text: '', is_correct: true },
              { answer_text: '', is_correct: false }
            ]
      });
    }
  }, [question]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'number' ? (parseInt(value, 10) || 0) : value
    });

    // Clear validation error when field is modified
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: null
      });
    }
  };

  const handleAnswerChange = (index, field, value) => {
    const updatedAnswers = [...formData.answers];
    updatedAnswers[index] = {
      ...updatedAnswers[index],
      [field]: field === 'is_correct' ? value : value
    };
    
    setFormData({
      ...formData,
      answers: updatedAnswers
    });

    // Clear validation error for answers
    if (errors.answers) {
      setErrors({
        ...errors,
        answers: null
      });
    }
  };

  const handleCorrectAnswerChange = (index) => {
    // When changing which answer is correct, ensure only one is marked as correct
    const updatedAnswers = formData.answers.map((answer, i) => ({
      ...answer,
      is_correct: i === index
    }));
    
    setFormData({
      ...formData,
      answers: updatedAnswers
    });
  };

  const addAnswer = () => {
    setFormData({
      ...formData,
      answers: [
        ...formData.answers,
        { answer_text: '', is_correct: false }
      ]
    });
  };

  const removeAnswer = (index) => {
    if (formData.answers.length <= 2) {
      setErrors({
        ...errors,
        answers: 'At least two answers are required'
      });
      return;
    }

    const updatedAnswers = [...formData.answers];
    updatedAnswers.splice(index, 1);
    
    // If we removed the correct answer, set the first one as correct
    if (formData.answers[index].is_correct && updatedAnswers.length > 0) {
      updatedAnswers[0].is_correct = true;
    }
    
    setFormData({
      ...formData,
      answers: updatedAnswers
    });
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.question_text.trim()) {
      newErrors.question_text = 'Question text is required';
    }
    
    if (formData.points <= 0) {
      newErrors.points = 'Points must be greater than 0';
    }
    
    // Check if any answer is empty
    if (formData.answers.some(answer => !answer.answer_text.trim())) {
      newErrors.answers = 'All answers must have text';
    }
    
    // Check if there's at least one correct answer
    if (!formData.answers.some(answer => answer.is_correct)) {
      newErrors.answers = 'At least one answer must be marked as correct';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSave(formData);
    }
  };

  return (
    <div>
      <h3 className="text-lg font-medium text-gray-800 mb-4">
        {question ? 'Edit Question' : 'Add New Question'}
      </h3>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="question_text" className="block text-sm font-medium text-gray-700 mb-1">
            Question Text
          </label>
          <textarea
            id="question_text"
            name="question_text"
            value={formData.question_text}
            onChange={handleChange}
            rows="3"
            className={`w-full px-3 py-2 border ${errors.question_text ? 'border-red-500' : 'border-gray-300'} rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500`}
            placeholder="Enter your question"
          ></textarea>
          {errors.question_text && (
            <p className="mt-1 text-sm text-red-600">{errors.question_text}</p>
          )}
        </div>
        
        <div className="mb-4">
          <label htmlFor="points" className="block text-sm font-medium text-gray-700 mb-1">
            Points
          </label>
          <input
            type="number"
            id="points"
            name="points"
            min="1"
            value={formData.points}
            onChange={handleChange}
            className={`w-full px-3 py-2 border ${errors.points ? 'border-red-500' : 'border-gray-300'} rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500`}
          />
          {errors.points && (
            <p className="mt-1 text-sm text-red-600">{errors.points}</p>
          )}
        </div>
        
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Answers
            </label>
            <button
              type="button"
              onClick={addAnswer}
              className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 flex items-center text-sm"
            >
              <i className="fas fa-plus mr-1"></i> Add Answer
            </button>
          </div>
          
          {errors.answers && (
            <p className="mb-3 text-sm text-red-600">{errors.answers}</p>
          )}
          
          <div className="space-y-3">
            {formData.answers.map((answer, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="pt-2">
                  <input
                    type="radio"
                    id={`correct-${index}`}
                    name="correctAnswer"
                    checked={answer.is_correct}
                    onChange={() => handleCorrectAnswerChange(index)}
                    className="w-4 h-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
                  />
                </div>
                <div className="flex-1">
                  <input
                    type="text"
                    value={answer.answer_text}
                    onChange={(e) => handleAnswerChange(index, 'answer_text', e.target.value)}
                    placeholder={`Answer ${index + 1}`}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => removeAnswer(index)}
                  className="text-red-600 hover:text-red-800 pt-2"
                  aria-label="Remove answer"
                >
                  <i className="fas fa-trash"></i>
                </button>
              </div>
            ))}
          </div>
          <p className="mt-2 text-sm text-gray-500">
            <i className="fas fa-info-circle mr-1"></i>
            Select the radio button next to the correct answer.
          </p>
        </div>
        
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Save Question
          </button>
        </div>
      </form>
    </div>
  );
};

QuestionForm.propTypes = {
  question: PropTypes.object,
  onSave: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired
};

export default QuestionForm; 