import { useState } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../services/authService';

const RegistrationForm = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState(null);
  const [emailError, setEmailError] = useState(null);
  const navigate = useNavigate();

  const validationSchema = Yup.object({
    first_name: Yup.string().required('First name is required'),
    last_name: Yup.string().required('Last name is required'),
    email: Yup.string().email('Invalid email address').required('Email is required'),
    password: Yup.string()
      .min(8, 'At least 8 characters')
      .matches(/[A-Z]/, 'At least 1 uppercase letter')
      .matches(/[0-9]/, 'At least 1 number')
      .required('Password is required'),
    password_confirm: Yup.string()
      .oneOf([Yup.ref('password')], 'Passwords must match')
      .required('Password confirmation is required'),
    role: Yup.string().oneOf(['student', 'teacher']).required('Role selection is required'),
    terms: Yup.boolean().oneOf([true], 'You must accept the terms and privacy policy')
  });

  const formik = useFormik({
    initialValues: {
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      password_confirm: '',
      role: '',
      terms: false
    },
    validationSchema,
    onSubmit: async (values) => {
      setSubmitting(true);
      setServerError(null);
      setEmailError(null);
      
      console.log('Submitting registration form with values:', values);
      
      try {
        const result = await register(values);
        console.log('Registration result:', result);
        
        // Show success message and redirect to verification page
        navigate('/verify-email', { 
          state: { 
            email: values.email,
            message: result.message || 'Registration successful. Please check your email for verification code.'
          }
        });
      } catch (error) {
        console.error('Registration failed:', error);
        
        // Check if it's an email already exists error
        if (error.message && error.message.includes('email is already used')) {
          console.log('Email already in use error detected');
          setEmailError(error.message);
        } else if (error.errors && error.errors.email) {
          // New error format
          console.log('Email error detected in new format');
          setEmailError(error.errors.email[0]);
        } else {
          console.log('Setting server error:', error.message);
          setServerError(error.message || 'Registration failed. Please try again.');
        }
      } finally {
        setSubmitting(false);
      }
    }
  });

  const togglePasswordVisibility = () => setShowPassword(!showPassword);
  const toggleConfirmPasswordVisibility = () => setShowConfirmPassword(!showConfirmPassword);

  const selectRole = (role) => {
    formik.setFieldValue('role', role);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden w-full max-w-md">
      <div className="bg-indigo-600 py-4 px-6">
        <h1 className="text-2xl font-bold text-white">Create Your Account</h1>
        <p className="text-indigo-100">Join our community today</p>
      </div>

      {serverError && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded m-6" role="alert">
          <span className="block sm:inline">{serverError}</span>
        </div>
      )}
      
      <form onSubmit={formik.handleSubmit} className="p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
              First Name
            </label>
            <div className="relative">
              <input
                id="first_name"
                type="text"
                name="first_name"
                placeholder="Rawad"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition ${
                  formik.touched.first_name && formik.errors.first_name ? 'border-red-500' : 'border-gray-300'
                }`}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                value={formik.values.first_name}
              />
              <i className="fas fa-user absolute right-3 top-3 text-gray-400"></i>
            </div>
            {formik.touched.first_name && formik.errors.first_name ? (
              <div className="text-red-500 text-xs mt-1">{formik.errors.first_name}</div>
            ) : null}
          </div>
          
          <div>
            <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
              Last Name
            </label>
            <div className="relative">
              <input
                id="last_name"
                type="text"
                name="last_name"
                placeholder="Alzoubi"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition ${
                  formik.touched.last_name && formik.errors.last_name ? 'border-red-500' : 'border-gray-300'
                }`}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                value={formik.values.last_name}
              />
              <i className="fas fa-user absolute right-3 top-3 text-gray-400"></i>
            </div>
            {formik.touched.last_name && formik.errors.last_name ? (
              <div className="text-red-500 text-xs mt-1">{formik.errors.last_name}</div>
            ) : null}
          </div>
        </div>
        
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email Address
          </label>
          <div className="relative">
            <input
              id="email"
              type="email"
              name="email"
              placeholder="rawad.mohammed@example.com"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition ${
                (formik.touched.email && formik.errors.email) || emailError ? 'border-red-500' : 'border-gray-300'
              }`}
              onChange={(e) => {
                // Clear email error when user types
                if (emailError) setEmailError(null);
                formik.handleChange(e);
              }}
              onBlur={formik.handleBlur}
              value={formik.values.email}
            />
            <i className="fas fa-envelope absolute right-3 top-3 text-gray-400"></i>
          </div>
          {formik.touched.email && formik.errors.email ? (
            <div className="text-red-500 text-xs mt-1">{formik.errors.email}</div>
          ) : emailError ? (
            <div className="text-red-500 text-xs mt-1">{emailError}</div>
          ) : null}
        </div>
        
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="••••••••"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition ${
                formik.touched.password && formik.errors.password ? 'border-red-500' : 'border-gray-300'
              }`}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              value={formik.values.password}
            />
            <i 
              className={`fas ${showPassword ? 'fa-eye' : 'fa-eye-slash'} password-toggle`} 
              onClick={togglePasswordVisibility}
            ></i>
          </div>
          {formik.touched.password && formik.errors.password ? (
            <div className="text-red-500 text-xs mt-1">{formik.errors.password}</div>
          ) : null}
          
          <div className="mt-1 text-xs text-gray-500">
            <p className="flex items-center">
              <span className={`w-4 h-4 mr-1 inline-flex items-center justify-center rounded-full
                ${formik.values.password.length >= 8 ? 'bg-green-500 text-white' : 'bg-gray-200'}`}>
                {formik.values.password.length >= 8 ? '✓' : '!'}
              </span>
              At least 8 characters
            </p>
            <p className="flex items-center">
              <span className={`w-4 h-4 mr-1 inline-flex items-center justify-center rounded-full
                ${/[A-Z]/.test(formik.values.password) ? 'bg-green-500 text-white' : 'bg-gray-200'}`}>
                {/[A-Z]/.test(formik.values.password) ? '✓' : '!'}
              </span>
              At least 1 uppercase letter
            </p>
            <p className="flex items-center">
              <span className={`w-4 h-4 mr-1 inline-flex items-center justify-center rounded-full
                ${/[0-9]/.test(formik.values.password) ? 'bg-green-500 text-white' : 'bg-gray-200'}`}>
                {/[0-9]/.test(formik.values.password) ? '✓' : '!'}
              </span>
              At least 1 number
            </p>
          </div>
        </div>
        
        <div>
          <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700 mb-1">
            Confirm Password
          </label>
          <div className="relative">
            <input
              id="password_confirm"
              type={showConfirmPassword ? "text" : "password"}
              name="password_confirm"
              placeholder="••••••••"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition ${
                formik.touched.password_confirm && formik.errors.password_confirm ? 'border-red-500' : 'border-gray-300'
              }`}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              value={formik.values.password_confirm}
            />
            <i 
              className={`fas ${showConfirmPassword ? 'fa-eye' : 'fa-eye-slash'} password-toggle`} 
              onClick={toggleConfirmPasswordVisibility}
            ></i>
          </div>
          {formik.touched.password_confirm && formik.errors.password_confirm ? (
            <div className="text-red-500 text-xs mt-1">{formik.errors.password_confirm}</div>
          ) : null}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Your Role
          </label>
          <div className="space-y-2">
            <label 
              className={`role-option ${formik.values.role === 'teacher' ? 'selected' : ''}`}
              onClick={() => selectRole('teacher')}
            >
              <input
                type="checkbox"
                name="role"
                value="teacher"
                className="role-checkbox sr-only"
                checked={formik.values.role === 'teacher'}
                onChange={() => {}}
              />
              <div className={`w-5 h-5 rounded-full border flex items-center justify-center mr-3
                ${formik.values.role === 'teacher' ? 'border-indigo-500' : 'border-gray-300'}`}>
                {formik.values.role === 'teacher' && (
                  <div className="w-3 h-3 rounded-full bg-indigo-500"></div>
                )}
              </div>
              <i className={`fas fa-chalkboard-teacher role-icon ${formik.values.role === 'teacher' ? 'text-indigo-600' : ''}`}></i>
              <div>
                <div className="font-medium">Teacher</div>
                <div className="text-xs text-gray-500">Educator or instructor</div>
              </div>
            </label>
            
            <label 
              className={`role-option ${formik.values.role === 'student' ? 'selected' : ''}`}
              onClick={() => selectRole('student')}
            >
              <input
                type="checkbox"
                name="role"
                value="student"
                className="role-checkbox sr-only"
                checked={formik.values.role === 'student'}
                onChange={() => {}}
              />
              <div className={`w-5 h-5 rounded-full border flex items-center justify-center mr-3
                ${formik.values.role === 'student' ? 'border-indigo-500' : 'border-gray-300'}`}>
                {formik.values.role === 'student' && (
                  <div className="w-3 h-3 rounded-full bg-indigo-500"></div>
                )}
              </div>
              <i className={`fas fa-user-graduate role-icon ${formik.values.role === 'student' ? 'text-indigo-600' : ''}`}></i>
              <div>
                <div className="font-medium">Student</div>
                <div className="text-xs text-gray-500">Learner or participant</div>
              </div>
            </label>
          </div>
          {formik.touched.role && formik.errors.role ? (
            <div className="text-red-500 text-xs mt-1">{formik.errors.role}</div>
          ) : null}
        </div>
        
        <div className="flex items-start mt-2">
          <input
            id="terms"
            name="terms"
            type="checkbox"
            className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 mt-1"
            onChange={formik.handleChange}
            checked={formik.values.terms}
          />
          <div className="ml-2 text-sm">
            <label htmlFor="terms" className="font-medium text-gray-700">
              I agree to the{' '}
              <Link to="/terms" className="text-indigo-600 hover:underline">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link to="/privacy" className="text-indigo-600 hover:underline">
                Privacy Policy
              </Link>
            </label>
            {formik.touched.terms && formik.errors.terms ? (
              <div className="text-red-500 text-xs mt-1">{formik.errors.terms}</div>
            ) : null}
          </div>
        </div>
        
        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition flex items-center justify-center"
        >
          <span>{submitting ? 'Processing...' : 'Register'}</span>
          {submitting && (
            <svg className="w-5 h-5 ml-2 text-white animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
        </button>
      </form>
      
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 text-center">
        <p className="text-sm text-gray-600">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-indigo-600 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegistrationForm; 