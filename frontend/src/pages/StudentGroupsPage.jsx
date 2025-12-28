import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../config/api";
import toast from "react-hot-toast";
import CreateGroupModal from "../components/groups/CreateGroupModal";
import EditGroupModal from "../components/groups/EditGroupModal";
import GroupCard from "../components/groups/GroupCard";

const StudentGroupsPage = () => {
  const { currentUser } = useAuth();
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingGroup, setEditingGroup] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    loadGroups();
  }, [refreshTrigger]);

  const loadGroups = async () => {
    try {
      setLoading(true);
      const response = await apiRequest("/api/recurring-sessions/groups/");
      if (response.ok) {
        const data = await response.json();
        setGroups(Array.isArray(data) ? data : []);
      } else {
        toast.error("فشل في تحميل المجموعات");
        setGroups([]);
      }
    } catch (error) {
      console.error("Error loading groups:", error);
      toast.error("فشل في تحميل المجموعات");
      setGroups([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSuccess = () => {
    setShowCreateModal(false);
    setRefreshTrigger((prev) => prev + 1);
    toast.success("تم إنشاء المجموعة بنجاح");
  };

  const handleEditSuccess = () => {
    setEditingGroup(null);
    setRefreshTrigger((prev) => prev + 1);
    toast.success("تم تحديث المجموعة بنجاح");
  };

  const handleDeleteGroup = async (groupId) => {
    if (!confirm("هل أنت متأكد من حذف هذه المجموعة؟")) return;

    try {
      const response = await apiRequest(
        `/api/recurring-sessions/groups/${groupId}/`,
        {
          method: "DELETE",
        }
      );
      if (response.ok) {
        toast.success("تم حذف المجموعة بنجاح");
        setRefreshTrigger((prev) => prev + 1);
      } else {
        toast.error("فشل في حذف المجموعة");
      }
    } catch (error) {
      console.error("Error deleting group:", error);
      toast.error("فشل في حذف المجموعة");
    }
  };

  const getUserRole = () => currentUser?.role?.toUpperCase() || "";

  const filteredGroups = groups.filter(
    (group) =>
      group.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      group.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Only advisors can access this page
  if (getUserRole() !== "ADVISOR") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <i className="fas fa-ban text-2xl text-red-600"></i>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            غير مصرح لك بالوصول
          </h2>
          <p className="text-gray-600">هذه الصفحة متاحة للمستشارين فقط</p>
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
                <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                  <i className="fas fa-users text-white text-sm"></i>
                </div>
              </div>
              <div className="ml-4">
                <h1 className="text-xl font-semibold text-gray-900">
                  مجموعات الطلاب
                </h1>
                <p className="text-sm text-gray-500">
                  إنشاء وإدارة مجموعات الطلاب للجلسات المتكررة
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
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center"
              >
                <i className="fas fa-plus mr-2"></i>
                إنشاء مجموعة جديدة
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <i className="fas fa-layer-group text-purple-600"></i>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">
                  إجمالي المجموعات
                </p>
                <p className="text-2xl font-semibold text-gray-900">
                  {groups.length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <i className="fas fa-user-graduate text-blue-600"></i>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">
                  إجمالي الطلاب
                </p>
                <p className="text-2xl font-semibold text-gray-900">
                  {groups.reduce(
                    (sum, g) =>
                      sum + (g.student_count || g.students?.length || 0),
                    0
                  )}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <i className="fas fa-check-circle text-green-600"></i>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">
                  المجموعات النشطة
                </p>
                <p className="text-2xl font-semibold text-gray-900">
                  {groups.filter((g) => g.is_active).length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <input
              type="text"
              placeholder="البحث في المجموعات..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full md:w-96 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          </div>
        </div>

        {/* Groups List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
            <p className="text-gray-600 mt-4">جاري التحميل...</p>
          </div>
        ) : filteredGroups.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow-sm border">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i className="fas fa-users text-2xl text-gray-400"></i>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchTerm ? "لا توجد نتائج" : "لا توجد مجموعات"}
            </h3>
            <p className="text-gray-600 mb-4">
              {searchTerm
                ? "جرب البحث بكلمات مختلفة"
                : "ابدأ بإنشاء مجموعة جديدة للطلاب"}
            </p>
            {!searchTerm && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <i className="fas fa-plus mr-2"></i>
                إنشاء مجموعة جديدة
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredGroups.map((group) => (
              <GroupCard
                key={group.id}
                group={group}
                onEdit={() => setEditingGroup(group)}
                onDelete={() => handleDeleteGroup(group.id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
      {showCreateModal && (
        <CreateGroupModal
          isOpen={true}
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleCreateSuccess}
        />
      )}

      {editingGroup && (
        <EditGroupModal
          isOpen={true}
          onClose={() => setEditingGroup(null)}
          group={editingGroup}
          onSuccess={handleEditSuccess}
        />
      )}
    </div>
  );
};

export default StudentGroupsPage;
