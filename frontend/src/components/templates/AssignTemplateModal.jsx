import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { apiRequest } from "../../config/api";

const AssignTemplateModal = ({ template, isOpen, onClose, onSuccess }) => {
  const [activeTab, setActiveTab] = useState("students"); // "students" or "groups"
  const [students, setStudents] = useState([]);
  const [groups, setGroups] = useState([]);
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [selectedGroups, setSelectedGroups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadStudents();
      loadGroups();
      setSelectedStudents([]);
      setSelectedGroups([]);
    }
  }, [isOpen]);

  const loadStudents = async () => {
    try {
      setLoading(true);
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
      setLoading(false);
    }
  };

  const loadGroups = async () => {
    try {
      const response = await apiRequest("/api/recurring-sessions/groups/");
      if (response.ok) {
        const data = await response.json();
        // Filter out individual groups and inactive groups
        const filteredGroups = (Array.isArray(data) ? data : []).filter(
          (g) => g.is_active && !g.name?.startsWith("Individual -")
        );
        setGroups(filteredGroups);
      } else {
        setGroups([]);
      }
    } catch (error) {
      console.error("Error loading groups:", error);
      setGroups([]);
    }
  };

  const handleStudentToggle = (studentId) => {
    setSelectedStudents((prev) =>
      prev.includes(studentId)
        ? prev.filter((id) => id !== studentId)
        : [...prev, studentId]
    );
  };

  const handleGroupToggle = (groupId) => {
    setSelectedGroups((prev) =>
      prev.includes(groupId)
        ? prev.filter((id) => id !== groupId)
        : [...prev, groupId]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const hasStudents = selectedStudents.length > 0;
    const hasGroups = selectedGroups.length > 0;

    if (!hasStudents && !hasGroups) {
      alert("يرجى اختيار طالب أو مجموعة واحدة على الأقل");
      return;
    }

    try {
      setSubmitting(true);
      let successCount = 0;

      // Assign individual students
      if (hasStudents) {
        const response = await apiRequest(
          `/api/recurring-sessions/templates/${template.id}/assignments/`,
          {
            method: "POST",
            body: JSON.stringify({ student_ids: selectedStudents }),
          }
        );
        if (response.ok) {
          const result = await response.json();
          successCount += result.assigned_count || selectedStudents.length;
        }
      }

      // Assign groups
      if (hasGroups) {
        for (const groupId of selectedGroups) {
          const response = await apiRequest(
            `/api/recurring-sessions/assignments/`,
            {
              method: "POST",
              body: JSON.stringify({
                template: template.id,
                group: groupId,
              }),
            }
          );
          if (response.ok) {
            successCount++;
          }
        }
      }

      if (successCount > 0) {
        onSuccess();
      } else {
        throw new Error("فشل في التعيين");
      }
    } catch (error) {
      console.error("Error assigning template:", error);
      alert(error.message || "فشل في تعيين القالب");
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">تعيين القالب</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <i className="fas fa-times"></i>
          </button>
        </div>

        {/* Template Info */}
        <div className="px-6 pt-4">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="font-medium text-blue-900">{template?.title}</div>
            <div className="text-sm text-blue-700">
              {template?.subject} - الصف {template?.level}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="px-6 pt-4">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab("students")}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "students"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <i className="fas fa-user mr-2"></i>
              طلاب فرديين ({selectedStudents.length})
            </button>
            <button
              onClick={() => setActiveTab("groups")}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "groups"
                  ? "border-purple-500 text-purple-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <i className="fas fa-users mr-2"></i>
              مجموعات ({selectedGroups.length})
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-gray-600 mt-2">جاري التحميل...</p>
            </div>
          ) : activeTab === "students" ? (
            <div className="space-y-2">
              {students.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <i className="fas fa-user-slash text-2xl mb-2"></i>
                  <p>لا يوجد طلاب متاحين</p>
                </div>
              ) : (
                students.map((student) => (
                  <label
                    key={student.id}
                    className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedStudents.includes(student.id)
                        ? "bg-blue-50 border-blue-300"
                        : "hover:bg-gray-50"
                    }`}
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
                  </label>
                ))
              )}
            </div>
          ) : (
            <div className="space-y-2">
              {groups.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <i className="fas fa-users-slash text-2xl mb-2"></i>
                  <p>لا توجد مجموعات متاحة</p>
                  <a
                    href="/student-groups"
                    className="text-purple-600 hover:underline text-sm mt-2 inline-block"
                  >
                    إنشاء مجموعة جديدة
                  </a>
                </div>
              ) : (
                groups.map((group) => (
                  <label
                    key={group.id}
                    className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedGroups.includes(group.id)
                        ? "bg-purple-50 border-purple-300"
                        : "hover:bg-gray-50"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedGroups.includes(group.id)}
                      onChange={() => handleGroupToggle(group.id)}
                      className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                    />
                    <div className="ml-3 flex-1">
                      <div className="font-medium text-gray-900">
                        {group.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {group.student_count || group.students?.length || 0}{" "}
                        طالب
                      </div>
                    </div>
                  </label>
                ))
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-between items-center p-6 border-t bg-gray-50">
          <div className="text-sm text-gray-600">
            {selectedStudents.length > 0 && (
              <span className="mr-3">
                <i className="fas fa-user text-blue-500 mr-1"></i>
                {selectedStudents.length} طالب
              </span>
            )}
            {selectedGroups.length > 0 && (
              <span>
                <i className="fas fa-users text-purple-500 mr-1"></i>
                {selectedGroups.length} مجموعة
              </span>
            )}
          </div>
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors"
            >
              إلغاء
            </button>
            <button
              onClick={handleSubmit}
              disabled={
                submitting ||
                (selectedStudents.length === 0 && selectedGroups.length === 0)
              }
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-lg transition-colors"
            >
              {submitting ? "جاري التعيين..." : "تعيين القالب"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

AssignTemplateModal.propTypes = {
  template: PropTypes.object,
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
};

export default AssignTemplateModal;
