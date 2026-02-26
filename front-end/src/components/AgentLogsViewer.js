import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * AgentLogsViewer Component
 * Displays detailed agent logs in an organized, expandable format
 */
const AgentLogsViewer = ({ agentSteps = [], isStreaming = false }) => {
  const [expandedLogs, setExpandedLogs] = useState(new Set());
  const [filterLevel, setFilterLevel] = useState('all');
  const [filterAgent, setFilterAgent] = useState('all');
  const [showTimestamps, setShowTimestamps] = useState(false);

  // Process and categorize logs
  const processedLogs = useMemo(() => {
    const detailedLogs = agentSteps.filter(step => step.isDetailedLog);
    const regularSteps = agentSteps.filter(step => !step.isDetailedLog);
    
    return {
      detailedLogs,
      regularSteps,
      agents: [...new Set(detailedLogs.map(log => log.agentName).filter(Boolean))],
      activityTypes: [...new Set(detailedLogs.map(log => log.activityType).filter(Boolean))]
    };
  }, [agentSteps]);

  // Filter logs based on current filters
  const filteredLogs = useMemo(() => {
    let logs = processedLogs.detailedLogs;
    
    if (filterLevel !== 'all') {
      logs = logs.filter(log => log.logLevel === filterLevel);
    }
    
    if (filterAgent !== 'all') {
      logs = logs.filter(log => log.agentName === filterAgent);
    }
    
    return logs;
  }, [processedLogs.detailedLogs, filterLevel, filterAgent]);

  const toggleLogExpansion = (logId) => {
    const newExpanded = new Set(expandedLogs);
    if (newExpanded.has(logId)) {
      newExpanded.delete(logId);
    } else {
      newExpanded.add(logId);
    }
    setExpandedLogs(newExpanded);
  };

  const getActivityIcon = (activityType) => {
    const icons = {
      'query_analysis': '🔍',
      'agent_selection': '🎯',
      'tool_execution': '🔧',
      'document_processing': '📄',
      'context_building': '🧩',
      'decision_making': '🤔',
      'iteration': '🔄',
      'synthesis': '⚡',
      'error_handling': '❌',
      'performance_metric': '📊'
    };
    return icons[activityType] || '📝';
  };

  const getLogLevelColor = (level) => {
    const colors = {
      'debug': 'text-gray-600 bg-gray-50 border-gray-300',
      'info': 'text-blue-700 bg-blue-50 border-blue-400',
      'warning': 'text-yellow-700 bg-yellow-50 border-yellow-400',
      'error': 'text-red-700 bg-red-50 border-red-400',
      'critical': 'text-red-800 bg-red-100 border-red-500'
    };
    return colors[level] || 'text-gray-700 bg-gray-50 border-gray-300';
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    try {
      return new Date(timestamp).toLocaleTimeString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        fractionalSecondDigits: 3
      });
    } catch {
      return timestamp;
    }
  };

  const formatExecutionTime = (timeMs) => {
    if (!timeMs) return '';
    if (timeMs < 1000) return `${Math.round(timeMs)}ms`;
    return `${(timeMs / 1000).toFixed(2)}s`;
  };

  if (!agentSteps.length) {
    return null;
  }

  return (
    <div className="agent-logs-viewer bg-white rounded-lg border border-gray-200 shadow-sm">
      {/* Header with controls */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center">
            <span className="mr-2">🤖</span>
            Agent Activity Logs
            {isStreaming && (
              <div className="ml-2 flex items-center">
                <div className="animate-pulse w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                <span className="text-sm text-green-600">Live</span>
              </div>
            )}
          </h3>
          <div className="text-sm text-gray-600">
            {filteredLogs.length} of {processedLogs.detailedLogs.length} logs
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Level:</label>
            <select
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1"
            >
              <option value="all">All</option>
              <option value="debug">Debug</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Agent:</label>
            <select
              value={filterAgent}
              onChange={(e) => setFilterAgent(e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1"
            >
              <option value="all">All</option>
              {processedLogs.agents.map(agent => (
                <option key={agent} value={agent}>{agent}</option>
              ))}
            </select>
          </div>

          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={showTimestamps}
              onChange={(e) => setShowTimestamps(e.target.checked)}
              className="rounded"
            />
            <span className="text-gray-700">Show timestamps</span>
          </label>
        </div>
      </div>

      {/* Regular processing steps (simplified view) */}
      {processedLogs.regularSteps.length > 0 && (
        <div className="p-4 border-b border-gray-100">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Processing Overview</h4>
          <div className="flex flex-wrap gap-2">
            {processedLogs.regularSteps.map((step, index) => (
              <div
                key={index}
                className={`px-2 py-1 rounded-full text-xs ${
                  step.status === 'completed' ? 'bg-green-100 text-green-700' :
                  step.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                  step.status === 'failed' ? 'bg-red-100 text-red-700' :
                  'bg-gray-100 text-gray-700'
                }`}
              >
                {step.message || step.step || step.state}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed logs */}
      <div className="max-h-96 overflow-y-auto">
        <AnimatePresence>
          {filteredLogs.map((log, index) => {
            const isExpanded = expandedLogs.has(log.executionId || index);
            const hasDetails = log.details && Object.keys(log.details).length > 0;
            const hasMetadata = log.metadata && Object.keys(log.metadata).length > 0;

            return (
              <motion.div
                key={log.executionId || index}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className={`border-b border-gray-100 ${getLogLevelColor(log.logLevel)}`}
              >
                <div
                  className="p-3 cursor-pointer hover:bg-opacity-80 transition-colors"
                  onClick={() => toggleLogExpansion(log.executionId || index)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1 min-w-0">
                      <div className="flex-shrink-0 text-lg">
                        {getActivityIcon(log.activityType)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-medium text-sm">
                            {log.message || log.state}
                          </span>
                          {log.agentName && (
                            <span className="px-2 py-0.5 bg-white bg-opacity-60 rounded-full text-xs font-medium">
                              {log.agentName}
                            </span>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-3 text-xs opacity-75">
                          <span className="capitalize">
                            {log.activityType?.replace('_', ' ')} • {log.status}
                          </span>
                          {showTimestamps && log.timestamp && (
                            <span>{formatTimestamp(log.timestamp)}</span>
                          )}
                          {log.execution_time_ms && (
                            <span>⏱️ {formatExecutionTime(log.execution_time_ms)}</span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 flex-shrink-0">
                      {(hasDetails || hasMetadata) && (
                        <button className="text-gray-400 hover:text-gray-600">
                          <svg
                            className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Expanded details */}
                  <AnimatePresence>
                    {isExpanded && (hasDetails || hasMetadata) && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.2 }}
                        className="mt-3 pl-8"
                      >
                        {hasDetails && (
                          <div className="mb-3">
                            <h5 className="text-xs font-medium text-gray-700 mb-2">Details:</h5>
                            <div className="bg-white bg-opacity-50 rounded p-2 text-xs font-mono">
                              <pre className="whitespace-pre-wrap overflow-x-auto">
                                {typeof log.details === 'string' 
                                  ? log.details 
                                  : JSON.stringify(log.details, null, 2)
                                }
                              </pre>
                            </div>
                          </div>
                        )}

                        {hasMetadata && (
                          <div>
                            <h5 className="text-xs font-medium text-gray-700 mb-2">Metadata:</h5>
                            <div className="bg-white bg-opacity-50 rounded p-2 text-xs font-mono">
                              <pre className="whitespace-pre-wrap overflow-x-auto">
                                {JSON.stringify(log.metadata, null, 2)}
                              </pre>
                            </div>
                          </div>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {filteredLogs.length === 0 && processedLogs.detailedLogs.length > 0 && (
          <div className="p-4 text-center text-gray-500">
            No logs match the current filters
          </div>
        )}

        {processedLogs.detailedLogs.length === 0 && (
          <div className="p-4 text-center text-gray-500">
            No detailed logs available yet
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentLogsViewer; 