import React from "react";
import PropTypes from "prop-types";
import TemplateCard from "./TemplateCard";

const TemplateList = ({ templates, loading, onTemplateAction, userRole }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">جاري تحميل القوالب...</p>
        </div>
      </div>
    );
  }

  if (templates.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <i className="fas fa-calendar-alt text-3xl text-gray-400"></i>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          لا توجد قوالب جلسات
        </h3>
        <p className="text-gray-500 mb-6">
          ابدأ بإنشاء قالب جلسة متكررة لتوفير الوقت في إنشاء الجلسات الأسبوعية
        </p>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <i className="fas fa-lightbulb text-blue-500 text-lg"></i>
            </div>
            <div className="ml-3 text-right">
              <h4 className="text-sm font-medium text-blue-900 mb-1">
                💡 نصيحة
              </h4>
              <p className="text-sm text-blue-700">
                القوالب تساعدك في إنشاء جلسات متكررة تلقائياً. أنشئ قالب واحد
                وسيتم إنشاء الجلسات كل أسبوع!
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Templates Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {templates.map((template) => (
          <TemplateCard
            key={template.id}
            template={template}
            onAction={onTemplateAction}
            userRole={userRole}
          />
        ))}
      </div>

      {/* Summary */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">ملخص القوالب</h3>
            <p className="text-sm text-gray-500">
              إجمالي {templates.length} قالب
            </p>
          </div>

          <div className="flex items-center space-x-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {templates.filter((t) => t.status === "ACTIVE").length}
              </div>
              <div className="text-xs text-gray-500">نشط</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {templates.filter((t) => t.status === "PAUSED").length}
              </div>
              <div className="text-xs text-gray-500">متوقف</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600">
                {templates.filter((t) => t.status === "ENDED").length}
              </div>
              <div className="text-xs text-gray-500">منتهي</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

TemplateList.propTypes = {
  templates: PropTypes.array.isRequired,
  loading: PropTypes.bool.isRequired,
  onTemplateAction: PropTypes.func.isRequired,
  userRole: PropTypes.string.isRequired,
};

export default TemplateList;
