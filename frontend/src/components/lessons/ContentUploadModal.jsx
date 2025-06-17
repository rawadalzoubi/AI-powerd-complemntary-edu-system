import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';

const ContentUploadModal = ({ isOpen, onClose, onUpload, lessonId, contentType, temporaryMode = false }) => {
  console.log("ContentUploadModal opened with lessonId:", lessonId, "contentType:", contentType, "temporaryMode:", temporaryMode);
  
  const [formData, setFormData] = useState({
    title: '',
    content_type: '',
    file: null
  });
  const [errors, setErrors] = useState({});
  const [filePreview, setFilePreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Initialize form data when modal opens or contentType changes
  useEffect(() => {
    if (isOpen && contentType) {
      console.log("Setting initial content_type to:", contentType);
      setFormData(prev => ({
        ...prev,
        content_type: contentType
      }));
    }
  }, [isOpen, contentType]);

  useEffect(() => {
    if (isOpen && lessonId && !temporaryMode) {
      console.log("ContentUploadModal is open with lessonId:", lessonId);
    } else if (isOpen && !lessonId && !temporaryMode) {
      console.error("ContentUploadModal opened without a lessonId in regular mode!");
    } else if (isOpen && temporaryMode) {
      console.log("ContentUploadModal opened in temporary mode - no lessonId needed");
    }
  }, [isOpen, lessonId, temporaryMode]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });

    // Clear validation error when field is modified
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: null
      });
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleFile = (file) => {
    setFormData({
      ...formData,
      file
    });

    // Clear file error if exists
    if (errors.file) {
      setErrors({
        ...errors,
        file: null
      });
    }

    // Create preview for image files
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFilePreview(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setFilePreview(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFile(file);
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (!formData.content_type) {
      newErrors.content_type = 'Content type is required';
    }
    if (!formData.file) {
      newErrors.file = 'File is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    // Handle temporary mode (content-first approach)
    if (temporaryMode) {
      console.log("Uploading in temporary mode - return data to parent without API call");
      // Just return content data to parent component without making API call
      const tempContentData = {
        title: formData.title,
        content_type: formData.content_type,
        file: formData.file,
        // Include any other needed data
        fileName: formData.file.name,
        fileSize: formData.file.size,
        fileType: formData.file.type,
        // Add a unique temporary ID so we can reference this item
        tempId: Date.now().toString()
      };
      
      onUpload(tempContentData);
      return;
    }

    // Non-temporary mode - requires a lessonId
    if (!lessonId) {
      console.error("Cannot upload content: No lesson ID provided");
      setErrors({
        general: "No lesson ID available. Please try again."
      });
      return;
    }

    console.log("Starting content upload for lessonId:", lessonId, "type:", typeof lessonId);
    setIsUploading(true);
    setUploadProgress(0);
    
    try {
      console.log('Starting upload for:', formData);
      console.log('Lesson ID:', lessonId);
      
      // Create FormData object for file upload
      const uploadData = new FormData();
      uploadData.append('title', formData.title);
      uploadData.append('content_type', formData.content_type);
      uploadData.append('file', formData.file);
      uploadData.append('lesson', lessonId.toString()); // Ensure lessonId is a string
      
      // Log FormData contents for debugging
      for (let pair of uploadData.entries()) {
        console.log(pair[0] + ': ' + (pair[1] instanceof File ? `${pair[1].name} (${pair[1].size} bytes)` : pair[1]));
      }
      
      // Make axios request with progress tracking
      // Check if the API URL has a leading slash and adjust accordingly
      const apiBaseUrl = import.meta.env.VITE_API_URL || '';
      const contentEndpoint = `${apiBaseUrl}/api/content/lessons/${lessonId}/contents/`;
      
      console.log('Using API endpoint:', contentEndpoint);
      
      const response = await axios.post(
        contentEndpoint, 
        uploadData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
          },
          withCredentials: true, // Include cookies for authentication
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            console.log(`Upload progress: ${percentCompleted}%`);
            setUploadProgress(percentCompleted);
          },
          timeout: 300000 // 5 minute timeout for large uploads
        }
      );
      
      console.log('Upload successful:', response.data);
      
      // Complete the progress to 100%
      setUploadProgress(100);
      
      // Wait a moment before closing to show 100% progress
      setTimeout(() => {
        // Call the onUpload callback with the response data
        onUpload(response.data);
        
        // Close the modal
        onClose();
      }, 500);
    } catch (error) {
      console.error('Upload failed:', error);
      
      let errorMsg = 'Failed to upload content. Please try again.';
      
      // Detailed error logging for debugging
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
        console.error('Response headers:', error.response.headers);
        
        if (error.response.status === 413) {
          errorMsg = 'File is too large. Maximum file size allowed is 100MB.';
        } else if (error.response.status === 401) {
          errorMsg = 'Authentication error. Please log in again.';
        } else if (error.response.status === 404) {
          errorMsg = 'API endpoint not found. Please check configuration.';
        }
        
        // Handle validation errors from backend
        if (error.response.data) {
          const backendErrors = error.response.data;
          const mappedErrors = {};
          
          // Map backend errors to form fields
          Object.keys(backendErrors).forEach(key => {
            mappedErrors[key] = Array.isArray(backendErrors[key]) 
              ? backendErrors[key].join(', ') 
              : backendErrors[key];
              
            // Add additional context to general error
            if (typeof backendErrors[key] === 'string') {
              errorMsg = backendErrors[key];
            } else if (Array.isArray(backendErrors[key])) {
              errorMsg = backendErrors[key].join(', ');
            }
          });
          
          setErrors(mappedErrors);
        }
      } else if (error.request) {
        // The request was made but no response was received
        console.error('No response received:', error.request);
        errorMsg = 'No response from server. Please check your connection.';
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Error message:', error.message);
        errorMsg = `Error: ${error.message}`;
      }
      
      // Set general error
      setErrors({
        general: errorMsg
      });
      
      // Reset upload state
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const getFileTypeIcon = () => {
    if (!formData.file) return null;
    
    const fileType = formData.file.type;
    
    if (fileType.startsWith('image/')) {
      return 'fa-file-image text-green-500';
    } else if (fileType.includes('pdf')) {
      return 'fa-file-pdf text-red-500';
    } else if (fileType.includes('video')) {
      return 'fa-file-video text-blue-500';
    } else if (fileType.includes('word') || fileType.includes('doc')) {
      return 'fa-file-word text-blue-700';
    } else if (fileType.includes('sheet') || fileType.includes('excel') || fileType.includes('csv')) {
      return 'fa-file-excel text-green-700';
    } else if (fileType.includes('presentation') || fileType.includes('powerpoint')) {
      return 'fa-file-powerpoint text-orange-600';
    } else if (fileType.includes('zip') || fileType.includes('rar') || fileType.includes('tar') || fileType.includes('gz')) {
      return 'fa-file-archive text-yellow-600';
    } else {
      return 'fa-file text-gray-500';
    }
  };

  const getFileTypeLabel = () => {
    if (!formData.file) return '';
    
    return formData.file.type.split('/')[0].charAt(0).toUpperCase() + formData.file.type.split('/')[0].slice(1);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center">
        {/* Background overlay */}
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={onClose}></div>
        
        {/* Modal panel */}
        <div className="relative inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                {formData.content_type === 'VIDEO' ? 'Upload Video' : 
                formData.content_type === 'PDF' ? 'Upload PDF' : 
                formData.content_type === 'DOC' ? 'Upload Document' : 
                'Upload Content'}
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
              <div className="space-y-4">
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                    Content Title
                  </label>
                  <input
                    type="text"
                    name="title"
                    id="title"
                    className={`mt-1 block w-full border ${errors.title ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500`}
                    value={formData.title}
                    onChange={handleChange}
                    disabled={isUploading}
                    placeholder={`Enter ${formData.content_type === 'VIDEO' ? 'video' : formData.content_type === 'PDF' ? 'PDF' : 'content'} title`}
                  />
                  {errors.title && (
                    <p className="mt-1 text-sm text-red-600">{errors.title}</p>
                  )}
                </div>
                
                <div>
                  <label htmlFor="content_type" className="block text-sm font-medium text-gray-700">
                    Content Type
                  </label>
                  <select
                    name="content_type"
                    id="content_type"
                    className={`mt-1 block w-full border ${errors.content_type ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500`}
                    value={formData.content_type}
                    onChange={handleChange}
                    disabled={isUploading}
                  >
                    <option value="">Select content type</option>
                    <option value="VIDEO">Video</option>
                    <option value="PDF">PDF</option>
                    <option value="DOC">Document</option>
                    <option value="IMAGE">Image</option>
                  </select>
                  {errors.content_type && (
                    <p className="mt-1 text-sm text-red-600">{errors.content_type}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Upload File
                  </label>
                  <div 
                    className={`mt-1 flex justify-center px-6 pt-5 pb-6 border-2 ${isDragging ? 'border-indigo-300 bg-indigo-50' : 'border-gray-300'} ${errors.file ? 'border-red-300 bg-red-50' : ''} border-dashed rounded-md`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                  >
                    <div className="space-y-1 text-center">
                      {formData.file ? (
                        <div className="flex flex-col items-center">
                          {filePreview ? (
                            <img src={filePreview} alt="Preview" className="h-24 w-auto mb-3 rounded" />
                          ) : (
                            <div className="mx-auto h-12 w-12 text-center mb-3">
                              <i className={`fas ${getFileTypeIcon()} text-3xl`}></i>
                            </div>
                          )}
                          <p className="text-sm text-gray-700 mb-1">
                            {formData.file.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {getFileTypeLabel()} • {(formData.file.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                          <button
                            type="button"
                            onClick={() => setFormData({...formData, file: null})}
                            className="mt-2 inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            disabled={isUploading}
                          >
                            Change file
                          </button>
                        </div>
                      ) : (
                        <>
                          <div className="flex text-sm text-gray-600">
                            <label
                              htmlFor="file-upload"
                              className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                            >
                              <span>Upload a file</span>
                              <input 
                                id="file-upload" 
                                name="file-upload" 
                                type="file" 
                                className="sr-only" 
                                onChange={handleFileChange}
                                disabled={isUploading}
                                accept={
                                  formData.content_type === 'VIDEO' ? 'video/*' :
                                  formData.content_type === 'PDF' ? 'application/pdf' :
                                  formData.content_type === 'DOC' ? '.doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document' :
                                  formData.content_type === 'IMAGE' ? 'image/*' : 
                                  undefined
                                }
                              />
                            </label>
                            <p className="pl-1">or drag and drop</p>
                          </div>
                          <p className="text-xs text-gray-500">
                            {formData.content_type === 'VIDEO' ? 'MP4, WebM, or AVI up to 500MB' :
                            formData.content_type === 'PDF' ? 'PDF up to 100MB' :
                            formData.content_type === 'DOC' ? 'DOC, DOCX up to 100MB' :
                            formData.content_type === 'IMAGE' ? 'PNG, JPG, GIF up to 20MB' :
                            'Select content type first'}
                          </p>
                        </>
                      )}
                    </div>
                  </div>
                  {errors.file && (
                    <p className="mt-1 text-sm text-red-600">{errors.file}</p>
                  )}
                </div>
              </div>
              
              {/* Upload progress bar */}
              {isUploading && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700">
                    Uploading... {uploadProgress}%
                  </p>
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300" 
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              <div className="mt-5 sm:mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 border border-gray-300 rounded-md"
                  onClick={onClose}
                  disabled={isUploading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUploading}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 flex items-center"
                >
                  {isUploading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Uploading...
                    </>
                  ) : temporaryMode ? 'Add Content' : 'Upload Content'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

ContentUploadModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onUpload: PropTypes.func.isRequired,
  lessonId: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  contentType: PropTypes.string,
  temporaryMode: PropTypes.bool
};

export default ContentUploadModal; 