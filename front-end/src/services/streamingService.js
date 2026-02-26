/**
 * Enhanced Streaming Service for LLM Responses
 * Based on Open WebUI streaming patterns and best practices
 */

class StreamingService {
  constructor() {
    this.activeStreams = new Map();
    this.retryAttempts = new Map();
    this.maxRetries = 3;
    this.baseRetryDelay = 1000;
  }

  /**
   * Create a streaming request with enhanced error handling and connection management
   * @param {string} url - The streaming endpoint URL
   * @param {Object} requestData - The request payload
   * @param {Object} callbacks - Event callbacks
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Stream result
   */
  async createStream(url, requestData, callbacks = {}, options = {}) {
    const streamId = `stream_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const {
      onStart = () => {},
      onToken = () => {},
      onProcessing = () => {},
      onComplete = () => {},
      onError = () => {},
      onProgress = () => {}
    } = callbacks;

    const {
      timeout = 300000, // 5 minutes default
      retryOnFailure = true,
      headers = {},
      signal = null
    } = options;

    let reader = null;
    let controller = null;
    let heartbeatInterval = null;
    let progressTracker = null;

    try {
      // Create abort controller for this stream
      controller = new AbortController();
      if (signal) {
        signal.addEventListener('abort', () => controller.abort());
      }

      // Store stream reference for cleanup
      this.activeStreams.set(streamId, {
        controller,
        reader,
        heartbeatInterval,
        progressTracker
      });

      // Prepare headers with authentication
      const token = localStorage.getItem('token');
      const requestHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache',
        ...headers
      };

      if (token) {
        requestHeaders['Authorization'] = `Bearer ${token}`;
      }

      // Set up timeout
      const timeoutId = setTimeout(() => {
        console.warn(`Stream ${streamId} timed out after ${timeout}ms`);
        this.abortStream(streamId);
        onError(new Error(`Request timed out after ${timeout}ms`));
      }, timeout);

      // Make the streaming request
      const response = await fetch(url, {
        method: 'POST',
        headers: requestHeaders,
        body: JSON.stringify({
          ...requestData,
          stream: true
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text().catch(() => '');
        throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
      }

      if (!response.body) {
        throw new Error('Response body is not readable');
      }

      reader = response.body.getReader();
      this.activeStreams.get(streamId).reader = reader;

      // Set up progress tracking
      let lastActivity = Date.now();
      let messageBuffer = '';
      let isProcessing = false;

      progressTracker = setInterval(() => {
        const now = Date.now();
        const timeSinceActivity = now - lastActivity;
        
        if (timeSinceActivity > 60000 && isProcessing) {
          onProgress({
            type: 'warning',
            message: 'Stream appears to be stalled, but still connected...',
            timeSinceActivity
          });
        }
      }, 30000);

      this.activeStreams.get(streamId).progressTracker = progressTracker;

      // Set up heartbeat for connection health
      heartbeatInterval = setInterval(() => {
        const now = Date.now();
        const timeSinceActivity = now - lastActivity;
        
        if (timeSinceActivity > 120000) {
          console.warn(`No activity for ${timeSinceActivity}ms, connection may be dead`);
          this.abortStream(streamId);
          onError(new Error('Connection appears to be dead'));
        }
      }, 45000);

      this.activeStreams.get(streamId).heartbeatInterval = heartbeatInterval;

      // Process the stream
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log(`Stream ${streamId} completed normally`);
          break;
        }

        lastActivity = Date.now();
        
        // Decode and process chunks
        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.trim() === '') continue;
          
          try {
            // Handle both JSON lines and SSE format
            let eventData;
            if (line.startsWith('data: ')) {
              const dataContent = line.slice(6);
              if (dataContent === '[DONE]') {
                onComplete({
                  message: messageBuffer,
                  streamId
                });
                return { success: true, streamId, message: messageBuffer };
              }
              eventData = JSON.parse(dataContent);
            } else {
              eventData = JSON.parse(line);
            }

            await this.processStreamEvent(eventData, {
              onStart,
              onToken,
              onProcessing,
              onComplete,
              onError,
              onProgress
            }, streamId, messageBuffer);

            // Update message buffer for token events
            if (eventData.type === 'token' && eventData.content) {
              messageBuffer += eventData.content;
            }

            // Mark as processing if we receive processing events
            if (eventData.type === 'processing' || eventData.type === 'start') {
              isProcessing = true;
            }

          } catch (parseError) {
            console.warn(`Failed to parse stream line: ${line}`, parseError);
            // Continue processing other lines instead of failing completely
            continue;
          }
        }
      }

      // Clean completion
      this.cleanupStream(streamId);
      return { success: true, streamId, message: messageBuffer };

    } catch (error) {
      console.error(`Stream ${streamId} error:`, error);
      
      // Handle retry logic
      if (retryOnFailure && this.shouldRetry(streamId, error)) {
        console.log(`Retrying stream ${streamId}...`);
        await this.delay(this.getRetryDelay(streamId));
        return this.createStream(url, requestData, callbacks, options);
      }

      this.cleanupStream(streamId);
      onError(error);
      throw error;
    }
  }

  /**
   * Process individual stream events with enhanced handling
   */
  async processStreamEvent(eventData, callbacks, streamId, messageBuffer) {
    const { onStart, onToken, onProcessing, onComplete, onError } = callbacks;

    switch (eventData.type) {
      case 'start':
        console.log(`Stream ${streamId} started`);
        onStart({
          streamId,
          timestamp: eventData.timestamp,
          requestId: eventData.request_id,
          agentMode: eventData.agent_mode
        });
        break;

      case 'processing':
        onProcessing({
          state: eventData.state,
          step: eventData.step,
          stepNumber: eventData.step_number,
          totalSteps: eventData.total_steps,
          details: eventData.details,
          internalThoughts: eventData.internal_thoughts,
          contextMetadata: eventData.context_metadata,
          timestamp: eventData.timestamp
        });
        break;

      case 'agent_step':
        // Handle agent processing steps
        onProcessing({
          state: eventData.message,
          step: eventData.step,
          details: eventData.details,
          progress: eventData.progress,
          executionId: eventData.execution_id,
          timestamp: eventData.timestamp,
          isAgentStep: true
        });
        break;

      case 'agent_detailed_log':
        // Handle detailed agent logging
        onProcessing({
          state: `[${eventData.log_entry.agent_name}] ${eventData.log_entry.message}`,
          step: eventData.log_entry.activity_type,
          details: eventData.log_entry.details,
          progress: eventData.log_entry.execution_time_ms ? 100 : undefined,
          executionId: eventData.log_entry.entry_id,
          timestamp: eventData.log_entry.timestamp,
          isDetailedLog: true,
          logLevel: eventData.log_entry.level,
          agentId: eventData.log_entry.agent_id,
          agentName: eventData.log_entry.agent_name,
          activityType: eventData.log_entry.activity_type,
          status: eventData.log_entry.status,
          metadata: eventData.log_entry.metadata
        });
        break;

      case 'token':
        if (eventData.content) {
          onToken({
            content: eventData.content,
            accumulated: messageBuffer + eventData.content
          });
        }
        break;

      case 'end':
        console.log(`Stream ${streamId} ended`);
        onComplete({
          message: eventData.message || messageBuffer,
          metadata: eventData.metadata || {},
          model: eventData.model,
          contextUsed: eventData.context_used,
          sessionId: eventData.session_id,
          sources: eventData.sources,
          contextQuality: eventData.context_quality,
          hallucination_risk: eventData.hallucination_risk,
          internalThoughts: eventData.internal_thoughts,
          toolsUsed: eventData.tools_used,
          agentUsed: eventData.agent_used,
          executionId: eventData.execution_id,
          streamId
        });
        break;

      case 'error':
        console.error(`Stream ${streamId} error:`, eventData.message);
        onError(new Error(eventData.message || 'Stream error occurred'));
        break;

      case 'metadata':
        // Handle metadata updates
        break;

      case 'agent_progress':
        onProcessing({
          state: 'Agent processing...',
          agentProgress: eventData.data
        });
        break;

      default:
        console.warn(`Unknown stream event type: ${eventData.type}`, eventData);
    }
  }

  /**
   * Abort a specific stream
   */
  abortStream(streamId) {
    const stream = this.activeStreams.get(streamId);
    if (stream) {
      if (stream.controller) {
        stream.controller.abort();
      }
      this.cleanupStream(streamId);
    }
  }

  /**
   * Abort all active streams
   */
  abortAllStreams() {
    for (const streamId of this.activeStreams.keys()) {
      this.abortStream(streamId);
    }
  }

  /**
   * Clean up stream resources
   */
  cleanupStream(streamId) {
    const stream = this.activeStreams.get(streamId);
    if (stream) {
      if (stream.reader) {
        stream.reader.cancel().catch(() => {});
      }
      if (stream.heartbeatInterval) {
        clearInterval(stream.heartbeatInterval);
      }
      if (stream.progressTracker) {
        clearInterval(stream.progressTracker);
      }
      this.activeStreams.delete(streamId);
      this.retryAttempts.delete(streamId);
    }
  }

  /**
   * Determine if a stream should be retried
   */
  shouldRetry(streamId, error) {
    const attempts = this.retryAttempts.get(streamId) || 0;
    
    // Don't retry if we've exceeded max attempts
    if (attempts >= this.maxRetries) {
      return false;
    }

    // Don't retry for certain error types
    if (error.name === 'AbortError' || 
        error.message.includes('401') || 
        error.message.includes('403')) {
      return false;
    }

    // Retry for network errors, timeouts, and 5xx errors
    return error.message.includes('timeout') ||
           error.message.includes('network') ||
           error.message.includes('500') ||
           error.message.includes('502') ||
           error.message.includes('503') ||
           error.message.includes('504');
  }

  /**
   * Get retry delay with exponential backoff
   */
  getRetryDelay(streamId) {
    const attempts = this.retryAttempts.get(streamId) || 0;
    this.retryAttempts.set(streamId, attempts + 1);
    return this.baseRetryDelay * Math.pow(2, attempts);
  }

  /**
   * Utility delay function
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get active stream count
   */
  getActiveStreamCount() {
    return this.activeStreams.size;
  }

  /**
   * Get stream status
   */
  getStreamStatus(streamId) {
    return this.activeStreams.has(streamId) ? 'active' : 'inactive';
  }
}

// Create singleton instance
const streamingService = new StreamingService();

export default streamingService; 