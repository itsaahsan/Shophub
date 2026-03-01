import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  withCredentials: true, // For httpOnly cookies
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized - try to refresh token
    const url = originalRequest?.url || '';
    const isAuthRoute =
      url.includes('/auth/login') ||
      url.includes('/auth/signup') ||
      url.includes('/auth/refresh') ||
      url.includes('/auth/logout');

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !isAuthRoute) {
      originalRequest._retry = true;
      
      try {
        // Refresh token is stored as httpOnly cookie; just attempt refresh.
        await api.post('/auth/refresh');
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, user is logged out. Redirect to login.
        if (window.location.pathname !== '/login') {
          const redirectTo = window.location.pathname + window.location.search;
          window.location.href = '/login?redirect=' + encodeURIComponent(redirectTo);
        }
        
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;