import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

// Create auth context
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const loadUser = async () => {
      if (authService.isAuthenticated()) {
        try {
          const userData = await authService.getCurrentUser();
          setCurrentUser(userData);
        } catch (err) {
          console.error('Failed to load user:', err);
          authService.logout(); // Clear bad tokens
        }
      }
      setLoading(false);
    };

    loadUser();
  }, []);

  // Register function
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    try {
      console.log('AuthContext: Registering with data:', { ...userData, password: '[REDACTED]' });
      
      // Make sure the userData matches expected backend format
      const sanitizedUserData = {
        email: userData.email,
        password: userData.password,
        full_name: userData.full_name,
        company: userData.company || undefined
      };
      
      const result = await authService.register(sanitizedUserData);
      console.log('AuthContext: Registration successful:', result);
      return result;
    } catch (err) {
      console.error('AuthContext: Registration error:', err);
      
      // Extract error message from various possible formats
      let errorDetail = 'Registration failed';
      if (typeof err === 'string') {
        errorDetail = err;
      } else if (err && typeof err === 'object') {
        if (err.detail) {
          errorDetail = err.detail;
        } else if (err.message) {
          errorDetail = err.message;
        }
      }
      
      setError(errorDetail);
      throw err; // Rethrow so the form component can also handle it
    } finally {
      setLoading(false);
    }
  };

  // Login function
  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const result = await authService.login(email, password);
      // Get user data after successful login
      const userData = await authService.getCurrentUser();
      setCurrentUser(userData);
      return result;
    } catch (err) {
      setError(err.detail || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    setLoading(true);
    try {
      await authService.logout();
      setCurrentUser(null);
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Value object for the context provider
  const value = {
    currentUser,
    loading,
    error,
    register,
    login,
    logout,
    isAuthenticated: authService.isAuthenticated,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext; 