import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { apiRequest } from "../../config/api";

const EditGroupModal = ({ isOpen, onClose, group, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    is_active: true,
  });
  const [allStudents, setAllStudents] = useState([]);
  const [currentStudents, setCurrentStudents] = useState([]);
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [errors, setErrors] = useState({});
  const [activeTab, setActiveTab] = useState("info");

  useEffect(() => {
    if (isOpen && group) {
      setFormData({
        name: group.name || "",
        description: group.description || "",
        is_active: group.is_active !== false,
      });
      loadStudents();
      loadGroupStudents();
      setErrors({});
      setActiveTab("info");
    }
  }, [isOpen, group]);

  const loadStudents = async () => {
    try {
      setLoadingStudents(true);
      const response = await apiRequest(
        "/api/recurring-sessions/students/available/"
      );
      if (response.ok) {
        const data = await response.json();
        setAllStudents(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error("Error loading students:", error);
    } finally {
      setLoadingStudents(false);
    }
  };

  const loadGroupStudents = async () => {
    try {
      const response = await apiRequest(
        `/api/recurring-sessions/groups/${group.id}/`
      );
      if (response.ok) {
        const data = await response.json();
        const studentIds = data.students?.map((s) => s.id || s) || [];
        setCurrentStudents(studentIds);
        setSelectedStudents(studentIds);
      }
    } catch (error) {
      console.error("Error loading group students:", error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleStudentToggle = (studentId) => {
    setSelectedStudents((prev) =>
      prev.includes(studentId)
        ? prev.filter((id) => id !== studentId)
        : [...prev, studentId]
    );
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) {
      newErrors.name = "اسم المجموعة مطلوب";
    }
    if (selectedStudents.length === 0) {
      newErrors.students = "يجب اختيار طالب واحد على الأقل";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      setLoading(true);

      // Use PATCH for partial update
      const updateResponse = await apiRequest(
        `/api/recurring-sessions/groups/${group.id}/`,
        {
          method: "PATCH",
          body: JSON.stringify({
            name: formData.name.trim(),
            description: formData.description.trim(),
            is_active: formData.is_active,
            students: selectedStudents,
          }),
        }
      );

      if (!updateResponse.ok) {
        const errorData = await updateResponse.json().catch(() => ({}));
        console.error("Update error details:", errorData);
        throw new Error("فشل في تحديث المجموعة");
      }

      onSuccess();
    } catch (error) {
      console.error("Error updating group:", error);
      setErrors({ submit: error.message || "فشل في تحديث المجموعة" });
    } finally {
      setLoading(false);
    }
  };

  const filteredStudents = allStudents.filter(
    (student) =>
      student.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <i className="fas fa-edit text-blue-600"></i>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                تعديل المجموعة
              </h3>
              <p className="text-sm text-gray-500">{group?.name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <i className="fas fa-times text-xl"></i>
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b px-6">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab("info")}
              className={`py-3 px-1 border-b-2 font-medium text-sm ${
                activeTab === "info"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <i className="fas fa-info-circle mr-2"></i>
              معلومات المجموعة
            </button>
            <button
              onClick={() => setActiveTab("students")}
              className={`py-3 px-1 border-b-2 font-medium text-sm ${
                activeTab === "students"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <i className="fas fa-users mr-2"></i>
              الطلاب ({selectedStudents.length})
            </button>
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {errors.submit && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              <i className="fas fa-exclamation-circle mr-2"></i>
              {errors.submit}
            </div>
          )}

          {activeTab === "info" && (
            <div className="space-y-4">
              {/* Group Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  اسم المجموعة <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.name ? "border-red-500" : "border-gray-300"
                  }`}
                />
                {errors.name && (
                  <p className="text-red-500 text-sm mt-1">{errors.name}</p>
                )}
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  الوصف
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Active Status */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="is_active"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label
                  htmlFor="is_active"
                  className="ml-2 text-sm text-gray-700"
                >
                  المجموعة نشطة
                </label>
              </div>
            </div>
          )}

          {activeTab === "students" && (
            <div>
              {errors.students && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                  <i className="fas fa-exclamation-circle mr-2"></i>
                  {errors.students}
                </div>
              )}
              {/* Search */}
              <div className="relative mb-4">
                <input
                  type="text"
                  placeholder="البحث عن طالب..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
              </div>

              {/* Students List */}
              <div className="border rounded-lg max-h-80 overflow-y-auto">
                {loadingStudents ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                  </div>
                ) : filteredStudents.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <i className="fas fa-user-slash text-2xl mb-2"></i>
                    <p>لا يوجد طلاب</p>
                  </div>
                ) : (
                  filteredStudents.map((student) => (
                    <label
                      key={student.id}
                      className="flex items-center p-3 hover:bg-gray-50 cursor-pointer border-b last:border-b-0"
                    >
                      <input
                        type="checkbox"
                        checked={selectedStudents.includes(student.id)}
                        onChange={() => handleStudentToggle(student.id)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <div className="ml-3 flex-1">
                        <div className="font-medium text-gray-900">
                          {student.first_name} {student.last_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {student.email}
                        </div>
                      </div>
                      {currentStudents.includes(student.id) && (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                          عضو حالي
                        </span>
                      )}
                    </label>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-3 p-6 border-t bg-gray-50">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors"
          >
            إلغاء
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-lg transition-colors flex items-center"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                جاري الحفظ...
              </>
            ) : (
              <>
                <i className="fas fa-save mr-2"></i>
                حفظ التغييرات
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

EditGroupModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  group: PropTypes.object,
  onSuccess: PropTypes.func.isRequired,
};

export default EditGroupModal;
