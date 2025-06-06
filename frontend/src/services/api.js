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
        // Log request details for debugging
        console.log('API Request:', {
            url: config.url,
            method: config.method,
            baseURL: config.baseURL,
            headers: config.headers,
            hasToken: !!cookieStorage.getItem('access_token')
        });

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
        // Log response details for debugging
        console.log('API Response:', {
            url: response.config.url,
            status: response.status,
            headers: response.headers,
            data: response.data
        });
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

        // Handle 401 Unauthorized errors
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // Try to refresh the token
                const refreshToken = cookieStorage.getItem('refresh_token');
                if (!refreshToken) {
                    throw new Error('No refresh token available');
                }

                const response = await axios.post(
                    `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/token/refresh/`,
                    { refresh: refreshToken }
                );

                const { access } = response.data;
                cookieStorage.setItem('access_token', access);

                // Update the original request with new token
                originalRequest.headers.Authorization = `Bearer ${access}`;
                return api(originalRequest);
            } catch (refreshError) {
                console.error('Token refresh failed:', refreshError);
                // Clear tokens and redirect to login
                cookieStorage.removeItem('access_token');
                cookieStorage.removeItem('refresh_token');
                if (router.currentRoute.value.name !== 'login') {
                    router.push('/login');
                }
                return Promise.reject(refreshError);
            }
        }

        // Handle 403 Forbidden errors
        if (error.response?.status === 403) {
            if (router.currentRoute.value.name !== 'login') {
                router.push('/login');
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
    const res = await fetch("/accounts/api/user/", {
      headers: authHeaders(),
    });
    if (!res.ok) return null;
    return await safeJson(res);
  } catch (err) {
    console.error("Error fetching user:", err);
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
      await fetch('/api/token/blacklist/', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ refresh }),
      });
    }
  } catch (err) {
    console.error('Error blacklisting token:', err);
  } finally {
    // clear tokens locally
    cookieStorage.removeItem('access_token');
    cookieStorage.removeItem('refresh_token');
  }
}
