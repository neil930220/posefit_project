// Cookie utility functions

/**
 * Set a cookie with the given name, value, and options
 * @param {string} name - Cookie name
 * @param {string} value - Cookie value
 * @param {Object} options - Cookie options
 * @param {number} options.days - Expiration in days (default: 7)
 * @param {string} options.path - Cookie path (default: '/')
 * @param {boolean} options.secure - Secure flag (default: false)
 * @param {string} options.sameSite - SameSite attribute (default: 'lax')
 */
export function setCookie(name, value, options = {}) {
  const defaults = {
    days: 7,
    path: '/',
    secure: location.protocol === 'https:',
    sameSite: 'lax'
  };
  
  const config = { ...defaults, ...options };
  
  let cookieString = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;
  
  if (config.days) {
    const date = new Date();
    date.setTime(date.getTime() + (config.days * 24 * 60 * 60 * 1000));
    cookieString += `; expires=${date.toUTCString()}`;
  }
  
  cookieString += `; path=${config.path}`;
  
  if (config.secure) {
    cookieString += '; secure';
  }
  
  cookieString += `; samesite=${config.sameSite}`;
  
  document.cookie = cookieString;
}

/**
 * Get a cookie value by name
 * @param {string} name - Cookie name
 * @returns {string|null} - Cookie value or null if not found
 */
export function getCookie(name) {
  const nameEQ = encodeURIComponent(name) + '=';
  const cookies = document.cookie.split(';');
  
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.indexOf(nameEQ) === 0) {
      return decodeURIComponent(cookie.substring(nameEQ.length));
    }
  }
  
  return null;
}

/**
 * Delete a cookie by name
 * @param {string} name - Cookie name
 * @param {string} path - Cookie path (default: '/')
 */
export function deleteCookie(name, path = '/') {
  setCookie(name, '', { days: -1, path });
}

/**
 * Check if cookies are enabled
 * @returns {boolean} - True if cookies are enabled
 */
export function cookiesEnabled() {
  try {
    setCookie('test', 'test', { days: 1 });
    const enabled = getCookie('test') === 'test';
    deleteCookie('test');
    return enabled;
  } catch {
    return false;
  }
}

/**
 * Storage utility that uses cookies instead of localStorage
 */
export const cookieStorage = {
  setItem(key, value, keepLogin = false) {
    const days = keepLogin ? 30 : 1; // 30 days for "keep login", 1 day otherwise
    setCookie(key, value, { days });
  },
  
  getItem(key) {
    return getCookie(key);
  },
  
  removeItem(key) {
    deleteCookie(key);
  },
  
  clear() {
    // Clear all auth-related cookies
    const authCookies = ['access_token', 'refresh_token'];
    authCookies.forEach(cookie => deleteCookie(cookie));
  }
}; 