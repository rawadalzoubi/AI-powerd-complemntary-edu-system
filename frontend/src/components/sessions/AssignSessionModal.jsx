import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { sessionService } from "../../services/sessionService";
import toast from "react-hot-toast";

const AssignSessionModal = ({ isOpen, onClose, session, onAssignSuccess }) => {
  const [students, setStudents] = useState([]);
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [assignedStudents, setAssignedStudents] = useState([]);
  const [showManageMode, setShowManageMode] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadStudents();
      loadAssignedStudents();
    }
  }, [isOpen]);

  const loadAssignedStudents = async () => {
    try {
      // For now, we'll use a placeholder since we need to create an endpoint for this
      // TODO: Create endpoint to get assigned students for a session
      setAssignedStudents([]);
    } catch (error) {
      console.error("Error loading assigned students:", error);
    }
  };

  const loadStudents = async () => {
    try {
      setSearchLoading(true);
      const data = await sessionService.searchStudents(searchQuery);
      setStudents(Array.isArray(data) ? data : data.results || []);
    } catch (error) {
      console.error("Error loading students:", error);
      toast.error("Failed to load students");
    } finally {
      setSearchLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.length >= 2 || query.length === 0) {
      try {
        setSearchLoading(true);
        const data = await sessionService.searchStudents(query);
        setStudents(Array.isArray(data) ? data : data.results || []);
      } catch (error) {
        console.error("Error searching students:", error);
      } finally {
        setSearchLoading(false);
      }
    }
  };

  const handleStudentToggle = (studentId) => {
    setSelectedStudents((prev) =>
      prev.includes(studentId)
        ? prev.filter((id) => id !== studentId)
        : [...prev, studentId]
    );
  };

  const handleSelectAll = () => {
    if (selectedStudents.length === students.length) {
      setSelectedStudents([]);
    } else {
      setSelectedStudents(students.map((student) => student.id));
    }
  };

  const handleAssign = async () => {
    if (selectedStudents.length === 0) {
      toast.error("Please select at least one student");
      return;
    }

    try {
      setLoading(true);
      await sessionService.assignSession(session.id, selectedStudents, message);
      toast.success(
        `Session assigned to ${selectedStudents.length} students successfully!`
      );
      onAssignSuccess();
      onClose();
    } catch (error) {
      console.error("Error assigning session:", error);
      toast.error("Failed to assign session");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSelectedStudents([]);
    setMessage("");
    setSearchQuery("");
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Assign Session to Students
            </h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <i className="fas fa-times text-xl"></i>
            </button>
          </div>
          <p className="mt-2 text-sm text-gray-600">
            Session: <span className="font-medium">{session?.title}</span>
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-4 max-h-96 overflow-y-auto">
          {/* Currently Assigned Students */}
          {session?.assigned_students_count > 0 && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="text-sm font-medium text-blue-900 mb-2">
                Currently Assigned Students ({session.assigned_students_count})
              </h3>
              <p className="text-xs text-blue-700">
                You can assign additional students or manage existing
                assignments below.
              </p>
            </div>
          )}

          {/* Search */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Students
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder="Search by name or email..."
                className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
              />
              <i className="fas fa-search absolute left-3 top-3 text-gray-400"></i>
              {searchLoading && (
                <div className="absolute right-3 top-3">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                </div>
              )}
            </div>
          </div>

          {/* Select All */}
          {students.length > 0 && (
            <div className="mb-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedStudents.length === students.length}
                  onChange={handleSelectAll}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Select All ({students.length} students)
                </span>
              </label>
            </div>
          )}

          {/* Students List */}
          <div className="space-y-2 mb-4">
            {students.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                {searchLoading ? (
                  <div>
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
                    <p>Loading students...</p>
                  </div>
                ) : (
                  <div>
                    <i className="fas fa-users text-4xl mb-2"></i>
                    <p>No students found</p>
                  </div>
                )}
              </div>
            ) : (
              students.map((student) => (
                <label
                  key={student.id}
                  className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedStudents.includes(student.id)}
                    onChange={() => handleStudentToggle(student.id)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <div className="ml-3 flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {student.first_name} {student.last_name}
                        </p>
                        <p className="text-sm text-gray-500">{student.email}</p>
                      </div>
                      {student.grade_level && (
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                          Grade {student.grade_level}
                        </span>
                      )}
                    </div>
                  </div>
                </label>
              ))
            )}
          </div>

          {/* Message */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Assignment Message (Optional)
            </label>
            <textarea
              placeholder="Add a message for the students..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {selectedStudents.length} student
            {selectedStudents.length !== 1 ? "s" : ""} selected
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              onClick={handleAssign}
              disabled={loading || selectedStudents.length === 0}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {loading && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              )}
              Assign Session
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

AssignSessionModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  session: PropTypes.object,
  onAssignSuccess: PropTypes.func.isRequired,
};

export default AssignSessionModal;
