import axios from 'axios';
import authService from './authService';
import { jwtDecode } from 'jwt-decode';
import streamingService from './streamingService';

// Base URL for API calls
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8090';

// Create axios instance with base URL and timeout
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 600000, // 10 minutes timeout (increased from 5 minutes)
});

// Utility function to ensure we always have proper Error objects
const createSafeError = (err, defaultMessage = 'An unexpected error occurred') => {
  if (!err) {
    console.warn('createSafeError: Received null/undefined error, using default message');
    return new Error(defaultMessage);
  }
  if (err instanceof Error) return err;
  if (typeof err === 'string') {
    console.log('createSafeError: Converting string error to Error object');
    return new Error(err);
  }
  if (err.message) {
    console.log('createSafeError: Converting object with message property to Error object');
    return new Error(err.message);
  }
  if (err.toString && typeof err.toString === 'function') {
    console.log('createSafeError: Converting object using toString() to Error object');
    return new Error(err.toString());
  }
  console.warn('createSafeError: Unknown error type, using default message:', typeof err);
  return new Error(defaultMessage);
};

// Add interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      
      // Add user ID from auth token if available
      const userData = authService.getCurrentUserData();
      if (userData) {
        // Try to find user ID in various possible locations
        const userId = userData.user_id || userData.sub || userData.id || userData.userId;
        
        if (userId) {
          config.headers['X-User-ID'] = userId;
        } else {
          // If no explicit user ID, try to extract from the token subject
          try {
            const decoded = jwtDecode(token);
            if (decoded && decoded.sub) {
              config.headers['X-User-ID'] = decoded.sub;
            }
          } catch (e) {
            console.warn('Could not extract user ID from token', e);
          }
        }
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If we get a 401 error and haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        await authService.refreshToken();
        
        // Update the authorization header with the new token
        const newToken = localStorage.getItem('token');
        if (newToken) {
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
        }
        
        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, redirect to login
        console.error('Token refresh failed:', refreshError);
        authService.logout();
        // Don't redirect here as it might interfere with the chat interface
        // Let the component handle the authentication state
      }
    }
    
    return Promise.reject(error);
  }
);

/**
 * Service to handle interactions with the chat API
 */
const chatService = {
  /**
   * Get chat sessions for the current user
   * @param {string} userId - Optional user ID
   * @param {number} limit - Maximum number of sessions to return
   * @param {number} offset - Offset for pagination
   * @returns {Promise<Array>} List of chat sessions
   */
  getChatSessions: async (userId = null, limit = 20, offset = 0) => {
    try {
      // If userId not provided, get from auth service
      if (!userId) {
        const userData = authService.getCurrentUserData();
        userId = userData?.user_id;
        
        // Additional logging to help diagnose issues
        if (!userId) {
          console.warn('No user ID available from getCurrentUserData()', userData);
        } else {
          console.log('Fetching chat sessions for user ID:', userId);
        }
      }
      
      const response = await api.get(`/chat/sessions`, {
        params: { user_id: userId, limit, offset },
        // Add timeout to prevent long-hanging requests
        timeout: 10000
      });
      
      // Log response status and data shape for debugging
      console.log(`Sessions response status: ${response.status}, found ${response.data.sessions?.length || 0} sessions`);
      
      // Check if we have valid sessions in the response
      if (!response.data.sessions) {
        console.warn('API response missing sessions array:', response.data);
        return [];
      }
      
      return response.data.sessions || [];
    } catch (error) {
      // Enhanced error logging with more details
      console.error('Error fetching chat sessions:', error);
      
      // Check if this is a 404 error, which could mean no sessions yet
      if (error.response && error.response.status === 404) {
        console.log('No sessions found for user - likely a new user');
        // Return empty array instead of throwing for new users
        return [];
      }
      
      // Check for network errors that might be transient
      if (!error.response && error.request) {
        console.error('Network error when fetching sessions - no response received');
      }
      
      // Check for timeout
      if (error.code === 'ECONNABORTED') {
        console.error('Request timeout when fetching sessions');
      }
      
      // Re-throw the error to be handled by the calling component
      throw error;
    }
  },

  /**
   * Send a message to the chat API
   * @param {string} sessionId - ID of the chat session
   * @param {string} message - Message content
   * @param {Object} options - Additional options for the request
   * @param {Array} allMessages - Optional array of all messages in the conversation history
   * @returns {Promise<Object>} Chat response
   */
  sendMessage: async (sessionId, message, options = {}, allMessages = null) => {
    try {
      // Log message length for debugging
      const messageLength = message.trim().length;
      console.log(`Sending message with length: ${messageLength}`);
      
      // Prepare LLM parameters
      const llmParams = {
        model: options.model || 'gpt-4',
        temperature: options.temperature !== undefined ? options.temperature : 0.7,
        max_tokens: options.max_tokens || 2048,
        top_p: options.top_p !== undefined ? options.top_p : 1.0,
        frequency_penalty: options.frequency_penalty !== undefined ? options.frequency_penalty : 0.0,
        presence_penalty: options.presence_penalty !== undefined ? options.presence_penalty : 0.0,
      };
      
      // Prepare agent parameters - ALWAYS ENABLED
      const agentParams = {
        use_agent: true  // Always use agents, no user control
      };
      
      // Prepare messages array - either use full history or just the current message
      const messages = allMessages || [{ role: 'user', content: message }];
      
      // For very short messages, ensure we're sending context
      if (messageLength <= 20 && !allMessages) {
        console.warn('Short message detected but no context provided. For better results, pass the conversation history.');
      }

      // Combine all parameters
      const requestParams = {
        session_id: sessionId,
        messages: messages,
        stream: false,
        include_context: options.includeContext !== undefined ? options.includeContext : true,
        context_query: options.contextQuery || null,
        retrieval_type: options.retrievalType || 'auto',
        ...llmParams,
        ...agentParams
      };

      const response = await api.post(`/chat`, requestParams);
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  /**
   * Enhanced streaming message service using the new StreamingService
   * @param {string} sessionId - ID of the chat session
   * @param {string} message - Message content
   * @param {Function} onChunk - Callback for each chunk of the streamed response
   * @param {Object} options - Additional options for the request
   * @param {Array} allMessages - Optional array of all messages in the conversation history
   * @param {string} requestId - Optional request ID for cancellation
   * @returns {Promise<Object>} Result info including execution IDs if applicable
   */
  sendMessageStreaming: async (sessionId, message, onChunk, options = {}, allMessages = null, requestId = null) => {
    console.log(`🚀 Starting enhanced streaming for session: ${sessionId}`);
    
    try {
      // Prepare LLM parameters with better defaults
      const llmParams = {
        model: options.model || 'gpt-4',
        temperature: options.temperature !== undefined ? options.temperature : 0.7,
        max_tokens: options.max_tokens || 2048,
        top_p: options.top_p !== undefined ? options.top_p : 1.0,
        frequency_penalty: options.frequency_penalty !== undefined ? options.frequency_penalty : 0.0,
        presence_penalty: options.presence_penalty !== undefined ? options.presence_penalty : 0.0,
      };

      // Prepare agent parameters - ALWAYS ENABLED
      const agentParams = {
        use_agent: true  // Always use agents, no user control
      };

      // Prepare messages array
      const messages = allMessages || [{ role: 'user', content: message }];

      // Combine all parameters with agents always enabled
      const requestData = {
        session_id: sessionId,
        messages: messages,
        include_context: options.includeContext !== undefined ? options.includeContext : true,
        context_query: options.contextQuery || null,
        retrieval_type: options.retrievalType || 'auto',
        use_agent: true,  // Always enable agents - no user control
        ...llmParams
      };

      // Enhanced callbacks with better error handling
      const callbacks = {
        onStart: (data) => {
          console.log('🎬 Stream started:', data);
          onChunk({
            type: 'start',
            timestamp: data.timestamp,
            request_id: data.requestId,
            streamId: data.streamId
          });
        },

        onToken: (data) => {
          onChunk({
            type: 'token',
            content: data.content,
            accumulated: data.accumulated
          });
        },

        onProcessing: (data) => {
          onChunk({
            type: 'processing',
            state: data.state,
            step: data.step,
            step_number: data.stepNumber,
            total_steps: data.totalSteps,
            details: data.details,
            internal_thoughts: data.internalThoughts,
            context_metadata: data.contextMetadata,
            timestamp: data.timestamp
          });
        },

        onComplete: (data) => {
          console.log('✅ Stream completed:', data);
          onChunk({
            type: 'end',
            message: data.message,
            metadata: data.metadata,
            model: data.model,
            context_used: data.contextUsed,
            session_id: data.sessionId,
            sources: data.sources,
            context_quality: data.contextQuality,
            hallucination_risk: data.hallucination_risk,
            internal_thoughts: data.internalThoughts,
            streamId: data.streamId
          });
        },

        onError: (error) => {
          console.error('❌ Stream error:', error);
          onChunk({
            type: 'error',
            message: error.message,
            error_code: 'STREAM_ERROR',
            request_id: requestId
          });
        },

        onProgress: (data) => {
          if (data.type === 'warning') {
            onChunk({
              type: 'processing',
              state: data.message,
              step: 'connection_warning',
              timestamp: new Date().toISOString()
            });
          }
        }
      };

      // Stream options with enhanced configuration
      const streamOptions = {
        timeout: options.timeout || 300000, // 5 minutes
        retryOnFailure: true,
        headers: {
          'X-Request-ID': requestId || `req_${Date.now()}`,
          'X-Session-ID': sessionId
        }
      };

      // Use the enhanced streaming service
      const result = await streamingService.createStream(
        `${API_URL}/chat`,
        requestData,
        callbacks,
        streamOptions
      );

      console.log('🎉 Streaming completed successfully:', result);
      return result;

    } catch (error) {
      console.error('💥 Streaming failed:', error);
      
      // Enhanced error handling
      const errorMessage = this.getEnhancedErrorMessage(error);
      onChunk({
        type: 'error',
        message: errorMessage,
        error_code: this.getErrorCode(error),
        request_id: requestId
      });
      
      throw error;
    }
  },

  /**
   * Enhanced error message extraction
   */
  getEnhancedErrorMessage: (error) => {
    if (error.message.includes('timeout')) {
      return 'Request timed out. The AI service may be experiencing high load. Please try again.';
    }
    if (error.message.includes('401')) {
      return 'Authentication failed. Please check your API key and try again.';
    }
    if (error.message.includes('429')) {
      return 'Rate limit exceeded. Please wait a moment before trying again.';
    }
    if (error.message.includes('500')) {
      return 'Server error occurred. Please try again in a few moments.';
    }
    if (error.message.includes('network')) {
      return 'Network connection error. Please check your internet connection.';
    }
    return error.message || 'An unexpected error occurred during streaming.';
  },

  /**
   * Get error code for categorization
   */
  getErrorCode: (error) => {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('401')) return 'UNAUTHORIZED';
    if (error.message.includes('429')) return 'RATE_LIMIT';
    if (error.message.includes('500')) return 'SERVER_ERROR';
    if (error.message.includes('network')) return 'NETWORK_ERROR';
    return 'UNKNOWN_ERROR';
  },

  /**
   * Stop all active streams
   */
  stopAllStreams: () => {
    console.log('🛑 Stopping all active streams');
    streamingService.abortAllStreams();
  },

  /**
   * Stop a specific stream
   */
  stopStream: (streamId) => {
    console.log(`🛑 Stopping stream: ${streamId}`);
    streamingService.abortStream(streamId);
  },

  /**
   * Get streaming statistics
   */
  getStreamingStats: () => {
    return {
      activeStreams: streamingService.getActiveStreamCount(),
      // Add more stats as needed
    };
  },

  /**
   * Create a new chat session
   * @param {string} userId - Optional user ID
   * @returns {Promise<Object>} New session information
   */
  createSession: async (userId = null) => {
    try {
      // If userId not provided, get from auth service
      if (!userId) {
        const userData = authService.getCurrentUserData();
        if (userData) {
          userId = userData.user_id || userData.sub || userData.id || userData.userId;
          console.log('Creating session for user ID:', userId);
        } else {
          console.warn('No user data available when creating session');
        }

        // If still no userId, try to get it from the token directly
        if (!userId) {
          const token = localStorage.getItem('token');
          if (token) {
            try {
              const decoded = jwtDecode(token);
              userId = decoded.sub || decoded.user_id || decoded.id || decoded.userId;
              console.log('Extracted user ID from token:', userId);
            } catch (e) {
              console.warn('Could not extract user ID from token', e);
            }
          } else {
            console.warn('No auth token found when creating session');
          }
        }
      }
      
      // If we still don't have a user ID, generate a temporary one
      // This ensures the API call doesn't fail just because of missing user ID
      if (!userId) {
        userId = `temp-${Date.now()}`;
        console.warn('Using temporary user ID for session creation:', userId);
      }
      
      const response = await api.post(`/chat/sessions`, {
        user_id: userId,
      }, {
        // Add timeout to prevent long-hanging requests
        timeout: 10000
      });
      
      // Validate the response contains a session ID
      if (!response.data || !response.data.session_id) {
        console.error('Invalid response from create session API:', response.data);
        throw new Error('Server returned invalid session data');
      }
      
      return response.data;
    } catch (error) {
      console.error('Error creating chat session:', error);
      
      // Check for specific error types for better handling
      if (error.response) {
        const status = error.response.status;
        // For 401/403 errors, we should clear the token and redirect to login
        if (status === 401 || status === 403) {
          console.error('Authentication error when creating session:', status);
        } else if (status === 429) {
          console.error('Rate limit exceeded when creating session');
        } else if (status === 500) {
          console.error('Server error when creating session:', error.response.data);
        }
        
        // Add more specific error message to the error object
        error.sessionCreationFailed = true;
        error.detailedMessage = error.response.data?.detail || `Server returned ${status}`;
      } else if (error.request) {
        console.error('Network error when creating session - no response received');
        // Add network-specific error info
        error.sessionCreationFailed = true;
        error.isNetworkError = true;
        error.detailedMessage = 'Network error: Could not reach the server';
      } else if (error.code === 'ECONNABORTED') {
        console.error('Request timeout when creating session');
        error.sessionCreationFailed = true;
        error.isTimeoutError = true;
        error.detailedMessage = 'Request timed out: Server took too long to respond';
      }
      
      throw error;
    }
  },
  
  /**
   * Track agent execution progress
   * @param {string} executionId - ID of the execution to track
   * @returns {Promise<Object>} Progress information
   */
  getAgentProgress: async (executionId) => {
    if (!executionId) return null;
    
    try {
      const response = await api.get(`/chat/progress/${executionId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching agent progress:', error);
      return null;
    }
  },
  
  /**
   * Get available agent types
   * @returns {Promise<Object>} Map of agent types to descriptions
   */
  getAgentTypes: async () => {
    try {
      const response = await api.get(`/agents/types`);
      return response.data;
    } catch (error) {
      console.error('Error fetching agent types:', error);
      return {};
    }
  },
  
  /**
   * Get available decision trees
   * @returns {Promise<Object>} Map of tree IDs to tree info
   */
  getDecisionTrees: async () => {
    try {
      const response = await api.get(`/agents/trees`);
      return response.data;
    } catch (error) {
      console.error('Error fetching decision trees:', error);
      return {};
    }
  },
  
  /**
   * Get details about a specific decision tree
   * @param {string} treeId - ID of the tree to get
   * @returns {Promise<Object>} Tree details
   */
  getDecisionTree: async (treeId) => {
    try {
      const response = await api.get(`/agents/trees/${treeId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching decision tree:', error);
      return null;
    }
  },
  
  /**
   * Send a chat message with RAG enabled by default
   * @param {Object} payload - The message payload
   * @returns {Promise<Object>} Chat response
   */
  sendChatMessage: async (payload) => {
    try {
      // Ensure RAG is enabled by default
      const requestPayload = {
        ...payload,
        use_rag: true
      };
      
      const response = await api.post(`/chat`, requestPayload);
      return response.data;
    } catch (error) {
      console.error('Error sending RAG-enabled message:', error);
      throw error;
    }
  },
  
  /**
   * Delete a chat session
   * @param {string} sessionId - ID of the session to delete
   * @returns {Promise<Object>} Result of the deletion
   */
  deleteSession: async (sessionId) => {
    try {
      console.log(`Preparing to delete session: ${sessionId}`);
      
      // Get auth headers and ensure we have a token
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No authentication token found for session deletion');
        throw new Error('Authentication required to delete sessions');
      }
      
      // Extract user ID from token to include in headers
      let userId = null;
      try {
        const decoded = jwtDecode(token);
        userId = decoded.sub || decoded.user_id || decoded.id;
        console.log(`Extracted user ID from token for deletion: ${userId}`);
      } catch (e) {
        console.warn('Could not extract user ID from token', e);
      }
      
      // Build headers with authentication information
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
      
      // Add user ID to headers if available
      if (userId) {
        headers['X-User-ID'] = userId;
      }
      
      console.log(`Sending DELETE request to /chat/sessions/${sessionId}`);
      console.log('Using authentication headers:', JSON.stringify(headers));
      
      // Use fetch with the DELETE method explicitly
      const response = await fetch(`${API_URL}/chat/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: headers,
        // Don't include body for DELETE requests to avoid issues with some servers
      });
      
      console.log(`Received response status: ${response.status} for session deletion: ${sessionId}`);
      
      // Handle error responses with more detailed logging
      if (!response.ok) {
        let errorText = '';
        try {
          // Try to parse error response as JSON
          const errorData = await response.json();
          errorText = errorData.detail || JSON.stringify(errorData);
        } catch (e) {
          // If not JSON, get as text
          errorText = await response.text();
        }
        
        console.error(`Error deleting session (${response.status}):`, errorText);
        throw new Error(`Failed to delete session: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      // Parse the response
      const data = await response.json();
      console.log('Delete session response:', data);
      
      // Log deletion results
      if (data.messages_deleted !== undefined) {
        console.log(`Successfully deleted session ${sessionId} with ${data.messages_deleted} messages`);
      } else {
        console.log(`Successfully deleted session ${sessionId}`);
      }
      
      return data;
    } catch (error) {
      console.error('Error deleting chat session:', error);
      
      // Add more specific error information
      if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        console.error('Network error: Could not connect to the server');
      } else if (error.name === 'AbortError') {
        console.error('Request was aborted');
      } else if (error.message.includes('401') || error.message.includes('403')) {
        console.error('Authentication or authorization error when deleting session');
      }
      
      throw error;
    }
  },
  
  /**
   * Get messages for a specific chat session
   * @param {string} sessionId - ID of the chat session
   * @param {number} limit - Maximum number of messages to return
   * @param {number} offset - Offset for pagination
   * @returns {Promise<Array>} List of messages in the session
   */
  getSessionMessages: async (sessionId, limit = 50, offset = 0) => {
    try {
      const response = await api.get(`/chat/sessions/${sessionId}/messages`, {
        params: { limit, offset },
      });
      return response.data.messages || [];
    } catch (error) {
      console.error('Error fetching session messages:', error);
      throw error;
    }
  },
  
  /**
   * Get LLM configuration
   * @returns {Promise<Object>} LLM configuration
   */
  getLLMConfig: async () => {
    try {
      const response = await api.get(`/config`);
      return response.data.llm || {};
    } catch (error) {
      console.error('Error fetching LLM config:', error);
      return {};
    }
  }
};

export default chatService; 