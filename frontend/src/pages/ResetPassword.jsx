import { useState, useEffect } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { validateResetToken, resetPassword } from '../services/authService';

const ResetPassword = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [tokenValidated, setTokenValidated] = useState(false);
  const [tokenError, setTokenError] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  useEffect(() => {
    async function checkToken() {
      try {
        const response = await validateResetToken(token);
        setTokenValidated(true);
        setUserEmail(response.email);
      } catch (err) {
        setTokenError(true);
        setError(err.message || 'Invalid or expired reset link');
      }
    }
    
    if (token) {
      checkToken();
    } else {
      setTokenError(true);
      setError('Reset token is missing');
    }
  }, [token]);

  const validationSchema = Yup.object({
    password: Yup.string()
      .min(8, 'Password must be at least 8 characters')
      .matches(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .matches(/[0-9]/, 'Password must contain at least one number')
      .required('New password is required'),
    password_confirm: Yup.string()
      .oneOf([Yup.ref('password'), null], 'Passwords must match')
      .required('Confirm password is required')
  });

  const formik = useFormik({
    initialValues: {
      password: '',
      password_confirm: ''
    },
    validationSchema,
    onSubmit: async (values) => {
      setIsSubmitting(true);
      setError(null);
      
      try {
        await resetPassword(token, values.password, values.password_confirm);
        setSuccess(true);
      } catch (err) {
        setError(err.message || 'Failed to reset password. Please try again.');
      } finally {
        setIsSubmitting(false);
      }
    }
  });

  const togglePasswordVisibility = () => setShowPassword(!showPassword);
  const toggleConfirmPasswordVisibility = () => setShowConfirmPassword(!showConfirmPassword);

  if (tokenError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="bg-white py-8 px-6 shadow rounded-lg sm:px-10">
            <div className="mb-6 text-center">
              <h2 className="text-3xl font-extrabold text-gray-900">Password Reset Failed</h2>
            </div>
            
            <div className="rounded-md bg-red-50 p-4 mb-6">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="text-center">
              <Link
                to="/forgot-password"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Request New Reset Link
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="bg-white py-8 px-6 shadow rounded-lg sm:px-10">
          <div className="mb-6 text-center">
            <h2 className="text-3xl font-extrabold text-gray-900">Reset Password</h2>
            {tokenValidated && !success && (
              <p className="mt-2 text-sm text-gray-600">
                Create a new password for <span className="font-medium">{userEmail}</span>
              </p>
            )}
          </div>
          
          {success ? (
            <div className="rounded-md bg-green-50 p-4 mb-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">Password Reset Successfully</h3>
                  <div className="mt-2 text-sm text-green-700">
                    <p>Your password has been reset successfully. You can now login with your new password.</p>
                  </div>
                  <div className="mt-4">
                    <Link
                      to="/login"
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Login
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <>
              {!tokenValidated ? (
                <div className="flex justify-center">
                  <svg className="animate-spin h-10 w-10 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
              ) : (
                <form className="space-y-6" onSubmit={formik.handleSubmit}>
                  {error && (
                    <div className="rounded-md bg-red-50 p-4">
                      <div className="flex">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-red-800">Error</h3>
                          <div className="mt-2 text-sm text-red-700">
                            <p>{error}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div>
                    <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                      New Password
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <input
                        id="password"
                        name="password"
                        type={showPassword ? "text" : "password"}
                        autoComplete="new-password"
                        className={`appearance-none block w-full px-3 py-2 border ${
                          formik.touched.password && formik.errors.password ? 'border-red-300' : 'border-gray-300'
                        } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        value={formik.values.password}
                      />
                      <button
                        type="button"
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        onClick={togglePasswordVisibility}
                      >
                        <svg 
                          className="h-5 w-5 text-gray-400" 
                          fill="none" 
                          xmlns="http://www.w3.org/2000/svg" 
                          viewBox="0 0 24 24" 
                          stroke="currentColor"
                        >
                          {showPassword ? (
                            <path 
                              strokeLinecap="round" 
                              strokeLinejoin="round" 
                              strokeWidth={2} 
                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                            />
                          ) : (
                            <path 
                              strokeLinecap="round" 
                              strokeLinejoin="round" 
                              strokeWidth={2} 
                              d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                            />
                          )}
                        </svg>
                      </button>
                    </div>
                    {formik.touched.password && formik.errors.password && (
                      <p className="mt-2 text-sm text-red-600">{formik.errors.password}</p>
                    )}

                    <div className="mt-2 text-xs text-gray-500">
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
                    <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700">
                      Confirm New Password
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <input
                        id="password_confirm"
                        name="password_confirm"
                        type={showConfirmPassword ? "text" : "password"}
                        autoComplete="new-password"
                        className={`appearance-none block w-full px-3 py-2 border ${
                          formik.touched.password_confirm && formik.errors.password_confirm ? 'border-red-300' : 'border-gray-300'
                        } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        value={formik.values.password_confirm}
                      />
                      <button
                        type="button"
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        onClick={toggleConfirmPasswordVisibility}
                      >
                        <svg 
                          className="h-5 w-5 text-gray-400" 
                          fill="none" 
                          xmlns="http://www.w3.org/2000/svg" 
                          viewBox="0 0 24 24" 
                          stroke="currentColor"
                        >
                          {showConfirmPassword ? (
                            <path 
                              strokeLinecap="round" 
                              strokeLinejoin="round" 
                              strokeWidth={2} 
                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                            />
                          ) : (
                            <path 
                              strokeLinecap="round" 
                              strokeLinejoin="round" 
                              strokeWidth={2} 
                              d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                            />
                          )}
                        </svg>
                      </button>
                    </div>
                    {formik.touched.password_confirm && formik.errors.password_confirm && (
                      <p className="mt-2 text-sm text-red-600">{formik.errors.password_confirm}</p>
                    )}
                  </div>

                  <div>
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-70"
                    >
                      {isSubmitting ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Resetting...
                        </>
                      ) : (
                        'Reset Password'
                      )}
                    </button>
                  </div>
                </form>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResetPassword; 