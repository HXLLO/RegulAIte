#!/usr/bin/env python3
"""
Test script to verify detailed agent logging functionality.
"""
import asyncio
import sys
import os

# Add the backend path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agent_framework.orchestrator import OrchestratorAgent
from agent_framework.integrations.llm_integration import get_llm_client
from agent_framework.agent import Query, QueryContext
from agent_framework.agent_logger import AgentLogger, ActivityType, ActivityStatus, LogLevel

async def test_detailed_logging():
    """Test detailed logging with the orchestrator."""
    print("🧪 Testing detailed agent logging...")
    
    # Mock log callback to capture logs
    captured_logs = []
    
    async def log_callback(log_data):
        """Capture logs for verification."""
        captured_logs.append(log_data)
        # Handle different log data structures
        if isinstance(log_data, dict):
            # Check if it's the detailed log structure from AgentLogger
            if 'log_entry' in log_data and isinstance(log_data['log_entry'], dict):
                log_entry = log_data['log_entry']
                message = log_entry.get('message', 'No message')
                print(f"📋 LOG: {message}")
                if log_entry.get('details'):
                    print(f"   📝 Details: {log_entry['details']}")
            else:
                # Handle simple log data structure
                message = log_data.get('message', 'No message')
                print(f"📋 LOG: {message}")
                if log_data.get('details'):
                    print(f"   📝 Details: {log_data['details']}")
        else:
            print(f"📋 LOG: Unexpected log data format: {log_data}")
    
    # Create orchestrator with detailed logging
    llm_client = get_llm_client()
    orchestrator = OrchestratorAgent(llm_client=llm_client, log_callback=log_callback)
    
    # Create a test query
    query = Query(
        query_text="Analysez les risques de cybersécurité pour notre organisation",
        context=QueryContext(session_id="test_session")
    )
    
    print("🚀 Starting query processing...")
    
    try:
        # Process the query
        response = await orchestrator.process_query(query)
        
        print(f"✅ Query completed successfully")
        print(f"📊 Captured {len(captured_logs)} detailed log entries")
        
        # Display log summary
        log_types = {}
        for log in captured_logs:
            activity_type = log.get('activity_type', 'unknown')
            log_types[activity_type] = log_types.get(activity_type, 0) + 1
        
        print("\n📈 Log Activity Breakdown:")
        for activity_type, count in log_types.items():
            print(f"   {activity_type}: {count} entries")
        
        # Show some detailed log examples
        print("\n🔍 Sample Detailed Logs:")
        for i, log in enumerate(captured_logs[:5]):  # Show first 5 logs
            print(f"\n   Log {i+1}:")
            print(f"   - Activity: {log.get('activity_type', 'unknown')}")
            print(f"   - Status: {log.get('status', 'unknown')}")
            print(f"   - Message: {log.get('message', 'No message')}")
            if log.get('details'):
                details = log['details']
                if isinstance(details, dict):
                    for key, value in list(details.items())[:3]:  # Show first 3 detail keys
                        print(f"   - {key}: {str(value)[:100]}...")
                else:
                    print(f"   - Details: {str(details)[:100]}...")
        
        print(f"\n✨ Response length: {len(response.content)} characters")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        print(f"📊 Captured {len(captured_logs)} log entries before failure")
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_detailed_logging())
    if success:
        print("\n🎉 Detailed logging test completed successfully!")
    else:
        print("\n💥 Detailed logging test failed!")
        sys.exit(1) 