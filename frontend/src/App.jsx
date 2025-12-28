import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { useState, useEffect, Component } from "react";
import { Toaster } from "react-hot-toast";

// Pages
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
import Home from "./pages/Home";
import Profile from "./pages/Profile";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import LessonsPage from "./pages/LessonsPage";
import LessonDetailsPage from "./pages/LessonDetailsPage";
import Dashboard from "./pages/Dashboard";
import StudentsPage from "./pages/StudentsPage";
import AdvisorDashboard from "./pages/AdvisorDashboard";
import AdvisorStudents from "./pages/AdvisorStudents";
import AdvisorLessons from "./pages/AdvisorLessons";
import StudentDashboard from "./pages/StudentDashboard";
import StudentPerformance from "./pages/StudentPerformance";
import HomeworkHelperPage from "./pages/HomeworkHelperPage_FINAL";
import LiveSessionsPage from "./pages/LiveSessionsPage";
import TemplatesPage from "./pages/TemplatesPage";
import MyRecurringSessionsPage from "./pages/MyRecurringSessionsPage";
import StudentGroupsPage from "./pages/StudentGroupsPage";

// Components
import Navbar from "./components/Navbar";

// Error Boundary Component to prevent app crashes
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
          <div className="bg-white p-6 rounded-lg shadow-md max-w-md w-full">
            <h2 className="text-xl font-bold text-red-600 mb-4">
              Something went wrong
            </h2>
            <p className="text-gray-600 mb-4">
              An unexpected error occurred. Please try refreshing the page or
              navigating back to the home page.
            </p>
            <div className="flex justify-between">
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Refresh Page
              </button>
              <button
                onClick={() => {
                  this.setState({ hasError: false });
                  window.location.href = "/";
                }}
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Go Home
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

// Loading component
const LoadingScreen = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-100">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
      <p className="mt-2 text-gray-600">Loading...</p>
    </div>
  </div>
);

// Protected route component
const ProtectedRoute = ({
  children,
  useDashboardLayout = false,
  allowedRoles,
}) => {
  const { currentUser, loading } = useAuth();
  const navigate = useNavigate();
  const [isReady, setIsReady] = useState(false);

  // Add a slight delay to ensure authentication state is fully loaded
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsReady(true);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  // Show loading screen if still loading auth state
  if (loading || !isReady) {
    return <LoadingScreen />;
  }

  // Redirect to login if not authenticated
  if (!currentUser) {
    return <Navigate to="/login" />;
  }

  const userRole = currentUser.role?.toLowerCase();

  // If allowedRoles are specified, check for authorization
  if (allowedRoles && !allowedRoles.includes(userRole)) {
    // If user is not authorized, redirect them to their default dashboard
    let redirectTo = "/home"; // fallback
    if (userRole === "student") redirectTo = "/student/dashboard";
    if (userRole === "teacher") redirectTo = "/dashboard";
    if (userRole === "advisor") redirectTo = "/advisor/dashboard";
    return <Navigate to={redirectTo} replace />;
  }

  // Return children wrapped in error boundary, with or without navbar depending on route type
  return (
    <ErrorBoundary>
      {!useDashboardLayout && <Navbar />}
      {children}
    </ErrorBoundary>
  );
};

// Add a new component for role-based routing
const RoleBasedRedirect = () => {
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (currentUser) {
      const role = currentUser.role?.toLowerCase();

      switch (role) {
        case "student":
          navigate("/student/dashboard");
          break;
        case "advisor":
          navigate("/advisor/dashboard");
          break;
        case "teacher":
          navigate("/dashboard");
          break;
        default:
          navigate("/home");
      }
    } else {
      navigate("/login");
    }
  }, [currentUser, navigate]);

  // Show loading while redirecting
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
        <p className="mt-2 text-gray-600">Redirecting to your dashboard...</p>
      </div>
    </div>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <ErrorBoundary>
          <Toaster position="top-right" />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/verify-email" element={<VerifyEmail />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password/:token" element={<ResetPassword />} />
            <Route
              path="/home"
              element={
                <ProtectedRoute
                  allowedRoles={["student", "teacher", "advisor"]}
                >
                  <Home />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute
                  allowedRoles={["student", "teacher", "advisor"]}
                >
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute
                  useDashboardLayout={true}
                  allowedRoles={["teacher"]}
                >
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/student/dashboard"
              element={
                <ProtectedRoute
                  useDashboardLayout={true}
                  allowedRoles={["student"]}
                >
                  <StudentDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/student/lessons/:lessonId"
              element={
                <ProtectedRoute
                  useDashboardLayout={true}
                  allowedRoles={["student"]}
                >
                  <LessonDetailsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/lessons"
              element={
                <ProtectedRoute
                  useDashboardLayout={true}
                  allowedRoles={["teacher", "advisor"]}
                >
                  <LessonsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/lessons/:lessonId"
              element={
                <ProtectedRoute
                  useDashboardLayout={true}
                  allowedRoles={["teacher", "advisor"]}
                >
                  <LessonDetailsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/students"
              element={
                <ProtectedRoute
                  useDashboardLayout={true}
                  allowedRoles={["teacher"]}
                >
                  <StudentsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/advisor/dashboard"
              element={
                <ProtectedRoute
                  useDashboardLayout={true}
                  allowedRoles={["advisor"]}
                >
                  <AdvisorDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/advisor/students"
              element={
                <ProtectedRoute
                  useDashboardLayout={true}
                  allowedRoles={["advisor"]}
                >
                  <AdvisorStudents />
                </ProtectedRoute>
              }
            />
            <Route
              path="/advisor/students/:studentId/performance"
              element={
                <ProtectedRoute
                  useDashboardLayout={true}
                  allowedRoles={["advisor"]}
                >
                  <StudentPerformance />
                </ProtectedRoute>
              }
            />
            <Route
              path="/advisor/lessons"
              element={
                <ProtectedRoute
                  useDashboardLayout={true}
                  allowedRoles={["advisor"]}
                >
                  <AdvisorLessons />
                </ProtectedRoute>
              }
            />
            <Route
              path="/advisor/analytics"
              element={
                <ProtectedRoute
                  useDashboardLayout={true}
                  allowedRoles={["advisor"]}
                >
                  <AdvisorDashboard tab="analytics" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/homework-helper"
              element={
                <ProtectedRoute allowedRoles={["student"]}>
                  <HomeworkHelperPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/live-sessions"
              element={
                <ProtectedRoute
                  allowedRoles={["student", "teacher", "advisor"]}
                >
                  <LiveSessionsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/templates"
              element={
                <ProtectedRoute allowedRoles={["teacher", "advisor"]}>
                  <TemplatesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/my-recurring-sessions"
              element={
                <ProtectedRoute allowedRoles={["student"]}>
                  <MyRecurringSessionsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/student-groups"
              element={
                <ProtectedRoute allowedRoles={["advisor"]}>
                  <StudentGroupsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <RoleBasedRedirect />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </ErrorBoundary>
      </AuthProvider>
    </Router>
  );
}

export default App;
