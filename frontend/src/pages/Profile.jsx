import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { getUserProfile, updateUserProfile } from '../services/userService';

const Profile = () => {
  const { currentUser, updateUser } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [isEditMode, setIsEditMode] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone_number: '',
    specialization: '',
    academic_degree: '',
    years_of_experience: '',
    country: '',
    state: '',
    profile_image: null,
    cover_image: null,
    birthdate: '',
    grade_level: ''
  });
  const [previewUrls, setPreviewUrls] = useState({
    profile_image: null,
    cover_image: null
  });
  const [profileLoaded, setProfileLoaded] = useState(false);

  // Use callback to prevent unnecessary re-renders
  const loadUserProfile = useCallback(async () => {
    if (!currentUser) return;
    
    try {
      setIsLoading(true);
      const userData = await getUserProfile();
      
      // Update all state in one go to prevent multiple re-renders
      setFormData({
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        phone_number: userData.phone_number || '',
        specialization: userData.specialization || '',
        academic_degree: userData.academic_degree || '',
        years_of_experience: userData.years_of_experience || '',
        country: userData.country || '',
        state: userData.state || '',
        profile_image: null,
        cover_image: null,
        birthdate: userData.birthdate || '',
        grade_level: userData.grade_level || ''
      });
      
      setPreviewUrls({
        profile_image: userData.profile_image || null,
        cover_image: userData.cover_image || null
      });
      
      setProfileLoaded(true);
      console.log('Loaded profile data:', userData);
    } catch (error) {
      console.error('Error loading profile data:', error);
      
      // Check for token expiration
      if (error.code === 'token_not_valid' || 
          (error.detail && error.detail.includes('token not valid')) ||
          (error.message && error.message.includes('expired'))) {
        console.log('Token expired, redirecting to login...');
        // Clear localStorage and redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        navigate('/login', { state: { message: 'Your session has expired. Please log in again.' }});
        return;
      }
      
      setMessage({
        type: 'error',
        text: 'Failed to load profile data'
      });
    } finally {
      setIsLoading(false);
    }
  }, [currentUser, navigate]);

  useEffect(() => {
    if (!currentUser) {
      navigate('/login');
      return;
    }

    // Load user data
    loadUserProfile();
  }, [currentUser, navigate, loadUserProfile]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    if (files && files[0]) {
      setFormData(prev => ({ ...prev, [name]: files[0] }));
      
      // Create preview URL for the local file
      const previewUrl = URL.createObjectURL(files[0]);
      setPreviewUrls(prev => ({ ...prev, [name]: previewUrl }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const formDataToSend = new FormData();
      
      // Add form fields to FormData
      Object.keys(formData).forEach(key => {
        if (formData[key] !== null && formData[key] !== '') {
          formDataToSend.append(key, formData[key]);
        }
      });
      
      // Explicitly add role information
      formDataToSend.append('role', currentUser.role || 'student');
      
      console.log('Sending profile update with form data', 
        Object.fromEntries(formDataToSend.entries())
      );

      const updatedUserData = await updateUserProfile(formDataToSend);
      
      if (updatedUserData) {
        console.log('Profile updated successfully:', updatedUserData);
        
        // Update the UI with the new data
        setFormData(prev => ({
          ...prev,
          first_name: updatedUserData.first_name || prev.first_name,
          last_name: updatedUserData.last_name || prev.last_name,
          phone_number: updatedUserData.phone_number || prev.phone_number,
          specialization: updatedUserData.specialization || prev.specialization,
          academic_degree: updatedUserData.academic_degree || prev.academic_degree,
          years_of_experience: updatedUserData.years_of_experience || prev.years_of_experience,
          country: updatedUserData.country || prev.country,
          state: updatedUserData.state || prev.state,
          profile_image: null,
          cover_image: null
        }));
        
        setPreviewUrls(prev => ({
          profile_image: updatedUserData.profile_image || prev.profile_image,
          cover_image: updatedUserData.cover_image || prev.cover_image
        }));
        
        // Update the user in context
        updateUser(updatedUserData);
        
        // Set success message and exit edit mode
        setMessage({
          type: 'success',
          text: 'Profile updated successfully'
        });
        
        // Important: Only toggle edit mode after state is updated
        setTimeout(() => {
          setIsEditMode(false);
        }, 0);
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      setMessage({
        type: 'error',
        text: typeof error === 'string' ? error : 'Failed to update profile'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleEditMode = () => {
    setIsEditMode(!isEditMode);
    // Clear any messages when toggling modes
    setMessage({ type: '', text: '' });
  };

  // Render the student profile form fields
  const renderStudentFields = () => {
    if (!currentUser || currentUser.role !== 'student') return null;

    return (
      <>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Birthdate</label>
          <input
            type="date"
            name="birthdate"
            value={formData.birthdate}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Grade Level</label>
          <select
            name="grade_level"
            value={formData.grade_level}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">Select Grade Level</option>
            <option value="1">1st Grade</option>
            <option value="2">2nd Grade</option>
            <option value="3">3rd Grade</option>
            <option value="4">4th Grade</option>
            <option value="5">5th Grade</option>
            <option value="6">6th Grade</option>
            <option value="7">7th Grade</option>
            <option value="8">8th Grade</option>
            <option value="9">9th Grade</option>
            <option value="10">10th Grade</option>
            <option value="11">11th Grade</option>
            <option value="12">12th Grade</option>
          </select>
        </div>
      </>
    );
  };

  // Render the teacher profile form fields
  const renderTeacherFields = () => {
    if (!currentUser || currentUser.role !== 'teacher') return null;

    return (
      <>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Specialization</label>
          <input
            type="text"
            name="specialization"
            value={formData.specialization}
            onChange={handleChange}
            placeholder="e.g. Arabic Teacher, Math Teacher"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Academic Degree</label>
          <input
            type="text"
            name="academic_degree"
            value={formData.academic_degree}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Years of Experience</label>
          <input
            type="number"
            name="years_of_experience"
            value={formData.years_of_experience}
            onChange={handleChange}
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Birthdate</label>
          <input
            type="date"
            name="birthdate"
            value={formData.birthdate}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
      </>
    );
  };

  // Render student-specific view fields
  const renderStudentViewFields = () => {
    if (!currentUser || currentUser.role !== 'student') return null;

    return (
      <>
        <div>
          <h3 className="text-sm font-medium text-gray-500">Birthdate</h3>
          <p className="text-gray-900">
            {formData.birthdate ? new Date(formData.birthdate).toLocaleDateString() : 'Not specified'}
          </p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-500">Grade Level</h3>
          <p className="text-gray-900">
            {formData.grade_level ? `${formData.grade_level}${getGradeSuffix(formData.grade_level)} Grade` : 'Not specified'}
          </p>
        </div>
      </>
    );
  };

  // Helper function to get the suffix for grade levels
  const getGradeSuffix = (grade) => {
    if (!grade) return '';
    const num = parseInt(grade, 10);
    if (num === 1) return 'st';
    if (num === 2) return 'nd';
    if (num === 3) return 'rd';
    return 'th';
  };

  // Render teacher-specific view fields
  const renderTeacherViewFields = () => {
    if (!currentUser || currentUser.role !== 'teacher') return null;

    return (
      <>
        <div>
          <h3 className="text-sm font-medium text-gray-500">Specialization</h3>
          <p className="text-gray-900">{formData.specialization || 'Not specified'}</p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-500">Academic Degree</h3>
          <p className="text-gray-900">{formData.academic_degree || 'Not specified'}</p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-500">Years of Experience</h3>
          <p className="text-gray-900">
            {formData.years_of_experience ? `${formData.years_of_experience} years` : 'Not specified'}
          </p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-500">Birthdate</h3>
          <p className="text-gray-900">
            {formData.birthdate ? new Date(formData.birthdate).toLocaleDateString() : 'Not specified'}
          </p>
        </div>
      </>
    );
  };

  // Add a loading indicator while profile is loading
  if (!profileLoaded && isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-100 min-h-screen">
      <div className="container mx-auto py-8 px-4">
        <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{currentUser?.role === 'student' ? 'Student Profile' : currentUser?.role === 'teacher' ? 'Teacher Profile' : 'Advisor Profile'}</h1>
          <div className="flex space-x-2">
            <button
              onClick={() => navigate('/home')}
              className="flex items-center px-3 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
              <span>Home</span>
            </button>
            <button
              onClick={toggleEditMode}
              className="flex items-center px-3 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
            >
              {isEditMode ? (
                <>
                  <span>View Profile</span>
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                  <span>Edit Profile</span>
                </>
              )}
            </button>
          </div>
        </div>
        
        {/* Message display */}
        {message.text && (
          <div className={`mb-4 p-3 rounded ${message.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
            {message.text}
          </div>
        )}
        
        {/* Loading indicator during form submission */}
        {isLoading && (
          <div className="mb-4 p-3 rounded bg-blue-100 text-blue-700 flex items-center">
            <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-blue-700 mr-2"></div>
            <span>Processing your request...</span>
          </div>
        )}
        
        {/* Cover Image */}
        <div className="relative h-48 bg-gray-200 rounded-lg overflow-hidden mb-8">
          {previewUrls.cover_image ? (
            <img 
              src={previewUrls.cover_image} 
              alt="Cover" 
              className="w-full h-full object-cover"
              onError={(e) => {
                console.error('Cover image failed to load', e);
                e.target.src = 'https://via.placeholder.com/800x200?text=Cover+Image';
              }}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <span className="text-gray-500">No cover image</span>
            </div>
          )}
          {isEditMode && (
            <label className="absolute bottom-2 right-2 bg-white rounded-full p-2 shadow cursor-pointer">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <input 
                type="file" 
                name="cover_image" 
                onChange={handleFileChange} 
                className="hidden" 
                accept="image/*"
              />
            </label>
          )}
        </div>
        
        {/* Profile Image */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            <div className="w-32 h-32 bg-gray-300 rounded-full overflow-hidden border-4 border-white shadow-md">
              {previewUrls.profile_image ? (
                <img 
                  src={previewUrls.profile_image} 
                  alt="Profile" 
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    console.error('Profile image failed to load', e);
                    e.target.src = `https://ui-avatars.com/api/?name=${formData.first_name}+${formData.last_name}&background=6366F1&color=fff&size=128`;
                  }}
                />
              ) : (
                <div className="flex items-center justify-center h-full bg-indigo-600 text-white text-2xl font-bold">
                  {formData.first_name?.charAt(0)}{formData.last_name?.charAt(0)}
                </div>
              )}
            </div>
            {isEditMode && (
              <label className="absolute bottom-0 right-0 bg-white rounded-full p-2 shadow cursor-pointer">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
                <input 
                  type="file" 
                  name="profile_image" 
                  onChange={handleFileChange} 
                  className="hidden" 
                  accept="image/*"
                />
              </label>
            )}
          </div>
        </div>
        
        {/* Profile Section */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-6">
            {isEditMode ? (
              /* Edit Mode */
              <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                    <input
                      type="text"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                    <input
                      type="text"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                    <input
                      type="tel"
                      name="phone_number"
                      value={formData.phone_number}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                    <input
                      type="text"
                      name="country"
                      value={formData.country}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">State/Province</label>
                    <input
                      type="text"
                      name="state"
                      value={formData.state}
                      onChange={handleChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  
                  {/* Render role-specific fields */}
                  {renderTeacherFields()}
                  {renderStudentFields()}
                </div>
                
                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={() => setIsEditMode(false)}
                    className="px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 mr-2"
                    disabled={isLoading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="px-4 py-2 bg-indigo-600 text-white font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                  >
                    {isLoading ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            ) : (
              /* View Mode */
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <h2 className="text-xl font-bold text-center mb-4">{formData.first_name} {formData.last_name}</h2>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Email</h3>
                    <p className="text-gray-900">{currentUser?.email}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Phone Number</h3>
                    <p className="text-gray-900">{formData.phone_number || 'Not specified'}</p>
                  </div>
                  
                  {/* Render role-specific view fields */}
                  {renderTeacherViewFields()}
                  {renderStudentViewFields()}
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Country</h3>
                    <p className="text-gray-900">{formData.country || 'Not specified'}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">State/Province</h3>
                    <p className="text-gray-900">{formData.state || 'Not specified'}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile; 