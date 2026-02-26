import asyncio
import sys
import json
sys.path.append('/app')

from agent_framework.integrations.llm_integration import get_llm_client
from agent_framework.factory import initialize_complete_agent_system
from agent_framework.agent import Query

async def test_full_orchestrator():
    print("=== FULL ORCHESTRATOR TEST ===")
    
    # Create a log callback to capture detailed logs
    detailed_logs = []
    
    async def log_callback(log_data):
        detailed_logs.append(log_data)
        # Handle different log data structures
        if isinstance(log_data, dict):
            # Check if it's the detailed log structure from AgentLogger
            if 'log_entry' in log_data and isinstance(log_data['log_entry'], dict):
                log_entry = log_data['log_entry']
                message = log_entry.get('message', 'No message')
                level = log_entry.get('level', 'INFO')
                print(f"LOG: {message} - {level}")
            else:
                # Handle simple log data structure
                message = log_data.get('message', 'No message')
                level = log_data.get('level', 'INFO')
                print(f"LOG: {message} - {level}")
        else:
            print(f"LOG: Unexpected log data format: {log_data}")
    
    print("1. Initializing complete system with logging...")
    orchestrator = await initialize_complete_agent_system(log_callback=log_callback)
    print(f"Specialized agents: {list(orchestrator.specialized_agents.keys())}")
    
    print("\n2. Processing full query...")
    test_query = Query(query_text='Quelles mesures sont prises pour la sûreté et la sécurité physique?')
    response = await orchestrator.process_query(test_query)
    
    print(f"\n3. Results:")
    print(f"Response length: {len(response.content)}")
    print(f"Sources: {len(response.sources)}")
    print(f"Tools used: {response.tools_used}")
    print(f"Confidence: {response.confidence}")
    
    # Check metadata
    metadata = response.metadata
    print(f"\n4. Metadata:")
    print(f"Total iterations: {metadata.get('total_iterations', 0)}")
    print(f"Agents involved: {metadata.get('agents_involved', [])}")
    print(f"Processing time: {metadata.get('total_processing_time_ms', 0):.2f}ms")
    
    # Check iteration summary
    iteration_summary = metadata.get('iteration_summary', {})
    print(f"\n5. Iteration Summary:")
    print(f"Total iterations: {iteration_summary.get('total_iterations', 0)}")
    print(f"Context gaps resolved: {metadata.get('context_gaps_resolved', 0)}")
    
    # Check detailed logs
    print(f"\n6. Detailed Logs Captured: {len(detailed_logs)}")
    if detailed_logs:
        print("Sample logs:")
        for i, log in enumerate(detailed_logs[:5]):  # Show first 5 logs
            print(f"  {i+1}. {log.get('agent_name', 'Unknown')} - {log.get('message', 'No message')}")
    
    # Show a portion of the response
    print(f"\n7. Response Preview:")
    print(response.content[:500] + "..." if len(response.content) > 500 else response.content)

if __name__ == "__main__":
    asyncio.run(test_full_orchestrator()) 