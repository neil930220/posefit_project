/**
 * Date utilities for consistent timezone handling
 * Optimized for GMT+8 timezone
 */

/**
 * Get today's date in local timezone formatted as YYYY-MM-DD
 * @returns {string} Date string in YYYY-MM-DD format
 */
export const getTodayDate = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Format a Date object to YYYY-MM-DD string in local timezone
 * @param {Date} date - Date object to format
 * @returns {string} Date string in YYYY-MM-DD format
 */
export const formatDateToString = (date) => {
  if (!date || !(date instanceof Date)) return ''
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Parse a date string (YYYY-MM-DD) to Date object in local timezone
 * @param {string} dateString - Date string in YYYY-MM-DD format
 * @returns {Date|null} Date object or null if invalid
 */
export const parseDateString = (dateString) => {
  if (!dateString || typeof dateString !== 'string') return null
  
  const [year, month, day] = dateString.split('-').map(Number)
  if (!year || !month || !day) return null
  
  // Create date in local timezone (month is 0-indexed)
  return new Date(year, month - 1, day)
}

/**
 * Get the current date and time formatted for display
 * @returns {string} Formatted date and time string
 */
export const getCurrentDateTime = () => {
  const now = new Date()
  return now.toLocaleString('zh-TW', {
    timeZone: 'Asia/Taipei',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

/**
 * Check if a date string represents today
 * @param {string} dateString - Date string in YYYY-MM-DD format
 * @returns {boolean} True if the date is today
 */
export const isToday = (dateString) => {
  return dateString === getTodayDate()
}

/**
 * Get number of days between two dates
 * @param {string} startDate - Start date in YYYY-MM-DD format
 * @param {string} endDate - End date in YYYY-MM-DD format
 * @returns {number} Number of days difference
 */
export const getDaysDifference = (startDate, endDate) => {
  const start = parseDateString(startDate)
  const end = parseDateString(endDate)
  
  if (!start || !end) return 0
  
  const diffTime = Math.abs(end - start)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
} 