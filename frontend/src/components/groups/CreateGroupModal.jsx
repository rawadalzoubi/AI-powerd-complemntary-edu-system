import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { apiRequest } from "../../config/api";

const CreateGroupModal = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
  });
  const [students, setStudents] = useState([]);
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (isOpen) {
      loadStudents();
      setFormData({ name: "", description: "" });
      setSelectedStudents([]);
      setErrors({});
    }
  }, [isOpen]);

  const loadStudents = async () => {
    try {
      setLoadingStudents(true);
      const response = await apiRequest(
        "/api/recurring-sessions/students/available/"
      );
      if (response.ok) {
        const data = await response.json();
        setStudents(Array.isArray(data) ? data : []);
      } else {
        setStudents([]);
      }
    } catch (error) {
      console.error("Error loading students:", error);
      setStudents([]);
    } finally {
      setLoadingStudents(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
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
    const filteredIds = filteredStudents.map((s) => s.id);
    const allSelected = filteredIds.every((id) =>
      selectedStudents.includes(id)
    );

    if (allSelected) {
      setSelectedStudents((prev) =>
        prev.filter((id) => !filteredIds.includes(id))
      );
    } else {
      setSelectedStudents((prev) => [...new Set([...prev, ...filteredIds])]);
    }
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

      // Create the group with students included
      const createResponse = await apiRequest(
        "/api/recurring-sessions/groups/",
        {
          method: "POST",
          body: JSON.stringify({
            name: formData.name.trim(),
            description: formData.description.trim(),
            is_active: true,
            students: selectedStudents,
          }),
        }
      );

      if (!createResponse.ok) {
        const errorData = await createResponse.json();
        const errorMsg =
          errorData.detail ||
          errorData.students?.[0] ||
          errorData.name?.[0] ||
          "فشل في إنشاء المجموعة";
        throw new Error(errorMsg);
      }

      onSuccess();
    } catch (error) {
      console.error("Error creating group:", error);
      setErrors({ submit: error.message || "فشل في إنشاء المجموعة" });
    } finally {
      setLoading(false);
    }
  };

  const filteredStudents = students.filter(
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
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
              <i className="fas fa-users text-purple-600"></i>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                إنشاء مجموعة جديدة
              </h3>
              <p className="text-sm text-gray-500">
                أضف مجموعة طلاب للجلسات المتكررة
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <i className="fas fa-times text-xl"></i>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6">
          {errors.submit && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              <i className="fas fa-exclamation-circle mr-2"></i>
              {errors.submit}
            </div>
          )}

          {/* Group Name */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              اسم المجموعة <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="مثال: مجموعة الرياضيات المتقدمة"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                errors.name ? "border-red-500" : "border-gray-300"
              }`}
            />
            {errors.name && (
              <p className="text-red-500 text-sm mt-1">{errors.name}</p>
            )}
          </div>

          {/* Description */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              الوصف
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="وصف اختياري للمجموعة..."
              rows={2}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          {/* Students Selection */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-700">
                اختر الطلاب <span className="text-red-500">*</span>
              </label>
              <span className="text-sm text-purple-600 font-medium">
                {selectedStudents.length} طالب محدد
              </span>
            </div>

            {/* Search */}
            <div className="relative mb-3">
              <input
                type="text"
                placeholder="البحث عن طالب..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
              <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
            </div>

            {/* Select All */}
            {filteredStudents.length > 0 && (
              <button
                type="button"
                onClick={handleSelectAll}
                className="text-sm text-purple-600 hover:text-purple-700 mb-2"
              >
                {filteredStudents.every((s) => selectedStudents.includes(s.id))
                  ? "إلغاء تحديد الكل"
                  : "تحديد الكل"}
              </button>
            )}

            {/* Students List */}
            <div className="border rounded-lg max-h-60 overflow-y-auto">
              {loadingStudents ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto"></div>
                  <p className="text-gray-600 mt-2 text-sm">جاري التحميل...</p>
                </div>
              ) : filteredStudents.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <i className="fas fa-user-slash text-2xl mb-2"></i>
                  <p>{searchTerm ? "لا توجد نتائج" : "لا يوجد طلاب متاحين"}</p>
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
                      className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                    />
                    <div className="ml-3 flex-1">
                      <div className="font-medium text-gray-900">
                        {student.first_name} {student.last_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {student.email}
                      </div>
                    </div>
                  </label>
                ))
              )}
            </div>
            {errors.students && (
              <p className="text-red-500 text-sm mt-1">{errors.students}</p>
            )}
          </div>
        </form>

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
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white rounded-lg transition-colors flex items-center"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                جاري الإنشاء...
              </>
            ) : (
              <>
                <i className="fas fa-plus mr-2"></i>
                إنشاء المجموعة
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

CreateGroupModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
};

export default CreateGroupModal;
