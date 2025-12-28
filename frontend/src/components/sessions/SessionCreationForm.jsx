import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";

const SessionCreationForm = ({ isOpen, onClose, onSave, session = null }) => {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    subject: "",
    level: "",
    scheduled_datetime: "",
    duration_minutes: 60,
    max_participants: 50,
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);

  // Reset form when modal opens/closes or session changes
  useEffect(() => {
    if (isOpen && session) {
      console.log("Initializing form with session data:", session);
      setFormData({
        title: session.title || "",
        description: session.description || "",
        subject: session.subject || "",
        level: session.level || "",
        scheduled_datetime: session.scheduled_datetime
          ? new Date(
              new Date(session.scheduled_datetime).getTime() -
                new Date().getTimezoneOffset() * 60000
            )
              .toISOString()
              .slice(0, 16)
          : "",
        duration_minutes: session.duration_minutes || 60,
        max_participants: session.max_participants || 50,
      });
      setErrors({});
      setIsEditMode(true);
    } else if (isOpen) {
      setFormData({
        title: "",
        description: "",
        subject: "",
        level: "",
        scheduled_datetime: "",
        duration_minutes: 60,
        max_participants: 50,
      });
      setErrors({});
      setIsEditMode(false);
    }
  }, [isOpen, session]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear errors when user types
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: null,
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = "Session title is required";
    }

    if (!formData.subject.trim()) {
      newErrors.subject = "Subject is required";
    }

    if (!formData.level) {
      newErrors.level = "Grade level is required";
    }

    if (!formData.scheduled_datetime) {
      newErrors.scheduled_datetime = "Session date and time is required";
    } else {
      // Check if the scheduled time is in the future
      const scheduledDate = new Date(formData.scheduled_datetime);
      const now = new Date();
      if (scheduledDate <= now) {
        newErrors.scheduled_datetime =
          "Session must be scheduled in the future";
      }
    }

    if (formData.duration_minutes < 15 || formData.duration_minutes > 240) {
      newErrors.duration_minutes =
        "Duration must be between 15 and 240 minutes";
    }

    if (formData.max_participants < 1 || formData.max_participants > 100) {
      newErrors.max_participants =
        "Maximum participants must be between 1 and 100";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    // Convert the form data to the expected format for the API
    const sessionData = {
      title: formData.title,
      description: formData.description,
      subject: formData.subject,
      level: formData.level,
      scheduled_datetime: new Date(formData.scheduled_datetime).toISOString(),
      duration_minutes: parseInt(formData.duration_minutes),
      max_participants: parseInt(formData.max_participants),
    };

    try {
      await onSave(sessionData);
      onClose();
    } catch (error) {
      console.error("Error saving session:", error);

      // Handle the error - check if it's a validation error from the backend
      if (error.response?.data) {
        const backendErrors = error.response.data;
        const mappedErrors = {};

        if (backendErrors.title) {
          mappedErrors.title = Array.isArray(backendErrors.title)
            ? backendErrors.title.join(", ")
            : backendErrors.title;
        }
        if (backendErrors.subject) {
          mappedErrors.subject = Array.isArray(backendErrors.subject)
            ? backendErrors.subject.join(", ")
            : backendErrors.subject;
        }
        if (backendErrors.level) {
          mappedErrors.level = Array.isArray(backendErrors.level)
            ? backendErrors.level.join(", ")
            : backendErrors.level;
        }
        if (backendErrors.scheduled_datetime) {
          mappedErrors.scheduled_datetime = Array.isArray(
            backendErrors.scheduled_datetime
          )
            ? backendErrors.scheduled_datetime.join(", ")
            : backendErrors.scheduled_datetime;
        }
        if (backendErrors.non_field_errors) {
          mappedErrors.general = Array.isArray(backendErrors.non_field_errors)
            ? backendErrors.non_field_errors.join(", ")
            : backendErrors.non_field_errors;
        }

        setErrors(mappedErrors);
      } else {
        setErrors({ general: "Failed to save session. Please try again." });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Get minimum datetime (current time + 1 hour)
  const getMinDateTime = () => {
    const now = new Date();
    now.setHours(now.getHours() + 1);
    return now.toISOString().slice(0, 16);
  };

  if (!isOpen) return null;

  return ReactDOM.createPortal(
    <div
      className="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center">
        {/* Background overlay */}
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          aria-hidden="true"
          onClick={onClose}
        ></div>

        {/* Modal panel */}
        <div className="relative inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex justify-between items-center pb-3">
              <h3
                className="text-lg leading-6 font-medium text-gray-900"
                id="modal-title"
              >
                <i className="fas fa-video mr-2 text-blue-500"></i>
                {isEditMode ? "Edit Live Session" : "Create Live Session"}
              </h3>
              <button
                type="button"
                className="text-gray-400 hover:text-gray-500"
                onClick={onClose}
              >
                <span className="sr-only">Close</span>
                <i className="fas fa-times"></i>
              </button>
            </div>

            {/* General error message */}
            {errors.general && (
              <div className="mb-4 bg-red-50 p-3 rounded text-red-600 text-sm">
                <i className="fas fa-exclamation-circle mr-2"></i>
                {errors.general}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                {/* Session Title */}
                <div>
                  <label
                    htmlFor="title"
                    className="block text-sm font-medium text-gray-700"
                  >
                    <i className="fas fa-heading mr-1"></i>
                    Session Title *
                  </label>
                  <input
                    type="text"
                    name="title"
                    id="title"
                    className={`mt-1 block w-full border ${
                      errors.title ? "border-red-500" : "border-gray-300"
                    } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500`}
                    value={formData.title}
                    onChange={handleChange}
                    required
                    placeholder="Enter session title"
                  />
                  {errors.title && (
                    <p className="mt-1 text-sm text-red-600">
                      <i className="fas fa-exclamation-triangle mr-1"></i>
                      {errors.title}
                    </p>
                  )}
                </div>

                {/* Description */}
                <div>
                  <label
                    htmlFor="description"
                    className="block text-sm font-medium text-gray-700"
                  >
                    <i className="fas fa-align-left mr-1"></i>
                    Description
                  </label>
                  <textarea
                    name="description"
                    id="description"
                    rows={3}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="Enter session description (optional)"
                  />
                </div>

                {/* Subject and Grade Level */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label
                      htmlFor="subject"
                      className="block text-sm font-medium text-gray-700"
                    >
                      <i className="fas fa-book mr-1"></i>
                      Subject *
                    </label>
                    <input
                      type="text"
                      name="subject"
                      id="subject"
                      className={`mt-1 block w-full border ${
                        errors.subject ? "border-red-500" : "border-gray-300"
                      } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500`}
                      value={formData.subject}
                      onChange={handleChange}
                      required
                      placeholder="e.g., Mathematics"
                    />
                    {errors.subject && (
                      <p className="mt-1 text-sm text-red-600">
                        <i className="fas fa-exclamation-triangle mr-1"></i>
                        {errors.subject}
                      </p>
                    )}
                  </div>

                  <div>
                    <label
                      htmlFor="level"
                      className="block text-sm font-medium text-gray-700"
                    >
                      <i className="fas fa-graduation-cap mr-1"></i>
                      Grade Level *
                    </label>
                    <select
                      name="level"
                      id="level"
                      className={`mt-1 block w-full border ${
                        errors.level ? "border-red-500" : "border-gray-300"
                      } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500`}
                      value={formData.level}
                      onChange={handleChange}
                      required
                    >
                      <option value="">Select grade</option>
                      {[...Array(12)].map((_, i) => (
                        <option key={i + 1} value={i + 1}>
                          Grade {i + 1}
                        </option>
                      ))}
                    </select>
                    {errors.level && (
                      <p className="mt-1 text-sm text-red-600">
                        <i className="fas fa-exclamation-triangle mr-1"></i>
                        {errors.level}
                      </p>
                    )}
                  </div>
                </div>

                {/* Date & Time and Duration */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label
                      htmlFor="scheduled_datetime"
                      className="block text-sm font-medium text-gray-700"
                    >
                      <i className="fas fa-calendar-alt mr-1"></i>
                      Date & Time *
                    </label>
                    <input
                      type="datetime-local"
                      name="scheduled_datetime"
                      id="scheduled_datetime"
                      className={`mt-1 block w-full border ${
                        errors.scheduled_datetime
                          ? "border-red-500"
                          : "border-gray-300"
                      } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500`}
                      value={formData.scheduled_datetime}
                      onChange={handleChange}
                      min={getMinDateTime()}
                      required
                    />
                    {errors.scheduled_datetime && (
                      <p className="mt-1 text-sm text-red-600">
                        <i className="fas fa-exclamation-triangle mr-1"></i>
                        {errors.scheduled_datetime}
                      </p>
                    )}
                  </div>

                  <div>
                    <label
                      htmlFor="duration_minutes"
                      className="block text-sm font-medium text-gray-700"
                    >
                      <i className="fas fa-clock mr-1"></i>
                      Duration (minutes)
                    </label>
                    <select
                      name="duration_minutes"
                      id="duration_minutes"
                      className={`mt-1 block w-full border ${
                        errors.duration_minutes
                          ? "border-red-500"
                          : "border-gray-300"
                      } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500`}
                      value={formData.duration_minutes}
                      onChange={handleChange}
                    >
                      <option value={30}>30 minutes</option>
                      <option value={45}>45 minutes</option>
                      <option value={60}>1 hour</option>
                      <option value={90}>1.5 hours</option>
                      <option value={120}>2 hours</option>
                    </select>
                    {errors.duration_minutes && (
                      <p className="mt-1 text-sm text-red-600">
                        <i className="fas fa-exclamation-triangle mr-1"></i>
                        {errors.duration_minutes}
                      </p>
                    )}
                  </div>
                </div>

                {/* Max Participants */}
                <div>
                  <label
                    htmlFor="max_participants"
                    className="block text-sm font-medium text-gray-700"
                  >
                    <i className="fas fa-users mr-1"></i>
                    Maximum Participants
                  </label>
                  <input
                    type="number"
                    name="max_participants"
                    id="max_participants"
                    min="1"
                    max="100"
                    className={`mt-1 block w-full border ${
                      errors.max_participants
                        ? "border-red-500"
                        : "border-gray-300"
                    } rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500`}
                    value={formData.max_participants}
                    onChange={handleChange}
                  />
                  {errors.max_participants && (
                    <p className="mt-1 text-sm text-red-600">
                      <i className="fas fa-exclamation-triangle mr-1"></i>
                      {errors.max_participants}
                    </p>
                  )}
                </div>

                {/* Info Box */}
                <div className="bg-blue-50 p-3 rounded-md">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <i className="fas fa-info-circle text-blue-400"></i>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-blue-700">
                        After creating the session, it will be in "Pending"
                        status until an advisor assigns it to students.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-5 sm:mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                  onClick={onClose}
                >
                  <i className="fas fa-times mr-1"></i>
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 flex items-center disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <svg
                        className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
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
                      {isEditMode ? "Updating..." : "Creating..."}
                    </>
                  ) : (
                    <>
                      <i
                        className={`fas ${
                          isEditMode ? "fa-save" : "fa-plus"
                        } mr-1`}
                      ></i>
                      {isEditMode ? "Update Session" : "Create Session"}
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};

SessionCreationForm.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired,
  session: PropTypes.object,
};

export default SessionCreationForm;
