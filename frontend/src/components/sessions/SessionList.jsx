import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import LiveSessionPopup from "./LiveSessionPopup";
import JoinErrorModal from "./JoinErrorModal";

const SessionList = ({
  sessions = [],
  loading = false,
  onEdit,
  onDelete,
  onViewDetails,
  onAssign,
  onManageAssignments,
  userRole = "TEACHER",
  showActions = true,
}) => {
  const [filteredSessions, setFilteredSessions] = useState(sessions);
  const [filters, setFilters] = useState({
    status: "",
    subject: "",
    level: "",
    search: "",
  });
  const [popupData, setPopupData] = useState({
    isOpen: false,
    meetingUrl: "",
    sessionTitle: "",
  });
  const [errorData, setErrorData] = useState({
    isOpen: false,
    error: null,
    sessionTitle: "",
  });

  useEffect(() => {
    let filtered = sessions;

    // Apply filters
    if (filters.status) {
      filtered = filtered.filter(
        (session) => session.status === filters.status
      );
    }
    if (filters.subject) {
      filtered = filtered.filter((session) =>
        session.subject.toLowerCase().includes(filters.subject.toLowerCase())
      );
    }
    if (filters.level) {
      filtered = filtered.filter((session) => session.level === filters.level);
    }
    if (filters.search) {
      filtered = filtered.filter(
        (session) =>
          session.title.toLowerCase().includes(filters.search.toLowerCase()) ||
          session.description
            ?.toLowerCase()
            .includes(filters.search.toLowerCase())
      );
    }

    setFilteredSessions(filtered);
  }, [sessions, filters]);

  const handleFilterChange = (filterName, value) => {
    setFilters((prev) => ({
      ...prev,
      [filterName]: value,
    }));
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      PENDING: {
        color: "bg-yellow-100 text-yellow-800",
        icon: "fa-clock",
        text: "Pending",
      },
      ASSIGNED: {
        color: "bg-blue-100 text-blue-800",
        icon: "fa-user-check",
        text: "Assigned",
      },
      ACTIVE: {
        color: "bg-green-100 text-green-800",
        icon: "fa-play-circle",
        text: "Active",
      },
      COMPLETED: {
        color: "bg-gray-100 text-gray-800",
        icon: "fa-check-circle",
        text: "Completed",
      },
      CANCELLED: {
        color: "bg-red-100 text-red-800",
        icon: "fa-times-circle",
        text: "Cancelled",
      },
    };

    const config = statusConfig[status] || statusConfig["PENDING"];

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}
      >
        <i className={`fas ${config.icon} mr-1`}></i>
        {config.text}
      </span>
    );
  };

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return {
      date: date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      }),
      time: date.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
  };

  const canEdit = (session) => {
    return userRole === "TEACHER" && session.can_be_modified;
  };

  const canDelete = (session) => {
    return (
      userRole === "TEACHER" &&
      (session.status === "PENDING" || session.status === "ASSIGNED")
    );
  };

  const canAssign = (session) => {
    // Advisors can assign to PENDING sessions or add more students to ASSIGNED sessions
    return (
      userRole === "ADVISOR" &&
      (session.status === "PENDING" || session.status === "ASSIGNED")
    );
  };

  const canJoin = (session) => {
    console.log(
      "DEBUG: Checking canJoin for session:",
      session.title,
      "User role:",
      userRole,
      "Session status:",
      session.status
    );

    const now = new Date();
    const sessionStart = new Date(session.scheduled_datetime);
    const sessionEnd = new Date(
      sessionStart.getTime() + session.duration_minutes * 60000
    );

    if (userRole === "TEACHER") {
      // Teachers can join if session is not cancelled and hasn't ended
      if (session.status === "CANCELLED") {
        console.log("DEBUG: Teacher cannot join - session cancelled");
        return false;
      }

      if (now > sessionEnd) {
        console.log("DEBUG: Teacher cannot join - session ended");
        return false;
      }

      // Can join 15 minutes before start
      const joinWindow = new Date(sessionStart.getTime() - 15 * 60000);
      if (now >= joinWindow) {
        console.log("DEBUG: Teacher can join session");
        return true;
      }

      console.log("DEBUG: Teacher cannot join - too early");
      return false;
    }

    if (userRole === "STUDENT") {
      // Students can join assigned sessions within first 10 minutes
      if (session.status !== "ASSIGNED" && session.status !== "ACTIVE") {
        console.log("DEBUG: Student cannot join - session not assigned");
        return false;
      }

      // Can join from start until 10 minutes after start
      const lateJoinWindow = new Date(sessionStart.getTime() + 10 * 60000);

      if (now >= sessionStart && now <= lateJoinWindow) {
        console.log(
          "DEBUG: Student can join session - within late join window"
        );
        return true;
      }

      console.log("DEBUG: Student cannot join - outside join window");
      return false;
    }

    if (userRole === "ADVISOR") {
      console.log("DEBUG: Advisor cannot join sessions - management role only");
      return false;
    }

    console.log(
      "DEBUG: Cannot join session - unknown role or conditions not met"
    );
    return false;
  };

  const getJoinButtonText = (session) => {
    const now = new Date();
    const sessionStart = new Date(session.scheduled_datetime);
    const sessionEnd = new Date(
      sessionStart.getTime() + session.duration_minutes * 60000
    );

    if (userRole === "TEACHER") {
      if (now >= sessionStart && now <= sessionEnd) {
        return "Join Now (Live)";
      } else if (now < sessionStart) {
        const minutesUntil = Math.floor((sessionStart - now) / (1000 * 60));
        if (minutesUntil <= 15) {
          return `Join (Starts in ${minutesUntil}m)`;
        }
      }
      return "Join Session";
    }

    if (userRole === "STUDENT") {
      if (now >= sessionStart && now <= sessionEnd) {
        const lateJoinWindow = new Date(sessionStart.getTime() + 10 * 60000);
        if (now <= lateJoinWindow) {
          return "Join Now";
        } else {
          return "Late Join Closed";
        }
      } else if (now < sessionStart) {
        const minutesUntil = Math.floor((sessionStart - now) / (1000 * 60));
        return `Starts in ${minutesUntil}m`;
      }
      return "Session Ended";
    }

    return "Join Session";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading sessions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <i className="fas fa-search mr-1"></i>
              Search
            </label>
            <input
              type="text"
              placeholder="Search sessions..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.search}
              onChange={(e) => handleFilterChange("search", e.target.value)}
            />
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <i className="fas fa-filter mr-1"></i>
              Status
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.status}
              onChange={(e) => handleFilterChange("status", e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="ASSIGNED">Assigned</option>
              <option value="ACTIVE">Active</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>

          {/* Subject Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <i className="fas fa-book mr-1"></i>
              Subject
            </label>
            <input
              type="text"
              placeholder="Filter by subject..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.subject}
              onChange={(e) => handleFilterChange("subject", e.target.value)}
            />
          </div>

          {/* Grade Level Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <i className="fas fa-graduation-cap mr-1"></i>
              Grade
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.level}
              onChange={(e) => handleFilterChange("level", e.target.value)}
            >
              <option value="">All Grades</option>
              {[...Array(12)].map((_, i) => (
                <option key={i + 1} value={i + 1}>
                  Grade {i + 1}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Sessions List */}
      {filteredSessions.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto h-24 w-24 text-gray-400">
            <i className="fas fa-video text-6xl"></i>
          </div>
          <h3 className="mt-4 text-lg font-medium text-gray-900">
            No sessions found
          </h3>
          <p className="mt-2 text-gray-500">
            {sessions.length === 0
              ? "No sessions have been created yet."
              : "No sessions match your current filters."}
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredSessions.map((session) => {
            const { date, time } = formatDateTime(session.scheduled_datetime);

            return (
              <div
                key={session.id}
                className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {session.title}
                        </h3>
                        {getStatusBadge(session.status)}
                        {canJoin(session) &&
                          (() => {
                            const now = new Date();
                            const sessionStart = new Date(
                              session.scheduled_datetime
                            );
                            const sessionEnd = new Date(
                              sessionStart.getTime() +
                                session.duration_minutes * 60000
                            );

                            if (now >= sessionStart && now <= sessionEnd) {
                              return (
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 animate-pulse">
                                  <span className="w-2 h-2 bg-red-500 rounded-full mr-1"></span>
                                  LIVE
                                </span>
                              );
                            } else if (now < sessionStart) {
                              const minutesUntil = Math.floor(
                                (sessionStart - now) / (1000 * 60)
                              );
                              if (minutesUntil <= 15) {
                                return (
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                                    <i className="fas fa-clock mr-1"></i>
                                    Starting in {minutesUntil}m
                                  </span>
                                );
                              }
                            }
                            return null;
                          })()}
                      </div>

                      {session.description && (
                        <p className="text-gray-600 mb-3 line-clamp-2">
                          {session.description}
                        </p>
                      )}

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <i className="fas fa-book mr-2 text-blue-500"></i>
                          <span>{session.subject}</span>
                        </div>
                        <div className="flex items-center">
                          <i className="fas fa-graduation-cap mr-2 text-green-500"></i>
                          <span>Grade {session.level}</span>
                        </div>
                        <div className="flex items-center">
                          <i className="fas fa-calendar mr-2 text-purple-500"></i>
                          <span>{date}</span>
                        </div>
                        <div className="flex items-center">
                          <i className="fas fa-clock mr-2 text-orange-500"></i>
                          <span>
                            {time} ({session.duration_minutes}min)
                          </span>
                        </div>
                      </div>

                      {userRole === "TEACHER" && (
                        <div className="mt-3 text-sm text-gray-500">
                          <i className="fas fa-users mr-1"></i>
                          {session.assigned_students_count || 0} students
                          assigned
                        </div>
                      )}

                      {/* Join Button - Only for Teachers and Students */}
                      {userRole !== "ADVISOR" && (
                        <div className="mt-3">
                          <button
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              console.log(
                                "DEBUG: Join button clicked for session:",
                                session.title
                              );

                              // Direct call to sessionService instead of relying on props
                              const joinSession = async () => {
                                try {
                                  console.log(
                                    "DEBUG: Calling sessionService directly..."
                                  );
                                  const { sessionService } = await import(
                                    "../../services/sessionService"
                                  );
                                  const joinData =
                                    await sessionService.joinSession(
                                      session.id
                                    );
                                  console.log(
                                    "DEBUG: Join response:",
                                    joinData
                                  );

                                  if (joinData.meeting_url) {
                                    // Open popup using the new component
                                    setPopupData({
                                      isOpen: true,
                                      meetingUrl: joinData.meeting_url,
                                      sessionTitle: session.title,
                                    });
                                  } else {
                                    alert("لم يتم الحصول على رابط الجلسة");
                                  }
                                } catch (error) {
                                  console.error(
                                    "Error joining session:",
                                    error
                                  );
                                  // Show error modal instead of alert
                                  setErrorData({
                                    isOpen: true,
                                    error: error,
                                    sessionTitle: session.title,
                                  });
                                }
                              };

                              joinSession();
                            }}
                            onMouseEnter={() =>
                              console.log("Mouse entered button")
                            }
                            onMouseLeave={() =>
                              console.log("Mouse left button")
                            }
                            className="px-4 py-2 text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors flex items-center text-sm font-medium cursor-pointer"
                            style={{ pointerEvents: "auto", zIndex: 1000 }}
                          >
                            <i className="fas fa-video mr-2"></i>
                            Join Session
                          </button>
                        </div>
                      )}
                    </div>

                    {showActions && (
                      <div className="flex items-center space-x-2 ml-4">
                        <button
                          onClick={() => onViewDetails(session)}
                          className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
                          title="View Details"
                        >
                          <i className="fas fa-eye"></i>
                        </button>

                        {canEdit(session) && (
                          <button
                            onClick={() => onEdit(session)}
                            className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-full transition-colors"
                            title="Edit Session"
                          >
                            <i className="fas fa-edit"></i>
                          </button>
                        )}

                        {canAssign(session) && (
                          <button
                            onClick={() => onAssign && onAssign(session)}
                            className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
                            title={
                              session.assigned_students_count > 0
                                ? "Add More Students"
                                : "Assign to Students"
                            }
                          >
                            <i className="fas fa-user-plus"></i>
                          </button>
                        )}

                        {userRole === "ADVISOR" &&
                          session.assigned_students_count > 0 && (
                            <button
                              onClick={() => {
                                console.log(
                                  "DEBUG: Manage assignments clicked for session:",
                                  session.title
                                );
                                if (onManageAssignments) {
                                  onManageAssignments(session);
                                }
                              }}
                              className="p-2 text-gray-400 hover:text-orange-600 hover:bg-orange-50 rounded-full transition-colors"
                              title="إدارة الطلاب المسندين"
                            >
                              <i className="fas fa-users-cog"></i>
                            </button>
                          )}

                        {canDelete(session) && (
                          <button
                            onClick={() => onDelete(session)}
                            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                            title="Cancel Session"
                          >
                            <i className="fas fa-trash"></i>
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      {/* Live Session Popup */}
      <LiveSessionPopup
        isOpen={popupData.isOpen}
        onClose={() =>
          setPopupData({ isOpen: false, meetingUrl: "", sessionTitle: "" })
        }
        meetingUrl={popupData.meetingUrl}
        sessionTitle={popupData.sessionTitle}
      />

      {/* Join Error Modal */}
      <JoinErrorModal
        isOpen={errorData.isOpen}
        onClose={() =>
          setErrorData({ isOpen: false, error: null, sessionTitle: "" })
        }
        error={errorData.error}
        sessionTitle={errorData.sessionTitle}
      />
    </div>
  );
};

SessionList.propTypes = {
  sessions: PropTypes.array,
  loading: PropTypes.bool,
  onEdit: PropTypes.func,
  onDelete: PropTypes.func,
  onViewDetails: PropTypes.func,
  onAssign: PropTypes.func,
  onJoin: PropTypes.func,
  onManageAssignments: PropTypes.func,
  userRole: PropTypes.string,
  showActions: PropTypes.bool,
};

export default SessionList;
