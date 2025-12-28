import React from "react";
import PropTypes from "prop-types";

const TemplateCard = ({ template, onAction, userRole }) => {
  const getStatusBadge = (status) => {
    const statusConfig = {
      ACTIVE: {
        color: "bg-green-100 text-green-800",
        icon: "fa-play",
        text: "نشط",
      },
      PAUSED: {
        color: "bg-yellow-100 text-yellow-800",
        icon: "fa-pause",
        text: "متوقف",
      },
      ENDED: {
        color: "bg-gray-100 text-gray-800",
        icon: "fa-stop",
        text: "منتهي",
      },
    };

    const config = statusConfig[status] || statusConfig["ACTIVE"];

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}
      >
        <i className={`fas ${config.icon} mr-1`}></i>
        {config.text}
      </span>
    );
  };

  const getRecurrenceDisplay = (type) => {
    const types = {
      WEEKLY: "أسبوعياً",
      BIWEEKLY: "كل أسبوعين",
      MONTHLY: "شهرياً",
    };
    return types[type] || type;
  };

  const formatTime = (timeString) => {
    if (!timeString) return "";
    const [hours, minutes] = timeString.split(":");
    return `${hours}:${minutes}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return "";
    return new Date(dateString).toLocaleDateString("ar-SA");
  };

  const getNextGenerationText = (nextDate) => {
    if (!nextDate) return "لا توجد جلسة قادمة";

    const next = new Date(nextDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time to start of day
    next.setHours(0, 0, 0, 0);

    const diffTime = next - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return "تاريخ في الماضي";
    if (diffDays === 0) return "اليوم";
    if (diffDays === 1) return "غداً";
    if (diffDays < 7) return `خلال ${diffDays} أيام`;

    return formatDate(nextDate);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-all duration-200">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
                {template.title}
              </h3>
              {getStatusBadge(template.status)}
            </div>

            {template.description && (
              <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                {template.description}
              </p>
            )}
          </div>

          {/* Template Icon */}
          <div className="flex-shrink-0 ml-4">
            <div
              className={`w-12 h-12 rounded-full flex items-center justify-center ${
                template.status === "ACTIVE"
                  ? "bg-green-100"
                  : template.status === "PAUSED"
                  ? "bg-yellow-100"
                  : "bg-gray-100"
              }`}
            >
              <i
                className={`fas fa-calendar-alt text-xl ${
                  template.status === "ACTIVE"
                    ? "text-green-600"
                    : template.status === "PAUSED"
                    ? "text-yellow-600"
                    : "text-gray-600"
                }`}
              ></i>
            </div>
          </div>
        </div>

        {/* Template Info */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="space-y-2">
            <div className="flex items-center text-sm text-gray-600">
              <i className="fas fa-book mr-2 text-blue-500 w-4"></i>
              <span>{template.subject}</span>
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <i className="fas fa-graduation-cap mr-2 text-green-500 w-4"></i>
              <span>الصف {template.level}</span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center text-sm text-gray-600">
              <i className="fas fa-calendar mr-2 text-purple-500 w-4"></i>
              <span>{template.day_of_week_display}</span>
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <i className="fas fa-clock mr-2 text-orange-500 w-4"></i>
              <span>
                {formatTime(template.start_time)} ({template.duration_minutes}{" "}
                دقيقة)
              </span>
            </div>
          </div>
        </div>

        {/* Recurrence Info */}
        <div className="bg-gray-50 rounded-lg p-3 mb-4">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center">
              <i className="fas fa-repeat mr-2 text-blue-500"></i>
              <span className="font-medium">
                {getRecurrenceDisplay(template.recurrence_type)}
              </span>
            </div>
            <div className="text-gray-600">
              {template.assigned_groups_count || 0} مجموعة مسندة
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-2 gap-4 mb-4 text-center">
          <div className="bg-blue-50 rounded-lg p-3">
            <div className="text-lg font-bold text-blue-600">
              {template.total_generated || 0}
            </div>
            <div className="text-xs text-blue-600">جلسة مولدة</div>
          </div>
          <div className="bg-green-50 rounded-lg p-3">
            <div className="text-lg font-bold text-green-600">
              {template.assigned_groups_count || 0}
            </div>
            <div className="text-xs text-green-600">مجموعة مسندة</div>
          </div>
        </div>

        {/* Next Generation */}
        {template.status === "ACTIVE" && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
            <div className="flex items-center">
              <i className="fas fa-calendar-plus text-blue-500 mr-2"></i>
              <div>
                <div className="text-sm font-medium text-blue-900">
                  الجلسة القادمة
                </div>
                <div className="text-sm text-blue-700">
                  {getNextGenerationText(template.next_generation_date)}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center space-x-2">
            {userRole === "ADVISOR" && (
              <>
                <button
                  onClick={() => onAction(template, "assign")}
                  className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-colors"
                  title="تعيين للطلاب"
                >
                  <i className="fas fa-user-plus"></i>
                </button>
                <button
                  onClick={() => onAction(template, "unassign")}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                  title="إلغاء تعيين الطلاب"
                >
                  <i className="fas fa-user-minus"></i>
                </button>
              </>
            )}

            {userRole === "TEACHER" && (
              <>
                <button
                  onClick={() => onAction(template, "edit")}
                  className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
                  title="تعديل القالب"
                >
                  <i className="fas fa-edit"></i>
                </button>

                {template.status === "ACTIVE" && (
                  <button
                    onClick={() => onAction(template, "pause")}
                    className="p-2 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded-full transition-colors"
                    title="إيقاف مؤقت"
                  >
                    <i className="fas fa-pause"></i>
                  </button>
                )}

                {template.status === "PAUSED" && (
                  <button
                    onClick={() => onAction(template, "resume")}
                    className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-full transition-colors"
                    title="استئناف"
                  >
                    <i className="fas fa-play"></i>
                  </button>
                )}

                {(template.status === "ACTIVE" ||
                  template.status === "PAUSED") && (
                  <button
                    onClick={() => onAction(template, "end")}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                    title="إنهاء نهائي"
                  >
                    <i className="fas fa-stop"></i>
                  </button>
                )}
              </>
            )}
          </div>

          <div className="text-xs text-gray-500">
            تم الإنشاء: {formatDate(template.created_at)}
          </div>
        </div>
      </div>
    </div>
  );
};

TemplateCard.propTypes = {
  template: PropTypes.object.isRequired,
  onAction: PropTypes.func.isRequired,
  userRole: PropTypes.string.isRequired,
};

export default TemplateCard;
