import { useState, useEffect } from "react";
import { useFormik } from "formik";
import * as Yup from "yup";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { login } from "../services/authService";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "react-i18next";
import LanguageSwitcher from "./LanguageSwitcher";

const LoginForm = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { updateUser } = useAuth();
  const { t } = useTranslation();

  // Check for verification success message
  useEffect(() => {
    if (location.state?.message) {
      setSuccess(location.state.message);
      // Clear location state after showing the message
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  const validationSchema = Yup.object({
    email: Yup.string()
      .email("Invalid email address")
      .required("Email is required"),
    password: Yup.string().required("Password is required"),
  });

  const formik = useFormik({
    initialValues: {
      email: "",
      password: "",
    },
    validationSchema,
    onSubmit: async (values) => {
      setSubmitting(true);
      setError(null);

      try {
        const result = await login(values.email, values.password);

        // Update auth context with user data
        if (result.user) {
          updateUser(result.user);
        }

        // Show success message
        setSuccess("Login successful! Redirecting to home...");

        // Redirect to home page
        setTimeout(() => {
          navigate("/home");
        }, 1000);
      } catch (error) {
        console.error("Login failed:", error);

        // Check if email is not verified
        if (error.requires_verification && error.email) {
          navigate("/verify-email", {
            state: {
              email: error.email,
              message:
                'Your email is not verified. Please check your email for the verification code or click "Resend" to get a new code.',
            },
          });
        } else {
          setError(
            error.message || "Invalid login credentials. Please try again."
          );
        }
      } finally {
        setSubmitting(false);
      }
    },
  });

  const togglePasswordVisibility = () => setShowPassword(!showPassword);

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden w-full max-w-md">
      <div className="bg-indigo-600 py-4 px-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">{t("login.title")}</h1>
          <p className="text-indigo-100">Login to your account to continue</p>
        </div>
        <LanguageSwitcher variant="login" />
      </div>

      <div className="p-6 space-y-4">
        {error && (
          <div
            className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded"
            role="alert"
          >
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {success && (
          <div
            className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded"
            role="alert"
          >
            <span className="block sm:inline">{success}</span>
          </div>
        )}

        <form onSubmit={formik.handleSubmit}>
          <div className="mb-4">
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              {t("login.email")}
            </label>
            <div className="relative">
              <input
                id="email"
                type="email"
                name="email"
                placeholder="rawad.mohammad@example.com"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition ${
                  formik.touched.email && formik.errors.email
                    ? "border-red-500"
                    : "border-gray-300"
                }`}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                value={formik.values.email}
              />
              <i className="fas fa-envelope absolute right-3 top-3 text-gray-400"></i>
            </div>
            {formik.touched.email && formik.errors.email ? (
              <div className="text-red-500 text-xs mt-1">
                {formik.errors.email}
              </div>
            ) : null}
          </div>

          <div className="mb-6">
            <div className="flex items-center justify-between mb-1">
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700"
              >
                {t("login.password")}
              </label>
              <Link
                to="/forgot-password"
                className="text-sm text-indigo-600 hover:underline"
              >
                {t("login.forgot_password")}
              </Link>
            </div>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                name="password"
                placeholder="••••••••"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition ${
                  formik.touched.password && formik.errors.password
                    ? "border-red-500"
                    : "border-gray-300"
                }`}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                value={formik.values.password}
              />
              <i
                className={`fas ${
                  showPassword ? "fa-eye" : "fa-eye-slash"
                } password-toggle`}
                onClick={togglePasswordVisibility}
              ></i>
            </div>
            {formik.touched.password && formik.errors.password ? (
              <div className="text-red-500 text-xs mt-1">
                {formik.errors.password}
              </div>
            ) : null}
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition flex items-center justify-center"
          >
            <span>{submitting ? "Logging in..." : t("login.submit")}</span>
            {submitting && (
              <svg
                className="w-5 h-5 ml-2 text-white animate-spin"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            )}
          </button>
        </form>

        {/* Admin Access Button */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={() =>
              window.open("http://localhost:8000/advisors/", "_blank")
            }
            className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition flex items-center justify-center"
          >
            <i className="fas fa-users-cog mr-2"></i>
            🎯 Admin: Advisor Management
          </button>
          <p className="text-xs text-gray-500 mt-2 text-center">
            For superusers only - Opens in new tab
          </p>
        </div>
      </div>

      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 text-center">
        <p className="text-sm text-gray-600">
          {t("login.no_account")}{" "}
          <Link
            to="/register"
            className="font-medium text-indigo-600 hover:underline"
          >
            {t("login.register")}
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginForm;
