import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Shield, PanelLeft, X, RefreshCw } from 'lucide-react';
import ChatHistory from '../components/chat/ChatHistory';
import LoadingOverlay from '../components/ui/LoadingOverlay';
import useMediaQuery from '../hooks/useMediaQuery';
import chatService from '../services/chatService';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ChatControls from '../components/chat/ChatControls';
import { Box, Flex, Heading, Button, IconButton, Text, Spinner, VStack, HStack, useToast, useColorModeValue } from '@chakra-ui/react';
import MessageInput from '../components/MessageInput';
import ChatContainer from '../components/chat/ChatContainer';
import { motion, AnimatePresence } from 'framer-motion';
import { getErrorMessage } from '../lib/utils';

// Initial message for new chats
const initialMessage = {
  role: "assistant",
  content:
    "Hello! I'm your GRC AI Assistant. I can help you with governance, risk, and compliance questions. How can I assist you today?",
};

// Sample suggested questions
const suggestedQuestions = [
  "What are the key requirements for SOC 2 compliance?",
  "How do I conduct a risk assessment for my organization?",
  "Explain the main components of a governance framework",
  "What are the GDPR requirements for data processing?",
];

/**
 * Chat page component
 */
const ChatPage = () => {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([initialMessage]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [error, setError] = useState(null);
  const [reasoningNodeId, setReasoningNodeId] = useState(null);
  const [agentProgress, setAgentProgress] = useState(null);
  const [currentRequestId, setCurrentRequestId] = useState(null);
  const [activeStreamId, setActiveStreamId] = useState(null);
  
  const messagesEndRef = useRef(null);
  const isMobile = useMediaQuery('(max-width: 768px)');
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  // Theme colors
  const accentColor = '#4415b6';
  const accentHoverColor = '#3a1296';
  const sidebarBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const headerBg = useColorModeValue('white', 'gray.800');
  const chatBg = useColorModeValue('gray.50', 'gray.900');
  const errorBg = useColorModeValue('red.100', 'red.900');
  const errorColor = useColorModeValue('red.800', 'red.200');
  const errorBorderColor = useColorModeValue('red.200', 'red.700');
  const textColor = useColorModeValue('gray.800', 'gray.200');
  const secondaryTextColor = useColorModeValue('gray.500', 'gray.400');
  const buttonHoverBg = useColorModeValue('purple.50', 'purple.900');
  const buttonHoverBorderColor = useColorModeValue('purple.300', 'purple.600');
  const questionButtonBg = useColorModeValue('white', 'gray.700');
  const questionButtonBorder = useColorModeValue('gray.200', 'gray.600');
  const loadingBg = useColorModeValue('blue.50', 'blue.900');
  const loadingBorderColor = useColorModeValue('blue.200', 'blue.700');
  const loadingTextColor = useColorModeValue('blue.700', 'blue.200');
  const fixedInputBg = useColorModeValue('white', 'gray.800');

  // Stream management
  const streamAbortControllerRef = useRef(null);

  // Close sidebar on mobile by default
  useEffect(() => {
    if (isMobile) {
      setIsSidebarOpen(false);
    } else {
      setIsSidebarOpen(true);
    }
  }, [isMobile]);

  // Redirect to login page if user is not authenticated
  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Fetch chat sessions on component mount
  useEffect(() => {
    fetchSessions();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Track agent progress if there's an active execution
  useEffect(() => {
    let timer = null;
    
    if (agentProgress && agentProgress.execution_id && agentProgress.status !== 'completed' && agentProgress.status !== 'failed') {
      timer = setInterval(async () => {
        try {
          const progress = await chatService.getAgentProgress(agentProgress.execution_id);
          if (progress) {
            setAgentProgress(progress);
            
            // If there's a current tree node, update the reasoning node ID
            if (progress.current_tree_node) {
              setReasoningNodeId(progress.current_tree_node);
            }
            
            // If completed or failed, clear the interval
            if (progress.status === 'completed' || progress.status === 'failed') {
              clearInterval(timer);
            }
          }
        } catch (err) {
          console.error('Error fetching agent progress:', err);
        }
      }, 1000);
    }
    
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [agentProgress]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      console.log('🧹 ChatPage unmounting, cleaning up');
    };
  }, []);

  const fetchSessions = async () => {
    setError(null);
    try {
      const fetchedSessions = await chatService.getChatSessions();
      
      if (fetchedSessions && Array.isArray(fetchedSessions) && fetchedSessions.length > 0) {
        // Process and deduplicate sessions
        const uniqueSessions = [];
        const sessionIds = new Set();
        
        fetchedSessions.forEach(session => {
          if (!session) return; // Skip null or undefined sessions
          
          const sessionId = session.session_id || session.id;
          if (!sessionId) return; // Skip sessions without ID
          
          if (!sessionIds.has(sessionId)) {
            sessionIds.add(sessionId);
            
            // Transform the backend format to our frontend format
            uniqueSessions.push({
              id: sessionId,
              title: session.title || "New Conversation",
              date: session.last_message_time ? new Date(session.last_message_time).toLocaleString() : "Just now",
              preview: session.preview || "",
              message_count: session.message_count || 0
            });
          }
        });
        
        setSessions(uniqueSessions);
        
        // Select the first session if we have any
        if (uniqueSessions.length > 0) {
          handleSelectSession(uniqueSessions[0].id);
        } else {
          await handleNewSession();
        }
      } else {
        // If no sessions, create a new one
        console.log('No existing sessions found, creating a new session');
        await handleNewSession();
      }
    } catch (err) {
      console.error('Failed to fetch chat sessions:', err);
      let errorMessage = 'Failed to load chat sessions. Creating a new session.';
      let errorType = 'session_load_error';
      let shouldCreateFallback = true;
      let shouldDisplayError = false;
      
      if (err.response) {
        const status = err.response.status;
        if (status === 401) {
          errorMessage = 'Authentication required to access chat sessions.';
          errorType = 'auth_error';
          shouldDisplayError = true;
          // Redirect to login page if unauthorized
          navigate('/login');
          return;
        } else if (status === 403) {
          errorMessage = 'You do not have permission to access these chat sessions.';
          errorType = 'permission_error';
          shouldDisplayError = true;
        } else if (status === 404) {
          errorMessage = 'User chat history not found. Starting a new session.';
          errorType = 'not_found_error';
        } else if (status === 500) {
          errorMessage = 'Server error while loading sessions. Creating a new session.';
          errorType = 'server_error';
        } else if (status === 400) {
          // Check if this is a specific error related to missing chat history
          const errorDetail = err.response.data?.detail || '';
          if (errorDetail.includes('history') || errorDetail.includes('sessions')) {
            errorMessage = 'No chat history found. Starting a new conversation.';
            errorType = 'no_history_error';
          }
        }
      } else if (err.request) {
        errorMessage = 'Network error. Unable to connect to the chat server.';
        errorType = 'network_error';
      }
      
      // Only set the error in state if we should display it
      if (shouldDisplayError) {
        setError(errorMessage);
        
        // Show toast notification for better user feedback
        toast({
          title: 'Chat History',
          description: errorMessage,
          status: 'info',
          duration: 5000,
          isClosable: true,
        });
      } else {
        // Clear any existing error
        setError(null);
      }
      
      // Only create fallback sessions if not redirecting due to auth error
      // and if we should create a fallback
      if (shouldCreateFallback) {
        console.log('Creating fallback session due to error:', errorType);
        const fallbackSessionId = Date.now().toString();
        setSessions([{
          id: fallbackSessionId,
          title: "New Conversation",
          date: "Just now",
          preview: "",
          messages: [initialMessage],
          is_fallback: true
        }]);
        
        setActiveSessionId(fallbackSessionId);
        setMessages([initialMessage]);
      }
    }
  };

  // Enhanced message sending with improved streaming
  const handleSendMessage = async (content) => {
    console.log('🎯 handleSendMessage called with content:', content);
    console.log('🔄 Current isLoading state:', isLoading);
    
    if (!content.trim() || isLoading) {
      console.log('❌ Message rejected - empty content or already loading');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    // Generate request ID for this message
    const requestId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setCurrentRequestId(requestId);
    
    console.log('✅ Starting message processing with requestId:', requestId);
    
    try {
      // Create a new user message
      const userMessage = {
        role: "user",
        content: content,
        timestamp: Date.now(),
        id: `user_${Date.now()}`
      };
      
      // Add to UI immediately
      const updatedMessages = [...messages, userMessage];
      
      // Create a temporary assistant message with streamlined metadata
      const tempAssistantMessage = {
        role: "assistant",
        content: "",
        isGenerating: true,
        processingState: "Initializing request...",
        requestId: requestId,
        timestamp: Date.now(),
        id: `assistant_${Date.now()}`,
        metadata: {
          internal_thoughts: "",
          processingSteps: [],
          startTime: Date.now(),
          requestId: requestId,
          isConnected: true,
          streamId: null
        }
      };
      
      // Add both messages to the UI
      setMessages([...updatedMessages, tempAssistantMessage]);
      
      // Update the session with the user message
      if (activeSessionId) {
        updateSessionWithMessages(activeSessionId, updatedMessages);
      }
      
      // Prepare messages for the API call
      const messagesForAPI = updatedMessages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      console.log('📞 Starting streamlined streaming request');
      
      // Create abort controller for this stream
      streamAbortControllerRef.current = new AbortController();
      
      // Use the enhanced streaming API with simplified chunk handling
      const result = await chatService.sendMessageStreaming(
        activeSessionId,
        content,
        (chunkData) => {
          // Streamlined chunk handling - delegate complex UI logic to StreamingMessage
          setMessages(currentMessages => {
            const updatedMessages = [...currentMessages];
            const lastMessage = updatedMessages[updatedMessages.length - 1];
            
            if (lastMessage.role === "assistant" && lastMessage.isGenerating) {
              // Handle different chunk types with simplified logic
              switch (chunkData.type) {
                case 'start':
                  lastMessage.processingState = "Connection established, starting processing...";
                  lastMessage.metadata.streamStarted = true;
                  lastMessage.metadata.backendRequestId = chunkData.request_id;
                  lastMessage.metadata.streamId = chunkData.streamId;
                  setActiveStreamId(chunkData.streamId);
                  break;

                case 'processing':
                  lastMessage.processingState = chunkData.state || "Processing...";
                  
                  if (chunkData.internal_thoughts) {
                    lastMessage.metadata.internal_thoughts = chunkData.internal_thoughts;
                  }
                  
                  // Handle agent steps differently from regular processing steps
                  if (chunkData.isAgentStep) {
                    // Agent processing steps
                    if (!lastMessage.metadata.agentSteps) {
                      lastMessage.metadata.agentSteps = [];
                    }
                    
                    const agentStepData = {
                      step: chunkData.step,
                      message: chunkData.state,
                      details: chunkData.details,
                      progress: chunkData.progress,
                      executionId: chunkData.executionId,
                      status: 'in_progress',
                      timestamp: chunkData.timestamp,
                      isAgentStep: true
                    };
                    
                    // Update or add agent step
                    const existingStepIndex = lastMessage.metadata.agentSteps.findIndex(
                      step => step.step === chunkData.step
                    );
                    
                    if (existingStepIndex >= 0) {
                      lastMessage.metadata.agentSteps[existingStepIndex] = agentStepData;
                    } else {
                      lastMessage.metadata.agentSteps.push(agentStepData);
                    }
                    
                    // Update processing state with agent-specific messaging
                    lastMessage.processingState = `🤖 Agent: ${chunkData.state}`;
                    
                  } else {
                    // Regular processing steps (RAG/LLM)
                    if (chunkData.step_number && chunkData.total_steps) {
                      if (!lastMessage.metadata.processingSteps) {
                        lastMessage.metadata.processingSteps = [];
                      }
                      
                      const stepData = {
                        step: chunkData.step,
                        stepNumber: chunkData.step_number,
                        totalSteps: chunkData.total_steps,
                        message: chunkData.state,
                        details: chunkData.details,
                        status: 'in_progress',
                        timestamp: chunkData.timestamp
                      };
                      
                      // Update or add step
                      const existingStepIndex = lastMessage.metadata.processingSteps.findIndex(
                        step => step.step === chunkData.step
                      );
                      
                      if (existingStepIndex >= 0) {
                        lastMessage.metadata.processingSteps[existingStepIndex] = stepData;
                      } else {
                        lastMessage.metadata.processingSteps.push(stepData);
                      }
                    }
                  }
                  break;

                case 'token':
                  if (chunkData.content) {
                    // Simple token accumulation - let StreamingMessage handle display logic
                    lastMessage.content = chunkData.accumulated || (lastMessage.content + chunkData.content);
                    lastMessage.processingState = "Generating response...";
                  }
                  break;

                case 'end':
                  // Completion handling
                  lastMessage.isGenerating = false;
                  lastMessage.processingState = "Complete";
                  setActiveStreamId(null);
                  
                  if (chunkData.message) {
                    lastMessage.content = chunkData.message;
                  }
                  
                  // Store metadata and sources
                  lastMessage.metadata = {
                    ...lastMessage.metadata,
                    ...(chunkData.metadata || {}),
                    completed: true,
                    endTime: Date.now(),
                    // Store sources from the completion event
                    sources: chunkData.sources || [],
                    contextUsed: chunkData.contextUsed,
                    contextQuality: chunkData.contextQuality,
                    hallucination_risk: chunkData.hallucination_risk,
                    internalThoughts: chunkData.internalThoughts,
                    toolsUsed: chunkData.toolsUsed,
                    agentUsed: chunkData.agentUsed,
                    model: chunkData.model,
                    sessionId: chunkData.sessionId
                  };
                  
                  // Mark all steps as completed
                  if (lastMessage.metadata.processingSteps) {
                    lastMessage.metadata.processingSteps.forEach(step => {
                      if (step.status === 'in_progress') {
                        step.status = 'completed';
                      }
                    });
                  }
                  break;

                case 'error':
                  // Error handling
                  lastMessage.isGenerating = false;
                  lastMessage.processingState = "Error occurred";
                  setActiveStreamId(null);
                  
                  lastMessage.metadata.error = {
                    message: chunkData.message,
                    error_code: chunkData.error_code,
                    request_id: chunkData.request_id
                  };
                  
                  if (!lastMessage.content.trim()) {
                    lastMessage.content = `❌ ${chunkData.message}`;
                  }
                  break;

                default:
                  console.warn('Unknown chunk type:', chunkData.type, chunkData);
              }
              
              // Update connection status
              lastMessage.metadata.isConnected = true;
              lastMessage.metadata.lastActivity = Date.now();
            }
            
            return updatedMessages;
          });
        },
        {
          model: 'gpt-4',
          temperature: 0.7,
          max_tokens: 2048,
          includeContext: true,
          use_agent: true,
          stream: true,
          timeout: 300000 // 5 minutes
        },
        messagesForAPI,
        requestId
      );
      
      console.log('✅ Streamlined streaming completed successfully:', result);
      
      // Final cleanup and session update
      if (activeSessionId) {
        setMessages(currentMessages => {
          updateSessionWithMessages(activeSessionId, currentMessages);
          return currentMessages;
        });
      }
      
    } catch (error) {
      console.error('💥 Streaming failed:', error);
      setError(getErrorMessage(error));
      
      // Update the last message to show error state
      setMessages(currentMessages => {
        const updatedMessages = [...currentMessages];
        const lastMessage = updatedMessages[updatedMessages.length - 1];
        
        if (lastMessage && lastMessage.role === "assistant" && lastMessage.isGenerating) {
          lastMessage.isGenerating = false;
          lastMessage.processingState = "Error occurred";
          lastMessage.metadata.error = {
            message: getErrorMessage(error),
            timestamp: Date.now()
          };
          
          if (!lastMessage.content.trim()) {
            lastMessage.content = `❌ ${getErrorMessage(error)}`;
          }
        }
        
        return updatedMessages;
      });
    } finally {
      setIsLoading(false);
      setCurrentRequestId(null);
      setActiveStreamId(null);
      streamAbortControllerRef.current = null;
    }
  };

  // Enhanced stop streaming function
  const handleStopStreaming = useCallback(() => {
    console.log('🛑 Stopping current stream');
    
    if (activeStreamId) {
      chatService.stopStream(activeStreamId);
    } else {
      chatService.stopAllStreams();
    }
    
    if (streamAbortControllerRef.current) {
      streamAbortControllerRef.current.abort();
    }
    
    setIsLoading(false);
    setActiveStreamId(null);
    
    // Update the last message to show stopped state
    setMessages(currentMessages => {
      const updatedMessages = [...currentMessages];
      const lastMessage = updatedMessages[updatedMessages.length - 1];
      
      if (lastMessage && lastMessage.role === "assistant" && lastMessage.isGenerating) {
        lastMessage.isGenerating = false;
        lastMessage.processingState = "Stopped by user";
        lastMessage.metadata.stopped = true;
        lastMessage.metadata.stopTime = Date.now();
      }
      
      return updatedMessages;
    });
  }, [activeStreamId]);

  // Enhanced retry function
  const handleRetryMessage = useCallback((messageIndex) => {
    console.log('🔄 Retrying message at index:', messageIndex);
    
    // Find the user message that triggered this response
    const userMessage = messages[messageIndex - 1];
    if (userMessage && userMessage.role === 'user') {
      // Remove the failed assistant message
      const updatedMessages = messages.slice(0, messageIndex);
      setMessages(updatedMessages);
      
      // Retry with the same content
      handleSendMessage(userMessage.content);
    }
  }, [messages, handleSendMessage]);

  const handleSelectSession = async (sessionId) => {
    setError(null);
    setIsLoading(true);
    
    try {
      // Fetch messages for this session
      const sessionMessages = await chatService.getSessionMessages(sessionId);
      
      if (sessionMessages && Array.isArray(sessionMessages) && sessionMessages.length > 0) {
        // Transform messages to the correct format if needed
        const formattedMessages = sessionMessages.map(msg => ({
          role: msg.role || msg.message_role,
          content: msg.content || msg.message_text,
        }));
        
        setMessages(formattedMessages);
      } else {
        // If no messages, add the initial welcome message
        setMessages([initialMessage]);
      }
      
      // Update the active session ID
      setActiveSessionId(sessionId);
    } catch (err) {
      console.error('Failed to load chat messages:', err);
      let errorMessage = 'Failed to load messages for this conversation.';
      
      if (err.response) {
        const status = err.response.status;
        if (status === 401) {
          errorMessage = 'Authentication required to access messages.';
          // Redirect to login page if unauthorized
          navigate('/login');
          return;
        } else if (status === 404) {
          errorMessage = 'Chat session not found. It may have been deleted.';
        } else if (status === 500) {
          errorMessage = 'Server error while loading messages.';
        }
      } else if (err.request) {
        errorMessage = 'Network error. Unable to connect to the chat server.';
      }
      
      setError(errorMessage);
      
      // Set empty messages with welcome message
      setMessages([initialMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewSession = async (force = false) => {
    setError(null);
    setIsLoading(true);
    
    // Check if there's already an empty conversation we can reuse
    if (!force) {
      const currentSession = sessions.find(s => s.id === activeSessionId);
      const hasNoUserMessages = messages.every(m => m.role !== 'user');
      
      // If we already have an active session with no user messages, just reset it
      if (currentSession && hasNoUserMessages) {
        setMessages([initialMessage]);
        setIsLoading(false);
        return activeSessionId;
      }
    }
    
    try {
      console.log('Creating new chat session via API...');
      // Create a new session
      const response = await chatService.createSession();
      const newSessionId = response.session_id;
      
      if (!newSessionId) {
        console.error('No session ID returned from createSession API call');
        throw new Error('Invalid session ID returned from server');
      }
      
      console.log('New session created successfully:', newSessionId);
      
      // Add the new session to our list
      const newSession = {
        id: newSessionId,
        title: "New Conversation",
        date: new Date().toLocaleString(),
        preview: "",
        message_count: 0
      };
      
      setSessions([newSession, ...sessions]);
      setActiveSessionId(newSessionId);
      setMessages([initialMessage]);
      
      return newSessionId;
    } catch (err) {
      console.error('Failed to create new session:', err);
      let errorMessage = 'Failed to create a new conversation.';
      let retryAttempted = false;
      let shouldDisplayError = false;
      
      if (err.response) {
        const status = err.response.status;
        if (status === 401) {
          errorMessage = 'Authentication required to create a new session.';
          shouldDisplayError = true;
          // Redirect to login page if unauthorized
          navigate('/login');
          return null;
        } else if (status === 429) {
          errorMessage = 'Too many requests. Please try again in a moment.';
          shouldDisplayError = true;
        } else if (status === 500) {
          errorMessage = 'Server error while creating a new session.';
          
          // Try once more if server error
          if (!retryAttempted) {
            retryAttempted = true;
            console.log('Retrying session creation after server error...');
            try {
              // Short delay before retry
              await new Promise(resolve => setTimeout(resolve, 500));
              const retryResponse = await chatService.createSession();
              const newSessionId = retryResponse.session_id;
              
              if (newSessionId) {
                // Success on retry
                const newSession = {
                  id: newSessionId,
                  title: "New Conversation",
                  date: new Date().toLocaleString(),
                  preview: "",
                  message_count: 0
                };
                
                setSessions([newSession, ...sessions]);
                setActiveSessionId(newSessionId);
                setMessages([initialMessage]);
                
                setIsLoading(false);
                return newSessionId;
              }
            } catch (retryErr) {
              console.error('Retry also failed:', retryErr);
            }
          }
        }
      } else if (err.request) {
        errorMessage = 'Network error. Unable to connect to the chat server.';
      }
      
      // Only set the error if we should display it
      if (shouldDisplayError) {
        setError(errorMessage);
        
        // Show toast notification for better user feedback
        toast({
          title: 'New Chat Session',
          description: errorMessage,
          status: 'warning',
          duration: 5000,
          isClosable: true,
        });
      } else {
        // Clear any existing error
        setError(null);
      }
      
      // Create a fallback session ID with a consistent format
      const fallbackSessionId = `fallback-${Date.now()}`;
      console.log('Creating fallback session with ID:', fallbackSessionId);
      
      const fallbackSession = {
        id: fallbackSessionId,
        title: "New Conversation",
        date: new Date().toLocaleString(),
        preview: "",
        is_fallback: true, // Mark this as a fallback session
      };
      
      setSessions([fallbackSession, ...sessions]);
      setActiveSessionId(fallbackSessionId);
      setMessages([initialMessage]);
      
      return fallbackSessionId;
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    setError(null);
    
    // For debugging purposes
    console.log('Attempting to delete session:', sessionId);
    
    try {
      // Find the session we want to delete
      const sessionToDelete = sessions.find(session => session.id === sessionId);
      
      if (!sessionToDelete) {
        console.error('Could not find session to delete:', sessionId);
        toast({
          title: 'Delete Error',
          description: 'Could not find the conversation to delete.',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      
      console.log('Found session to delete:', sessionToDelete);
      
      // Show loading state to indicate deletion in progress
      setIsLoading(true);
      
      // First, remove from local state to update UI immediately (for better responsiveness)
      const updatedSessions = sessions.filter(session => session.id !== sessionId);
      setSessions(updatedSessions);
      
      // If we deleted the active session, switch to another one immediately for better UX
      if (sessionId === activeSessionId) {
        if (updatedSessions.length > 0) {
          handleSelectSession(updatedSessions[0].id);
        } else {
          handleNewSession();
        }
      }
      
      // If the session was a fallback session, we don't need to delete from server
      const isFallbackSession = sessionToDelete.is_fallback === true || 
                                sessionId.startsWith('fallback-');
      
      if (isFallbackSession) {
        console.log('Skipping server delete for fallback session:', sessionId);
        
        // Short delay to ensure UI updates are visible
        await new Promise(resolve => setTimeout(resolve, 300));
        setIsLoading(false);
        
        toast({
          title: 'Conversation Deleted',
          description: 'The conversation has been removed.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        
        return;
      }
      
      // For regular sessions, attempt to delete from server
      let serverDeletionSuccess = false;
      let errorDetails = null;
      
      try {
        // Add a small delay to ensure UI updates first
        await new Promise(resolve => setTimeout(resolve, 300));
        
        console.log('Deleting session from server:', sessionId);
        const result = await chatService.deleteSession(sessionId);
        console.log('Server deletion response:', result);
        
        if (result && result.messages_deleted !== undefined) {
          console.log(`Deleted ${result.messages_deleted} messages from session ${sessionId}`);
        }
        
        serverDeletionSuccess = true;
      } catch (serverError) {
        console.error('Server deletion failed:', serverError);
        errorDetails = serverError?.message || 'Unknown server error';
        
        // Try one more time with a slight delay in case it was a temporary issue
        try {
          console.log('Retrying session deletion after failure...');
          await new Promise(resolve => setTimeout(resolve, 500)); // 500ms delay
          const result = await chatService.deleteSession(sessionId);
          console.log('Server deletion retry response:', result);
          serverDeletionSuccess = true;
        } catch (retryError) {
          console.error('Server deletion retry also failed:', retryError);
          // We'll continue with UI updates even though server deletion failed
        }
      } finally {
        // Always turn off loading state
        setIsLoading(false);
      }
      
      // Show appropriate toast based on server deletion success
      if (serverDeletionSuccess) {
        toast({
          title: 'Conversation Deleted',
          description: 'The conversation has been deleted.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        toast({
          title: 'Partial Success',
          description: `The conversation was removed from your view, but the server reported an error: ${errorDetails}`,
          status: 'warning',
          duration: 5000,
          isClosable: true,
        });
      }
      
    } catch (error) {
      console.error('Error in handleDeleteSession:', error);
      setIsLoading(false);
      
      // Make sure we still update the UI even if there was an error
      const updatedSessions = sessions.filter(session => session.id !== sessionId);
      setSessions(updatedSessions);
      
      // If we deleted the active session, switch to another one
      if (sessionId === activeSessionId) {
        if (updatedSessions.length > 0) {
          handleSelectSession(updatedSessions[0].id);
        } else {
          handleNewSession();
        }
      }
      
      toast({
        title: 'Note',
        description: 'The conversation was removed from your history, but there might have been an issue with the server.',
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const updateSessionWithMessages = (sessionId, updatedMessages) => {
    // Update the sessions list with new message information
    const updatedSessions = sessions.map(session => {
      if (session.id === sessionId) {
        // Get the last message for preview (from either user or assistant)
        const lastMessage = updatedMessages.length > 0 ? updatedMessages[updatedMessages.length - 1] : null;
        
        // Create preview text from the last message
        const preview = lastMessage 
          ? lastMessage.content.substring(0, 60) + (lastMessage.content.length > 60 ? '...' : '') 
          : '';
        
        return {
          ...session,
          preview,
          message_count: updatedMessages.length,
          date: new Date().toLocaleString()
        };
      }
      return session;
    });
    
    setSessions(updatedSessions);
  };

  const generateSessionTitle = (message) => {
    // Create a title from the user's message
    // Truncate long messages, capitalize first letter
    if (!message) return "New Conversation";
    
    // Clean up message - remove excess whitespace
    const cleanMessage = message.trim().replace(/\s+/g, ' ');
    
    // Truncate if too long
    const truncated = cleanMessage.length > 50 
      ? cleanMessage.substring(0, 47) + '...'
      : cleanMessage;
      
    // Capitalize first letter
    return truncated.charAt(0).toUpperCase() + truncated.slice(1);
  };
  
  const updateSessionTitle = (sessionId, title) => {
    // Update the title of a session
    setSessions(prevSessions => 
      prevSessions.map(session => 
        session.id === sessionId 
          ? { ...session, title }
          : session
      )
    );
    
    // If this is a real session (not a fallback), update on the server too
    const session = sessions.find(s => s.id === sessionId);
    if (session && !session.is_fallback) {
      try {
        // This could be implemented with a real API call if backend supports it
        console.log(`Updating session title on server: ${sessionId} => "${title}"`);
        // Async function to update title on server could go here
        // e.g., chatService.updateSessionTitle(sessionId, title);
      } catch (err) {
        console.error('Failed to update session title on server:', err);
        // Continue anyway as this is not critical
      }
    }
  };

  const handleSuggestedQuestion = (question) => {
    handleSendMessage(question);
  };

  return (
    <Box h="100vh" flexDirection="column">
      {/* Header with sidebar toggle */}
      <Box
        bg={headerBg}
        borderBottomWidth="1px"
        borderBottomColor={borderColor}
        px={4}
        py={2}
        display="flex"
        alignItems="center"
        justifyContent="space-between"
        zIndex="3"
      >
        <HStack spacing={3}>
          <IconButton
            icon={<PanelLeft size={20} />}
            variant="ghost"
            size="sm"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            aria-label="Toggle sidebar"
            color={textColor}
          />
          <Text fontSize="lg" fontWeight="semibold" color={textColor}>
            RegulAIte
          </Text>
        </HStack>
        
      </Box>
            
      <Flex flex="1" h="calc(100vh - 60px)" overflow="hidden">
        {/* Chat history sidebar */}
        <Box
          w={isSidebarOpen ? { base: "full", md: "300px" } : "0px"}
          h="full"
          bg={sidebarBg}
          borderRightWidth="1px"
          borderRightColor={borderColor}
          position={{ base: isSidebarOpen ? "absolute" : "static", md: "static" }}
          zIndex="2"
          transition="width 0.3s"
          overflow="hidden"
          display={isSidebarOpen ? "block" : "none"}
          boxShadow={isMobile && isSidebarOpen ? "0 0 15px rgba(0,0,0,0.2)" : "none"}
        >
          <ChatHistory
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={handleSelectSession}
            onNewSession={handleNewSession}
            onDeleteSession={handleDeleteSession}
          />
        </Box>
        
        {/* Main chat area */}
        <Flex 
          flex="1" 
          flexDirection="column" 
          h="100%" 
          overflow="hidden"
          bg={chatBg}
        >
                   
          {/* Error notification - Simplified */}
          {error && (
            <Box 
              bg={errorBg} 
              color={errorColor} 
              p={3} 
              borderBottomWidth="1px" 
              borderBottomColor={errorBorderColor}
            >
              <Flex align="center" justify="space-between">
                <Text fontSize="sm">{error}</Text>
                <Button 
                  size="xs" 
                  onClick={() => setError(null)}
                  variant="ghost"
                  color={errorColor}
                >
                  ×
                </Button>
              </Flex>
            </Box>
          )}
          
          {/* Welcome header for new chats - Simplified */}
          {messages.length <= 1 && (
            <Box textAlign="center" my={8} px={6}>
              <Heading as="h2" size="lg" mb={4} color={textColor}>
                How can I help you today?
              </Heading>
              <Text color={secondaryTextColor} mb={6}>
                Ask me about governance, risk, and compliance
              </Text>
              
              {/* Suggested questions - Simplified */}
              <VStack spacing={2} maxW="md" mx="auto">
                {suggestedQuestions.slice(0, 3).map((question, index) => (
                  <Button
                    key={index}
                    size="sm"
                    variant="outline"
                    width="full"
                    onClick={() => handleSuggestedQuestion(question)}
                    textAlign="left"
                    justifyContent="flex-start"
                  >
                    {question}
                  </Button>
                ))}
              </VStack>
            </Box>
          )}
          
          {/* Chat Container with new component hierarchy */}
          <ChatContainer
            messages={messages}
            isLoading={isLoading}
            onRetry={handleRetryMessage}
            onStop={handleStopStreaming}
          />
          
          {/* Streaming Stats Display */}
          {activeStreamId && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-xs text-gray-500 text-center p-2"
            >
              Active Stream: {activeStreamId} | 
              Active Streams: {chatService.getStreamingStats().activeStreams}
            </motion.div>
          )}
          
          {/* Fixed chat input area at bottom */}
          <Box
            position="fixed"
            bottom="0"
            left={isSidebarOpen && !isMobile ? { base: "0", md: "300px" } : "0"}
            right="0"
            bg={fixedInputBg}
            borderTopWidth="1px"
            borderTopColor={borderColor}
            zIndex="1"
            transition="left 0.3s"
          >
            <MessageInput
              onSendMessage={handleSendMessage}
              disabled={isLoading}
              placeholder={isLoading ? "AI is thinking..." : "Type your message..."}
              showStopButton={isLoading && activeStreamId}
              onStop={handleStopStreaming}
            />
          </Box>
        </Flex>
      </Flex>
      
      {/* Loading Overlay for critical operations */}
      <LoadingOverlay
        isVisible={isLoading && !currentRequestId} // Show for session operations, not chat messages
        message="Setting up your session..."
        subMessage="Please wait while we prepare your chat environment."
      />
    </Box>
  );
};

export default ChatPage; 