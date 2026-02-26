# Agent Detailed Logging System

## Overview

The RegulAIte Agent Framework now includes a comprehensive logging system that provides detailed visibility into agent activities, decisions, and processing steps. This system allows users to see exactly what agents are doing, how they make decisions, and how they process information.

## Features

### 🔍 **Detailed Activity Tracking**
- **Query Analysis**: Track how agents interpret and analyze user queries
- **Agent Selection**: See which agents are selected and why
- **Tool Execution**: Monitor tool usage with parameters and results
- **Decision Making**: Understand agent reasoning and alternatives considered
- **Iteration Tracking**: Follow iterative processing steps and context building
- **Error Handling**: Capture and display errors with context

### 📊 **Real-time Streaming**
- Live streaming of agent activities to the UI
- Real-time updates during agent processing
- Visual indicators for different activity types and statuses

### 🎯 **Comprehensive Metadata**
- Execution times for performance analysis
- Confidence scores for decision quality
- Context gaps identification
- Tool parameters and results
- Agent performance metrics

### 🔧 **Filtering and Organization**
- Filter by log level (debug, info, warning, error, critical)
- Filter by agent type
- Expandable details for complex information
- Timeline view of all activities
- Session summaries with performance metrics

## Architecture

### Core Components

#### `AgentLogger`
The main logging class that tracks all agent activities:

```python
from agent_framework.agent_logger import AgentLogger, ActivityType, ActivityStatus, LogLevel

# Initialize with callback for real-time streaming
logger = AgentLogger(session_id="session_123", callback=stream_callback)

# Log different types of activities
await logger.log_query_analysis(agent_id, agent_name, query, analysis_result)
await logger.log_tool_execution(agent_id, agent_name, tool_id, params, result)
await logger.log_decision_making(agent_id, agent_name, context, decision, reasoning)
```

#### `ActivityType` Enum
Categorizes different types of agent activities:
- `QUERY_ANALYSIS`: Query interpretation and analysis
- `AGENT_SELECTION`: Agent selection decisions
- `TOOL_EXECUTION`: Tool usage and execution
- `DOCUMENT_PROCESSING`: Document analysis and processing
- `CONTEXT_BUILDING`: Context accumulation and building
- `DECISION_MAKING`: Decision processes and reasoning
- `ITERATION`: Iterative processing steps
- `SYNTHESIS`: Response synthesis and generation
- `ERROR_HANDLING`: Error capture and handling
- `PERFORMANCE_METRIC`: Performance measurements

#### `ActivityStatus` Enum
Tracks the status of activities:
- `STARTED`: Activity has begun
- `IN_PROGRESS`: Activity is ongoing
- `COMPLETED`: Activity finished successfully
- `FAILED`: Activity failed with error
- `SKIPPED`: Activity was skipped
- `RETRY`: Activity is being retried

#### `LogLevel` Enum
Standard logging levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General information
- `WARNING`: Warning conditions
- `ERROR`: Error conditions
- `CRITICAL`: Critical errors

### Integration Points

#### Orchestrator Integration
The orchestrator automatically logs:
- Query analysis and interpretation
- Agent selection decisions with reasoning
- Iteration planning and execution
- Context gap identification
- Final synthesis process

#### Agent Integration
Individual agents can log:
- Tool executions with parameters and results
- Decision-making processes
- Error conditions
- Performance metrics

#### UI Integration
The frontend displays logs through:
- `AgentLogsViewer` component for detailed log display
- Real-time streaming during agent processing
- Filtering and search capabilities
- Expandable details for complex information

## Usage Examples

### Basic Logging

```python
# Initialize logger
logger = AgentLogger(session_id="user_session_123")

# Log query analysis
await logger.log_query_analysis(
    agent_id="orchestrator",
    agent_name="Main Orchestrator",
    query="What are the main cybersecurity risks?",
    analysis_result={
        "intent": "risk_assessment",
        "entities": ["cybersecurity", "risks"],
        "frameworks": ["ISO27001"],
        "complexity_score": 0.7
    },
    execution_time_ms=150.5
)

# Log tool execution
await logger.log_tool_execution(
    agent_id="risk_agent",
    agent_name="Risk Assessment Agent",
    tool_id="document_finder",
    tool_params={"query": "cybersecurity risks", "max_results": 10},
    result={"documents_found": 5, "relevance_scores": [0.9, 0.8, 0.7, 0.6, 0.5]},
    execution_time_ms=320.1
)
```

### Streaming to UI

```python
async def stream_callback(log_data):
    """Callback to stream logs to UI"""
    # Send to websocket or SSE stream
    await websocket.send(json.dumps(log_data))

logger = AgentLogger(session_id="session_123", callback=stream_callback)
```

### Session Analysis

```python
# Get comprehensive session summary
summary = logger.get_session_summary()

print(f"Total activities: {summary['metrics']['total_activities']}")
print(f"Agents involved: {summary['metrics']['agents_involved']}")
print(f"Success rate: {summary['metrics']['successful_activities'] / summary['metrics']['total_activities']}")

# Analyze agent performance
for agent_id, perf in summary['agent_performance'].items():
    print(f"{perf['agent_name']}: {perf['total_execution_time_ms']}ms total")
```

## UI Components

### AgentLogsViewer
A React component that displays detailed agent logs:

```jsx
import AgentLogsViewer from './components/AgentLogsViewer';

<AgentLogsViewer 
  agentSteps={message.metadata.agentSteps} 
  isStreaming={isStreaming}
/>
```

Features:
- **Filtering**: By log level, agent type, activity type
- **Expandable Details**: Click to see full details and metadata
- **Real-time Updates**: Live updates during streaming
- **Visual Indicators**: Color-coded by activity type and status
- **Performance Metrics**: Execution times and success rates

### StreamingMessage Integration
The existing `StreamingMessage` component automatically displays agent logs when available.

## Configuration

### Environment Variables
```bash
# Enable detailed logging (default: true)
AGENT_DETAILED_LOGGING=true

# Log level threshold (default: info)
AGENT_LOG_LEVEL=info

# Maximum logs per session (default: 1000)
AGENT_MAX_LOGS_PER_SESSION=1000
```

### Agent Configuration
```python
# Enable logging for specific agents
agent = RiskAssessmentModule(
    llm_client=llm_client,
    agent_logger=logger  # Pass logger instance
)
```

## Performance Considerations

### Memory Usage
- Logs are stored in memory during the session
- Automatic cleanup after session completion
- Configurable maximum logs per session

### Streaming Performance
- Asynchronous callback system
- Non-blocking log streaming
- Efficient JSON serialization

### UI Performance
- Virtual scrolling for large log lists
- Lazy loading of log details
- Efficient React rendering with keys

## Troubleshooting

### Common Issues

#### Logs Not Appearing
1. Check that `agent_logger` is passed to agents
2. Verify callback function is properly set
3. Ensure WebSocket/SSE connection is active

#### Performance Issues
1. Reduce log level to `WARNING` or `ERROR`
2. Decrease `AGENT_MAX_LOGS_PER_SESSION`
3. Implement log rotation for long sessions

#### Missing Details
1. Check that agents are calling logging methods
2. Verify log level allows the activity type
3. Ensure proper error handling in logging code

### Debug Mode
Enable debug logging to see internal logging system activity:

```python
import logging
logging.getLogger('agent_framework.agent_logger').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Log Persistence**: Save logs to database for historical analysis
- **Advanced Analytics**: Performance trends and pattern analysis
- **Export Functionality**: Export logs in various formats (JSON, CSV, PDF)
- **Alert System**: Notifications for errors or performance issues
- **Log Aggregation**: Cross-session analysis and reporting

### Integration Opportunities
- **Monitoring Systems**: Integration with Prometheus/Grafana
- **APM Tools**: Integration with application performance monitoring
- **Business Intelligence**: Export to BI tools for analysis
- **Audit Trails**: Compliance and audit trail generation

## Testing

Run the test suite to verify logging functionality:

```bash
cd backend
python3 test_agent_logging.py
```

The test covers:
- All activity types
- Error conditions
- Session summaries
- Performance metrics
- Streaming callbacks

## API Reference

### AgentLogger Methods

#### `log_query_analysis(agent_id, agent_name, query, analysis_result, execution_time_ms=None)`
Log query analysis activities.

#### `log_agent_selection(orchestrator_id, selected_agents, reasoning, execution_time_ms=None)`
Log agent selection decisions.

#### `log_tool_execution(agent_id, agent_name, tool_id, tool_params, result, status=COMPLETED, execution_time_ms=None, error=None)`
Log tool execution with parameters and results.

#### `log_decision_making(agent_id, agent_name, decision_context, decision_made, reasoning, confidence=None, alternatives_considered=None)`
Log decision-making processes.

#### `log_iteration(agent_id, agent_name, iteration_number, reason_for_iteration, context_gaps, reformulated_query=None, execution_time_ms=None)`
Log iterative processing steps.

#### `get_session_summary()`
Get comprehensive session summary with metrics and performance data.

### Data Structures

#### LogEntry
```python
{
    "entry_id": "uuid",
    "timestamp": "ISO8601",
    "agent_id": "string",
    "agent_name": "string",
    "activity_type": "ActivityType",
    "status": "ActivityStatus",
    "level": "LogLevel",
    "message": "string",
    "details": {},
    "metadata": {},
    "execution_time_ms": float,
    "session_id": "string"
}
```

#### Session Summary
```python
{
    "session_id": "string",
    "metrics": {
        "total_activities": int,
        "successful_activities": int,
        "failed_activities": int,
        "agents_involved": [str],
        "tools_used": [str],
        "total_duration_seconds": float
    },
    "activity_breakdown": {activity_type: count},
    "agent_performance": {agent_id: performance_data},
    "timeline": [timeline_events]
}
``` 