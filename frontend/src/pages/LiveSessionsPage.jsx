import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import SessionCreationForm from "../components/sessions/SessionCreationForm";
import SessionList from "../components/sessions/SessionList";
import SessionCard from "../components/sessions/SessionCard";
import AssignSessionModal from "../components/sessions/AssignSessionModal";
import SessionDetailsModal from "../components/sessions/SessionDetailsModal";
import ManageAssignmentsModal from "../components/sessions/ManageAssignmentsModal";
import ConfirmDeleteSessionModal from "../components/sessions/ConfirmDeleteSessionModal";
import { sessionService } from "../services/sessionService";
import toast from "react-hot-toast";

const LiveSessionsPage = () => {
  const { currentUser } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingSession, setEditingSession] = useState(null);
  const [assigningSession, setAssigningSession] = useState(null);
  const [viewingSession, setViewingSession] = useState(null);
  const [managingSession, setManagingSession] = useState(null);
  const [deletingSession, setDeletingSession] = useState(null);
  const [viewMode, setViewMode] = useState("list"); // 'list' or 'cards'
  const [activeTab, setActiveTab] = useState("active"); // 'active', 'completed', 'cancelled'
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    console.log("DEBUG: useEffect triggered, refreshTrigger:", refreshTrigger);
    loadSessions();
  }, [refreshTrigger]);

  // Auto-refresh for students to see newly assigned sessions
  useEffect(() => {
    if (getUserRole() === "STUDENT") {
      const interval = setInterval(() => {
        loadSessions(true); // Show notifications for auto-refresh
      }, 30000); // Refresh every 30 seconds for students

      return () => clearInterval(interval);
    }
  }, [sessions]);

  const loadSessions = async (showNotification = false) => {
    try {
      setLoading(true);
      let data;

      const role = getUserRole();
      console.log("DEBUG: Loading sessions for role:", role);

      if (role === "STUDENT") {
        data = await sessionService.getMySchedule();
      } else if (role === "ADVISOR") {
        // Advisors might want to see both pending and assigned sessions
        data = await sessionService.getSessions();
      } else {
        // Teachers see their own sessions
        data = await sessionService.getSessions();
      }

      console.log("DEBUG: Received data:", data);

      const newSessions = Array.isArray(data) ? data : data.results || [];

      // Check for new sessions for students
      if (role === "STUDENT" && showNotification && sessions.length > 0) {
        const newSessionIds = newSessions.map((s) => s.id);
        const oldSessionIds = sessions.map((s) => s.id);
        const addedSessions = newSessions.filter(
          (s) => !oldSessionIds.includes(s.id)
        );

        if (addedSessions.length > 0) {
          addedSessions.forEach((session) => {
            toast.success(`New session assigned: ${session.title}`, {
              duration: 5000,
            });
          });
        }
      }

      console.log("DEBUG: Setting sessions:", newSessions);
      setSessions(newSessions);
    } catch (error) {
      console.error("Error loading sessions:", error);
      toast.error("Failed to load sessions");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSession = async (sessionData) => {
    try {
      console.log("DEBUG: Creating session with data:", sessionData);
      const result = await sessionService.createSession(sessionData);
      console.log("DEBUG: Session created successfully:", result);
      toast.success("Session created successfully!");
      console.log("DEBUG: Triggering refresh...");
      setRefreshTrigger((prev) => prev + 1);
    } catch (error) {
      console.error("Error creating session:", error);
      throw error; // Re-throw to let the form handle the error
    }
  };

  const handleEditSession = async (sessionData) => {
    try {
      await sessionService.updateSession(editingSession.id, sessionData);
      toast.success("Session updated successfully!");
      setEditingSession(null);
      setRefreshTrigger((prev) => prev + 1);
    } catch (error) {
      console.error("Error updating session:", error);
      throw error;
    }
  };

  const handleDeleteSession = (session) => {
    setDeletingSession(session);
  };

  const confirmDeleteSession = async () => {
    try {
      await sessionService.cancelSession(deletingSession.id);
      toast.success("تم حذف الجلسة بنجاح!");
      setDeletingSession(null);
      setRefreshTrigger((prev) => prev + 1);
    } catch (error) {
      console.error("Error cancelling session:", error);
      toast.error("فشل في حذف الجلسة");
    }
  };

  const handleJoinSession = async (session) => {
    console.log("DEBUG: handleJoinSession called with session:", session);
    try {
      console.log("DEBUG: Attempting to join session:", session);
      const joinData = await sessionService.joinSession(session.id);
      console.log("DEBUG: Join response:", joinData);
      console.log("DEBUG: joinData.meeting_url:", joinData.meeting_url);
      console.log("DEBUG: typeof joinData:", typeof joinData);
      console.log("DEBUG: Object.keys(joinData):", Object.keys(joinData));

      // Open Jitsi meeting in new window/tab
      if (joinData.meeting_url) {
        console.log("DEBUG: Opening meeting URL:", joinData.meeting_url);

        // Simple solution: show URL and let user click
        alert(
          `Meeting URL: ${joinData.meeting_url}\n\nClick OK then manually open this link in a new tab.`
        );

        // Also try to open automatically
        window.open(joinData.meeting_url, "_blank");

        toast.success(`Meeting URL ready: ${joinData.meeting_url}`);
      } else {
        console.error("DEBUG: No meeting URL in response");
        toast.error("Unable to get meeting URL");
      }
    } catch (error) {
      console.error("Error joining session:", error);
      if (error.response?.data?.error) {
        toast.error(error.response.data.error);
      } else {
        toast.error("Failed to join session");
      }
    }
  };

  const handleViewDetails = (session) => {
    console.log("View details for session:", session);
    setViewingSession(session);
  };

  const handleAssignSession = (session) => {
    setAssigningSession(session);
  };

  const handleAssignSuccess = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleManageAssignments = (session) => {
    setManagingSession(session);
  };

  // Filter sessions based on active tab
  const getFilteredSessions = () => {
    switch (activeTab) {
      case "active":
        return sessions.filter((session) =>
          ["PENDING", "ASSIGNED", "ACTIVE"].includes(session.status)
        );
      case "completed":
        return sessions.filter((session) => session.status === "COMPLETED");
      case "cancelled":
        return sessions.filter((session) => session.status === "CANCELLED");
      default:
        return sessions;
    }
  };

  // Get tab counts
  const getTabCounts = () => {
    return {
      active: sessions.filter((session) =>
        ["PENDING", "ASSIGNED", "ACTIVE"].includes(session.status)
      ).length,
      completed: sessions.filter((session) => session.status === "COMPLETED")
        .length,
      cancelled: sessions.filter((session) => session.status === "CANCELLED")
        .length,
    };
  };

  const tabCounts = getTabCounts();
  const filteredSessions = getFilteredSessions();

  const getUserRole = () => {
    return currentUser?.role?.toUpperCase() || "";
  };

  const getPageTitle = () => {
    const role = getUserRole();
    switch (role) {
      case "TEACHER":
        return "My Live Sessions";
      case "ADVISOR":
        return "Manage Live Sessions";
      case "STUDENT":
        return "My Schedule";
      default:
        return "Live Sessions";
    }
  };

  const getPageDescription = () => {
    const role = getUserRole();
    switch (role) {
      case "TEACHER":
        return "Create and manage your live teaching sessions";
      case "ADVISOR":
        return "Assign live sessions to students and monitor attendance";
      case "STUDENT":
        return "View and join your assigned live sessions";
      default:
        return "Manage live sessions";
    }
  };

  // Debug: Check user role
  console.log("Current User:", currentUser);
  console.log("User Role:", currentUser?.role);
  console.log("Normalized Role:", getUserRole());

  const canCreateSessions = getUserRole() === "TEACHER";
  const showAsCards = getUserRole() === "STUDENT" || viewMode === "cards";

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <i className="fas fa-video mr-3 text-blue-600"></i>
                {getPageTitle()}
              </h1>
              <p className="mt-2 text-gray-600">{getPageDescription()}</p>
            </div>

            <div className="flex items-center space-x-3">
              {/* View Mode Toggle (for non-students) */}
              {getUserRole() !== "STUDENT" && (
                <div className="flex items-center bg-white rounded-lg border p-1">
                  <button
                    onClick={() => setViewMode("list")}
                    className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                      viewMode === "list"
                        ? "bg-blue-100 text-blue-700"
                        : "text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    <i className="fas fa-list mr-1"></i>
                    List
                  </button>
                  <button
                    onClick={() => setViewMode("cards")}
                    className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                      viewMode === "cards"
                        ? "bg-blue-100 text-blue-700"
                        : "text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    <i className="fas fa-th-large mr-1"></i>
                    Cards
                  </button>
                </div>
              )}

              {/* Create Session Button */}
              {canCreateSessions && (
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center"
                >
                  <i className="fas fa-plus mr-2"></i>
                  Create Session
                </button>
              )}

              {/* Refresh Button */}
              <button
                onClick={() => setRefreshTrigger((prev) => prev + 1)}
                className="bg-white hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg border font-medium transition-colors flex items-center"
                disabled={loading}
              >
                <i
                  className={`fas fa-sync-alt mr-2 ${
                    loading ? "animate-spin" : ""
                  }`}
                ></i>
                Refresh
                {getUserRole() === "STUDENT" && (
                  <span className="ml-2 text-xs text-green-600">
                    (Auto-updates)
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab("active")}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === "active"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <i className="fas fa-play-circle mr-2"></i>
                Active Sessions
                {tabCounts.active > 0 && (
                  <span className="ml-2 bg-blue-100 text-blue-600 py-0.5 px-2 rounded-full text-xs">
                    {tabCounts.active}
                  </span>
                )}
              </button>

              <button
                onClick={() => setActiveTab("completed")}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === "completed"
                    ? "border-green-500 text-green-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <i className="fas fa-check-circle mr-2"></i>
                Completed
                {tabCounts.completed > 0 && (
                  <span className="ml-2 bg-green-100 text-green-600 py-0.5 px-2 rounded-full text-xs">
                    {tabCounts.completed}
                  </span>
                )}
              </button>

              <button
                onClick={() => setActiveTab("cancelled")}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === "cancelled"
                    ? "border-red-500 text-red-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <i className="fas fa-times-circle mr-2"></i>
                Cancelled
                {tabCounts.cancelled > 0 && (
                  <span className="ml-2 bg-red-100 text-red-600 py-0.5 px-2 rounded-full text-xs">
                    {tabCounts.cancelled}
                  </span>
                )}
              </button>
            </nav>
          </div>
        </div>

        {/* Quick Stats (for teachers and advisors) */}
        {getUserRole() !== "STUDENT" && sessions.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <i className="fas fa-video text-blue-600"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">
                    Total Sessions
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {sessions.length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                    <i className="fas fa-clock text-yellow-600"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Pending</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {sessions.filter((s) => s.status === "PENDING").length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <i className="fas fa-play-circle text-green-600"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Active</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {sessions.filter((s) => s.status === "ACTIVE").length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                    <i className="fas fa-check-circle text-gray-600"></i>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Completed</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {sessions.filter((s) => s.status === "COMPLETED").length}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Sessions Display */}
        {showAsCards ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSessions.map((session) => (
              <SessionCard
                key={session.id}
                session={session}
                userRole={getUserRole()}
                onJoin={handleJoinSession}
                onViewDetails={handleViewDetails}
                showJoinButton={getUserRole() === "STUDENT"}
              />
            ))}
          </div>
        ) : (
          <SessionList
            sessions={filteredSessions}
            loading={loading}
            onEdit={setEditingSession}
            onDelete={handleDeleteSession}
            onViewDetails={handleViewDetails}
            onAssign={handleAssignSession}
            onJoin={handleJoinSession}
            onManageAssignments={handleManageAssignments}
            userRole={getUserRole()}
            showActions={true}
          />
        )}

        {/* Empty State */}
        {!loading && filteredSessions.length === 0 && (
          <div className="text-center py-12">
            <div className="mx-auto h-24 w-24 text-gray-400">
              <i
                className={`fas text-6xl ${
                  activeTab === "active"
                    ? "fa-video"
                    : activeTab === "completed"
                    ? "fa-check-circle"
                    : "fa-times-circle"
                }`}
              ></i>
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              {activeTab === "active" &&
                (getUserRole() === "STUDENT"
                  ? "No active sessions"
                  : "No active sessions")}
              {activeTab === "completed" && "No completed sessions"}
              {activeTab === "cancelled" && "No cancelled sessions"}
            </h3>
            <p className="mt-2 text-gray-500">
              {activeTab === "active" &&
                (getUserRole() === "STUDENT"
                  ? "Your advisor will assign live sessions to you."
                  : getUserRole() === "TEACHER"
                  ? "Create your first live session to get started."
                  : "No active sessions available to manage.")}
              {activeTab === "completed" &&
                "Completed sessions will appear here."}
              {activeTab === "cancelled" &&
                "Cancelled sessions will appear here."}
            </p>
            {canCreateSessions && activeTab === "active" && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center mx-auto"
              >
                <i className="fas fa-plus mr-2"></i>
                Create Your First Session
              </button>
            )}
          </div>
        )}
      </div>

      {/* Create/Edit Session Modal */}
      {(showCreateModal || editingSession) && (
        <SessionCreationForm
          isOpen={true}
          onClose={() => {
            setShowCreateModal(false);
            setEditingSession(null);
          }}
          onSave={editingSession ? handleEditSession : handleCreateSession}
          session={editingSession}
        />
      )}

      {/* Assign Session Modal */}
      {assigningSession && (
        <AssignSessionModal
          isOpen={true}
          onClose={() => setAssigningSession(null)}
          session={assigningSession}
          onAssignSuccess={handleAssignSuccess}
        />
      )}

      {/* Session Details Modal */}
      {viewingSession && (
        <SessionDetailsModal
          isOpen={true}
          onClose={() => setViewingSession(null)}
          session={viewingSession}
          userRole={getUserRole()}
        />
      )}

      {/* Manage Assignments Modal */}
      {managingSession && (
        <ManageAssignmentsModal
          isOpen={true}
          onClose={() => setManagingSession(null)}
          session={managingSession}
          onSuccess={handleAssignSuccess}
          userRole={getUserRole()}
        />
      )}

      {/* Delete Confirmation Modal */}
      {deletingSession && (
        <ConfirmDeleteSessionModal
          isOpen={true}
          onClose={() => setDeletingSession(null)}
          onConfirm={confirmDeleteSession}
          session={deletingSession}
        />
      )}
    </div>
  );
};

export default LiveSessionsPage;
