import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import lessonService from '../services/lessonService';
import LessonModal from '../components/lessons/LessonModal';

const LessonsPage = () => {
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [currentLesson, setCurrentLesson] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLessons();
  }, []);

  const fetchLessons = async () => {
    try {
      setLoading(true);
      const data = await lessonService.getLessons();
      setLessons(data);
      setError('');
    } catch (err) {
      setError('Failed to load lessons. Please try again later.');
      console.error('Error fetching lessons:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLesson = () => {
    setCurrentLesson(null);
    setShowModal(true);
  };

  const handleEditLesson = (lesson) => {
    console.log('Editing lesson:', lesson);
    setCurrentLesson({
      id: lesson.id,
      name: lesson.name,
      description: lesson.description,
      level: lesson.level,
      subject: lesson.subject
    });
    setShowModal(true);
  };

  const handleDeleteLesson = async (lessonId) => {
    if (window.confirm('Are you sure you want to delete this lesson?')) {
      try {
        await lessonService.deleteLesson(lessonId);
        setLessons(lessons.filter(lesson => lesson.id !== lessonId));
      } catch (err) {
        setError('Failed to delete lesson. Please try again.');
        console.error('Error deleting lesson:', err);
      }
    }
  };

  const handleModalClose = () => {
    setShowModal(false);
  };

  const handleLessonSave = async (lessonData) => {
    try {
      let savedLessonId;
      
      // Extract content data from lessonData
      const { contents, quizzes, ...lessonDetails } = lessonData;
      
      if (currentLesson) {
        // Update existing lesson
        console.log('Updating lesson with ID:', currentLesson.id, 'Data:', lessonDetails);
        const updatedLesson = await lessonService.updateLesson(currentLesson.id, lessonDetails);
        setLessons(lessons.map(lesson => 
          lesson.id === updatedLesson.id ? updatedLesson : lesson
        ));
        savedLessonId = updatedLesson.id;
        console.log("Updated existing lesson with ID:", savedLessonId);
      } else {
        // Create new lesson
        console.log('Creating new lesson with data:', lessonDetails);
        const newLesson = await lessonService.createLesson(lessonDetails);
        setLessons([...lessons, newLesson]);
        savedLessonId = newLesson.id;
        console.log("Created new lesson with ID:", savedLessonId);
        
        // After lesson is created, handle uploaded content if any
        if (contents && contents.length > 0) {
          console.log("Processing uploaded content for new lesson:", contents.length, "items");
          for (const content of contents) {
            try {
              // Prepare content data for API call
              const contentFormData = new FormData();
              contentFormData.append('title', content.title);
              contentFormData.append('content_type', content.content_type);
              contentFormData.append('file', content.file);
              
              await lessonService.uploadLessonContent(savedLessonId, {
                title: content.title,
                content_type: content.content_type,
                file: content.file
              });
              console.log("Content uploaded successfully:", content.title);
            } catch (contentError) {
              console.error("Error uploading content:", contentError);
            }
          }
        }
        
        // Handle quizzes if any
        if (quizzes && quizzes.length > 0) {
          console.log("Processing quizzes for new lesson:", quizzes.length, "items");
          for (const quiz of quizzes) {
            try {
              await lessonService.createQuiz(savedLessonId, quiz);
              console.log("Quiz created successfully:", quiz.title);
            } catch (quizError) {
              console.error("Error creating quiz:", quizError);
            }
          }
        }
      }
      
      // Close the modal
      setShowModal(false);
      
      // Refresh the lessons list to show the new content
      fetchLessons();
    } catch (err) {
      console.error('Error saving lesson:', err);
      setError('Failed to save lesson. Please try again.');
    }
  };

  const handleBackToDashboard = () => {
    navigate('/student/dashboard');
  };

  // Function to determine badge color based on subject
  const getSubjectBadgeColor = (subject) => {
    const subjectMap = {
      'Mathematics': 'blue',
      'Science': 'green',
      'History': 'purple',
      'English': 'yellow',
      'Geography': 'orange',
      'Art': 'pink',
      'Music': 'indigo',
      'Physical Education': 'red',
      'Foreign Language': 'teal',
      'Computer Science': 'cyan'
    };
    
    return subjectMap[subject] || 'gray';
  };

  return (
    <div className="p-6">
      <div className="bg-white rounded-xl shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-800">Lessons Management</h2>
          <div className="flex space-x-3">
            <button 
              onClick={handleBackToDashboard}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center"
            >
              <i className="fas fa-arrow-left mr-2"></i> Back to Dashboard
            </button>
            <button 
              onClick={handleCreateLesson}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center"
            >
              <i className="fas fa-plus mr-2"></i> New Lesson
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-8">
            <i className="fas fa-spinner fa-spin text-indigo-600 text-2xl"></i>
            <p className="mt-2 text-gray-600">Loading lessons...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            {lessons.length === 0 ? (
              <div className="text-center py-8">
                <i className="fas fa-book text-gray-400 text-4xl mb-3"></i>
                <p className="text-gray-500">No lessons found. Create your first lesson!</p>
              </div>
            ) : (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade & Subject</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Content</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {lessons.map((lesson) => (
                    <tr key={lesson.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{lesson.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full bg-${getSubjectBadgeColor(lesson.subject)}-100 text-${getSubjectBadgeColor(lesson.subject)}-800`}>
                          {lesson.level_display} - {lesson.subject}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex space-x-2">
                          {lesson.content_count > 0 && (
                            <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800 flex items-center">
                              {lesson.content_count} items
                            </span>
                          )}
                          {lesson.quiz_count > 0 && (
                            <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800 flex items-center">
                              <i className="fas fa-tasks mr-1"></i> {lesson.quiz_count} quizzes
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(lesson.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <Link to={`/lessons/${lesson.id}`} className="text-blue-600 hover:text-blue-900 mr-3">
                          <i className="fas fa-eye"></i>
                        </Link>
                        <button 
                          onClick={() => handleEditLesson(lesson)} 
                          className="text-indigo-600 hover:text-indigo-900 mr-3"
                          aria-label="Edit lesson"
                        >
                          <i className="fas fa-edit"></i>
                        </button>
                        <button 
                          onClick={() => handleDeleteLesson(lesson.id)} 
                          className="text-red-600 hover:text-red-900"
                        >
                          <i className="fas fa-trash"></i>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>

      {showModal && (
        <LessonModal 
          isOpen={showModal}
          onClose={handleModalClose}
          onSave={handleLessonSave}
          lesson={currentLesson}
        />
      )}
    </div>
  );
};

export default LessonsPage; 