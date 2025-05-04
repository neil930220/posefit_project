// frontend/src/services/api.js

// frontend/src/services/api.js

async function safeJson(res) {
    const ct = res.headers.get("content-type")||"";
    if (!ct.includes("application/json")) return null;
    return res.json();
  }
  
  export async function fetchUser() {
    try {
      const res = await fetch("/api/accounts/user/", {
        credentials: "include",   // send the session cookie
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
      const res = await fetch("/api/accounts/messages/", {
        credentials: "include",
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
      await fetch('/api/accounts/logout/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'X-CSRFToken': getCsrfToken() },
      })
    } catch (err) {
      console.error('Logout failed:', err)
    }
  }
  
  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/)
    return match ? match[1] : ''
  }
  