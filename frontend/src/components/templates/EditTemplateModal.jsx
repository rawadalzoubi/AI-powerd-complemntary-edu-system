import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { templateService } from "../../services/templateService";
import toast from "react-hot-toast";

const EditTemplateModal = ({ isOpen, onClose, template, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    subject: "",
    level: "",
    day_of_week: "",
    start_time: "",
    duration_minutes: 60,
    recurrence_type: "WEEKLY",
    start_date: "",
    end_date: "",
    max_participants: 50,
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const dayOfWeekOptions = [
    { value: 0, label: "الاثنين" },
    { value: 1, label: "الثلاثاء" },
    { value: 2, label: "الأربعاء" },
    { value: 3, label: "الخميس" },
    { value: 4, label: "الجمعة" },
    { value: 5, label: "السبت" },
    { value: 6, label: "الأحد" },
  ];

  const gradeOptions = [
    { value: "1", label: "الصف الأول" },
    { value: "2", label: "الصف الثاني" },
    { value: "3", label: "الصف الثالث" },
    { value: "4", label: "الصف الرابع" },
    { value: "5", label: "الصف الخامس" },
    { value: "6", label: "الصف السادس" },
    { value: "7", label: "الصف السابع" },
    { value: "8", label: "الصف الثامن" },
    { value: "9", label: "الصف التاسع" },
    { value: "10", label: "الصف العاشر" },
    { value: "11", label: "الصف الحادي عشر" },
    { value: "12", label: "الصف الثاني عشر" },
  ];

  const recurrenceOptions = [
    { value: "WEEKLY", label: "أسبوعياً" },
    { value: "BIWEEKLY", label: "كل أسبوعين" },
    { value: "MONTHLY", label: "شهرياً" },
  ];

  // Load template data when modal opens
  useEffect(() => {
    if (isOpen && template) {
      setFormData({
        title: template.title || "",
        description: template.description || "",
        subject: template.subject || "",
        level: template.level || "",
        day_of_week: template.day_of_week?.toString() || "",
        start_time: template.start_time || "",
        duration_minutes: template.duration_minutes || 60,
        recurrence_type: template.recurrence_type || "WEEKLY",
        start_date: template.start_date || "",
        end_date: template.end_date || "",
        max_participants: template.max_participants || 50,
      });
      setErrors({});
    }
  }, [isOpen, template]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = "عنوان القالب مطلوب";
    }

    if (!formData.subject.trim()) {
      newErrors.subject = "المادة مطلوبة";
    }

    if (!formData.level) {
      newErrors.level = "الصف مطلوب";
    }

    if (formData.day_of_week === "") {
      newErrors.day_of_week = "يوم الأسبوع مطلوب";
    }

    if (!formData.start_time) {
      newErrors.start_time = "وقت البداية مطلوب";
    }

    if (!formData.start_date) {
      newErrors.start_date = "تاريخ البداية مطلوب";
    }

    if (formData.end_date && formData.end_date <= formData.start_date) {
      newErrors.end_date = "تاريخ النهاية يجب أن يكون بعد تاريخ البداية";
    }

    if (formData.duration_minutes < 15 || formData.duration_minutes > 240) {
      newErrors.duration_minutes = "مدة الجلسة يجب أن تكون بين 15 و 240 دقيقة";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const updatedTemplate = await templateService.updateTemplate(
        template.id,
        {
          ...formData,
          day_of_week: parseInt(formData.day_of_week),
          duration_minutes: parseInt(formData.duration_minutes),
          max_participants: parseInt(formData.max_participants),
        }
      );

      toast.success("تم تحديث القالب بنجاح");
      onSuccess(updatedTemplate);
      onClose();
    } catch (error) {
      console.error("Error updating template:", error);
      toast.error(error.response?.data?.error || "فشل في تحديث القالب");
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
              تعديل قالب الجلسة
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <i className="fas fa-times text-xl"></i>
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Title */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                عنوان القالب *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.title ? "border-red-500" : "border-gray-300"
                }`}
                placeholder="مثال: درس الرياضيات الأسبوعي"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title}</p>
              )}
            </div>

            {/* Description */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                الوصف
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="وصف مختصر للقالب..."
              />
            </div>

            {/* Subject */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                المادة *
              </label>
              <input
                type="text"
                name="subject"
                value={formData.subject}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.subject ? "border-red-500" : "border-gray-300"
                }`}
                placeholder="مثال: الرياضيات"
              />
              {errors.subject && (
                <p className="mt-1 text-sm text-red-600">{errors.subject}</p>
              )}
            </div>

            {/* Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                الصف *
              </label>
              <select
                name="level"
                value={formData.level}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.level ? "border-red-500" : "border-gray-300"
                }`}
              >
                <option value="">اختر الصف</option>
                {gradeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {errors.level && (
                <p className="mt-1 text-sm text-red-600">{errors.level}</p>
              )}
            </div>

            {/* Day of Week */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                يوم الأسبوع *
              </label>
              <select
                name="day_of_week"
                value={formData.day_of_week}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.day_of_week ? "border-red-500" : "border-gray-300"
                }`}
              >
                <option value="">اختر اليوم</option>
                {dayOfWeekOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {errors.day_of_week && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.day_of_week}
                </p>
              )}
            </div>

            {/* Start Time */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                وقت البداية *
              </label>
              <input
                type="time"
                name="start_time"
                value={formData.start_time}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.start_time ? "border-red-500" : "border-gray-300"
                }`}
              />
              {errors.start_time && (
                <p className="mt-1 text-sm text-red-600">{errors.start_time}</p>
              )}
            </div>

            {/* Duration */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                مدة الجلسة (دقيقة)
              </label>
              <input
                type="number"
                name="duration_minutes"
                value={formData.duration_minutes}
                onChange={handleInputChange}
                min="15"
                max="240"
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.duration_minutes ? "border-red-500" : "border-gray-300"
                }`}
              />
              {errors.duration_minutes && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.duration_minutes}
                </p>
              )}
            </div>

            {/* Max Participants */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                الحد الأقصى للمشاركين
              </label>
              <input
                type="number"
                name="max_participants"
                value={formData.max_participants}
                onChange={handleInputChange}
                min="1"
                max="200"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Recurrence Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                نمط التكرار
              </label>
              <select
                name="recurrence_type"
                value={formData.recurrence_type}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {recurrenceOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Start Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                تاريخ البداية *
              </label>
              <input
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.start_date ? "border-red-500" : "border-gray-300"
                }`}
              />
              {errors.start_date && (
                <p className="mt-1 text-sm text-red-600">{errors.start_date}</p>
              )}
            </div>

            {/* End Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                تاريخ النهاية (اختياري)
              </label>
              <input
                type="date"
                name="end_date"
                value={formData.end_date}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.end_date ? "border-red-500" : "border-gray-300"
                }`}
              />
              {errors.end_date && (
                <p className="mt-1 text-sm text-red-600">{errors.end_date}</p>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
            >
              إلغاء
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center"
            >
              {loading && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              )}
              تحديث القالب
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

EditTemplateModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  template: PropTypes.object,
  onSuccess: PropTypes.func.isRequired,
};

export default EditTemplateModal;
