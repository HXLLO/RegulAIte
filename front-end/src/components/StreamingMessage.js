import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AgentLogsViewer from './AgentLogsViewer';

/**
 * Enhanced Streaming Message Component
 * Handles real-time streaming updates with visual feedback
 * Focused on UI presentation, delegates streaming logic to services
 */
const StreamingMessage = ({ 
  message, 
  isStreaming = false, 
  onRetry = null,
  onStop = null,
  className = '' 
}) => {
  const [displayContent, setDisplayContent] = useState('');
  const [processingState, setProcessingState] = useState('');
  const [showCursor, setShowCursor] = useState(false);
  const [isInternalThoughtsExpanded, setIsInternalThoughtsExpanded] = useState(false);
  const [streamingStats, setStreamingStats] = useState({
    tokensReceived: 0,
    startTime: null,
    lastTokenTime: null
  });

  const contentRef = useRef(null);
  const cursorIntervalRef = useRef(null);
  const lastContentRef = useRef('');
  const lastContentLengthRef = useRef(0);

  // Animate content updates with better performance
  useEffect(() => {
    if (message.content !== lastContentRef.current) {
      setDisplayContent(message.content);
      lastContentRef.current = message.content;
      
      // Update streaming stats only if content actually grew (new tokens)
      if (isStreaming && message.content.length > lastContentLengthRef.current) {
        const newTokens = message.content.length - lastContentLengthRef.current;
        setStreamingStats(prev => ({
          ...prev,
          tokensReceived: prev.tokensReceived + newTokens,
          lastTokenTime: Date.now(),
          startTime: prev.startTime || Date.now()
        }));
        lastContentLengthRef.current = message.content.length;
      }
    }
  }, [message.content, isStreaming]);

  // Handle processing state updates
  useEffect(() => {
    if (message.processingState) {
      setProcessingState(message.processingState);
    }
  }, [message.processingState]);

  // Manage cursor blinking during streaming
  useEffect(() => {
    if (isStreaming) {
      setShowCursor(true);
      cursorIntervalRef.current = setInterval(() => {
        setShowCursor(prev => !prev);
      }, 500);
    } else {
      setShowCursor(false);
      if (cursorIntervalRef.current) {
        clearInterval(cursorIntervalRef.current);
        cursorIntervalRef.current = null;
      }
    }

    return () => {
      if (cursorIntervalRef.current) {
        clearInterval(cursorIntervalRef.current);
      }
    };
  }, [isStreaming]);

  // Auto-scroll to bottom when content updates
  useEffect(() => {
    if (contentRef.current && isStreaming) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [displayContent, isStreaming]);

  // Reset stats when streaming starts/stops
  useEffect(() => {
    if (isStreaming && streamingStats.startTime === null) {
      setStreamingStats({
        tokensReceived: 0,
        startTime: Date.now(),
        lastTokenTime: Date.now()
      });
      lastContentLengthRef.current = 0;
    } else if (!isStreaming) {
      // Keep final stats but mark as completed
      setStreamingStats(prev => ({
        ...prev,
        completed: true
      }));
    }
  }, [isStreaming]);

  // Calculate streaming metrics
  const streamingMetrics = useMemo(() => {
    if (!streamingStats.startTime || !streamingStats.lastTokenTime) {
      return null;
    }

    const duration = (streamingStats.lastTokenTime - streamingStats.startTime) / 1000;
    const tokensPerSecond = duration > 0 ? (streamingStats.tokensReceived / duration).toFixed(1) : 0;

    return {
      duration: duration.toFixed(1),
      tokensPerSecond,
      totalTokens: streamingStats.tokensReceived
    };
  }, [streamingStats]);

  // Render processing steps with enhanced animations
  const renderProcessingSteps = () => {
    const hasRegularSteps = message.metadata?.processingSteps?.length > 0;
    const hasAgentSteps = message.metadata?.agentSteps?.length > 0;
    
    if (!hasRegularSteps && !hasAgentSteps) return null;

    return (
      <div className="processing-steps mb-3">
        {/* Use the new AgentLogsViewer for agent steps */}
        {hasAgentSteps && (
          <AgentLogsViewer 
            agentSteps={message.metadata.agentSteps} 
            isStreaming={isStreaming}
          />
        )}
        
        {/* Regular Processing Steps */}
        {hasRegularSteps && (
          <div className="regular-steps">
            <div className="text-sm text-blue-600 mb-2 font-medium flex items-center">
              <span className="mr-2">⚙️</span>
              System Processing Steps:
            </div>
            <div className="space-y-1">
              {message.metadata.processingSteps.map((step, index) => (
                <motion.div
                  key={step.step || index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className={`flex items-center text-xs ${
                    step.status === 'completed' ? 'text-green-600' :
                    step.status === 'in_progress' ? 'text-blue-600' :
                    step.status === 'failed' ? 'text-red-600' :
                    'text-gray-500'
                  }`}
                >
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    step.status === 'completed' ? 'bg-green-500' :
                    step.status === 'in_progress' ? 'bg-blue-500 animate-pulse' :
                    step.status === 'failed' ? 'bg-red-500' :
                    'bg-gray-300'
                  }`} />
                  <span className="flex-1">{step.message || step.step}</span>
                  {step.status === 'in_progress' && (
                    <div className="ml-2">
                      <div className="animate-spin w-3 h-3 border border-blue-500 border-t-transparent rounded-full" />
                    </div>
                  )}
                  {step.details && (
                    <div className="ml-2 text-xs text-gray-400">
                      {step.details}
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render enhanced streaming controls
  const renderStreamingControls = () => {
    if (!isStreaming) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="streaming-controls flex items-center justify-between mt-3 p-2 bg-gray-50 rounded-lg border"
      >
        <div className="flex items-center space-x-4 text-xs text-gray-600">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-1" />
            <span className="font-medium">Streaming</span>
          </div>
          {streamingMetrics && (
            <>
              <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">
                {streamingMetrics.tokensPerSecond} tokens/s
              </span>
              <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded">
                {streamingMetrics.totalTokens} tokens
              </span>
              <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded">
                {streamingMetrics.duration}s
              </span>
            </>
          )}
        </div>
        <div className="flex space-x-2">
          {onStop && (
            <button
              onClick={onStop}
              className="px-3 py-1 text-xs bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50"
            >
              Stop
            </button>
          )}
        </div>
      </motion.div>
    );
  };

  // Render error state with better styling
  const renderErrorState = () => {
    if (!message.metadata?.error) return null;

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="error-state mt-3 p-3 bg-red-50 border border-red-200 rounded-lg"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="text-sm font-medium text-red-800 mb-1">
              Error occurred during streaming
            </div>
            <div className="text-xs text-red-600">
              {message.metadata.error.message}
            </div>
            {message.metadata.error.error_code && (
              <div className="text-xs text-red-500 mt-1 font-mono">
                Code: {message.metadata.error.error_code}
              </div>
            )}
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="ml-3 px-3 py-1 text-xs bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50"
            >
              Retry
            </button>
          )}
        </div>
      </motion.div>
    );
  };

  // Render internal thoughts with collapsible design
  const renderInternalThoughts = () => {
    if (!message.metadata?.internal_thoughts) return null;

    const thoughts = message.metadata.internal_thoughts;
    const isLong = thoughts.length > 200;

    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="internal-thoughts mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg"
      >
        <div className="flex items-center justify-between mb-1">
          <div className="text-sm font-medium text-blue-800">
            Internal Thoughts
          </div>
          {isLong && (
            <button
              onClick={() => setIsInternalThoughtsExpanded(!isInternalThoughtsExpanded)}
              className="text-xs text-blue-600 hover:text-blue-800 focus:outline-none"
            >
              {isInternalThoughtsExpanded ? 'Collapse' : 'Expand'}
            </button>
          )}
        </div>
        <div className="text-xs text-blue-600">
          {isLong && !isInternalThoughtsExpanded ? `${thoughts.substring(0, 200)}...` : thoughts}
        </div>
      </motion.div>
    );
  };

  // Render metadata information
  const renderMetadata = () => {
    if (!message.metadata || isStreaming) return null;

    const metadata = message.metadata;
    const hasMetadata = metadata.model || metadata.context_used || metadata.sources;

    if (!hasMetadata) return null;

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="metadata mt-3 p-2 bg-gray-50 border border-gray-200 rounded text-xs text-gray-600"
      >
        <div className="flex flex-wrap gap-2">
          {metadata.model && (
            <span className="bg-gray-200 px-2 py-1 rounded">
              Model: {metadata.model}
            </span>
          )}
          {metadata.context_used && (
            <span className="bg-green-200 text-green-800 px-2 py-1 rounded">
              Context Used
            </span>
          )}
          {metadata.sources && metadata.sources.length > 0 && (
            <span className="bg-blue-200 text-blue-800 px-2 py-1 rounded">
              {metadata.sources.length} Sources
            </span>
          )}
        </div>
      </motion.div>
    );
  };

  return (
    <div className={`streaming-message ${className}`}>
      <div className="flex justify-start">
        <div className="max-w-3xl bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
          {/* Processing Steps */}
          <AnimatePresence>
            {renderProcessingSteps()}
          </AnimatePresence>
          
          {/* Processing State */}
          <AnimatePresence>
            {isStreaming && processingState && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="processing-state text-sm text-blue-600 mb-2 italic font-medium"
              >
                {processingState}
              </motion.div>
            )}
          </AnimatePresence>
          
          {/* Message Content */}
          <div 
            ref={contentRef}
            className="message-content whitespace-pre-wrap leading-relaxed"
          >
            {displayContent}
            {isStreaming && showCursor && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="inline-block w-2 h-5 bg-blue-500 ml-1"
              />
            )}
          </div>
          
          {/* Internal Thoughts */}
          {renderInternalThoughts()}
          
          {/* Error State */}
          {renderErrorState()}
          
          {/* Streaming Controls */}
          {renderStreamingControls()}
          
          {/* Metadata */}
          {renderMetadata()}
        </div>
      </div>
    </div>
  );
};

export default StreamingMessage; 