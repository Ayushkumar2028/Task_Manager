// Auth API calls
import api from './axios';

export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
  // Admin only
  listUsers: () => api.get('/auth/users/'),
  deleteUser: (id) => api.delete(`/auth/users/${id}/`),
  promoteUser: (id) => api.post(`/auth/users/${id}/promote/`),
};

// Tasks API calls
export const tasksAPI = {
  list: (params) => api.get('/tasks/', { params }),
  create: (data) => api.post('/tasks/', data),
  get: (id) => api.get(`/tasks/${id}/`),
  update: (id, data) => api.patch(`/tasks/${id}/`, data),
  delete: (id) => api.delete(`/tasks/${id}/`),
  getStats: () => api.get('/tasks/stats/'),
};
