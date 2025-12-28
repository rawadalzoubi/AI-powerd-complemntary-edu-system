import { useState, useEffect } from "react";
import PropTypes from "prop-types";

const LiveSessionPopup = ({ isOpen, onClose, meetingUrl, sessionTitle }) => {
  const [popupWindow, setPopupWindow] = useState(null);
  const [isPopupBlocked, setIsPopupBlocked] = useState(false);

  useEffect(() => {
    if (isOpen && meetingUrl) {
      openPopup();
    }

    return () => {
      if (popupWindow && !popupWindow.closed) {
        popupWindow.close();
      }
    };
  }, [isOpen, meetingUrl]);

  const openPopup = () => {
    const popupFeatures =
      "width=1200,height=800,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no,status=no,left=100,top=100";

    try {
      const popup = window.open(meetingUrl, "LiveSession", popupFeatures);

      if (popup) {
        setPopupWindow(popup);
        popup.focus();

        // Monitor popup window
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed);
            onClose();
          }
        }, 1000);

        setIsPopupBlocked(false);
      } else {
        setIsPopupBlocked(true);
      }
    } catch (error) {
      console.error("Error opening popup:", error);
      setIsPopupBlocked(true);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(meetingUrl);
      alert("تم نسخ رابط الجلسة إلى الحافظة");
    } catch (error) {
      console.error("Failed to copy:", error);
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = meetingUrl;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      alert("تم نسخ رابط الجلسة إلى الحافظة");
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Success Modal */}
      {!isPopupBlocked && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <i className="fas fa-video text-2xl text-green-600"></i>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                تم فتح الجلسة المباشرة
              </h3>

              <p className="text-gray-600 mb-4">{sessionTitle}</p>

              <p className="text-sm text-gray-500 mb-6">
                تم فتح الجلسة في نافذة منفصلة. إذا لم تظهر النافذة، تأكد من
                السماح للنوافذ المنبثقة.
              </p>

              <div className="flex space-x-3">
                <button
                  onClick={onClose}
                  className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
                >
                  إغلاق
                </button>
                <button
                  onClick={() => {
                    if (popupWindow && !popupWindow.closed) {
                      popupWindow.focus();
                    } else {
                      openPopup();
                    }
                  }}
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  <i className="fas fa-external-link-alt mr-2"></i>
                  فتح الجلسة
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Popup Blocked Modal */}
      {isPopupBlocked && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <i className="fas fa-exclamation-triangle text-2xl text-orange-600"></i>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                تم حظر النافذة المنبثقة
              </h3>

              <p className="text-gray-600 mb-4">
                المتصفح منع فتح النافذة المنبثقة. يرجى نسخ الرابط أدناه والدخول
                يدوياً.
              </p>

              <div className="bg-gray-50 p-3 rounded-lg mb-4 text-left">
                <p className="text-sm text-gray-700 break-all font-mono">
                  {meetingUrl}
                </p>
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={onClose}
                  className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
                >
                  إغلاق
                </button>
                <button
                  onClick={copyToClipboard}
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  <i className="fas fa-copy mr-2"></i>
                  نسخ الرابط
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

LiveSessionPopup.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  meetingUrl: PropTypes.string,
  sessionTitle: PropTypes.string,
};

export default LiveSessionPopup;
