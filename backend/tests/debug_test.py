import asyncio
import sys
import json
sys.path.append('/app')

from agent_framework.integrations.llm_integration import get_llm_client
from agent_framework.orchestrator import OrchestratorAgent
from agent_framework.factory import initialize_complete_agent_system
from agent_framework.agent import Query

async def test_orchestrator():
    try:
        print("=== ORCHESTRATOR DEBUG TEST ===")
        
        print("1. Testing LLM client...")
        llm_client = get_llm_client()
        
        print("2. Testing orchestrator analysis...")
        orchestrator = OrchestratorAgent(llm_client=llm_client)
        analysis = await orchestrator._analyze_request('Quelles mesures sont prises pour la sûreté et la sécurité physique?')
        print(f"Analysis result: {json.dumps(analysis, indent=2)}")
        
        print("3. Testing complete system initialization...")
        full_orchestrator = await initialize_complete_agent_system()
        print(f"Specialized agents: {list(full_orchestrator.specialized_agents.keys())}")
        
        print("4. Testing execution sequence...")
        execution_seq = analysis.get('sequence_execution', [])
        print(f"Execution sequence: {execution_seq}")
        
        if execution_seq:
            print("5. Testing agent execution...")
            from agent_framework.orchestrator import IterationContext
            context = IterationContext()
            test_query = Query(query_text='Quelles mesures sont prises pour la sûreté et la sécurité physique?')
            result = await full_orchestrator._execute_plan_with_iteration(analysis, test_query, context)
            print(f"Agent results: {list(result.get('agent_results', {}).keys())}")
            print(f"Sources: {len(result.get('all_sources', []))}")
            print(f"Errors: {result.get('errors', [])}")
        else:
            print("5. No execution sequence found - this is the problem!")
        
        print("6. Testing full process...")
        test_query = Query(query_text='Quelles mesures sont prises pour la sûreté et la sécurité physique?')
        response = await full_orchestrator.process_query(test_query)
        
        print(f"Response length: {len(response.content)}")
        print(f"Sources: {len(response.sources)}")
        print(f"Tools used: {response.tools_used}")
        
        # Check iteration summary
        iteration_summary = response.metadata.get('iteration_summary', {})
        print(f"Total iterations: {iteration_summary.get('total_iterations', 0)}")
        print(f"Agents involved: {response.metadata.get('agents_involved', [])}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_orchestrator()) 