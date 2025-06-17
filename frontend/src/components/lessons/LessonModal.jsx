import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import ReactDOM from 'react-dom';
import ContentUploadModal from './ContentUploadModal';
import QuizModal from './QuizModal';

const LessonModal = ({ isOpen, onClose, onSave, lesson = null }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    level: '',
    subject: '',
  });
  const [errors, setErrors] = useState({});
  const [showContentUploadModal, setShowContentUploadModal] = useState(false);
  const [showQuizModal, setShowQuizModal] = useState(false);
  const [contentType, setContentType] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  
  // Store uploaded content before lesson creation
  const [uploadedContents, setUploadedContents] = useState([]);
  const [uploadedQuizzes, setUploadedQuizzes] = useState([]);

  // Reset form when modal opens/closes or lesson changes
  useEffect(() => {
    if (isOpen && lesson) {
      console.log('Initializing form with lesson data:', lesson);
      setFormData({
        title: lesson.name || '',
        description: lesson.description || '',
        level: lesson.level || '',
        subject: lesson.subject || '',
      });
      setErrors({});
      setIsEditMode(true);
      // For edit mode, we don't reset the content
    } else if (isOpen) {
      setFormData({
        title: '',
        description: '',
        level: '',
        subject: '',
      });
      setErrors({});
      setIsEditMode(false);
      // Clear any previously uploaded content
      setUploadedContents([]);
      setUploadedQuizzes([]);
    }
  }, [isOpen, lesson]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    
    // Clear errors when user types
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.title.trim()) {
      newErrors.title = "Title is required";
    }
    
    if (!formData.level) {
      newErrors.level = "Grade level is required";
    }
    
    if (!formData.subject) {
      newErrors.subject = "Subject is required";
    }
    
    // Check if at least one content has been uploaded
    if (uploadedContents.length === 0 && uploadedQuizzes.length === 0 && !isEditMode) {
      newErrors.content = "At least one content item (video, PDF, or exercise) is required";
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
    
    // Convert the form data to the expected format for the API
    // Include both the lesson details and the uploaded content
    const lessonData = {
      name: formData.title,
      description: formData.description,
      level: formData.level,
      subject: formData.subject,
      // Include content data if needed by backend API 
      // (depends on how your backend handles this)
      contents: uploadedContents,
      quizzes: uploadedQuizzes
    };

    try {
      // Save the lesson with all associated content
      await onSave(lessonData);
      
      // Close the modal after successful save
      onClose();
    } catch (error) {
      // Handle error
      console.error("Error saving lesson:", error);
      
      // Handle the error - check if it's a validation error from the backend
      if (error.response?.data) {
        const backendErrors = error.response.data;
        const mappedErrors = {};
        
        if (backendErrors.name) {
          mappedErrors.title = backendErrors.name.join(', ');
        }
        if (backendErrors.level) {
          mappedErrors.level = backendErrors.level.join(', ');
        }
        if (backendErrors.subject) {
          mappedErrors.subject = backendErrors.subject.join(', ');
        }
        
        setErrors(mappedErrors);
      } else {
        // Set general error
        setErrors({ general: "Failed to save lesson. Please try again." });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleContentClick = (type) => {
    console.log("Content click for type:", type);
    
    setContentType(type);
    if (type === 'EXERCISE') {
      setShowQuizModal(true);
    } else {
      setShowContentUploadModal(true);
    }
  };

  const handleContentUpload = async (contentData) => {
    try {
      console.log('Content uploaded:', contentData);
      
      // Store the uploaded content in our state
      setUploadedContents(prev => [...prev, contentData]);
      
      // Close the content upload modal
      setShowContentUploadModal(false);
    } catch (error) {
      console.error('Error handling uploaded content:', error);
    }
  };

  const handleQuizSave = async (quizData) => {
    try {
      console.log('Quiz saved:', quizData);
      
      // Store the quiz in our state
      setUploadedQuizzes(prev => [...prev, quizData]);
      
      // Close the quiz modal
      setShowQuizModal(false);
    } catch (error) {
      console.error('Error saving quiz:', error);
    }
  };

  const removeUploadedContent = (index) => {
    setUploadedContents(prev => prev.filter((_, i) => i !== index));
  };

  const removeUploadedQuiz = (index) => {
    setUploadedQuizzes(prev => prev.filter((_, i) => i !== index));
  };

  if (!isOpen) return null;

  // Use a portal to render the modal at the root level of the DOM
  return ReactDOM.createPortal(
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center">
        {/* Background overlay */}
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={onClose}></div>
        
        {/* Modal panel */}
        <div className="relative inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex justify-between items-center pb-3">
              <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                {isEditMode ? 'Edit Lesson' : 'Create New Lesson'}
              </h3>
              <button
                type="button"
                className="text-gray-400 hover:text-gray-500"
                onClick={onClose}
              >
                <span className="sr-only">Close</span>
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            {/* General error message */}
            {errors.general && (
              <div className="mb-4 bg-red-50 p-3 rounded text-red-600 text-sm">
                {errors.general}
              </div>
            )}
            
            <form onSubmit={handleSubmit}>
              {/* Step 1: Upload Content (moved to the top) */}
              <div className="space-y-4">
                <div className="grid grid-cols-1 gap-4 pt-3">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Lesson Content</h4>
                  <div className="grid grid-cols-3 gap-3">
                    <div 
                      className="border border-dashed border-gray-300 rounded-md p-3 flex flex-col items-center justify-center text-center hover:bg-gray-50 cursor-pointer"
                      onClick={() => handleContentClick('VIDEO')}
                    >
                      <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mb-2">
                        <i className="fas fa-video text-blue-500"></i>
                      </div>
                      <span className="text-sm text-gray-600">Upload Video</span>
                    </div>
                    <div 
                      className="border border-dashed border-gray-300 rounded-md p-3 flex flex-col items-center justify-center text-center hover:bg-gray-50 cursor-pointer"
                      onClick={() => handleContentClick('PDF')}
                    >
                      <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mb-2">
                        <i className="fas fa-file-pdf text-red-500"></i>
                      </div>
                      <span className="text-sm text-gray-600">Upload PDF</span>
                    </div>
                    <div 
                      className="border border-dashed border-gray-300 rounded-md p-3 flex flex-col items-center justify-center text-center hover:bg-gray-50 cursor-pointer"
                      onClick={() => handleContentClick('EXERCISE')}
                    >
                      <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-2">
                        <i className="fas fa-tasks text-green-500"></i>
                      </div>
                      <span className="text-sm text-gray-600">Add Exercise</span>
                    </div>
                  </div>
                </div>
                
                {/* Display uploaded content */}
                {uploadedContents.length > 0 && (
                  <div className="mt-3">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Uploaded Content</h5>
                    <div className="space-y-2">
                      {uploadedContents.map((content, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded-md">
                          <div className="flex items-center">
                            <i className={`fas ${content.content_type === 'VIDEO' ? 'fa-video text-blue-500' : 'fa-file-pdf text-red-500'} mr-2`}></i>
                            <span className="text-sm">{content.title}</span>
                          </div>
                          <button 
                            type="button" 
                            onClick={() => removeUploadedContent(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <i className="fas fa-times"></i>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Display uploaded quizzes */}
                {uploadedQuizzes.length > 0 && (
                  <div className="mt-3">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Exercises/Quizzes</h5>
                    <div className="space-y-2">
                      {uploadedQuizzes.map((quiz, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded-md">
                          <div className="flex items-center">
                            <i className="fas fa-tasks text-green-500 mr-2"></i>
                            <span className="text-sm">{quiz.title}</span>
                          </div>
                          <button 
                            type="button" 
                            onClick={() => removeUploadedQuiz(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <i className="fas fa-times"></i>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Content error message */}
                {errors.content && (
                  <p className="mt-1 text-sm text-red-600">{errors.content}</p>
                )}
                
                {/* Step 2: Lesson Details (after content) */}
                <div className="border-t border-gray-200 pt-4 mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Lesson Details</h4>
                  
                  <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                      Lesson Title
                    </label>
                    <input
                      type="text"
                      name="title"
                      id="title"
                      className={`mt-1 block w-full border ${errors.title ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500`}
                      value={formData.title}
                      onChange={handleChange}
                      required
                      placeholder="Enter lesson title"
                    />
                    {errors.title && (
                      <p className="mt-1 text-sm text-red-600">{errors.title}</p>
                    )}
                  </div>
                  
                  <div className="mt-3">
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                      Description
                    </label>
                    <textarea
                      name="description"
                      id="description"
                      rows={3}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      value={formData.description}
                      onChange={handleChange}
                      placeholder="Enter lesson description"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <label htmlFor="level" className="block text-sm font-medium text-gray-700">
                        Grade Level
                      </label>
                      <select
                        name="level"
                        id="level"
                        className={`mt-1 block w-full border ${errors.level ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500`}
                        value={formData.level}
                        onChange={handleChange}
                        required
                      >
                        <option value="">Select grade level</option>
                        <option value="1">Grade 1</option>
                        <option value="2">Grade 2</option>
                        <option value="3">Grade 3</option>
                        <option value="4">Grade 4</option>
                        <option value="5">Grade 5</option>
                        <option value="6">Grade 6</option>
                        <option value="7">Grade 7</option>
                        <option value="8">Grade 8</option>
                        <option value="9">Grade 9</option>
                        <option value="10">Grade 10</option>
                        <option value="11">Grade 11</option>
                        <option value="12">Grade 12</option>
                      </select>
                      {errors.level && (
                        <p className="mt-1 text-sm text-red-600">{errors.level}</p>
                      )}
                    </div>
                    
                    <div>
                      <label htmlFor="subject" className="block text-sm font-medium text-gray-700">
                        Subject
                      </label>
                      <select
                        name="subject"
                        id="subject"
                        className={`mt-1 block w-full border ${errors.subject ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500`}
                        value={formData.subject}
                        onChange={handleChange}
                        required
                      >
                        <option value="">Select subject</option>
                        <option value="Mathematics">Mathematics</option>
                        <option value="Science">Science</option>
                        <option value="History">History</option>
                        <option value="English">English</option>
                        <option value="Art">Art</option>
                        <option value="Music">Music</option>
                        <option value="Physical Education">Physical Education</option>
                        <option value="Computer Science">Computer Science</option>
                      </select>
                      {errors.subject && (
                        <p className="mt-1 text-sm text-red-600">{errors.subject}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-5 sm:mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 border border-gray-300 rounded-md"
                  onClick={onClose}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 flex items-center"
                >
                  {isSubmitting ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      {isEditMode ? 'Updating...' : 'Creating...'}
                    </>
                  ) : (
                    isEditMode ? 'Update Lesson' : 'Create Lesson'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Content Upload Modal */}
      {showContentUploadModal && (
        <ContentUploadModal
          isOpen={showContentUploadModal}
          onClose={() => setShowContentUploadModal(false)}
          onUpload={handleContentUpload}
          contentType={contentType}
          temporaryMode={true}
        />
      )}

      {/* Quiz Modal */}
      {showQuizModal && (
        <QuizModal
          isOpen={showQuizModal}
          onClose={() => setShowQuizModal(false)}
          onSave={handleQuizSave}
          quiz={null}
          temporaryMode={true}
        />
      )}
    </div>,
    document.body
  );
};

LessonModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired,
  lesson: PropTypes.object
};

export default LessonModal; 