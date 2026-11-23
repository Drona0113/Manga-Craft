import api from './api';

export const memoryService = {
  // Memory CRUD
  createMemory: async (memoryData) => {
    const response = await api.post('/memories/', memoryData);
    return response.data;
  },

  listMemories: async (projectId, memoryType = null, skip = 0, limit = 50) => {
    const params = { project_id: projectId, skip, limit };
    if (memoryType) {
      params.memory_type = memoryType;
    }
    const response = await api.get('/memories/', { params });
    return response.data; // { memories, total, skip, limit, has_more }
  },

  getMemory: async (memoryId) => {
    const response = await api.get(`/memories/${memoryId}`);
    return response.data;
  },

  updateMemory: async (memoryId, memoryData) => {
    const response = await api.put(`/memories/${memoryId}`, memoryData);
    return response.data;
  },

  deleteMemory: async (memoryId) => {
    const response = await api.delete(`/memories/${memoryId}`);
    return response.data;
  },

  // Search
  searchMemories: async (projectId, query, skip = 0, limit = 50) => {
    const response = await api.get('/memories/search/', {
      params: { project_id: projectId, query, skip, limit }
    });
    return response.data;
  },
};
