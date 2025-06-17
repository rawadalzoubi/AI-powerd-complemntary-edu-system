import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { verifyEmail } from '../services/authService';
import { resendVerificationEmail } from '../services/userService';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';

const EmailVerification = () => {
  const [submitting, setSubmitting] = useState(false);
  const [resending, setResending] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();
  const { updateUser } = useAuth();
  
  // Get email from location state or use empty string
  const email = location.state?.email || '';
  const message = location.state?.message || 'Please enter the verification code sent to your email.';

  const handleResendCode = async () => {
    if (!email) {
      setError('Email is missing. Please go back to login.');
      toast.error('Email is missing. Please go back to login.');
      return;
    }

    setResending(true);
    setError(null);
    
    try {
      const result = await resendVerificationEmail(email);
      setSuccess(result.message || 'Verification code has been resent to your email.');
      toast.success(result.message || 'Verification code has been resent to your email.');
    } catch (error) {
      console.error('Failed to resend code:', error);
      const errorMsg = error.message || 'Failed to resend verification code. Please try again.';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setResending(false);
    }
  };

  const validationSchema = Yup.object({
    verificationCode: Yup.string()
      .required('Verification code is required')
      .matches(/^\d{6}$/, 'Verification code must be 6 digits')
  });

  const formik = useFormik({
    initialValues: {
      verificationCode: ''
    },
    validationSchema,
    onSubmit: async (values) => {
      if (!email) {
        setError('Email is missing. Please try again or contact support.');
        return;
      }
      
      setSubmitting(true);
      setError(null);
      
      try {
        const result = await verifyEmail(email, values.verificationCode);
        setSuccess('Email verification successful! Redirecting to login...');
        
        // Update auth context with user data
        if (result.user) {
          updateUser(result.user);
        }
        
        // Redirect to login page after successful verification
        setTimeout(() => {
          navigate('/login', {
            state: {
              message: 'Your email has been verified! You can now log in.'
            }
          });
        }, 1500);
      } catch (error) {
        console.error('Verification failed:', error);
        setError(error.message || 'Invalid verification code. Please try again.');
      } finally {
        setSubmitting(false);
      }
    }
  });

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden w-full max-w-md">
      <div className="bg-indigo-600 py-4 px-6">
        <h1 className="text-2xl font-bold text-white">Verify Your Email</h1>
        <p className="text-indigo-100">{message}</p>
      </div>
      
      <div className="p-6 space-y-4">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}
        
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded" role="alert">
            <span className="block sm:inline">{success}</span>
          </div>
        )}
        
        <form onSubmit={formik.handleSubmit}>
          <div className="mb-6">
            <label htmlFor="verificationCode" className="block text-sm font-medium text-gray-700 mb-1">
              Verification Code
            </label>
            <div className="relative">
              <input
                id="verificationCode"
                name="verificationCode"
                type="text"
                placeholder="Enter 6-digit code"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition ${
                  formik.touched.verificationCode && formik.errors.verificationCode 
                    ? 'border-red-500' 
                    : 'border-gray-300'
                }`}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                value={formik.values.verificationCode}
                maxLength={6}
              />
              <i className="fas fa-key absolute right-3 top-3 text-gray-400"></i>
            </div>
            {formik.touched.verificationCode && formik.errors.verificationCode ? (
              <div className="text-red-500 text-xs mt-1">{formik.errors.verificationCode}</div>
            ) : null}
          </div>
          
          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition flex items-center justify-center"
          >
            <span>{submitting ? 'Verifying...' : 'Verify Email'}</span>
            {submitting && (
              <svg className="w-5 h-5 ml-2 text-white animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
          </button>
        </form>
        
        <div className="text-center mt-4">
          <p className="text-sm text-gray-600">
            Didn't receive a code?{' '}
            <button
              type="button"
              className="text-indigo-600 hover:underline font-medium"
              onClick={handleResendCode}
              disabled={resending}
            >
              {resending ? 'Sending...' : 'Resend'}
            </button>
          </p>
        </div>
      </div>
      
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 text-center">
        <p className="text-sm text-gray-600">
          Remember your account?{' '}
          <a href="/login" className="font-medium text-indigo-600 hover:underline">
            Sign in
          </a>
        </p>
      </div>
    </div>
  );
};

export default EmailVerification; 