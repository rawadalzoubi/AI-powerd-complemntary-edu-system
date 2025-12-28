import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    // Try both token names for compatibility
    const token =
      localStorage.getItem("accessToken") || localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem("token");
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const sessionService = {
  // Get all sessions (filtered by user role)
  async getSessions(params = {}) {
    try {
      const response = await apiClient.get("/live-sessions/", { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching sessions:", error);
      throw error;
    }
  },

  // Get user's session schedule
  async getMySchedule(params = {}) {
    try {
      const response = await apiClient.get("/live-sessions/my-schedule/", {
        params,
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching schedule:", error);
      throw error;
    }
  },

  // Get pending sessions (for advisors)
  async getPendingSessions() {
    try {
      const response = await apiClient.get("/live-sessions/pending/");
      return response.data;
    } catch (error) {
      console.error("Error fetching pending sessions:", error);
      throw error;
    }
  },

  // Get session details
  async getSessionDetails(sessionId) {
    try {
      const response = await apiClient.get(`/live-sessions/${sessionId}/`);
      return response.data;
    } catch (error) {
      console.error("Error fetching session details:", error);
      throw error;
    }
  },

  // Create new session (teachers only)
  async createSession(sessionData) {
    try {
      const response = await apiClient.post("/live-sessions/", sessionData);
      return response.data;
    } catch (error) {
      console.error("Error creating session:", error);
      throw error;
    }
  },

  // Update session (teachers only)
  async updateSession(sessionId, sessionData) {
    try {
      const response = await apiClient.put(
        `/live-sessions/${sessionId}/`,
        sessionData
      );
      return response.data;
    } catch (error) {
      console.error("Error updating session:", error);
      throw error;
    }
  },

  // Cancel session (teachers only)
  async cancelSession(sessionId, reason = "") {
    try {
      const response = await apiClient.delete(
        `/live-sessions/${sessionId}/cancel/`,
        {
          data: { reason },
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error cancelling session:", error);
      throw error;
    }
  },

  // Assign session to students (advisors only)
  async assignSession(sessionId, studentIds, message = "") {
    try {
      const response = await apiClient.post(
        `/live-sessions/${sessionId}/assign/`,
        {
          student_ids: studentIds,
          message,
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error assigning session:", error);
      throw error;
    }
  },

  // Get assigned students for a session (advisors only)
  async getAssignedStudents(sessionId) {
    try {
      console.log(
        "DEBUG: Calling API for assigned students, sessionId:",
        sessionId
      );
      const response = await apiClient.get(
        `/live-sessions/${sessionId}/assigned-students/`
      );
      console.log("DEBUG: API response for assigned students:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error getting assigned students:", error);
      throw error;
    }
  },

  // Unassign students from session (advisors only)
  async unassignStudents(sessionId, studentIds) {
    try {
      console.log(
        "DEBUG: Unassigning students:",
        studentIds,
        "from session:",
        sessionId
      );
      const response = await apiClient.delete(
        `/live-sessions/${sessionId}/unassign/`,
        {
          data: { student_ids: studentIds },
        }
      );
      console.log("DEBUG: Unassign response:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error unassigning students:", error);
      throw error;
    }
  },

  // Join session (students and teachers)
  async joinSession(sessionId) {
    try {
      const response = await apiClient.get(`/live-sessions/${sessionId}/join/`);
      return response.data;
    } catch (error) {
      console.error("Error joining session:", error);
      throw error;
    }
  },

  // Join session (students and teachers)
  async joinSession(sessionId) {
    try {
      const response = await apiClient.get(`/live-sessions/${sessionId}/join/`);
      return response.data;
    } catch (error) {
      console.error("Error joining session:", error);
      throw error;
    }
  },

  // Record attendance (when leaving session)
  async recordAttendance(sessionId, attendanceData) {
    try {
      const response = await apiClient.post(
        `/live-sessions/${sessionId}/attendance/`,
        attendanceData
      );
      return response.data;
    } catch (error) {
      console.error("Error recording attendance:", error);
      throw error;
    }
  },

  // Get calendar data
  async getCalendarData(params = {}) {
    try {
      const response = await apiClient.get("/live-sessions/calendar/", {
        params,
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching calendar data:", error);
      throw error;
    }
  },

  // Get attendance report (advisors and teachers)
  async getAttendanceReport(params = {}) {
    try {
      const response = await apiClient.get(
        "/live-sessions/attendance-report/",
        { params }
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching attendance report:", error);
      throw error;
    }
  },

  // Session Materials
  async getSessionMaterials(sessionId) {
    try {
      const response = await apiClient.get(
        `/live-session-materials/?session=${sessionId}`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching session materials:", error);
      throw error;
    }
  },

  async uploadSessionMaterial(sessionId, materialData) {
    try {
      const formData = new FormData();
      formData.append("session", sessionId);
      formData.append("title", materialData.title);
      formData.append("description", materialData.description || "");
      formData.append("content_type", materialData.content_type);
      formData.append("is_public", materialData.is_public || true);

      if (materialData.file) {
        formData.append("file", materialData.file);
      }
      if (materialData.url) {
        formData.append("url", materialData.url);
      }
      if (materialData.text_content) {
        formData.append("text_content", materialData.text_content);
      }

      const response = await apiClient.post(
        "/live-session-materials/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error uploading session material:", error);
      throw error;
    }
  },

  async downloadMaterial(materialId) {
    try {
      const response = await apiClient.get(
        `/live-session-materials/${materialId}/download/`,
        {
          responseType: "blob",
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error downloading material:", error);
      throw error;
    }
  },

  // Search students (for advisors)
  async searchStudents(query = "", params = {}) {
    try {
      // Use the advisor endpoint for getting students
      const response = await apiClient.get("/user/advisor/students/", {
        params: { search: query, ...params },
      });
      return response.data;
    } catch (error) {
      console.error("Error searching students:", error);
      throw error;
    }
  },

  // Get session statistics
  async getSessionStats(params = {}) {
    try {
      const response = await apiClient.get("/live-sessions/stats/", { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching session stats:", error);
      throw error;
    }
  },

  // Utility functions
  formatSessionForCalendar(session) {
    const startDate = new Date(session.scheduled_datetime);
    const endDate = new Date(
      startDate.getTime() + session.duration_minutes * 60000
    );

    return {
      id: session.id,
      title: session.title,
      start: startDate,
      end: endDate,
      resource: session,
      allDay: false,
      backgroundColor: this.getStatusColor(session.status),
      borderColor: this.getStatusColor(session.status),
      textColor: "#ffffff",
    };
  },

  getStatusColor(status) {
    const colors = {
      PENDING: "#f59e0b", // yellow
      ASSIGNED: "#3b82f6", // blue
      ACTIVE: "#10b981", // green
      COMPLETED: "#6b7280", // gray
      CANCELLED: "#ef4444", // red
    };
    return colors[status] || colors["PENDING"];
  },

  // Check if user can join session
  canJoinSession(session, userRole) {
    const now = new Date();
    const sessionStart = new Date(session.scheduled_datetime);
    const sessionEnd = new Date(
      sessionStart.getTime() + session.duration_minutes * 60000
    );

    // Session must be assigned or active
    if (!["ASSIGNED", "ACTIVE"].includes(session.status)) {
      return false;
    }

    // Check timing - allow joining 15 minutes before start
    const joinWindow = new Date(sessionStart.getTime() - 15 * 60000);

    return now >= joinWindow && now <= sessionEnd;
  },

  // Format duration for display
  formatDuration(minutes) {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0
      ? `${hours}h ${remainingMinutes}m`
      : `${hours}h`;
  },

  // Get relative time until session
  getTimeUntilSession(scheduledDateTime) {
    const now = new Date();
    const sessionTime = new Date(scheduledDateTime);
    const diffMs = sessionTime.getTime() - now.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffMins < 0) {
      return "Session ended";
    } else if (diffMins === 0) {
      return "Starting now";
    } else if (diffMins < 60) {
      return `Starts in ${diffMins} min`;
    } else if (diffMins < 1440) {
      // Less than 24 hours
      const hours = Math.floor(diffMins / 60);
      return `Starts in ${hours}h ${diffMins % 60}m`;
    } else {
      const days = Math.floor(diffMins / 1440);
      return `Starts in ${days} day${days > 1 ? "s" : ""}`;
    }
  },
};

export default sessionService;
