import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';

const Home = () => {
  const { currentUser } = useAuth();

  if (!currentUser) {
    return <Navigate to="/login" />;
  }

  // Safely access user properties
  const firstName = currentUser.first_name || 'User';
  const lastName = currentUser.last_name || '';
  const email = currentUser.email || 'No email provided';
  const role = currentUser.role || 'user';
  const isVerified = currentUser.is_email_verified || false;

  return (
    <div className="min-h-screen bg-gray-100">
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-6">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-4">Welcome, {firstName}!</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="bg-indigo-50 p-6 rounded-lg">
                  <h3 className="text-lg font-medium text-indigo-800 mb-3">Your Profile</h3>
                  <div className="space-y-2">
                    <p className="flex items-center text-gray-700">
                      <i className="fas fa-user mr-3 text-indigo-500 w-5"></i>
                      <span className="font-medium mr-2">Name:</span> 
                      {firstName} {lastName}
                    </p>
                    <p className="flex items-center text-gray-700">
                      <i className="fas fa-envelope mr-3 text-indigo-500 w-5"></i>
                      <span className="font-medium mr-2">Email:</span> 
                      {email}
                    </p>
                    <p className="flex items-center text-gray-700">
                      <i className="fas fa-user-tag mr-3 text-indigo-500 w-5"></i>
                      <span className="font-medium mr-2">Role:</span> 
                      {role.charAt(0).toUpperCase() + role.slice(1)}
                    </p>
                    <p className="flex items-center text-gray-700">
                      <i className="fas fa-check-circle mr-3 text-indigo-500 w-5"></i>
                      <span className="font-medium mr-2">Status:</span> 
                      {isVerified ? 
                        <span className="text-green-600">Verified</span> : 
                        <span className="text-red-600">Not Verified</span>
                      }
                    </p>
                  </div>
                </div>
                
                <div className="bg-yellow-50 p-6 rounded-lg">
                  <h3 className="text-lg font-medium text-yellow-800 mb-3">Getting Started</h3>
                  <ul className="space-y-3">
                    <li className="flex items-start">
                      <i className="fas fa-check-circle text-green-500 mt-1 mr-3"></i>
                      <span>Create your account <span className="text-green-600 font-medium">(Completed)</span></span>
                    </li>
                    <li className="flex items-start">
                      <i className="fas fa-check-circle text-green-500 mt-1 mr-3"></i>
                      <span>Verify your email <span className="text-green-600 font-medium">(Completed)</span></span>
                    </li>
                    <li className="flex items-start">
                      <i className="fas fa-arrow-circle-right text-indigo-500 mt-1 mr-3"></i>
                      <span>Explore available courses</span>
                    </li>
                    <li className="flex items-start">
                      <i className="fas fa-arrow-circle-right text-indigo-500 mt-1 mr-3"></i>
                      <span>{role === 'student' ? 'Enroll in courses' : 'Create your first course'}</span>
                    </li>
                  </ul>
                </div>
              </div>
              
              <div className="bg-indigo-100 p-6 rounded-lg">
                <h3 className="text-lg font-medium text-indigo-800 mb-3">What's Next?</h3>
                <p className="text-gray-700 mb-4">
                  This is a placeholder home page. In a complete application, you would see:
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-white p-4 rounded shadow">
                    <i className="fas fa-book text-2xl text-indigo-600 mb-2"></i>
                    <h4 className="font-medium mb-1">Courses</h4>
                    <p className="text-sm text-gray-600">Browse and manage your courses</p>
                  </div>
                  <div className="bg-white p-4 rounded shadow">
                    <i className="fas fa-users text-2xl text-indigo-600 mb-2"></i>
                    <h4 className="font-medium mb-1">Community</h4>
                    <p className="text-sm text-gray-600">Connect with other students and teachers</p>
                  </div>
                  <div className="bg-white p-4 rounded shadow">
                    <i className="fas fa-chart-line text-2xl text-indigo-600 mb-2"></i>
                    <h4 className="font-medium mb-1">Progress</h4>
                    <p className="text-sm text-gray-600">Track your learning journey</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home; 