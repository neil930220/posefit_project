// frontend/src/services/api.js

// helper: grab access token & build headers

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
});

export default api;

function authHeaders() {
  const token = localStorage.getItem('access_token');
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
    const refresh = localStorage.getItem('refresh_token');
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
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}
