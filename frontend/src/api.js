import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const domains = {
  list: () => api.get('/domains/'),
  create: (data) => api.post('/domains/', data),
  activate: (id) => api.put(`/domains/${id}/activate`),
  delete: (id) => api.delete(`/domains/${id}`),
}

export const jobs = {
  list: (status) => api.get('/jobs/', { params: status ? { status } : {} }),
  get: (id) => api.get(`/jobs/${id}`),
  scan: () => api.post('/jobs/scan'),
  newJobs: () => api.get('/jobs/new'),
  updateStatus: (id, status) => api.put(`/jobs/${id}/status`, null, { params: { status } }),
}

export const institutions = {
  list: () => api.get('/institutions/'),
  create: (data) => api.post('/institutions/', data),
  toggleFavorite: (id) => api.put(`/institutions/${id}/favorite`),
  delete: (id) => api.delete(`/institutions/${id}`),
}

export const resumes = {
  list: () => api.get('/resumes/'),
  get: (id) => api.get(`/resumes/${id}`),
  build: (job_id) => api.post('/resumes/build', { job_id, user_id: 1 }),
  pdfUrl: (id) => `/api/resumes/${id}/pdf`,
  docxUrl: (id) => `/api/resumes/${id}/docx`,
}

export const applications = {
  list: () => api.get('/applications/'),
  create: (data) => api.post('/applications/', data),
  update: (id, data) => api.put(`/applications/${id}`, data),
}

export const profile = {
  get: () => api.get('/profile/'),
  update: (data) => api.put('/profile/', data),
  getSkills: () => api.get('/profile/skills'),
  addSkill: (data) => api.post('/profile/skills', data),
  deleteSkill: (id) => api.delete(`/profile/skills/${id}`),
  getExperience: () => api.get('/profile/experience'),
  addExperience: (data) => api.post('/profile/experience', data),
}

export default api
