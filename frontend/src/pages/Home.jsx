import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, Link } from 'react-router-dom';

// --- مكونات صغيرة ومساعدة ---

// لعرض صف من معلومات الملف الشخصي مع أيقونة
const ProfileInfoRow = ({ icon, label, value, valueClassName = "text-gray-900" }) => (
  <div className="flex items-center">
    <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-indigo-100 rounded-full">
      <i className={`fas ${icon} text-indigo-600`}></i>
    </div>
    <div className="ml-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className={`text-sm font-semibold ${valueClassName}`}>{value}</p>
    </div>
  </div>
);

// لعرض عنصر في قائمة خطوات البدء
const ChecklistItem = ({ text, isCompleted }) => (
  <li className="flex items-center">
    <i className={`fas ${isCompleted ? 'fa-check-circle text-green-500' : 'fa-dot-circle text-gray-400'} mr-3 text-lg`}></i>
    <span className={`${isCompleted ? 'text-gray-700' : 'text-gray-500'}`}>{text}</span>
  </li>
);

// بطاقة لعرض الميزات أو الإجراءات التالية
const FeatureCard = ({ to, icon, title, description }) => (
  <Link 
    to={to} 
    className="bg-white p-6 rounded-xl shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300 flex items-start space-x-4"
  >
    <div className="flex-shrink-0 w-12 h-12 flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg shadow-md">
        <i className={`fas ${icon} text-white text-xl`}></i>
    </div>
    <div>
        <h4 className="font-bold text-gray-800">{title}</h4>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
    </div>
  </Link>
);


// --- المكون الرئيسي للصفحة الرئيسية ---

const Home = () => {
  const { currentUser } = useAuth();

  if (!currentUser) {
    return <Navigate to="/login" />;
  }

  // استخراج البيانات مع قيم افتراضية آمنة
  const { 
    first_name: firstName = 'User', 
    last_name: lastName = '', 
    email = 'No email provided', 
    role = 'user', 
    is_email_verified: isVerified = false 
  } = currentUser;
  
  const userInitial = firstName.charAt(0).toUpperCase();

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        
        {/* --- قسم الترحيب الرئيسي --- */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl shadow-lg p-8 mb-8 flex items-center justify-between">
            <div>
                <h1 className="text-3xl font-bold">Welcome back, {firstName}!</h1>
                <p className="opacity-80 mt-1">Ready to continue your learning journey?</p>
            </div>
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center text-indigo-600 text-2xl font-bold shadow-inner">
                {userInitial}
            </div>
        </div>

        {/* --- شبكة المحتوى --- */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* --- العمود الأيسر: الملف الشخصي والخطوات --- */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* بطاقة الملف الشخصي */}
            <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-6">Your Profile</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <ProfileInfoRow icon="fa-user" label="Full Name" value={`${firstName} ${lastName}`} />
                    <ProfileInfoRow icon="fa-envelope" label="Email" value={email} />
                    <ProfileInfoRow icon="fa-user-tag" label="Role" value={role.charAt(0).toUpperCase() + role.slice(1)} />
                    <ProfileInfoRow 
                        icon={isVerified ? "fa-check-circle" : "fa-exclamation-circle"} 
                        label="Account Status" 
                        value={isVerified ? "Verified" : "Not Verified"}
                        valueClassName={isVerified ? "text-green-600" : "text-yellow-600"}
                    />
                </div>
            </div>

            {/* بطاقة خطوات البدء */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Getting Started</h3>
              <ul className="space-y-3">
                <ChecklistItem text="Create your account" isCompleted={true} />
                <ChecklistItem text="Verify your email address" isCompleted={isVerified} />
                <ChecklistItem text="Explore available courses" isCompleted={false} />
                <ChecklistItem text={role === 'student' ? 'Enroll in your first course' : 'Create your first course'} isCompleted={false} />
              </ul>
            </div>

          </div>

          {/* --- العمود الأيمن: ماذا بعد؟ --- */}
          <div className="lg:col-span-1 space-y-6">
              <h3 className="text-xl font-bold text-gray-800 px-1">What's Next?</h3>
              <FeatureCard 
                to="/courses"
                icon="fa-book-open"
                title="Browse Courses"
                description="Find and manage your courses"
              />
              <FeatureCard 
                to="/community"
                icon="fa-users"
                title="Community"
                description="Connect with peers and instructors"
              />
              <FeatureCard 
                to="/progress"
                icon="fa-chart-pie"
                title="Track Progress"
                description="Monitor your learning journey"
              />
          </div>

        </div>

      </main>
    </div>
  );
};

export default Home;