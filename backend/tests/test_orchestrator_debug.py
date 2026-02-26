import asyncio
import sys
import os
sys.path.append('backend')

from agent_framework.integrations.llm_integration import get_llm_client
from agent_framework.orchestrator import OrchestratorAgent
from agent_framework.factory import initialize_complete_agent_system

async def test_orchestrator():
    try:
        print("1. Testing LLM client...")
        llm_client = get_llm_client()
        response = await llm_client.generate_response(
            messages=[
                {'role': 'user', 'content': 'Test: Quelles mesures sont prises pour la sûreté et la sécurité physique?'}
            ],
            model='gpt-4',
            temperature=0.1
        )
        print(f'LLM Response: {response[:200]}...')
        
        print("\n2. Testing orchestrator analysis...")
        orchestrator = OrchestratorAgent(llm_client=llm_client)
        analysis = await orchestrator._analyze_request('Quelles mesures sont prises pour la sûreté et la sécurité physique?')
        print(f'Analysis result: {analysis}')
        
        print("\n3. Testing complete system initialization...")
        full_orchestrator = await initialize_complete_agent_system()
        print(f'Specialized agents: {list(full_orchestrator.specialized_agents.keys())}')
        
        print("\n4. Testing full query processing...")
        from agent_framework.query import Query
        test_query = Query(query_text='Quelles mesures sont prises pour la sûreté et la sécurité physique?')
        response = await full_orchestrator.process_query(test_query)
        
        print(f'Response content length: {len(response.content)}')
        print(f'Sources: {len(response.sources)}')
        print(f'Tools used: {response.tools_used}')
        print(f'Metadata: {response.metadata}')
        
        # Check iteration summary
        iteration_summary = response.metadata.get('iteration_summary', {})
        print(f'Total iterations: {iteration_summary.get("total_iterations", 0)}')
        print(f'Agents involved: {response.metadata.get("agents_involved", [])}')
        
    except Exception as e:
        print(f'Error: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_orchestrator()) 