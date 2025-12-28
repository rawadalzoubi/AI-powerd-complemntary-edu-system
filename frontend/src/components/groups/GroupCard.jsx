import React from "react";
import PropTypes from "prop-types";

const GroupCard = ({ group, onEdit, onDelete }) => {
  const studentCount = group.student_count || group.students?.length || 0;
  const isIndividual = group.name?.startsWith("Individual -");

  return (
    <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center">
            <div
              className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                isIndividual ? "bg-gray-100" : "bg-purple-100"
              }`}
            >
              <i
                className={`fas ${isIndividual ? "fa-user" : "fa-users"} ${
                  isIndividual ? "text-gray-600" : "text-purple-600"
                }`}
              ></i>
            </div>
            <div className="ml-3">
              <h3 className="font-semibold text-gray-900 line-clamp-1">
                {group.name}
              </h3>
              <span
                className={`text-xs px-2 py-0.5 rounded-full ${
                  group.is_active
                    ? "bg-green-100 text-green-700"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                {group.is_active ? "نشطة" : "غير نشطة"}
              </span>
            </div>
          </div>

          {!isIndividual && (
            <div className="flex items-center space-x-1">
              <button
                onClick={onEdit}
                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="تعديل"
              >
                <i className="fas fa-edit text-sm"></i>
              </button>
              <button
                onClick={onDelete}
                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="حذف"
              >
                <i className="fas fa-trash text-sm"></i>
              </button>
            </div>
          )}
        </div>

        {/* Description */}
        {group.description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">
            {group.description}
          </p>
        )}

        {/* Stats */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center text-sm text-gray-600">
            <i className="fas fa-user-graduate mr-2"></i>
            <span>{studentCount} طالب</span>
          </div>

          {group.template_assignments_count > 0 && (
            <div className="flex items-center text-sm text-blue-600">
              <i className="fas fa-calendar-alt mr-2"></i>
              <span>{group.template_assignments_count} قالب</span>
            </div>
          )}
        </div>

        {/* Students Preview */}
        {group.students && group.students.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-xs text-gray-500 mb-2">الطلاب:</p>
            <div className="flex flex-wrap gap-1">
              {group.students.slice(0, 3).map((student, idx) => (
                <span
                  key={student.id || idx}
                  className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                >
                  {student.first_name} {student.last_name}
                </span>
              ))}
              {group.students.length > 3 && (
                <span className="text-xs bg-gray-100 text-gray-500 px-2 py-1 rounded">
                  +{group.students.length - 3} آخرين
                </span>
              )}
            </div>
          </div>
        )}

        {/* Individual Group Badge */}
        {isIndividual && (
          <div className="mt-4 pt-4 border-t">
            <span className="text-xs text-gray-500">
              <i className="fas fa-info-circle mr-1"></i>
              مجموعة فردية (تم إنشاؤها تلقائياً)
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

GroupCard.propTypes = {
  group: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
    is_active: PropTypes.bool,
    student_count: PropTypes.number,
    students: PropTypes.array,
    template_assignments_count: PropTypes.number,
  }).isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};

export default GroupCard;
