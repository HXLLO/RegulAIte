"""
Comprehensive Agent Logging System for RegulAIte
Provides detailed visibility into agent activities, decisions, and processing steps.
"""
import json
import uuid
import asyncio
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

class LogLevel(str, Enum):
    """Log levels for agent activities."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ActivityType(str, Enum):
    """Types of agent activities."""
    QUERY_ANALYSIS = "query_analysis"
    AGENT_SELECTION = "agent_selection" 
    TOOL_EXECUTION = "tool_execution"
    DOCUMENT_PROCESSING = "document_processing"
    CONTEXT_BUILDING = "context_building"
    DECISION_MAKING = "decision_making"
    ITERATION = "iteration"
    SYNTHESIS = "synthesis"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE_METRIC = "performance_metric"

class ActivityStatus(str, Enum):
    """Status of activities."""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"

@dataclass
class AgentLogEntry:
    """Individual log entry for agent activities."""
    entry_id: str
    timestamp: str
    agent_id: str
    agent_name: str
    activity_type: ActivityType
    status: ActivityStatus
    level: LogLevel
    message: str
    details: Dict[str, Any]
    metadata: Dict[str, Any]
    execution_time_ms: Optional[float] = None
    parent_entry_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return asdict(self)

class AgentLogger:
    """
    Comprehensive logging system for agent activities.
    Provides detailed visibility into agent decision-making and processing.
    """
    
    def __init__(self, session_id: str = None, callback: Callable = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.logs: List[AgentLogEntry] = []
        self.callback = callback  # For real-time streaming to UI
        self.metrics: Dict[str, Any] = {
            "start_time": datetime.now(timezone.utc).isoformat(),
            "total_activities": 0,
            "successful_activities": 0,
            "failed_activities": 0,
            "agents_involved": set(),
            "tools_used": set(),
            "documents_processed": 0,
            "iterations_performed": 0
        }
        
    async def log_activity(self, agent_id: str, agent_name: str, activity_type: ActivityType,
                          status: ActivityStatus, level: LogLevel, message: str,
                          details: Dict[str, Any] = None, metadata: Dict[str, Any] = None,
                          execution_time_ms: float = None, parent_entry_id: str = None) -> str:
        """Log an agent activity with detailed information."""
        
        entry_id = str(uuid.uuid4())
        entry = AgentLogEntry(
            entry_id=entry_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_id=agent_id,
            agent_name=agent_name,
            activity_type=activity_type,
            status=status,
            level=level,
            message=message,
            details=details or {},
            metadata=metadata or {},
            execution_time_ms=execution_time_ms,
            parent_entry_id=parent_entry_id,
            session_id=self.session_id
        )
        
        self.logs.append(entry)
        self._update_metrics(agent_id, activity_type, status, details)
        
        # Stream to UI if callback is provided
        if self.callback:
            await self._stream_log_entry(entry)
        
        return entry_id
    
    async def log_query_analysis(self, agent_id: str, agent_name: str, query: str, 
                                analysis_result: Dict[str, Any], execution_time_ms: float = None) -> str:
        """Log query analysis activity."""
        return await self.log_activity(
            agent_id=agent_id,
            agent_name=agent_name,
            activity_type=ActivityType.QUERY_ANALYSIS,
            status=ActivityStatus.COMPLETED,
            level=LogLevel.INFO,
            message=f"Analyzed user query: {query[:100]}{'...' if len(query) > 100 else ''}",
            details={
                "original_query": query,
                "analysis_result": analysis_result,
                "query_intent": analysis_result.get("intent"),
                "identified_entities": analysis_result.get("entities", []),
                "frameworks_identified": analysis_result.get("frameworks", []),
                "complexity_score": analysis_result.get("complexity_score"),
                "requires_iteration": analysis_result.get("requires_iteration", False)
            },
            execution_time_ms=execution_time_ms
        )
    
    async def log_agent_selection(self, orchestrator_id: str, selected_agents: List[Dict[str, Any]], 
                                 reasoning: str, execution_time_ms: float = None) -> str:
        """Log agent selection decision."""
        return await self.log_activity(
            agent_id=orchestrator_id,
            agent_name="Orchestrator",
            activity_type=ActivityType.AGENT_SELECTION,
            status=ActivityStatus.COMPLETED,
            level=LogLevel.INFO,
            message=f"Selected {len(selected_agents)} agents for execution",
            details={
                "selected_agents": selected_agents,
                "selection_reasoning": reasoning,
                "execution_sequence": [agent.get("agent_id") for agent in selected_agents],
                "collaboration_required": len(selected_agents) > 1
            },
            execution_time_ms=execution_time_ms
        )
    
    async def log_tool_execution(self, agent_id: str, agent_name: str, tool_id: str, 
                                tool_params: Dict[str, Any], result: Any, 
                                status: ActivityStatus = ActivityStatus.COMPLETED,
                                execution_time_ms: float = None, error: str = None) -> str:
        """Log tool execution with detailed parameters and results."""
        return await self.log_activity(
            agent_id=agent_id,
            agent_name=agent_name,
            activity_type=ActivityType.TOOL_EXECUTION,
            status=status,
            level=LogLevel.INFO if status == ActivityStatus.COMPLETED else LogLevel.ERROR,
            message=f"Executed tool '{tool_id}' with {len(tool_params)} parameters",
            details={
                "tool_id": tool_id,
                "tool_parameters": tool_params,
                "execution_result": result if status == ActivityStatus.COMPLETED else None,
                "error_message": error,
                "result_type": type(result).__name__ if result else None,
                "result_size": len(str(result)) if result else 0,
                "success": status == ActivityStatus.COMPLETED
            },
            execution_time_ms=execution_time_ms
        )
    
    async def log_iteration(self, agent_id: str, agent_name: str, iteration_number: int,
                           reason_for_iteration: str, context_gaps: List[str],
                           reformulated_query: str = None, execution_time_ms: float = None) -> str:
        """Log iterative processing step."""
        return await self.log_activity(
            agent_id=agent_id,
            agent_name=agent_name,
            activity_type=ActivityType.ITERATION,
            status=ActivityStatus.IN_PROGRESS,
            level=LogLevel.INFO,
            message=f"Starting iteration #{iteration_number}: {reason_for_iteration}",
            details={
                "iteration_number": iteration_number,
                "reason_for_iteration": reason_for_iteration,
                "context_gaps_identified": context_gaps,
                "reformulated_query": reformulated_query,
                "previous_iterations": iteration_number - 1
            },
            execution_time_ms=execution_time_ms
        )
    
    async def log_decision_making(self, agent_id: str, agent_name: str, decision_context: str,
                                 decision_made: str, reasoning: str, confidence: float = None,
                                 alternatives_considered: List[str] = None) -> str:
        """Log agent decision-making process."""
        return await self.log_activity(
            agent_id=agent_id,
            agent_name=agent_name,
            activity_type=ActivityType.DECISION_MAKING,
            status=ActivityStatus.COMPLETED,
            level=LogLevel.INFO,
            message=f"Made decision: {decision_made}",
            details={
                "decision_context": decision_context,
                "decision_made": decision_made,
                "reasoning": reasoning,
                "confidence_score": confidence,
                "alternatives_considered": alternatives_considered or [],
                "decision_timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    def _update_metrics(self, agent_id: str, activity_type: ActivityType, 
                       status: ActivityStatus, details: Dict[str, Any] = None):
        """Update internal metrics."""
        self.metrics["total_activities"] += 1
        self.metrics["agents_involved"].add(agent_id)
        
        if status == ActivityStatus.COMPLETED:
            self.metrics["successful_activities"] += 1
        elif status == ActivityStatus.FAILED:
            self.metrics["failed_activities"] += 1
        
        if activity_type == ActivityType.TOOL_EXECUTION and details:
            tool_id = details.get("tool_id")
            if tool_id:
                self.metrics["tools_used"].add(tool_id)
        
        if activity_type == ActivityType.ITERATION:
            self.metrics["iterations_performed"] += 1
    
    async def _stream_log_entry(self, entry: AgentLogEntry):
        """Stream log entry to UI in real-time."""
        if self.callback:
            try:
                log_data = {
                    "type": "agent_detailed_log",
                    "log_entry": entry.to_dict(),
                    "session_id": self.session_id,
                    "timestamp": entry.timestamp
                }
                await self.callback(log_data)
            except Exception as e:
                logger.error(f"Error streaming log entry: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary."""
        end_time = datetime.now(timezone.utc)
        start_time = datetime.fromisoformat(self.metrics["start_time"].replace('Z', '+00:00'))
        total_duration = (end_time - start_time).total_seconds()
        
        # Convert sets to lists for JSON serialization
        metrics = self.metrics.copy()
        metrics["agents_involved"] = list(metrics["agents_involved"])
        metrics["tools_used"] = list(metrics["tools_used"])
        metrics["end_time"] = end_time.isoformat()
        metrics["total_duration_seconds"] = total_duration
        
        return {
            "session_id": self.session_id,
            "metrics": metrics,
            "total_log_entries": len(self.logs),
            "activity_breakdown": self._get_activity_breakdown(),
            "agent_performance": self._get_agent_performance(),
            "timeline": self._get_activity_timeline()
        }
    
    def _get_activity_breakdown(self) -> Dict[str, int]:
        """Get breakdown of activities by type."""
        breakdown = {}
        for log in self.logs:
            activity_type = log.activity_type.value
            breakdown[activity_type] = breakdown.get(activity_type, 0) + 1
        return breakdown
    
    def _get_agent_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics per agent."""
        performance = {}
        
        for log in self.logs:
            agent_id = log.agent_id
            if agent_id not in performance:
                performance[agent_id] = {
                    "agent_name": log.agent_name,
                    "total_activities": 0,
                    "successful_activities": 0,
                    "failed_activities": 0,
                    "total_execution_time_ms": 0,
                    "activity_types": set()
                }
            
            perf = performance[agent_id]
            perf["total_activities"] += 1
            perf["activity_types"].add(log.activity_type.value)
            
            if log.status == ActivityStatus.COMPLETED:
                perf["successful_activities"] += 1
            elif log.status == ActivityStatus.FAILED:
                perf["failed_activities"] += 1
            
            if log.execution_time_ms:
                perf["total_execution_time_ms"] += log.execution_time_ms
        
        # Convert sets to lists
        for agent_perf in performance.values():
            agent_perf["activity_types"] = list(agent_perf["activity_types"])
        
        return performance
    
    def _get_activity_timeline(self) -> List[Dict[str, Any]]:
        """Get chronological timeline of activities."""
        timeline = []
        for log in self.logs:
            timeline.append({
                "timestamp": log.timestamp,
                "agent_id": log.agent_id,
                "agent_name": log.agent_name,
                "activity_type": log.activity_type.value,
                "status": log.status.value,
                "message": log.message,
                "execution_time_ms": log.execution_time_ms
            })
        
        return sorted(timeline, key=lambda x: x["timestamp"]) 