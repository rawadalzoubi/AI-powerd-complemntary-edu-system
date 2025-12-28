import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import TemplateList from "../components/templates/TemplateList";
import CreateTemplateModal from "../components/templates/CreateTemplateModal";
import EditTemplateModal from "../components/templates/EditTemplateModal";
import AssignTemplateModal from "../components/templates/AssignTemplateModal";
import UnassignTemplateModal from "../components/templates/UnassignTemplateModal";
import ConfirmEndTemplateModal from "../components/templates/ConfirmEndTemplateModal";
import ConfirmPauseTemplateModal from "../components/templates/ConfirmPauseTemplateModal";
import { templateService } from "../services/templateService";
import toast from "react-hot-toast";

const TemplatesPage = () => {
  const { currentUser } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [assigningTemplate, setAssigningTemplate] = useState(null);
  const [unassigningTemplate, setUnassigningTemplate] = useState(null);
  const [endingTemplate, setEndingTemplate] = useState(null);
  const [pausingTemplate, setPausingTemplate] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [activeTab, setActiveTab] = useState("ACTIVE");

  useEffect(() => {
    loadTemplates();
  }, [refreshTrigger]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const data = await templateService.getTemplates();
      setTemplates(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error loading templates:", error);
      toast.error("فشل في تحميل القوالب");
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSuccess = () => {
    setShowCreateModal(false);
    setRefreshTrigger((prev) => prev + 1);
    toast.success("تم إنشاء القالب بنجاح");
  };

  const handleEditSuccess = () => {
    setEditingTemplate(null);
    setRefreshTrigger((prev) => prev + 1);
    toast.success("تم تحديث القالب بنجاح");
  };

  const handleAssignSuccess = () => {
    setAssigningTemplate(null);
    setRefreshTrigger((prev) => prev + 1);
    toast.success("تم تعيين القالب للمجموعات بنجاح");
  };

  const handleUnassignSuccess = () => {
    setUnassigningTemplate(null);
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleConfirmEnd = async () => {
    if (!endingTemplate) return;

    try {
      await templateService.endTemplate(endingTemplate.id);
      toast.success("تم إنهاء القالب نهائياً");
      setEndingTemplate(null);
      setRefreshTrigger((prev) => prev + 1);
    } catch (error) {
      console.error("Error ending template:", error);
      toast.error("فشل في إنهاء القالب");
    }
  };

  const handleConfirmPause = async () => {
    if (!pausingTemplate) return;

    try {
      await templateService.pauseTemplate(pausingTemplate.id);
      toast.success("تم إيقاف القالب مؤقتاً");
      setPausingTemplate(null);
      setRefreshTrigger((prev) => prev + 1);
    } catch (error) {
      console.error("Error pausing template:", error);
      toast.error("فشل في إيقاف القالب");
    }
  };

  const handleTemplateAction = async (template, action) => {
    try {
      let message = "";

      switch (action) {
        case "pause":
          setPausingTemplate(template);
          return;
        case "resume":
          await templateService.resumeTemplate(template.id);
          message = "تم استئناف القالب";
          break;
        case "end":
          setEndingTemplate(template);
          return;
        case "edit":
          setEditingTemplate(template);
          return;
        case "assign":
          setAssigningTemplate(template);
          return;
        case "unassign":
          setUnassigningTemplate(template);
          return;
        default:
          return;
      }

      toast.success(message);
      setRefreshTrigger((prev) => prev + 1);
    } catch (error) {
      console.error(`Error ${action} template:`, error);
      toast.error(
        `فشل في ${
          action === "pause"
            ? "إيقاف"
            : action === "resume"
            ? "استئناف"
            : "إنهاء"
        } القالب`
      );
    }
  };

  const getUserRole = () => {
    return currentUser?.role?.toUpperCase() || "";
  };

  const getFilteredTemplates = () => {
    return templates.filter((template) => template.status === activeTab);
  };

  const getTabCount = (status) => {
    return templates.filter((t) => t.status === status).length;
  };

  // Only teachers and advisors can access templates
  const allowedRoles = ["TEACHER", "ADVISOR"];
  if (!allowedRoles.includes(getUserRole())) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <i className="fas fa-ban text-2xl text-red-600"></i>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            غير مصرح لك بالوصول
          </h2>
          <p className="text-gray-600">
            هذه الصفحة متاحة للمدرسين والمستشارين فقط
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <i className="fas fa-calendar-alt text-white text-sm"></i>
                </div>
              </div>
              <div className="ml-4">
                <h1 className="text-xl font-semibold text-gray-900">
                  قوالب الجلسات المتكررة
                </h1>
                <p className="text-sm text-gray-500">
                  إنشاء وإدارة قوالب الجلسات الأسبوعية والشهرية
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => setRefreshTrigger((prev) => prev + 1)}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
                title="تحديث"
              >
                <i className="fas fa-sync-alt"></i>
              </button>

              {getUserRole() === "TEACHER" && (
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center"
                >
                  <i className="fas fa-plus mr-2"></i>
                  إنشاء قالب جديد
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              <button
                onClick={() => setActiveTab("ACTIVE")}
                className={`${
                  activeTab === "ACTIVE"
                    ? "border-green-500 text-green-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <i className="fas fa-play mr-2"></i>
                القوالب النشطة
                <span
                  className={`${
                    activeTab === "ACTIVE"
                      ? "bg-green-100 text-green-600"
                      : "bg-gray-100 text-gray-900"
                  } ml-3 py-0.5 px-2.5 rounded-full text-xs font-medium`}
                >
                  {getTabCount("ACTIVE")}
                </span>
              </button>

              <button
                onClick={() => setActiveTab("PAUSED")}
                className={`${
                  activeTab === "PAUSED"
                    ? "border-yellow-500 text-yellow-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <i className="fas fa-pause mr-2"></i>
                القوالب المتوقفة
                <span
                  className={`${
                    activeTab === "PAUSED"
                      ? "bg-yellow-100 text-yellow-600"
                      : "bg-gray-100 text-gray-900"
                  } ml-3 py-0.5 px-2.5 rounded-full text-xs font-medium`}
                >
                  {getTabCount("PAUSED")}
                </span>
              </button>

              <button
                onClick={() => setActiveTab("ENDED")}
                className={`${
                  activeTab === "ENDED"
                    ? "border-gray-500 text-gray-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <i className="fas fa-stop mr-2"></i>
                القوالب المنتهية
                <span
                  className={`${
                    activeTab === "ENDED"
                      ? "bg-gray-200 text-gray-600"
                      : "bg-gray-100 text-gray-900"
                  } ml-3 py-0.5 px-2.5 rounded-full text-xs font-medium`}
                >
                  {getTabCount("ENDED")}
                </span>
              </button>
            </nav>
          </div>
        </div>

        {/* Quick Stats */}
        {templates.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <i className="fas fa-calendar-alt text-blue-600 text-sm"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">
                    إجمالي القوالب
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {templates.length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                    <i className="fas fa-play text-green-600 text-sm"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">
                    القوالب النشطة
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {templates.filter((t) => t.status === "ACTIVE").length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <i className="fas fa-pause text-yellow-600 text-sm"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">
                    القوالب المتوقفة
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {templates.filter((t) => t.status === "PAUSED").length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                    <i className="fas fa-chart-line text-purple-600 text-sm"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">
                    الجلسات المولدة
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {templates.reduce(
                      (sum, t) => sum + (t.total_generated || 0),
                      0
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Templates List */}
        <TemplateList
          templates={getFilteredTemplates()}
          loading={loading}
          onTemplateAction={handleTemplateAction}
          userRole={getUserRole()}
        />
      </div>

      {/* Modals */}
      {showCreateModal && (
        <CreateTemplateModal
          isOpen={true}
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleCreateSuccess}
        />
      )}

      {editingTemplate && (
        <EditTemplateModal
          isOpen={true}
          onClose={() => setEditingTemplate(null)}
          template={editingTemplate}
          onSuccess={handleEditSuccess}
        />
      )}

      {assigningTemplate && (
        <AssignTemplateModal
          isOpen={true}
          onClose={() => setAssigningTemplate(null)}
          template={assigningTemplate}
          onSuccess={handleAssignSuccess}
        />
      )}

      {unassigningTemplate && (
        <UnassignTemplateModal
          isOpen={true}
          onClose={() => setUnassigningTemplate(null)}
          template={unassigningTemplate}
          onSuccess={handleUnassignSuccess}
        />
      )}

      {endingTemplate && (
        <ConfirmEndTemplateModal
          isOpen={true}
          onClose={() => setEndingTemplate(null)}
          onConfirm={handleConfirmEnd}
          template={endingTemplate}
        />
      )}

      {pausingTemplate && (
        <ConfirmPauseTemplateModal
          isOpen={true}
          onClose={() => setPausingTemplate(null)}
          onConfirm={handleConfirmPause}
          template={pausingTemplate}
        />
      )}
    </div>
  );
};

export default TemplatesPage;
