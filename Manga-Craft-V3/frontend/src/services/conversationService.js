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

  // Send a message and receive an AI reply
  sendChatMessage: async (conversationId, content) => {
    const response = await api.post('/chat/', {
      conversation_id: conversationId,
      content,
    });
    return response.data;
  },

  // Stream an AI reply using Server-Sent Events (SSE).
  // Unlike axios, fetch lets us read the response body piece by piece.
  streamChatMessage: async (conversationId, content, handlers = {}) => {
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const token = localStorage.getItem('token');

    const response = await fetch(`${baseURL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ conversation_id: conversationId, content }),
    });

    if (!response.ok || !response.body) {
      throw new Error('Failed to start the stream');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    // Read chunks until the server closes the stream.
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      // SSE events are separated by a blank line.
      const events = buffer.split('\n\n');
      buffer = events.pop();

      for (const event of events) {
        const line = event.trim();
        if (!line.startsWith('data:')) continue;
        const data = JSON.parse(line.slice(5).trim());

        if (data.type === 'start' && handlers.onStart) handlers.onStart(data);
        else if (data.type === 'token' && handlers.onToken) handlers.onToken(data.content);
        else if (data.type === 'done' && handlers.onDone) handlers.onDone(data);
        else if (data.type === 'error' && handlers.onError) handlers.onError(data.message);
      }
    }
  },
};
