import React from "react";
import PropTypes from "prop-types";

const SessionDetailsModal = ({ isOpen, onClose, session, userRole }) => {
  if (!isOpen || !session) return null;

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return {
      date: date.toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      }),
      time: date.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      PENDING: {
        color: "bg-yellow-100 text-yellow-800",
        icon: "fa-clock",
        text: "Pending Assignment",
      },
      ASSIGNED: {
        color: "bg-blue-100 text-blue-800",
        icon: "fa-user-check",
        text: "Assigned to Students",
      },
      ACTIVE: {
        color: "bg-green-100 text-green-800",
        icon: "fa-play-circle",
        text: "Currently Active",
      },
      COMPLETED: {
        color: "bg-gray-100 text-gray-800",
        icon: "fa-check-circle",
        text: "Completed",
      },
      CANCELLED: {
        color: "bg-red-100 text-red-800",
        icon: "fa-times-circle",
        text: "Cancelled",
      },
    };

    const config = statusConfig[status] || statusConfig["PENDING"];

    return (
      <span
        className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}
      >
        <i className={`fas ${config.icon} mr-2`}></i>
        {config.text}
      </span>
    );
  };

  const { date, time } = formatDateTime(session.scheduled_datetime);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Session Details
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <i className="fas fa-times text-xl"></i>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-6">
          {/* Title and Status */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-2xl font-bold text-gray-900">
                {session.title}
              </h3>
              {getStatusBadge(session.status)}
            </div>
            {session.description && (
              <p className="text-gray-600 text-lg">{session.description}</p>
            )}
          </div>

          {/* Session Info Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Basic Info */}
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-gray-900 border-b pb-2">
                Session Information
              </h4>

              <div className="flex items-center">
                <i className="fas fa-book text-blue-500 w-5 mr-3"></i>
                <div>
                  <span className="text-sm text-gray-500">Subject</span>
                  <p className="font-medium">{session.subject}</p>
                </div>
              </div>

              <div className="flex items-center">
                <i className="fas fa-graduation-cap text-green-500 w-5 mr-3"></i>
                <div>
                  <span className="text-sm text-gray-500">Grade Level</span>
                  <p className="font-medium">Grade {session.level}</p>
                </div>
              </div>

              <div className="flex items-center">
                <i className="fas fa-clock text-orange-500 w-5 mr-3"></i>
                <div>
                  <span className="text-sm text-gray-500">Duration</span>
                  <p className="font-medium">
                    {session.duration_minutes} minutes
                  </p>
                </div>
              </div>

              {session.teacher_name && (
                <div className="flex items-center">
                  <i className="fas fa-chalkboard-teacher text-indigo-500 w-5 mr-3"></i>
                  <div>
                    <span className="text-sm text-gray-500">Teacher</span>
                    <p className="font-medium">{session.teacher_name}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Schedule Info */}
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-gray-900 border-b pb-2">
                Schedule
              </h4>

              <div className="flex items-center">
                <i className="fas fa-calendar text-purple-500 w-5 mr-3"></i>
                <div>
                  <span className="text-sm text-gray-500">Date</span>
                  <p className="font-medium">{date}</p>
                </div>
              </div>

              <div className="flex items-center">
                <i className="fas fa-clock text-orange-500 w-5 mr-3"></i>
                <div>
                  <span className="text-sm text-gray-500">Time</span>
                  <p className="font-medium">{time}</p>
                </div>
              </div>

              {session.assigned_students_count !== undefined && (
                <div className="flex items-center">
                  <i className="fas fa-users text-blue-500 w-5 mr-3"></i>
                  <div>
                    <span className="text-sm text-gray-500">
                      Assigned Students
                    </span>
                    <p className="font-medium">
                      {session.assigned_students_count} students
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Additional Info */}
          {(session.created_at || session.updated_at) && (
            <div className="border-t pt-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">
                Timestamps
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                {session.created_at && (
                  <div>
                    <span className="font-medium">Created:</span>{" "}
                    {new Date(session.created_at).toLocaleString()}
                  </div>
                )}
                {session.updated_at && (
                  <div>
                    <span className="font-medium">Last Updated:</span>{" "}
                    {new Date(session.updated_at).toLocaleString()}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Session ID for debugging */}
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <span className="text-xs text-gray-500">
              Session ID: {session.id}
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

SessionDetailsModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  session: PropTypes.object,
  userRole: PropTypes.string,
};

export default SessionDetailsModal;
