import PropTypes from "prop-types";

const ConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = "تأكيد",
  cancelText = "إلغاء",
  type = "danger", // danger, warning, info, success
}) => {
  if (!isOpen) return null;

  const getTypeStyles = (type) => {
    const styles = {
      danger: {
        icon: "fas fa-exclamation-triangle",
        iconBg: "bg-red-100",
        iconColor: "text-red-600",
        confirmBtn: "bg-red-600 hover:bg-red-700",
        border: "border-red-200",
      },
      warning: {
        icon: "fas fa-exclamation-circle",
        iconBg: "bg-yellow-100",
        iconColor: "text-yellow-600",
        confirmBtn: "bg-yellow-600 hover:bg-yellow-700",
        border: "border-yellow-200",
      },
      info: {
        icon: "fas fa-info-circle",
        iconBg: "bg-blue-100",
        iconColor: "text-blue-600",
        confirmBtn: "bg-blue-600 hover:bg-blue-700",
        border: "border-blue-200",
      },
      success: {
        icon: "fas fa-check-circle",
        iconBg: "bg-green-100",
        iconColor: "text-green-600",
        confirmBtn: "bg-green-600 hover:bg-green-700",
        border: "border-green-200",
      },
    };
    return styles[type] || styles.danger;
  };

  const typeStyles = getTypeStyles(type);

  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  const handleCancel = () => {
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div className="text-center">
          {/* Icon */}
          <div
            className={`w-16 h-16 ${typeStyles.iconBg} rounded-full flex items-center justify-center mx-auto mb-4`}
          >
            <i
              className={`${typeStyles.icon} text-2xl ${typeStyles.iconColor}`}
            ></i>
          </div>

          {/* Title */}
          <h3 className="text-lg font-semibold text-gray-900 mb-3">{title}</h3>

          {/* Message */}
          <div
            className={`p-4 ${typeStyles.iconBg} ${typeStyles.border} border rounded-lg mb-6`}
          >
            <p className="text-sm text-gray-700 leading-relaxed">{message}</p>
          </div>

          {/* Warning note for dangerous actions */}
          {type === "danger" && (
            <div className="text-xs text-gray-500 mb-6 text-right">
              <p className="mb-1">⚠️ تحذير:</p>
              <p>هذا الإجراء لا يمكن التراجع عنه</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex space-x-3">
            <button
              onClick={handleCancel}
              className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors font-medium"
            >
              {cancelText}
            </button>
            <button
              onClick={handleConfirm}
              className={`flex-1 px-4 py-2 ${typeStyles.confirmBtn} text-white rounded-lg transition-colors font-medium`}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

ConfirmationModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  message: PropTypes.string.isRequired,
  confirmText: PropTypes.string,
  cancelText: PropTypes.string,
  type: PropTypes.oneOf(["danger", "warning", "info", "success"]),
};

export default ConfirmationModal;
