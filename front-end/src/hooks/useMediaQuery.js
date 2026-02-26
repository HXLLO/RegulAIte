import { useState, useEffect } from 'react';

/**
 * Custom hook to detect if a media query matches
 * @param {string} query - The media query to check
 * @returns {boolean} Whether the media query matches
 */
const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    
    // Set initial value
    setMatches(media.matches);
    
    // Create a listener function
    const listener = (e) => setMatches(e.matches);
    
    // Add the listener to media query
    media.addEventListener('change', listener);
    
    // Clean up
    return () => {
      media.removeEventListener('change', listener);
    };
  }, [query]);

  return matches;
};

export default useMediaQuery; 