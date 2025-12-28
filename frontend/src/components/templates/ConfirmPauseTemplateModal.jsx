import React from "react";
import PropTypes from "prop-types";

const ConfirmPauseTemplateModal = ({
  isOpen,
  onClose,
  onConfirm,
  template,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
              <i className="fas fa-pause text-yellow-600 text-xl"></i>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mr-4">
              إيقاف القالب مؤقتاً
            </h2>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          <p className="text-gray-700 mb-4">
            هل تريد إيقاف القالب{" "}
            <span className="font-bold text-gray-900">"{template?.title}"</span>{" "}
            مؤقتاً؟
          </p>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex items-start">
              <i className="fas fa-info-circle text-blue-600 mt-1 mr-2"></i>
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-2">ماذا سيحدث:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>سيتوقف إنشاء الجلسات الجديدة مؤقتاً</li>
                  <li>يمكنك استئناف القالب في أي وقت</li>
                  <li>الجلسات المولدة سابقاً ستبقى كما هي</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg transition-colors font-medium"
          >
            إلغاء
          </button>
          <button
            onClick={onConfirm}
            className="px-6 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors font-medium flex items-center"
          >
            <i className="fas fa-pause mr-2"></i>
            إيقاف مؤقت
          </button>
        </div>
      </div>
    </div>
  );
};

ConfirmPauseTemplateModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  template: PropTypes.object,
};

export default ConfirmPauseTemplateModal;
