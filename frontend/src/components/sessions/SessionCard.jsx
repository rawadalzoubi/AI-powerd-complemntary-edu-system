import React, { useState } from "react";
import PropTypes from "prop-types";
import JoinErrorModal from "./JoinErrorModal";

const SessionCard = ({
  session,
  userRole = "STUDENT",
  onJoin,
  onViewDetails,
  onManageAssignments,
  showJoinButton = true,
}) => {
  const [errorData, setErrorData] = useState({
    isOpen: false,
    error: null,
    sessionTitle: "",
  });
  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    const isTomorrow =
      date.toDateString() ===
      new Date(now.getTime() + 24 * 60 * 60 * 1000).toDateString();

    let dateLabel;
    if (isToday) {
      dateLabel = "Today";
    } else if (isTomorrow) {
      dateLabel = "Tomorrow";
    } else {
      dateLabel = date.toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
      });
    }

    const time = date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });

    return { dateLabel, time, fullDate: date };
  };

  const getTimeUntilSession = (scheduledDateTime) => {
    const now = new Date();
    const sessionTime = new Date(scheduledDateTime);
    const diffMs = sessionTime.getTime() - now.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffMins < 0) {
      return { text: "Session ended", color: "text-gray-500", canJoin: false };
    } else if (diffMins === 0) {
      return { text: "Starting now", color: "text-green-600", canJoin: true };
    } else if (diffMins <= 15) {
      return {
        text: `Starts in ${diffMins} min`,
        color: "text-orange-600",
        canJoin: true,
      };
    } else if (diffMins < 60) {
      return {
        text: `Starts in ${diffMins} min`,
        color: "text-blue-600",
        canJoin: false,
      };
    } else {
      const hours = Math.floor(diffMins / 60);
      return {
        text: `Starts in ${hours}h ${diffMins % 60}m`,
        color: "text-gray-600",
        canJoin: false,
      };
    }
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
        text: "Live",
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

  const { dateLabel, time } = formatDateTime(session.scheduled_datetime);
  const timeInfo = getTimeUntilSession(session.scheduled_datetime);
  const isActive =
    session.status === "ACTIVE" ||
    (session.status === "ASSIGNED" && timeInfo.canJoin);

  return (
    <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-all duration-200">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
                {session.title}
              </h3>
              {getStatusBadge(session.status)}
            </div>

            {session.description && (
              <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                {session.description}
              </p>
            )}
          </div>

          {/* Session Icon */}
          <div className="flex-shrink-0 ml-4">
            <div
              className={`w-12 h-12 rounded-full flex items-center justify-center ${
                isActive ? "bg-green-100" : "bg-blue-100"
              }`}
            >
              <i
                className={`fas fa-video text-xl ${
                  isActive ? "text-green-600" : "text-blue-600"
                }`}
              ></i>
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
              <span>Grade {session.level}</span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center text-sm text-gray-600">
              <i className="fas fa-calendar mr-2 text-purple-500 w-4"></i>
              <span>{dateLabel}</span>
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <i className="fas fa-clock mr-2 text-orange-500 w-4"></i>
              <span>
                {time} ({session.duration_minutes}min)
              </span>
            </div>
          </div>
        </div>

        {/* Teacher Info (for students) */}
        {userRole === "STUDENT" && session.teacher_name && (
          <div className="flex items-center text-sm text-gray-600 mb-4">
            <i className="fas fa-chalkboard-teacher mr-2 text-indigo-500 w-4"></i>
            <span>Teacher: {session.teacher_name}</span>
          </div>
        )}

        {/* Time Until Session */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <i className="fas fa-clock mr-2 text-gray-400"></i>
            <span className={`text-sm font-medium ${timeInfo.color}`}>
              {timeInfo.text}
            </span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => onViewDetails(session)}
              className="px-3 py-1.5 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            >
              <i className="fas fa-info-circle mr-1"></i>
              Details
            </button>

            {userRole === "STUDENT" && (
              <>
                {(() => {
                  const now = new Date();
                  const sessionStart = new Date(session.scheduled_datetime);
                  const sessionEnd = new Date(
                    sessionStart.getTime() + session.duration_minutes * 60000
                  );
                  const lateJoinWindow = new Date(
                    sessionStart.getTime() + 10 * 60000
                  );

                  // Check if student can join (same logic as SessionList)
                  const canJoin =
                    (session.status === "ASSIGNED" ||
                      session.status === "ACTIVE") &&
                    now >= sessionStart &&
                    now <= lateJoinWindow;

                  if (canJoin) {
                    return (
                      <button
                        onClick={async () => {
                          try {
                            const { sessionService } = await import(
                              "../../services/sessionService"
                            );
                            const joinData = await sessionService.joinSession(
                              session.id
                            );

                            if (joinData.meeting_url) {
                              // Open in popup window instead of new tab
                              const popupFeatures =
                                "width=1200,height=800,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no,status=no";
                              const popup = window.open(
                                joinData.meeting_url,
                                "LiveSession",
                                popupFeatures
                              );

                              if (popup) {
                                // Focus the popup window
                                popup.focus();

                                // Show success message
                                if (joinData.message) {
                                  alert(
                                    `تم الانضمام للجلسة!\n\n${joinData.message}`
                                  );
                                } else {
                                  alert("تم فتح الجلسة في نافذة منفصلة");
                                }
                              } else {
                                // Popup blocked - fallback to alert with URL
                                alert(
                                  `تم حظر النافذة المنبثقة. يرجى نسخ الرابط والدخول يدوياً:\n\n${joinData.meeting_url}`
                                );
                              }
                            } else {
                              alert("لم يتم الحصول على رابط الجلسة");
                            }
                          } catch (error) {
                            console.error("Error joining session:", error);
                            setErrorData({
                              isOpen: true,
                              error: error,
                              sessionTitle: session.title,
                            });
                          }
                        }}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md transition-colors flex items-center"
                      >
                        <i className="fas fa-video mr-2"></i>
                        Join Now
                      </button>
                    );
                  } else if (now < sessionStart) {
                    const minutesUntil = Math.floor(
                      (sessionStart - now) / (1000 * 60)
                    );
                    return (
                      <button
                        disabled
                        className="px-4 py-2 bg-gray-300 text-gray-500 text-sm font-medium rounded-md cursor-not-allowed flex items-center"
                      >
                        <i className="fas fa-clock mr-2"></i>
                        Starts in {minutesUntil}m
                      </button>
                    );
                  } else if (now > lateJoinWindow) {
                    return (
                      <button
                        disabled
                        className="px-4 py-2 bg-red-300 text-red-700 text-sm font-medium rounded-md cursor-not-allowed flex items-center"
                      >
                        <i className="fas fa-times mr-2"></i>
                        Late Join Closed
                      </button>
                    );
                  } else {
                    return (
                      <button
                        disabled
                        className="px-4 py-2 bg-gray-300 text-gray-500 text-sm font-medium rounded-md cursor-not-allowed flex items-center"
                      >
                        <i className="fas fa-clock mr-2"></i>
                        Not Available
                      </button>
                    );
                  }
                })()}
              </>
            )}

            {userRole === "ADVISOR" && (
              <div className="flex items-center space-x-2">
                {session.assigned_students_count > 0 && (
                  <button
                    onClick={() => onManageAssignments(session)}
                    className="px-3 py-1.5 bg-orange-600 hover:bg-orange-700 text-white text-sm font-medium rounded-md transition-colors flex items-center"
                  >
                    <i className="fas fa-users-cog mr-2"></i>
                    إدارة الطلاب ({session.assigned_students_count})
                  </button>
                )}
                <span className="text-xs text-gray-500">
                  {session.assigned_students_count || 0} طالب مسند
                </span>
              </div>
            )}

            {userRole === "TEACHER" && (
              <>
                {(() => {
                  const now = new Date();
                  const sessionStart = new Date(session.scheduled_datetime);
                  const sessionEnd = new Date(
                    sessionStart.getTime() + session.duration_minutes * 60000
                  );
                  const joinWindow = new Date(
                    sessionStart.getTime() - 15 * 60000
                  );

                  // Check if teacher can join (same logic as SessionList)
                  const canJoin =
                    session.status !== "CANCELLED" &&
                    now <= sessionEnd &&
                    now >= joinWindow;

                  if (canJoin) {
                    return (
                      <button
                        onClick={async () => {
                          try {
                            const { sessionService } = await import(
                              "../../services/sessionService"
                            );
                            const joinData = await sessionService.joinSession(
                              session.id
                            );

                            if (joinData.meeting_url) {
                              // Open in popup window instead of new tab
                              const popupFeatures =
                                "width=1200,height=800,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no,status=no";
                              const popup = window.open(
                                joinData.meeting_url,
                                "LiveSession",
                                popupFeatures
                              );

                              if (popup) {
                                // Focus the popup window
                                popup.focus();
                                alert("تم فتح الجلسة في نافذة منفصلة");
                              } else {
                                // Popup blocked - fallback to alert with URL
                                alert(
                                  `تم حظر النافذة المنبثقة. يرجى نسخ الرابط والدخول يدوياً:\n\n${joinData.meeting_url}`
                                );
                              }
                            } else {
                              alert("لم يتم الحصول على رابط الجلسة");
                            }
                          } catch (error) {
                            console.error("Error joining session:", error);
                            setErrorData({
                              isOpen: true,
                              error: error,
                              sessionTitle: session.title,
                            });
                          }
                        }}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors flex items-center"
                      >
                        <i className="fas fa-chalkboard-teacher mr-2"></i>
                        {now >= sessionStart ? "Join Session" : "Join Early"}
                      </button>
                    );
                  } else if (session.status === "CANCELLED") {
                    return (
                      <button
                        disabled
                        className="px-4 py-2 bg-red-300 text-red-700 text-sm font-medium rounded-md cursor-not-allowed flex items-center"
                      >
                        <i className="fas fa-times mr-2"></i>
                        Cancelled
                      </button>
                    );
                  } else if (now > sessionEnd) {
                    return (
                      <button
                        disabled
                        className="px-4 py-2 bg-gray-300 text-gray-500 text-sm font-medium rounded-md cursor-not-allowed flex items-center"
                      >
                        <i className="fas fa-clock mr-2"></i>
                        Session Ended
                      </button>
                    );
                  } else {
                    const minutesUntil = Math.floor(
                      (joinWindow - now) / (1000 * 60)
                    );
                    return (
                      <button
                        disabled
                        className="px-4 py-2 bg-gray-300 text-gray-500 text-sm font-medium rounded-md cursor-not-allowed flex items-center"
                      >
                        <i className="fas fa-clock mr-2"></i>
                        Available in {minutesUntil}m
                      </button>
                    );
                  }
                })()}
              </>
            )}
          </div>
        </div>

        {/* Progress Bar for Active Sessions */}
        {session.status === "ACTIVE" && (
          <div className="mt-4">
            <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>Session in progress</span>
              <span>{session.assigned_students_count || 0} participants</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-green-500 h-1.5 rounded-full animate-pulse"
                style={{ width: "60%" }}
              ></div>
            </div>
          </div>
        )}
      </div>

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

SessionCard.propTypes = {
  session: PropTypes.object.isRequired,
  userRole: PropTypes.string,
  onJoin: PropTypes.func,
  onViewDetails: PropTypes.func,
  onManageAssignments: PropTypes.func,
  showJoinButton: PropTypes.bool,
};

export default SessionCard;
