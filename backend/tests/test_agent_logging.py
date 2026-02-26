#!/usr/bin/env python3
"""
Test script for the agent logging system.
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_framework.agent_logger import AgentLogger, ActivityType, ActivityStatus, LogLevel

async def test_agent_logging():
    """Test the agent logging functionality."""
    print("🧪 Testing Agent Logging System")
    print("=" * 50)
    
    # Create a logger with a simple callback
    logged_events = []
    
    async def test_callback(log_data):
        logged_events.append(log_data)
        print(f"📝 Log received: {log_data['type']} - {log_data['log_entry']['message']}")
    
    logger = AgentLogger(session_id="test_session", callback=test_callback)
    
    # Test different types of logging
    print("\n1. Testing Query Analysis Logging...")
    await logger.log_query_analysis(
        agent_id="test_agent",
        agent_name="Test Agent",
        query="What are the main cybersecurity risks?",
        analysis_result={
            "intent": "risk_assessment",
            "entities": ["cybersecurity", "risks"],
            "frameworks": ["ISO27001"],
            "complexity_score": 0.7
        },
        execution_time_ms=150.5
    )
    
    print("\n2. Testing Agent Selection Logging...")
    await logger.log_agent_selection(
        orchestrator_id="orchestrator",
        selected_agents=[
            {"agent_id": "risk_assessment", "priority": 1},
            {"agent_id": "compliance_analysis", "priority": 2}
        ],
        reasoning="Query requires both risk assessment and compliance analysis",
        execution_time_ms=75.2
    )
    
    print("\n3. Testing Tool Execution Logging...")
    await logger.log_tool_execution(
        agent_id="risk_agent",
        agent_name="Risk Assessment Agent",
        tool_id="document_finder",
        tool_params={"query": "cybersecurity risks", "max_results": 10},
        result={"documents_found": 5, "relevance_scores": [0.9, 0.8, 0.7, 0.6, 0.5]},
        execution_time_ms=320.1
    )
    
    print("\n4. Testing Decision Making Logging...")
    await logger.log_decision_making(
        agent_id="orchestrator",
        agent_name="Orchestrator",
        decision_context="Analyzing query complexity",
        decision_made="Proceed with iterative analysis",
        reasoning="Query complexity score above threshold requires deeper analysis",
        confidence=0.85,
        alternatives_considered=["Single-pass analysis", "Iterative analysis", "Multi-agent collaboration"]
    )
    
    print("\n5. Testing Iteration Logging...")
    await logger.log_iteration(
        agent_id="risk_agent",
        agent_name="Risk Assessment Agent",
        iteration_number=2,
        reason_for_iteration="Insufficient context about organizational assets",
        context_gaps=["asset inventory", "threat landscape", "existing controls"],
        reformulated_query="What are the cybersecurity risks for our specific organizational assets?",
        execution_time_ms=45.3
    )
    
    print("\n6. Testing Error Logging...")
    await logger.log_activity(
        agent_id="compliance_agent",
        agent_name="Compliance Analysis Agent",
        activity_type=ActivityType.ERROR_HANDLING,
        status=ActivityStatus.FAILED,
        level=LogLevel.ERROR,
        message="Failed to access compliance framework database",
        details={
            "error_type": "ConnectionError",
            "error_message": "Database connection timeout",
            "retry_attempts": 3
        }
    )
    
    # Get session summary
    print("\n7. Session Summary:")
    print("-" * 30)
    summary = logger.get_session_summary()
    
    print(f"Session ID: {summary['session_id']}")
    print(f"Total Log Entries: {summary['total_log_entries']}")
    print(f"Total Activities: {summary['metrics']['total_activities']}")
    print(f"Successful Activities: {summary['metrics']['successful_activities']}")
    print(f"Failed Activities: {summary['metrics']['failed_activities']}")
    print(f"Agents Involved: {', '.join(summary['metrics']['agents_involved'])}")
    print(f"Tools Used: {', '.join(summary['metrics']['tools_used'])}")
    
    print(f"\nActivity Breakdown:")
    for activity_type, count in summary['activity_breakdown'].items():
        print(f"  - {activity_type.replace('_', ' ').title()}: {count}")
    
    print(f"\nAgent Performance:")
    for agent_id, perf in summary['agent_performance'].items():
        print(f"  - {perf['agent_name']}: {perf['total_activities']} activities, "
              f"{perf['successful_activities']} successful, "
              f"{perf['total_execution_time_ms']:.1f}ms total")
    
    print(f"\nTimeline ({len(summary['timeline'])} events):")
    for event in summary['timeline'][:3]:  # Show first 3 events
        print(f"  - {event['timestamp']}: {event['agent_name']} - {event['message']}")
    if len(summary['timeline']) > 3:
        print(f"  ... and {len(summary['timeline']) - 3} more events")
    
    print(f"\n✅ Test completed! {len(logged_events)} events were logged and streamed.")
    
    # Verify that all events were properly logged
    assert len(logged_events) == 6, f"Expected 6 logged events, got {len(logged_events)}"
    assert summary['total_log_entries'] == 6, f"Expected 6 log entries, got {summary['total_log_entries']}"
    assert summary['metrics']['total_activities'] == 6, f"Expected 6 activities, got {summary['metrics']['total_activities']}"
    
    print("🎉 All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_agent_logging()) 