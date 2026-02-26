/**
 * Combines multiple class names into a single string, filtering out falsy values
 * @param  {...any} classes - Class names to combine
 * @returns {string} - Combined class names
 */
export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}

/**
 * Extract user-friendly error message from error object
 * @param {Error|Object|string} error - Error object or message
 * @returns {string} - User-friendly error message
 */
export function getErrorMessage(error) {
  if (!error) {
    return 'An unexpected error occurred';
  }

  // If it's already a string, return it
  if (typeof error === 'string') {
    return error;
  }

  // If it's an Error object with a message
  if (error instanceof Error) {
    return error.message || 'An unexpected error occurred';
  }

  // If it's an object with a message property
  if (error.message) {
    return error.message;
  }

  // If it's an axios error response
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;
    
    // Try to extract message from response data
    if (data) {
      if (typeof data === 'string') {
        return data;
      }
      if (data.detail) {
        return data.detail;
      }
      if (data.message) {
        return data.message;
      }
      if (data.error) {
        return data.error;
      }
    }
    
    // Fallback to status-based messages
    switch (status) {
      case 400:
        return 'Bad request. Please check your input and try again.';
      case 401:
        return 'Authentication required. Please log in and try again.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 429:
        return 'Too many requests. Please wait a moment and try again.';
      case 500:
        return 'Server error. Please try again later.';
      case 502:
        return 'Bad gateway. The server is temporarily unavailable.';
      case 503:
        return 'Service unavailable. Please try again later.';
      default:
        return `Server error (${status}). Please try again.`;
    }
  }

  // If it's a network error
  if (error.request) {
    return 'Network error. Please check your internet connection and try again.';
  }

  // If it has a toString method
  if (error.toString && typeof error.toString === 'function') {
    const stringified = error.toString();
    if (stringified !== '[object Object]') {
      return stringified;
    }
  }

  // Last resort
  return 'An unexpected error occurred';
} 