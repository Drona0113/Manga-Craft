import api from './api';

export const conversationService = {
  // Conversation CRUD
  createConversation: async (projectId, title) => {
    const response = await api.post('/conversations', {
      project_id: projectId,
      title,
    });
    return response.data;
  },

  listConversations: async (projectId) => {
    const response = await api.get('/conversations', {
      params: { project_id: projectId },
    });
    return response.data;
  },

  getConversation: async (conversationId) => {
    const response = await api.get(`/conversations/${conversationId}`);
    return response.data;
  },

  updateConversation: async (conversationId, title) => {
    const response = await api.put(`/conversations/${conversationId}`, {
      title,
    });
    return response.data;
  },

  deleteConversation: async (conversationId) => {
    const response = await api.delete(`/conversations/${conversationId}`);
    return response.data;
  },

  // Message operations
  getMessages: async (conversationId, skip = 0, limit = 50) => {
    const response = await api.get(`/conversations/${conversationId}/messages`, {
      params: { skip, limit },
    });
    return response.data; // { messages, total, skip, limit, has_more }
  },

  createMessage: async (conversationId, content) => {
    const response = await api.post('/conversations/messages', {
      conversation_id: conversationId,
      role: 'user',
      content,
    });
    return response.data;
  },
};
