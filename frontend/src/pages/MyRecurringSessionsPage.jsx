import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../config/api";
import toast from "react-hot-toast";

const MyRecurringSessionsPage = () => {
  const { currentUser } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("ACTIVE");

  useEffect(() => {
    loadMySessions();
  }, []);

  const loadMySessions = async () => {
    try {
      setLoading(true);
      console.log("DEBUG: Loading my sessions...");
      const response = await apiRequest("/api/recurring-sessions/my-sessions/");

      console.log("DEBUG: Response status:", response.status);

      if (response.ok) {
        const data = await response.json();
        console.log("DEBUG: Received data:", data);
        setSessions(data);
      } else {
        console.error("Failed to load sessions. Status:", response.status);
        const errorText = await response.text();
        console.error("Error response:", errorText);
        setSessions([]);
      }
    } catch (error) {
      console.error("Error loading sessions:", error);
      toast.error("فشل في تحميل الجلسات");
      setSessions([]);
    } finally {
      setLoading(false);
    }
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

  const getFilteredSessions = () => {
    return sessions.filter((session) => session.status === activeTab);
  };

  const getTabCount = (status) => {
    return sessions.filter((s) => s.status === status).length;
  };

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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">جاري تحميل الجلسات...</p>
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
                  جلساتي المتكررة
                </h1>
                <p className="text-sm text-gray-500">
                  الجلسات المعينة لك من قبل المستشار
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={loadMySessions}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
                title="تحديث"
              >
                <i className="fas fa-sync-alt"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        {sessions.length > 0 && (
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
                  الجلسات النشطة
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
                  الجلسات المتوقفة
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
                  الجلسات المنتهية
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
        )}

        {sessions.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i className="fas fa-calendar-alt text-3xl text-gray-400"></i>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              لا توجد جلسات معينة
            </h3>
            <p className="text-gray-500 mb-6">
              لم يتم تعيين أي جلسات متكررة لك بعد. تواصل مع مستشارك الأكاديمي.
            </p>
          </div>
        ) : getFilteredSessions().length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i className="fas fa-calendar-alt text-2xl text-gray-400"></i>
            </div>
            <p className="text-gray-600">
              لا توجد جلسات{" "}
              {activeTab === "ACTIVE"
                ? "نشطة"
                : activeTab === "PAUSED"
                ? "متوقفة"
                : "منتهية"}
            </p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {getFilteredSessions().map((session) => (
              <div
                key={session.id}
                className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-all duration-200"
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {session.title}
                        </h3>
                        {getStatusBadge(session.status)}
                      </div>

                      {session.description && (
                        <p className="text-gray-600 text-sm mb-3">
                          {session.description}
                        </p>
                      )}
                    </div>

                    <div className="flex-shrink-0 ml-4">
                      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <i className="fas fa-calendar-alt text-xl text-blue-600"></i>
                      </div>
                    </div>
                  </div>

                  {/* Session Info */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="space-y-2">
                      <div className="flex items-center text-sm text-gray-600">
                        <i className="fas fa-book mr-2 text-blue-500 w-4"></i>
                        <span>{session.subject}</span>
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <i className="fas fa-graduation-cap mr-2 text-green-500 w-4"></i>
                        <span>الصف {session.level}</span>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center text-sm text-gray-600">
                        <i className="fas fa-calendar mr-2 text-purple-500 w-4"></i>
                        <span>{session.day_of_week_display}</span>
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <i className="fas fa-clock mr-2 text-orange-500 w-4"></i>
                        <span>
                          {formatTime(session.start_time)} (
                          {session.duration_minutes} دقيقة)
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Teacher Info */}
                  <div className="bg-gray-50 rounded-lg p-3 mb-4">
                    <div className="flex items-center text-sm">
                      <i className="fas fa-user-tie mr-2 text-indigo-500"></i>
                      <span className="font-medium">المدرس:</span>
                      <span className="ml-2">{session.teacher_name}</span>
                    </div>
                  </div>

                  {/* Next Session */}
                  {session.status === "ACTIVE" &&
                    session.next_generation_date && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <div className="flex items-center">
                          <i className="fas fa-calendar-plus text-blue-500 mr-2"></i>
                          <div>
                            <div className="text-sm font-medium text-blue-900">
                              الجلسة القادمة
                            </div>
                            <div className="text-sm text-blue-700">
                              {formatDate(session.next_generation_date)}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyRecurringSessionsPage;
