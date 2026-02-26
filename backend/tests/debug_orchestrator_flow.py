import asyncio
import sys
import json
sys.path.append('/app')

from agent_framework.factory import initialize_complete_agent_system
from agent_framework.agent import Query

async def debug_orchestrator_flow():
    print("=== DEBUGGING ORCHESTRATOR FLOW ===")
    
    async def debug_callback(log_data):
        # Handle different log data structures
        if isinstance(log_data, dict):
            # Check if it's the detailed log structure from AgentLogger
            if 'log_entry' in log_data and isinstance(log_data['log_entry'], dict):
                log_entry = log_data['log_entry']
                agent_name = log_entry.get('agent_name', 'Unknown')
                message = log_entry.get('message', 'No message')
                activity_type = log_entry.get('activity_type', 'unknown')
                print(f"DEBUG LOG: {agent_name} - {message} [{activity_type}]")
            else:
                # Handle simple log data structure
                agent_name = log_data.get('agent_name', 'Unknown')
                message = log_data.get('message', 'No message')
                activity_type = log_data.get('activity_type', 'UNKNOWN')
                print(f"DEBUG LOG: {agent_name} - {message} [{activity_type}]")
        else:
            print(f"DEBUG LOG: Unexpected log data format: {log_data}")
    
    print("1. Initialize system...")
    orchestrator = await initialize_complete_agent_system(log_callback=debug_callback)
    
    print("2. Test direct analysis...")
    analysis = await orchestrator._analyze_request('Quelles mesures sont prises pour la sûreté et la sécurité physique?')
    print(f"Analysis result:")
    print(json.dumps(analysis, indent=2))
    
    print("\n3. Check execution sequence...")
    execution_seq = analysis.get('sequence_execution', [])
    print(f"Found {len(execution_seq)} steps")
    for i, step in enumerate(execution_seq):
        agent_id = step.get('agent')
        print(f"  Step {i+1}: {step.get('action', 'Unknown')} -> Agent: {agent_id}")
        if agent_id in orchestrator.specialized_agents:
            print(f"    ✅ Agent {agent_id} is registered")
        else:
            print(f"    ❌ Agent {agent_id} NOT found")
    
    print("\n4. Test iteration context...")
    from agent_framework.orchestrator import IterationContext
    iteration_ctx = IterationContext()
    print(f"Should continue iteration: {iteration_ctx.should_continue_iteration()}")
    print(f"Iteration count: {iteration_ctx.iteration_count}")
    print(f"Max iterations: {iteration_ctx.max_iterations}")
    
    print("\n5. Test execution manually...")
    test_query = Query(query_text='Quelles mesures sont prises pour la sûreté et la sécurité physique?')
    try:
        result = await orchestrator._execute_plan_with_iteration(analysis, test_query, iteration_ctx)
        print(f"Manual execution result:")
        print(f"  Agent results: {list(result.get('agent_results', {}).keys())}")
        print(f"  Errors: {result.get('errors', [])}")
    except Exception as e:
        print(f"Manual execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_orchestrator_flow()) 