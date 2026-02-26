import asyncio
import sys
import json
sys.path.append('/app')

from agent_framework.integrations.llm_integration import get_llm_client
from agent_framework.orchestrator import OrchestratorAgent, IterationContext
from agent_framework.factory import initialize_complete_agent_system
from agent_framework.agent import Query

async def test_agent_execution():
    print("=== AGENT EXECUTION TEST ===")
    
    print("1. Creating complete system...")
    orchestrator = await initialize_complete_agent_system()
    print(f"Specialized agents: {list(orchestrator.specialized_agents.keys())}")
    
    print("\n2. Getting analysis plan...")
    analysis = await orchestrator._analyze_request('Quelles mesures sont prises pour la sûreté et la sécurité physique?')
    execution_seq = analysis.get('sequence_execution', [])
    print(f"Found {len(execution_seq)} execution steps")
    
    print("\n3. Testing single agent execution...")
    if execution_seq and len(execution_seq) > 0:
        first_step = execution_seq[0]
        agent_id = first_step.get('agent')
        print(f"Testing agent: {agent_id}")
        
        if agent_id in orchestrator.specialized_agents:
            print(f"Agent {agent_id} is registered!")
            agent = orchestrator.specialized_agents[agent_id]
            print(f"Agent type: {type(agent)}")
            
            # Test the agent directly
            test_query = Query(query_text='Quelles mesures sont prises pour la sûreté et la sécurité physique?')
            try:
                print("Calling agent.process_query...")
                result = await agent.process_query(test_query)
                print(f"Agent result type: {type(result)}")
                print(f"Response length: {len(result.content)}")
                print(f"Sources: {len(result.sources)}")
                print(f"Tools used: {result.tools_used}")
            except Exception as e:
                print(f"Error calling agent: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Agent {agent_id} NOT registered!")
            print(f"Available agents: {list(orchestrator.specialized_agents.keys())}")
    
    print("\n4. Testing full execution...")
    try:
        context = IterationContext()
        test_query = Query(query_text='Quelles mesures sont prises pour la sûreté et la sécurité physique?')
        result = await orchestrator._execute_plan_with_iteration(analysis, test_query, context)
        
        print(f"Execution completed!")
        print(f"Agent results: {list(result.get('agent_results', {}).keys())}")
        print(f"All sources: {len(result.get('all_sources', []))}")
        print(f"Errors: {result.get('errors', [])}")
        
        # Check individual agent results
        for agent_id, agent_result in result.get('agent_results', {}).items():
            print(f"\nAgent {agent_id} results:")
            print(f"  Response length: {len(agent_result.get('response', ''))}")
            print(f"  Tools used: {agent_result.get('tools_used', [])}")
            print(f"  Sources: {len(agent_result.get('sources', []))}")
            print(f"  Confidence: {agent_result.get('confidence', 'N/A')}")
    except Exception as e:
        print(f"Error in full execution: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_agent_execution()) 