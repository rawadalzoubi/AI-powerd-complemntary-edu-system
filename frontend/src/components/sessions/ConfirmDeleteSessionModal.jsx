import React from "react";
import PropTypes from "prop-types";

const ConfirmDeleteSessionModal = ({ isOpen, onClose, onConfirm, session }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="bg-red-50 px-6 py-4 border-b border-red-100">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <i className="fas fa-trash-alt text-red-600 text-xl"></i>
              </div>
            </div>
            <div className="mr-4">
              <h3 className="text-lg font-semibold text-red-900">حذف الجلسة</h3>
              <p className="text-sm text-red-700">
                هل أنت متأكد من حذف هذه الجلسة؟
              </p>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-4">
          {/* Session Info */}
          {session && (
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <div className="flex items-start">
                <i className="fas fa-video text-blue-500 mt-1 ml-3"></i>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 mb-1">
                    {session.title}
                  </h4>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div className="flex items-center">
                      <i className="fas fa-book text-xs ml-2 w-4"></i>
                      <span>{session.subject}</span>
                    </div>
                    <div className="flex items-center">
                      <i className="fas fa-calendar text-xs ml-2 w-4"></i>
                      <span>
                        {new Date(
                          session.scheduled_datetime
                        ).toLocaleDateString("ar-SA")}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Warning Message */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <div className="flex items-start">
              <i className="fas fa-exclamation-triangle text-red-500 mt-0.5 ml-2"></i>
              <div className="text-sm text-red-800">
                <p className="font-medium mb-2">
                  تحذير: هذا الإجراء لا يمكن التراجع عنه!
                </p>
                <p>سيتم حذف الجلسة نهائياً من النظام.</p>
              </div>
            </div>
          </div>

          {/* Consequences */}
          <div className="space-y-2 mb-4">
            <p className="text-sm font-medium text-gray-700">
              ماذا سيحدث عند الحذف:
            </p>
            <ul className="space-y-2">
              <li className="flex items-start text-sm text-gray-600">
                <i className="fas fa-times-circle text-red-500 mt-0.5 ml-2"></i>
                <span>سيتم حذف الجلسة من قائمة الجلسات</span>
              </li>
              <li className="flex items-start text-sm text-gray-600">
                <i className="fas fa-times-circle text-red-500 mt-0.5 ml-2"></i>
                <span>سيتم إلغاء تسجيل جميع الطلاب المسجلين</span>
              </li>
              <li className="flex items-start text-sm text-gray-600">
                <i className="fas fa-times-circle text-red-500 mt-0.5 ml-2"></i>
                <span>لن يتمكن أحد من الوصول إلى رابط الجلسة</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 flex justify-end space-x-3 rounded-b-lg">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            إلغاء
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors mr-3"
          >
            <i className="fas fa-trash-alt ml-2"></i>
            حذف الجلسة
          </button>
        </div>
      </div>
    </div>
  );
};

ConfirmDeleteSessionModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  session: PropTypes.object,
};

export default ConfirmDeleteSessionModal;
