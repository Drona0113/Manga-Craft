import api from './api';

export const panelService = {
  // Panel CRUD
  uploadPanel: async (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/projects/${projectId}/panels/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  listPanels: async (projectId, skip = 0, limit = 50) => {
    const response = await api.get(`/projects/${projectId}/panels`, {
      params: { skip, limit }
    });
    return response.data; // { panels, total, skip, limit, has_more }
  },

  getPanel: async (panelId) => {
    const response = await api.get(`/panels/${panelId}`);
    return response.data;
  },

  deletePanel: async (panelId) => {
    const response = await api.delete(`/panels/${panelId}`);
    return response.data;
  },

  updatePanel: async (panelId, data) => {
    const response = await api.patch(`/panels/${panelId}`, data);
    return response.data;
  },
};
