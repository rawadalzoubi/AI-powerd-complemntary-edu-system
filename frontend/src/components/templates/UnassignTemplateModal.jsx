import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { apiRequest } from "../../config/api";
import toast from "react-hot-toast";

const UnassignTemplateModal = ({ isOpen, onClose, template, onSuccess }) => {
  const [assignedStudents, setAssignedStudents] = useState([]);
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingStudents, setLoadingStudents] = useState(true);

  useEffect(() => {
    if (isOpen && template) {
      loadAssignedStudents();
    }
  }, [isOpen, template]);

  const loadAssignedStudents = async () => {
    try {
      setLoadingStudents(true);
      const response = await apiRequest(
        `/api/recurring-sessions/templates/${template.id}/assigned_students/`
      );

      if (response.ok) {
        const data = await response.json();
        setAssignedStudents(data);
      } else {
        toast.error("فشل في تحميل الطلاب المعينين");
      }
    } catch (error) {
      console.error("Error loading assigned students:", error);
      toast.error("فشل في تحميل الطلاب المعينين");
    } finally {
      setLoadingStudents(false);
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
    if (selectedStudents.length === assignedStudents.length) {
      setSelectedStudents([]);
    } else {
      setSelectedStudents(assignedStudents.map((s) => s.id));
    }
  };

  const handleUnassign = async () => {
    if (selectedStudents.length === 0) {
      toast.error("الرجاء اختيار طالب واحد على الأقل");
      return;
    }

    setLoading(true);
    try {
      const response = await apiRequest(
        `/api/recurring-sessions/templates/${template.id}/unassign/`,
        {
          method: "POST",
          body: JSON.stringify({
            student_ids: selectedStudents,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        toast.success(data.message || "تم إلغاء التعيين بنجاح");
        onSuccess();
      } else {
        const errorData = await response.json();
        toast.error(errorData.error || "فشل في إلغاء التعيين");
      }
    } catch (error) {
      console.error("Error unassigning students:", error);
      toast.error("فشل في إلغاء التعيين");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              إلغاء تعيين الطلاب
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <i className="fas fa-times text-xl"></i>
            </button>
          </div>
          <p className="mt-2 text-sm text-gray-600">
            القالب: <span className="font-medium">{template?.title}</span>
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          {loadingStudents ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <span className="ml-3 text-gray-600">جاري تحميل الطلاب...</span>
            </div>
          ) : assignedStudents.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <i className="fas fa-user-slash text-2xl text-gray-400"></i>
              </div>
              <p className="text-gray-600">لا يوجد طلاب معينين لهذا القالب</p>
            </div>
          ) : (
            <>
              {/* Select All */}
              <div className="mb-4 pb-4 border-b">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={
                      selectedStudents.length === assignedStudents.length
                    }
                    onChange={handleSelectAll}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="mr-2 text-sm font-medium text-gray-700">
                    تحديد الكل ({assignedStudents.length} طالب)
                  </span>
                </label>
              </div>

              {/* Students List */}
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {assignedStudents.map((student) => (
                  <label
                    key={student.id}
                    className="flex items-center p-3 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={selectedStudents.includes(student.id)}
                      onChange={() => handleStudentToggle(student.id)}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <div className="mr-3 flex-1">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <i className="fas fa-user text-blue-600 text-sm"></i>
                        </div>
                        <div className="mr-3">
                          <p className="text-sm font-medium text-gray-900">
                            {student.full_name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {student.email}
                          </p>
                        </div>
                      </div>
                    </div>
                  </label>
                ))}
              </div>

              {/* Selected Count */}
              {selectedStudents.length > 0 && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <i className="fas fa-info-circle mr-2"></i>
                    تم تحديد {selectedStudents.length} طالب
                  </p>
                </div>
              )}
            </>
          )}
        </div>

        {/* Actions */}
        {!loadingStudents && assignedStudents.length > 0 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-end space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
            >
              إلغاء
            </button>
            <button
              onClick={handleUnassign}
              disabled={loading || selectedStudents.length === 0}
              className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {loading && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              )}
              إلغاء التعيين
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

UnassignTemplateModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  template: PropTypes.object,
  onSuccess: PropTypes.func.isRequired,
};

export default UnassignTemplateModal;
