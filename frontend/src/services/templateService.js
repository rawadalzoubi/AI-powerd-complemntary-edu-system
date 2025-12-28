import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/recurring-sessions`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
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
      localStorage.removeItem("token");
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const templateService = {
  // Get all templates for current teacher
  async getTemplates() {
    try {
      const response = await apiClient.get("/templates/");
      return response.data;
    } catch (error) {
      console.error("Error getting templates:", error);
      throw error;
    }
  },

  // Get simple templates list for dropdowns
  async getSimpleTemplates() {
    try {
      const response = await apiClient.get("/templates/simple/");
      return response.data;
    } catch (error) {
      console.error("Error getting simple templates:", error);
      throw error;
    }
  },

  // Get template details
  async getTemplate(templateId) {
    try {
      const response = await apiClient.get(`/templates/${templateId}/`);
      return response.data;
    } catch (error) {
      console.error("Error getting template:", error);
      throw error;
    }
  },

  // Create new template
  async createTemplate(templateData) {
    try {
      const response = await apiClient.post("/templates/", templateData);
      return response.data;
    } catch (error) {
      console.error("Error creating template:", error);
      throw error;
    }
  },

  // Update template
  async updateTemplate(templateId, templateData) {
    try {
      const response = await apiClient.put(
        `/templates/${templateId}/`,
        templateData
      );
      return response.data;
    } catch (error) {
      console.error("Error updating template:", error);
      throw error;
    }
  },

  // Delete template
  async deleteTemplate(templateId) {
    try {
      const response = await apiClient.delete(`/templates/${templateId}/`);
      return response.data;
    } catch (error) {
      console.error("Error deleting template:", error);
      throw error;
    }
  },

  // Pause template
  async pauseTemplate(templateId) {
    try {
      const response = await apiClient.post(`/templates/${templateId}/pause/`);
      return response.data;
    } catch (error) {
      console.error("Error pausing template:", error);
      throw error;
    }
  },

  // Resume template
  async resumeTemplate(templateId) {
    try {
      const response = await apiClient.post(`/templates/${templateId}/resume/`);
      return response.data;
    } catch (error) {
      console.error("Error resuming template:", error);
      throw error;
    }
  },

  // End template
  async endTemplate(templateId) {
    try {
      const response = await apiClient.post(`/templates/${templateId}/end/`);
      return response.data;
    } catch (error) {
      console.error("Error ending template:", error);
      throw error;
    }
  },

  // Get generated sessions from template
  async getGeneratedSessions(templateId) {
    try {
      const response = await apiClient.get(
        `/templates/${templateId}/generated_sessions/`
      );
      return response.data;
    } catch (error) {
      console.error("Error getting generated sessions:", error);
      throw error;
    }
  },

  // Get template assignments
  async getTemplateAssignments(templateId) {
    try {
      const response = await apiClient.get(
        `/templates/${templateId}/assignments/`
      );
      return response.data;
    } catch (error) {
      console.error("Error getting template assignments:", error);
      throw error;
    }
  },

  // Get template statistics
  async getTemplateStatistics() {
    try {
      const response = await apiClient.get("/statistics/");
      return response.data;
    } catch (error) {
      console.error("Error getting template statistics:", error);
      throw error;
    }
  },
};
