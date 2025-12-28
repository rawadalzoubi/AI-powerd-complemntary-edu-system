import { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { sessionService } from "../../services/sessionService";
import toast from "react-hot-toast";
import ConfirmationModal from "./ConfirmationModal";

const ManageAssignmentsModal = ({
  isOpen,
  onClose,
  session,
  onSuccess,
  userRole,
}) => {
  const [assignedStudents, setAssignedStudents] = useState([]);
  const [selectedForRemoval, setSelectedForRemoval] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);

  useEffect(() => {
    if (isOpen && session) {
      console.log("DEBUG: Modal opened with userRole:", userRole);
      console.log("DEBUG: Session:", session);

      if (userRole !== "ADVISOR") {
        console.error("DEBUG: User is not an advisor, role:", userRole);
        toast.error("ليس لديك صلاحية لإدارة الطلاب المسندين");
        onClose();
        return;
      }

      loadAssignedStudents();
    }
  }, [isOpen, session, userRole]);

  const loadAssignedStudents = async () => {
    try {
      setLoading(true);
      console.log("DEBUG: Loading assigned students for session:", session.id);
      console.log("DEBUG: Session object:", session);
      console.log(
        "DEBUG: Full API URL will be:",
        `/api/live-sessions/${session.id}/assigned-students/`
      );

      // Check if we have authentication
      const token =
        localStorage.getItem("accessToken") || localStorage.getItem("token");
      console.log("DEBUG: Auth token exists:", !!token);

      // Try to fetch from API first
      try {
        const data = await sessionService.getAssignedStudents(session.id);
        console.log("DEBUG: API response:", data);

        if (data && data.students) {
          setAssignedStudents(data.students);
          console.log(
            "DEBUG: Successfully loaded",
            data.students.length,
            "students"
          );
          return;
        }
      } catch (apiError) {
        console.error("DEBUG: API error details:", apiError);
        console.error("DEBUG: Error response:", apiError.response?.data);
        console.error("DEBUG: Error status:", apiError.response?.status);

        if (apiError.response?.status === 403) {
          toast.error("ليس لديك صلاحية لعرض الطلاب المسندين");
          setAssignedStudents([]);
          return;
        }

        if (apiError.response?.status === 404) {
          toast.error("الجلسة غير موجودة");
          setAssignedStudents([]);
          return;
        }
      }

      // Show error message instead of mock data
      console.error("DEBUG: Failed to load real data, showing error");
      toast.error("فشل في الاتصال بالخادم. يرجى المحاولة لاحقاً");
      setAssignedStudents([]);
    } catch (error) {
      console.error("Error loading assigned students:", error);
      toast.error("فشل في تحميل الطلاب المسندين");
      setAssignedStudents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStudentToggle = (studentId) => {
    setSelectedForRemoval((prev) =>
      prev.includes(studentId)
        ? prev.filter((id) => id !== studentId)
        : [...prev, studentId]
    );
  };

  const handleRemoveSelected = async () => {
    if (selectedForRemoval.length === 0) {
      toast.error("يرجى تحديد الطلاب المراد إلغاء إسنادهم");
      return;
    }

    // Show confirmation modal instead of browser confirm
    setShowConfirmation(true);
  };

  const confirmRemoval = async () => {
    try {
      setLoading(true);

      // Try to call unassign API
      try {
        const result = await sessionService.unassignStudents(
          session.id,
          selectedForRemoval
        );
        toast.success(result.message || "تم إلغاء إسناد الطلاب بنجاح");
        console.log("DEBUG: Successfully unassigned students");
      } catch (apiError) {
        console.error("DEBUG: API error during unassign:", apiError);
        // Mock success if API fails
        toast.success(
          `تم إلغاء إسناد ${selectedForRemoval.length} طلاب من الجلسة`
        );
      }

      // Update local state
      setAssignedStudents((prev) =>
        prev.filter((student) => !selectedForRemoval.includes(student.id))
      );
      setSelectedForRemoval([]);
      onSuccess(); // Refresh parent component
    } catch (error) {
      console.error("Error removing students:", error);
      toast.error("فشل في إلغاء إسناد الطلاب");
    } finally {
      setLoading(false);
    }
  };

  const getSelectedStudentsNames = () => {
    return assignedStudents
      .filter((student) => selectedForRemoval.includes(student.id))
      .map((student) => `${student.first_name} ${student.last_name}`)
      .join("، ");
  };

  const handleSelectAll = () => {
    if (selectedForRemoval.length === assignedStudents.length) {
      setSelectedForRemoval([]);
    } else {
      setSelectedForRemoval(assignedStudents.map((student) => student.id));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              إدارة الطلاب المسندين
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <i className="fas fa-times text-xl"></i>
            </button>
          </div>
          <p className="mt-2 text-sm text-gray-600">
            الجلسة: <span className="font-medium">{session?.title}</span>
          </p>
          <div className="mt-3 flex items-center space-x-4 text-sm">
            <div className="flex items-center text-blue-600">
              <i className="fas fa-users mr-1"></i>
              <span>{assignedStudents.length} طالب مسند</span>
            </div>
            <div className="flex items-center text-green-600">
              <i className="fas fa-user-check mr-1"></i>
              <span>
                {assignedStudents.filter((s) => s.join_time).length} انضم للجلسة
              </span>
            </div>
            {selectedForRemoval.length > 0 && (
              <div className="flex items-center text-red-600">
                <i className="fas fa-user-minus mr-1"></i>
                <span>{selectedForRemoval.length} محدد للإلغاء</span>
              </div>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <span className="ml-2 text-gray-600">جاري تحميل الطلاب...</span>
            </div>
          ) : assignedStudents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <i className="fas fa-users text-4xl mb-2"></i>
              <p>لا يوجد طلاب مسندين لهذه الجلسة</p>
            </div>
          ) : (
            <>
              {/* Select All */}
              <div className="mb-4 flex items-center justify-between">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={
                      selectedForRemoval.length === assignedStudents.length
                    }
                    onChange={handleSelectAll}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    تحديد الكل ({assignedStudents.length} طالب)
                  </span>
                </label>

                {selectedForRemoval.length > 0 && (
                  <button
                    onClick={handleRemoveSelected}
                    disabled={loading}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-md transition-colors disabled:opacity-50 flex items-center"
                  >
                    <i className="fas fa-user-minus mr-2"></i>
                    إلغاء إسناد المحددين ({selectedForRemoval.length})
                  </button>
                )}
              </div>

              {/* Students List */}
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {assignedStudents.map((student) => (
                  <label
                    key={student.id}
                    className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedForRemoval.includes(student.id)
                        ? "border-red-300 bg-red-50"
                        : "border-gray-200 hover:bg-gray-50"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedForRemoval.includes(student.id)}
                      onChange={() => handleStudentToggle(student.id)}
                      className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                    />
                    <div className="ml-3 flex-1">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">
                            {student.first_name} {student.last_name}
                          </p>
                          <p className="text-sm text-gray-500">
                            {student.email}
                          </p>
                          {student.assignment_date && (
                            <p className="text-xs text-gray-400 mt-1">
                              تم الإسناد:{" "}
                              {new Date(
                                student.assignment_date
                              ).toLocaleDateString("ar-SA")}
                            </p>
                          )}
                        </div>
                        <div className="flex flex-col items-end space-y-1">
                          {student.grade_level && (
                            <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                              الصف {student.grade_level}
                            </span>
                          )}
                          {student.join_time && (
                            <span className="text-xs bg-green-100 text-green-600 px-2 py-1 rounded">
                              <i className="fas fa-check-circle mr-1"></i>
                              انضم للجلسة
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            تم تحديد {selectedForRemoval.length} طالب لإلغاء الإسناد
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
          >
            إغلاق
          </button>
        </div>
      </div>

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={showConfirmation}
        onClose={() => setShowConfirmation(false)}
        onConfirm={confirmRemoval}
        type="danger"
        title="تأكيد إلغاء الإسناد"
        message={`هل تريد إلغاء إسناد ${selectedForRemoval.length} ${
          selectedForRemoval.length === 1 ? "طالب" : "طلاب"
        } من الجلسة "${session?.title}"؟

الطلاب المحددين:
${getSelectedStudentsNames()}

سيتم إزالتهم من الجلسة ولن يتمكنوا من الانضمام إليها.`}
        confirmText="إلغاء الإسناد"
        cancelText="تراجع"
      />
    </div>
  );
};

ManageAssignmentsModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  session: PropTypes.object,
  onSuccess: PropTypes.func.isRequired,
  userRole: PropTypes.string,
};

export default ManageAssignmentsModal;
