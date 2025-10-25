// frontend/src/services/api.js

// helper: grab access token & build headers

import axios from 'axios';
import router from '../router';
import { cookieStorage } from '../utils/cookies';

// Create axios instance with base configuration
const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// Add request interceptor
api.interceptors.request.use(
    (config) => {
        // Add auth token if available
        const token = cookieStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
    }
);

// Add response interceptor
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        console.error('API Response Error:', {
            url: error.config?.url,
            status: error.response?.status,
            data: error.response?.data,
            headers: error.response?.headers
        });

        const originalRequest = error.config;

        // Only attempt token refresh for 401 errors and not for token endpoints
        if (error.response?.status === 401 && 
            !originalRequest._retry && 
            !originalRequest.url.includes('/token/')) {
            originalRequest._retry = true;

            try {
                // Try to refresh the token
                const refreshToken = cookieStorage.getItem('refresh_token');
                if (!refreshToken) {
                    // If no refresh token, just reject the error
                    return Promise.reject(error);
                }

                const response = await api.post(
                    'token/refresh/',
                    { refresh: refreshToken }
                );

                const { access } = response.data;
                cookieStorage.setItem('access_token', access);

                // Update the original request with new token
                originalRequest.headers.Authorization = `Bearer ${access}`;
                return api(originalRequest);
            } catch (refreshError) {
                console.error('Token refresh failed:', refreshError);
                // Clear tokens and redirect to login only if not already on login page
                cookieStorage.removeItem('access_token');
                cookieStorage.removeItem('refresh_token');
                if (router.currentRoute.value.name !== 'LoginForm') {
                    router.push('/accounts/login/');
                }
                return Promise.reject(error);
            }
        }

        // Handle 403 Forbidden errors
        if (error.response?.status === 403) {
            if (router.currentRoute.value.name !== 'LoginForm') {
                router.push('/accounts/login/');
            }
        }

        return Promise.reject(error);
    }
);

export default api;

function authHeaders() {
  const token = cookieStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

async function safeJson(res) {
  const ct = res.headers.get("content-type") || "";
  if (!ct.includes("application/json")) return null;
  return res.json();
}

export async function fetchUser() {
  try {
    const response = await api.get('/accounts/api/user/');
    return response.data;
  } catch (err) {
    console.error("Error fetching user:", err);
    // If we get a 401, the token is invalid, so clear it
    if (err.response?.status === 401) {
      cookieStorage.removeItem('access_token');
      cookieStorage.removeItem('refresh_token');
    }
    return null;
  }
}

export async function fetchMessages() {
  try {
    const res = await fetch("api/user/", {
      headers: authHeaders(),
    });
    if (!res.ok) return [];
    const data = await safeJson(res);
    return Array.isArray(data) ? data : [];
  } catch (err) {
    console.error("Error fetching messages:", err);
    return [];
  }
}

export async function doLogout() {
  try {
    const refresh = cookieStorage.getItem('refresh_token');
    if (refresh) {
      // blacklist the refresh token
      await api.post('token/blacklist/', { refresh });
    }
  } catch (err) {
    console.error('Error blacklisting token:', err);
  } finally {
    // clear tokens locally
    cookieStorage.removeItem('access_token');
    cookieStorage.removeItem('refresh_token');
  }
}
