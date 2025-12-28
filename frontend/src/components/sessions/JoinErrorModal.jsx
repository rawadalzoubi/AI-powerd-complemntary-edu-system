import { useState, useEffect } from "react";
import PropTypes from "prop-types";

const JoinErrorModal = ({ isOpen, onClose, error, sessionTitle }) => {
  const [errorInfo, setErrorInfo] = useState({
    title: "فشل في الانضمام للجلسة",
    message: "حدث خطأ غير متوقع",
    icon: "fas fa-exclamation-triangle",
    color: "red",
  });

  useEffect(() => {
    if (error && isOpen) {
      parseError(error);
    }
  }, [error, isOpen]);

  const parseError = (errorObj) => {
    let title = "فشل في الانضمام للجلسة";
    let message = "حدث خطأ غير متوقع";
    let icon = "fas fa-exclamation-triangle";
    let color = "red";

    // Check if it's an axios error with response
    if (errorObj.response?.data?.error) {
      const errorMessage = errorObj.response.data.error;

      if (errorMessage.includes("Session has ended")) {
        title = "انتهت الجلسة";
        message = "لقد انتهت هذه الجلسة ولم يعد بإمكانك الانضمام إليها.";
        icon = "fas fa-clock";
        color = "gray";
      } else if (errorMessage.includes("Session starts in")) {
        const minutes = errorMessage.match(/(\d+) minutes?/)?.[1];
        title = "الجلسة لم تبدأ بعد";
        message = minutes
          ? `ستبدأ الجلسة خلال ${minutes} دقيقة. يرجى المحاولة لاحقاً.`
          : "لم تبدأ الجلسة بعد. يرجى المحاولة لاحقاً.";
        icon = "fas fa-hourglass-half";
        color = "blue";
      } else if (errorMessage.includes("Late join window has closed")) {
        title = "فات وقت الانضمام";
        message =
          "لقد فات الوقت المسموح للانضمام المتأخر للجلسة (10 دقائق من بداية الجلسة).";
        icon = "fas fa-door-closed";
        color = "orange";
      } else if (errorMessage.includes("not assigned")) {
        title = "غير مسند للجلسة";
        message =
          "لم يتم إسنادك لهذه الجلسة. يرجى التواصل مع المستشار الأكاديمي.";
        icon = "fas fa-user-slash";
        color = "red";
      } else if (errorMessage.includes("cancelled")) {
        title = "تم إلغاء الجلسة";
        message = "تم إلغاء هذه الجلسة من قبل المدرس.";
        icon = "fas fa-ban";
        color = "red";
      } else if (errorMessage.includes("15 minutes before")) {
        title = "مبكر جداً";
        message = "يمكن للمدرسين الانضمام قبل 15 دقيقة فقط من بداية الجلسة.";
        icon = "fas fa-clock";
        color = "blue";
      } else {
        // Generic error message
        message = errorMessage;
      }
    } else if (errorObj.message) {
      message = errorObj.message;
    }

    setErrorInfo({ title, message, icon, color });
  };

  const getColorClasses = (color) => {
    const colors = {
      red: {
        bg: "bg-red-100",
        text: "text-red-600",
        border: "border-red-200",
        button: "bg-red-600 hover:bg-red-700",
      },
      orange: {
        bg: "bg-orange-100",
        text: "text-orange-600",
        border: "border-orange-200",
        button: "bg-orange-600 hover:bg-orange-700",
      },
      blue: {
        bg: "bg-blue-100",
        text: "text-blue-600",
        border: "border-blue-200",
        button: "bg-blue-600 hover:bg-blue-700",
      },
      gray: {
        bg: "bg-gray-100",
        text: "text-gray-600",
        border: "border-gray-200",
        button: "bg-gray-600 hover:bg-gray-700",
      },
    };
    return colors[color] || colors.red;
  };

  if (!isOpen) return null;

  const colorClasses = getColorClasses(errorInfo.color);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div className="text-center">
          {/* Icon */}
          <div
            className={`w-16 h-16 ${colorClasses.bg} rounded-full flex items-center justify-center mx-auto mb-4`}
          >
            <i
              className={`${errorInfo.icon} text-2xl ${colorClasses.text}`}
            ></i>
          </div>

          {/* Title */}
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {errorInfo.title}
          </h3>

          {/* Session Title */}
          {sessionTitle && (
            <p className="text-sm text-gray-500 mb-3">الجلسة: {sessionTitle}</p>
          )}

          {/* Error Message */}
          <div
            className={`p-4 ${colorClasses.bg} ${colorClasses.border} border rounded-lg mb-6`}
          >
            <p className="text-sm text-gray-700">{errorInfo.message}</p>
          </div>

          {/* Suggestions */}
          <div className="text-xs text-gray-500 mb-6 text-right">
            <p className="mb-1">💡 اقتراحات:</p>
            <ul className="list-disc list-inside space-y-1">
              {errorInfo.color === "blue" && (
                <li>حاول الانضمام في الوقت المحدد</li>
              )}
              {errorInfo.color === "orange" && (
                <li>انضم للجلسات في أول 10 دقائق</li>
              )}
              {errorInfo.color === "red" && (
                <li>تواصل مع المستشار الأكاديمي</li>
              )}
              {errorInfo.color === "gray" && (
                <li>تحقق من جدول الجلسات القادمة</li>
              )}
              <li>تحديث الصفحة وإعادة المحاولة</li>
            </ul>
          </div>

          {/* Actions */}
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
            >
              إغلاق
            </button>
            <button
              onClick={() => window.location.reload()}
              className={`flex-1 px-4 py-2 ${colorClasses.button} text-white rounded-lg transition-colors`}
            >
              <i className="fas fa-refresh mr-2"></i>
              تحديث الصفحة
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

JoinErrorModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  error: PropTypes.object,
  sessionTitle: PropTypes.string,
};

export default JoinErrorModal;
