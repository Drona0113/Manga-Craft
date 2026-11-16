import api from './api';

export const authService = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (username, email, password, fullName) => {
    const response = await api.post('/auth/register', {
      username,
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};
