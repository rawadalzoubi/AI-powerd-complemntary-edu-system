import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import lessonService from '../services/lessonService';
import ContentUploadModal from '../components/lessons/ContentUploadModal';
import QuizModal from '../components/lessons/QuizModal';
import axios from 'axios';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';

// Backend media URL configuration
const BACKEND_URL = 'http://localhost:8000';

// Initialize pdfjs worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const LessonDetailsPage = () => {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const isStudent = currentUser?.role?.toLowerCase() === 'student';
  
  const [lesson, setLesson] = useState(null);
  const [contents, setContents] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [activeTab, setActiveTab] = useState('contents');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Modals for content creation
  const [showContentModal, setShowContentModal] = useState(false);
  const [showQuizModal, setShowQuizModal] = useState(false);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  
  // Modals for student interaction with content
  const [showVideoModal, setShowVideoModal] = useState(false);
  const [showPdfModal, setShowPdfModal] = useState(false);
  const [showQuizTakingModal, setShowQuizTakingModal] = useState(false);
  const [selectedContent, setSelectedContent] = useState(null);
  const [selectedQuizToTake, setSelectedQuizToTake] = useState(null);

  // Add these new state variables after the existing state declarations:
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [pdfError, setPdfError] = useState(false);
  const [showQuizResultModal, setShowQuizResultModal] = useState(false);
  const [quizResult, setQuizResult] = useState({ earnedPoints: 0, totalQuizMarks: 0, detailedMessage: '' });

  useEffect(() => {
    fetchLessonDetails();
  }, [lessonId]);

  const fetchLessonDetails = async () => {
    try {
      setLoading(true);
      console.log(`Fetching lesson details for lessonId: ${lessonId}`);
      
      // FINAL DEBUG ATTEMPT: Use direct axios call with full URL and extra debug info
      const token = localStorage.getItem('accessToken');
      console.log("%c AUTH TOKEN", "background:yellow; color:black", token ? `${token.substring(0, 10)}...` : "Missing");
      
      // Try THREE different API URLs to see which one works
      const urlOptions = [
        `http://localhost:8000/api/student/lessons/${lessonId}/`,
        `http://localhost:8000/api/content/lessons/${lessonId}/`,
        `/api/student/lessons/${lessonId}/`
      ];
      
      console.log("%c ATTEMPTING MULTIPLE URLs", "background:orange; color:white", urlOptions);
      
      let lessonData = null;
      let successUrl = null;
      
      for (const url of urlOptions) {
        try {
          console.log(`Trying URL: ${url}`);
          const response = await axios.get(url, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            withCredentials: true
          });
          
          // If we get here, the request succeeded
          console.log(`%c SUCCESS with URL: ${url}`, "background:green; color:white", response.data);
          lessonData = response.data;
          successUrl = url;
          break;
        } catch (err) {
          console.error(`Failed with URL: ${url}`, err.response || err.message);
        }
      }
      
      if (!lessonData) {
        throw new Error("All URL attempts failed");
      }
      
      console.log(`%c Using successful URL: ${successUrl}`, "background:green; color:white");
      setLesson(lessonData);
      
      // Continue with content and quiz fetching
      try {
        console.log(`Fetching lesson contents for lessonId: ${lessonId}`);
      const contentsData = await lessonService.getLessonContents(lessonId);
        console.log(`%c CONTENT DATA:`, "background:blue; color:white", contentsData);
        console.log(`Successfully fetched ${contentsData.length} content items`);
        
        // Additional debug to inspect each content item
        contentsData.forEach((item, index) => {
          console.log(`Content item ${index + 1}:`, {
            id: item.id,
            title: item.title,
            type: item.content_type,
            file: item.file ? item.file.substring(0, 50) + '...' : 'No file'
          });
        });
        
      setContents(contentsData);
      } catch (contentErr) {
        console.error("Error fetching contents:", contentErr);
        // Don't fail the whole request for this
      }
      
      try {
        console.log(`Fetching lesson quizzes for lessonId: ${lessonId}`);
      const quizzesData = await lessonService.getLessonQuizzes(lessonId);
        console.log(`%c QUIZ DATA:`, "background:purple; color:white", quizzesData);
        console.log(`Successfully fetched ${quizzesData.length} quizzes`);
      setQuizzes(quizzesData);
      } catch (quizErr) {
        console.error("Error fetching quizzes:", quizErr);
        // Don't fail the whole request for this
      }
      
      setError('');
    } catch (err) {
      console.error('%c CRITICAL ERROR fetching lesson details:', 'background:red; color:white', err);
      
      // Handle specific error responses
      if (err.response) {
        console.error('Response data:', err.response.data);
        console.error('Response status:', err.response.status);
        console.error('Response headers:', err.response.headers);
        
        // For 404 errors specifically coming from student API
        if (err.response.status === 404) {
          if (err.response.data?.detail === 'Lesson not found') {
            setError('Lesson not found. Please check if the lesson exists or you have the correct URL.');
          } else if (err.response.data?.detail?.includes('not enrolled')) {
            setError('You are not enrolled in this lesson or it has not been assigned to you.');
          } else {
            setError(err.response.data?.detail || 'Lesson not found.');
          }
        } else if (err.response.status === 403) {
          setError('You do not have permission to access this lesson. Please log in again.');
          // Force re-login after a delay
          setTimeout(() => {
            localStorage.removeItem('accessToken');
            navigate('/login');
          }, 3000);
        } else {
          setError(err.response.data?.detail || 'Failed to load lesson details. Please try again later.');
        }
      } else if (err.request) {
        console.error('No response received:', err.request);
        setError('Network error. Please check your connection and try again.');
      } else {
        console.error('Error message:', err.message);
        setError('An error occurred. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteContent = async (contentId) => {
    if (window.confirm('Are you sure you want to delete this content?')) {
      try {
        await lessonService.deleteLessonContent(contentId);
        setContents(contents.filter(content => content.id !== contentId));
      } catch (err) {
        setError('Failed to delete content. Please try again.');
        console.error('Error deleting content:', err);
      }
    }
  };

  const handleDeleteQuiz = async (quizId) => {
    if (window.confirm('Are you sure you want to delete this quiz?')) {
      try {
        await lessonService.deleteQuiz(quizId);
        setQuizzes(quizzes.filter(quiz => quiz.id !== quizId));
      } catch (err) {
        setError('Failed to delete quiz. Please try again.');
        console.error('Error deleting quiz:', err);
      }
    }
  };

  const handleContentUpload = async (contentData) => {
    try {
      const newContent = await lessonService.uploadLessonContent(lessonId, contentData);
      setContents([...contents, newContent]);
      setShowContentModal(false);
    } catch (err) {
      setError('Failed to upload content. Please try again.');
      console.error('Error uploading content:', err);
    }
  };

  const handleCreateQuiz = async (quizData) => {
    try {
      const newQuiz = await lessonService.createQuiz(lessonId, quizData);
      setQuizzes([...quizzes, newQuiz]);
      setShowQuizModal(false);
    } catch (err) {
      setError('Failed to create quiz. Please try again.');
      console.error('Error creating quiz:', err);
    }
  };

  const handleUpdateQuiz = async (quizData) => {
    try {
      console.log('Updating quiz:', selectedQuiz.id, quizData);
      
      // Make sure we include the lessonId in the quizData
      const updatedQuizData = {
        ...quizData,
        lesson: parseInt(lessonId, 10) // Ensure lessonId is included
      };
      
      const updatedQuiz = await lessonService.updateQuiz(selectedQuiz.id, updatedQuizData);
      setQuizzes(quizzes.map(quiz => 
        quiz.id === updatedQuiz.id ? updatedQuiz : quiz
      ));
      setShowQuizModal(false);
      setSelectedQuiz(null);
    } catch (err) {
      console.error('Failed to update quiz:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to update quiz. Please try again.';
      setError(errorMessage);
      
      if (err.response?.status === 401 || err.response?.status === 403) {
        console.error('Authentication error when updating quiz. Trying to refresh token...');
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    }
  };

  // Function to get proper URL for media files
  const getMediaUrl = (path) => {
    if (!path) return null;
    
    // If path is already a full URL, return as is
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path;
    }
    
    // If path is relative, add the backend URL
    if (path.startsWith('/media/')) {
      return `${BACKEND_URL}${path}`;
    }
    
    // Fallback case
    return `${BACKEND_URL}/media/${path}`;
  };

  // Function to properly handle file downloads
  const handleDownload = (content) => {
    try {
      if (!content || !content.file) {
        setError('No file available for download.');
        return;
      }
      
      console.log("Starting download process for:", content.title, content.file);
      
      // Try multiple approaches to download the file
      const downloadWithMethod = (method) => {
        let fileUrl;
        
        switch(method) {
          case 'direct':
            // Direct media URL - simplest approach
            fileUrl = getMediaUrl(content.file);
            console.log("Trying direct media URL:", fileUrl);
            break;
            
          case 'api':
            // Use the API endpoint
            fileUrl = `${BACKEND_URL}/api/files/?file=${encodeURIComponent(content.file)}`;
            console.log("Trying API endpoint URL:", fileUrl);
            break;
            
          case 'flexible':
            // Get just the filename part from the path
            const pathParts = content.file.split('/');
            const filename = pathParts[pathParts.length - 1];
            
            // Extract base name and extension
            let baseFilename, extension;
            if (filename.includes('.')) {
              // Split at the last period to handle filenames with multiple periods
              const lastDotIndex = filename.lastIndexOf('.');
              baseFilename = filename.substring(0, lastDotIndex).split('_')[0]; // Get part before first underscore
              extension = filename.substring(lastDotIndex + 1);
            } else {
              baseFilename = filename.split('_')[0]; // Get part before first underscore
              extension = '';
            }
            
            // Use the direct download endpoint with base name
            fileUrl = `${BACKEND_URL}/download/${baseFilename}.${extension}`;
            console.log("Trying direct download URL with base filename:", fileUrl);
            break;
            
          default:
            fileUrl = getMediaUrl(content.file);
        }
        
        // For better user experience, trigger download without page navigation
        const link = document.createElement('a');
        link.href = fileUrl;
        link.download = content.title || 'download'; // Use the content title as filename
        link.target = '_blank'; // Open in new tab as fallback
        document.body.appendChild(link);
        link.click();
        setTimeout(() => document.body.removeChild(link), 100);
      };
      
      // Try the flexible approach first as it's most likely to work
      downloadWithMethod('flexible');
      
      // Show options to the user if they need alternatives
      console.log("Alternative download methods available in browser console:");
      console.log("  downloadWithMethod('direct') - Use direct media URL");
      console.log("  downloadWithMethod('api') - Use API endpoint");
      
    } catch (err) {
      console.error("Download error:", err);
      setError('Failed to download file. Please try again or try a different format.');
    }
  };
  
  // Function to get file serving URL
  const getFileServingUrl = (path) => {
    if (!path) return null;
    
    // Extract the relative path from the full URL
    let relativePath = path;
    if (path.startsWith('http://') || path.startsWith('https://')) {
      const urlObj = new URL(path);
      relativePath = urlObj.pathname;
    }
    
    // Make sure we have a proper media path
    if (!relativePath.startsWith('/media/') && !relativePath.startsWith('media/')) {
      relativePath = `/media/${relativePath}`;
    }
    
    // Use the direct URL with the media path
    // The Django settings are configured to serve /media/ URLs directly
    const directUrl = `${BACKEND_URL}${relativePath}`;
    console.log("Direct media URL:", directUrl);
    return directUrl;
  };

  // Helper function to get proxy URL for PDF files to avoid CORS issues
  const getPdfProxyUrl = (url) => {
    if (!url) return '';
    
    console.log("Original PDF URL:", url);
    
    // Extract the relative path from the full URL
    let relativePath = url;
    if (url.startsWith('http://') || url.startsWith('https://')) {
      const urlObj = new URL(url);
      relativePath = urlObj.pathname;
    }
    
    // Make sure we have a proper media path
    if (!relativePath.startsWith('/media/') && !relativePath.startsWith('media/')) {
      relativePath = `/media/${relativePath}`;
    }
    
    // Create the proxy URL
    const proxyUrl = `${BACKEND_URL}/api/pdf-proxy/?file=${encodeURIComponent(relativePath)}`;
    console.log("PDF Proxy URL:", proxyUrl);
    return proxyUrl;
  };

  // Helper function to get PDF viewer URL using Google PDF Viewer as fallback
  const getPdfViewerUrl = (url) => {
    if (!url) return '';
    
    const fullUrl = getMediaUrl(url);
    console.log("Full PDF URL:", fullUrl);
    
    // Use Google PDF Viewer as a reliable fallback
    return `https://docs.google.com/viewer?url=${encodeURIComponent(fullUrl)}&embedded=true`;
  };

  const handleWatchVideo = (content) => {
    // Make sure we have a valid file URL
    if (content.file) {
      console.log("Opening video with URL:", getMediaUrl(content.file));
      setSelectedContent({
        ...content,
        file: getMediaUrl(content.file)
      });
      setShowVideoModal(true);
    } else {
      setError('Video file is not available.');
    }
  };
  
  const handleViewPdf = (content) => {
    // Make sure we have a valid file URL
    if (content.file) {
      console.log("Opening PDF with URL:", getMediaUrl(content.file));
      setSelectedContent({
        ...content,
        file: getMediaUrl(content.file),
        viewerUrl: getPdfViewerUrl(content.file)
      });
      setShowPdfModal(true);
      setPdfError(false);
    } else {
      setError('PDF file is not available.');
    }
  };
  
  const handleTakeQuiz = (quiz) => {
    setSelectedQuizToTake(quiz);
    setShowQuizTakingModal(true);
  };
  
  const handleSubmitQuizAnswers = async (answers) => {
    try {
      console.log('Processing quiz answers:', answers);
      
      // Check if we have any answers
      if (!answers || answers.length === 0) {
        setError('Please answer at least one question.');
        return;
      }
      
      // Calculate correct answers and total questions
      const correctAnswers = answers.filter(a => a.isCorrect).length;
      const totalQuestions = answers.length;
      
      // Get total marks for the quiz
      const totalQuizMarks = selectedQuizToTake.total_marks;

      // Calculate earned points based on the proportion of correct answers
      const earnedPoints = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * totalQuizMarks) : 0;
      
      // Get result message based on score (number of correct questions)
      // This message can remain focused on question count for clarity
      let detailedMessage;
      const percentageOfQuestionsCorrect = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0;

      if (percentageOfQuestionsCorrect === 100) {
        detailedMessage = `Excellent! You got all ${totalQuestions} questions correct!`;
      } else if (percentageOfQuestionsCorrect >= 80) {
        detailedMessage = `Great job! You got ${correctAnswers} out of ${totalQuestions} questions correct.`;
      } else if (percentageOfQuestionsCorrect >= 60) {
        detailedMessage = `Good effort! You got ${correctAnswers} out of ${totalQuestions} questions correct.`;
      } else {
        detailedMessage = `You got ${correctAnswers} out of ${totalQuestions} questions correct. Keep practicing!`;
      }
      
      // Create a quiz attempt using the API
      const token = localStorage.getItem('accessToken');
      
      // 1. Start a quiz attempt
      const startResponse = await axios.post(`http://localhost:8000/api/student/quizzes/${selectedQuizToTake.id}/attempt/`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const attemptId = startResponse.data.id;
      console.log('Started quiz attempt:', attemptId);
      
      // 2. Submit each answer
      for (const answer of answers) {
        if (answer.answerId) {
          await axios.post(`http://localhost:8000/api/student/quiz-attempts/${attemptId}/submit-answer/`, {
            question_id: answer.questionId,
            answer_id: answer.answerId
          }, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          console.log(`Submitted answer for question ${answer.questionId}`);
        }
      }
      
      // 3. Complete the quiz attempt
      const completeResponse = await axios.post(`http://localhost:8000/api/student/quiz-attempts/${attemptId}/complete/`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('Quiz attempt completed:', completeResponse.data);
      
      // Show the result in a modal
      setQuizResult({ 
        earnedPoints,
        totalQuizMarks,
        detailedMessage 
      });
      setShowQuizResultModal(true);
      
      // Close the quiz taking modal and refresh the lesson data
      setShowQuizTakingModal(false);
      fetchLessonDetails();
    } catch (err) {
      console.error('Error submitting quiz answers:', err);
      setError('Failed to submit quiz. Please try again.');
    }
  };

  const handleEditQuiz = (quiz) => {
    setSelectedQuiz(quiz);
    setShowQuizModal(true);
  };

  const handleBack = () => {
    if (currentUser && currentUser.role) {
      const role = currentUser.role.toLowerCase();
      
      if (role === 'student') {
        navigate('/student/dashboard');
      } else if (role === 'advisor') {
        navigate('/advisor/lessons');
      } else {
        navigate('/lessons');
      }
    } else {
    navigate('/lessons');
    }
  };

  const getContentTypeIcon = (contentType) => {
    switch (contentType) {
      case 'VIDEO':
        return <i className="fas fa-video text-indigo-500"></i>;
      case 'IMAGE':
        return <i className="fas fa-image text-blue-500"></i>;
      case 'PDF':
        return <i className="fas fa-file-pdf text-red-500"></i>;
      case 'DOC':
        return <i className="fas fa-file-word text-blue-700"></i>;
      default:
        return <i className="fas fa-file text-gray-500"></i>;
    }
  };

  // Add these new functions after handleViewPdf:
  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setPdfError(false);
  };

  const handlePdfError = (error) => {
    console.error("PDF failed to load:", error);
    setPdfError(true);
  };

  const changePage = (offset) => {
    setPageNumber(prevPageNumber => {
      const newPageNumber = prevPageNumber + offset;
      return Math.max(1, Math.min(newPageNumber, numPages || 1));
    });
  };

  const previousPage = () => changePage(-1);
  const nextPage = () => changePage(1);

  if (loading) {
    return (
      <div className="p-6 text-center">
        <i className="fas fa-spinner fa-spin text-indigo-600 text-3xl mb-4"></i>
        <p className="text-gray-600">Loading lesson details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
          {error}
        </div>
        <button
          onClick={handleBack}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center"
        >
          <i className="fas fa-arrow-left mr-2"></i> Back to Lessons
        </button>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="p-6">
        <div className="bg-yellow-100 text-yellow-700 p-4 rounded-lg mb-4">
          Lesson not found.
        </div>
        <button
          onClick={handleBack}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center"
        >
          <i className="fas fa-arrow-left mr-2"></i> Back to Lessons
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex items-center mb-6">
        <button
          onClick={handleBack}
          className="mr-4 text-indigo-600 hover:text-indigo-800"
        >
          <i className="fas fa-arrow-left"></i>
        </button>
        <h1 className="text-2xl font-bold text-gray-800">{lesson.name}</h1>
      </div>

      <div className="bg-white rounded-xl shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="px-3 py-1 text-sm rounded-full bg-blue-100 text-blue-800">
                {lesson.level_display}
              </span>
              <span className="px-3 py-1 text-sm rounded-full bg-purple-100 text-purple-800">
                {lesson.subject}
              </span>
            </div>
            <p className="text-gray-600">
              Created on: {new Date(lesson.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="border-b border-gray-200 mb-6">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('contents')}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                activeTab === 'contents'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <i className="fas fa-file-alt mr-2"></i>Contents
            </button>
            <button
              onClick={() => setActiveTab('quizzes')}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                activeTab === 'quizzes'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <i className="fas fa-tasks mr-2"></i>Quizzes
            </button>
          </nav>
        </div>

        {activeTab === 'contents' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium text-gray-800">Lesson Contents</h2>
              
              {!isStudent && (
              <button
                onClick={() => setShowContentModal(true)}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center"
              >
                <i className="fas fa-plus mr-2"></i> Add Content
              </button>
              )}
            </div>

            {contents.length === 0 ? (
              <div className="text-center py-8 border border-dashed border-gray-300 rounded-lg">
                <i className="fas fa-file-upload text-gray-400 text-4xl mb-3"></i>
                {isStudent ? (
                  <p className="text-gray-500">No content available for this lesson yet.</p>
                ) : (
                <p className="text-gray-500">No content yet. Add your first content!</p>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {contents.map((content) => (
                  <div key={content.id} className="border border-gray-200 rounded-lg p-4 flex items-start">
                    <div className="mr-4 mt-1">
                      {getContentTypeIcon(content.content_type)}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{content.title}</h3>
                      <p className="text-sm text-gray-500">{content.content_type_display || content.content_type}</p>
                      <div className="mt-2">
                        {isStudent ? (
                          <>
                            {content.content_type === 'VIDEO' && (
                              <button
                                onClick={() => handleWatchVideo(content)}
                                className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded text-sm mr-2"
                              >
                                <i className="fas fa-play mr-1"></i> Watch Video
                              </button>
                            )}
                            {content.content_type === 'PDF' && (
                              <>
                                <button
                                  onClick={() => handleDownload(content)}
                                  className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-3 py-1 rounded text-sm"
                                >
                                  <i className="fas fa-download mr-1"></i> Download
                                </button>
                              </>
                            )}
                            {content.content_type !== 'VIDEO' && content.content_type !== 'PDF' && (
                              <button
                                onClick={() => handleDownload(content)}
                                className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-3 py-1 rounded text-sm"
                              >
                                <i className="fas fa-download mr-1"></i> Download
                              </button>
                            )}
                          </>
                        ) : (
                          <>
                        <button
                          onClick={() => handleDownload(content)}
                          className="text-indigo-600 hover:text-indigo-800 text-sm mr-3"
                        >
                          <i className="fas fa-download mr-1"></i> Download
                        </button>
                        <button
                          onClick={() => handleDeleteContent(content.id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          <i className="fas fa-trash mr-1"></i> Delete
                        </button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'quizzes' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium text-gray-800">Quizzes</h2>
              
              {!isStudent && (
              <button
                onClick={() => {
                  setSelectedQuiz(null);
                  setShowQuizModal(true);
                }}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center"
              >
                <i className="fas fa-plus mr-2"></i> Add Quiz
              </button>
              )}
            </div>

            {quizzes.length === 0 ? (
              <div className="text-center py-8 border border-dashed border-gray-300 rounded-lg">
                <i className="fas fa-tasks text-gray-400 text-4xl mb-3"></i>
                {isStudent ? (
                  <p className="text-gray-500">No quizzes available for this lesson yet.</p>
                ) : (
                <p className="text-gray-500">No quizzes yet. Create your first quiz!</p>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {quizzes.map((quiz) => (
                  <div key={quiz.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium text-gray-900">{quiz.title}</h3>
                        <p className="text-sm text-gray-500">Total marks: {quiz.total_marks}</p>
                        <p className="text-sm text-gray-500">
                          Questions: {quiz.questions ? quiz.questions.length : 0}
                        </p>
                      </div>
                      <div>
                        {!isStudent && (
                          <>
                        <button
                          onClick={() => handleEditQuiz(quiz)}
                          className="text-indigo-600 hover:text-indigo-800 mr-3"
                        >
                          <i className="fas fa-edit"></i>
                        </button>
                        <button
                          onClick={() => handleDeleteQuiz(quiz.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <i className="fas fa-trash"></i>
                        </button>
                          </>
                        )}
                        {isStudent && (
                          <button
                            onClick={() => handleTakeQuiz(quiz)}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded text-sm"
                          >
                            Take Quiz
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modals for teachers to create/edit content and quizzes */}
      {!isStudent && (
        <>
      {showContentModal && (
        <ContentUploadModal
          isOpen={showContentModal}
          onClose={() => setShowContentModal(false)}
          onUpload={handleContentUpload}
          lessonId={parseInt(lessonId, 10)}
          contentType="VIDEO"
        />
      )}

      {showQuizModal && (
        <QuizModal
          isOpen={showQuizModal}
          onClose={() => {
            setShowQuizModal(false);
            setSelectedQuiz(null);
          }}
          onSave={selectedQuiz ? handleUpdateQuiz : handleCreateQuiz}
          quiz={selectedQuiz}
          lessonId={parseInt(lessonId, 10)}
        />
          )}
        </>
      )}
      
      {/* Modals for students to interact with content */}
      {isStudent && (
        <>
          {/* Video Player Modal */}
          {showVideoModal && selectedContent && (
            <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-lg w-full max-w-4xl">
                <div className="p-4 border-b flex justify-between items-center">
                  <h3 className="text-lg font-medium">{selectedContent.title}</h3>
                  <button 
                    onClick={() => setShowVideoModal(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <i className="fas fa-times"></i>
                  </button>
                </div>
                <div className="p-4">
                  {/* Video player with error handling */}
                  <div className="relative pt-56.25%">
                    <video 
                      controls 
                      className="w-full rounded" 
                      src={selectedContent.file}
                      autoPlay
                      onError={(e) => {
                        console.error("Error loading video:", e, selectedContent.file);
                        setError('Error loading video. The format may not be supported by your browser.');
                      }}
                    >
                      <source src={selectedContent.file} type="video/mp4" />
                      <source src={selectedContent.file} type="video/webm" />
                      <p>Your browser does not support the video tag.</p>
                    </video>
                  </div>
                  
                  {/* Fallback message if video fails to load */}
                  <div className="mt-4 text-center">
                    <button 
                      onClick={() => handleDownload(selectedContent)}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded text-sm"
                    >
                      <i className="fas fa-download mr-1"></i> Download Video
                    </button>
                    <p className="text-gray-500 text-sm mt-2">
                      If the video doesn't play, try downloading it.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* PDF Viewer Modal */}
          {showPdfModal && selectedContent && (
            <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-lg w-full max-w-4xl h-5/6">
                <div className="p-4 border-b flex justify-between items-center">
                  <h3 className="text-lg font-medium">{selectedContent.title}</h3>
                  <div>
                    <button 
                      onClick={() => handleDownload(selectedContent)}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded text-sm mr-3"
                    >
                      <i className="fas fa-download mr-1"></i> Download
                    </button>
                    <button 
                      onClick={() => setShowPdfModal(false)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  </div>
                </div>
                <div className="p-0 h-5/6">
                  {/* Update the iframe source */}
                  <iframe
                    src={selectedContent.viewerUrl}
                    className="w-full h-full border-0"
                    title={selectedContent.title}
                    onError={(e) => {
                      console.error("PDF iframe error:", e);
                      setPdfError(true);
                    }}
                  />
                  
                  {/* Error fallback */}
                  {pdfError && (
                    <div className="absolute inset-0 bg-white flex flex-col items-center justify-center">
                      <p className="text-red-500 text-center mb-4">
                        The PDF could not be displayed in the browser.
                      </p>
                      <button 
                        onClick={() => handleDownload(selectedContent)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
                      >
                        <i className="fas fa-download mr-1"></i> Download PDF
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {/* Quiz Taking Modal */}
          {showQuizTakingModal && selectedQuizToTake && (
            <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-lg w-full max-w-4xl max-h-90vh overflow-y-auto">
                <div className="p-4 border-b flex justify-between items-center sticky top-0 bg-white">
                  <h3 className="text-lg font-medium">{selectedQuizToTake.title}</h3>
                  <button 
                    onClick={() => setShowQuizTakingModal(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <i className="fas fa-times"></i>
                  </button>
                </div>
                <div className="p-6">
                  <h4 className="text-lg font-medium mb-4">Quiz Questions</h4>
                  
                  {selectedQuizToTake.questions && selectedQuizToTake.questions.length > 0 ? (
                    <form onSubmit={(e) => {
                      e.preventDefault();
                      const formData = new FormData(e.target);
                      const answers = [];
                      
                      // Process form data to collect answers
                      selectedQuizToTake.questions.forEach(question => {
                        // Get the answer ID selected by the user
                        const selectedAnswerId = formData.get(`question_${question.id}`);
                        
                        if (selectedAnswerId) {
                          // Find the selected answer object
                          const selectedAnswer = question.answers.find(a => a.id.toString() === selectedAnswerId);
                          
                          // Determine if the answer is correct
                          const isCorrect = selectedAnswer ? selectedAnswer.is_correct : false;
                          
                          console.log(`Question ${question.id}: Selected answer=${selectedAnswerId}, isCorrect=${isCorrect}`);
                          
                          answers.push({
                            questionId: question.id,
                            answerId: selectedAnswerId,
                            isCorrect: isCorrect
                          });
                        } else {
                          // If no answer was selected, count it as incorrect
                          console.log(`Question ${question.id}: No answer selected`);
                          answers.push({
                            questionId: question.id,
                            answerId: null,
                            isCorrect: false
                          });
                        }
                      });
                      
                      handleSubmitQuizAnswers(answers);
                    }}>
                      {selectedQuizToTake.questions.map((question, qIndex) => (
                        <div key={question.id} className="mb-6 p-4 border border-gray-200 rounded-lg">
                          <div className="flex items-start mb-3">
                            <span className="bg-indigo-100 text-indigo-800 text-xs rounded-full h-6 w-6 flex items-center justify-center mr-2 mt-1">
                              {qIndex + 1}
                            </span>
                            <div>
                              <p className="font-medium">{question.question_text}</p>
                              <p className="text-sm text-gray-500">
                                {question.question_type === 'SINGLE' && 'Select one answer'}
                                {question.question_type === 'MULTIPLE' && 'Select all that apply'}
                                {question.question_type === 'TRUE_FALSE' && 'True or False'}
                              </p>
                            </div>
                          </div>
                          
                          <div className="pl-8">
                            {question.answers && question.answers.map((answer) => (
                              <div key={answer.id} className="mb-2 flex items-center">
                                <input
                                  type={question.question_type === 'MULTIPLE' ? 'checkbox' : 'radio'}
                                  id={`answer_${answer.id}`}
                                  name={`question_${question.id}`}
                                  value={answer.id}
                                  className="mr-2"
                                  required={question.question_type !== 'MULTIPLE'}
                                />
                                <label htmlFor={`answer_${answer.id}`} className="text-gray-700">
                                  {answer.answer_text}
                                </label>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                      
                      <div className="mt-6 flex justify-end">
                        <button 
                          type="button"
                          onClick={() => setShowQuizTakingModal(false)}
                          className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-lg mr-3"
                        >
                          Cancel
                        </button>
                        <button 
                          type="submit"
                          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
                        >
                          Submit Answers
                        </button>
                      </div>
                    </form>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-500">This quiz has no questions yet.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Quiz Result Modal */}
      {showQuizResultModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-md">
            <div className="p-4 border-b flex justify-between items-center bg-indigo-600 rounded-t-lg">
              <h3 className="text-lg font-medium text-white">Quiz Result</h3>
              <button 
                onClick={() => setShowQuizResultModal(false)}
                className="text-white hover:text-gray-200"
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="p-6 text-center">
              <h4 className="text-2xl font-bold mb-2">Your Score: {quizResult.earnedPoints}/{quizResult.totalQuizMarks}</h4>
              <p className="text-gray-600 mb-2">{quizResult.detailedMessage}</p>
              <button 
                onClick={() => setShowQuizResultModal(false)}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LessonDetailsPage; 