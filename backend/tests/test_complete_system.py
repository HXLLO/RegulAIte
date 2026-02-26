import asyncio
import sys
import json
sys.path.append('/app')

from agent_framework.factory import initialize_complete_agent_system
from agent_framework.agent import Query

async def test_complete_system():
    print("=== COMPLETE SYSTEM TEST WITH RAG INTEGRATION ===")
    
    detailed_logs = []
    
    async def log_callback(log_data):
        detailed_logs.append(log_data)
        # Handle different log data structures
        if isinstance(log_data, dict):
            # Check if it's the detailed log structure from AgentLogger
            if 'log_entry' in log_data and isinstance(log_data['log_entry'], dict):
                log_entry = log_data['log_entry']
                agent_name = log_entry.get('agent_name', 'Unknown')
                message = log_entry.get('message', 'No message')
                activity = log_entry.get('activity_type', 'UNKNOWN')
                print(f"LOG: [{agent_name}] {message} [{activity}]")
            else:
                # Handle simple log data structure
                agent_name = log_data.get('agent_name', 'Unknown')
                message = log_data.get('message', 'No message')
                activity = log_data.get('activity_type', 'UNKNOWN')
                print(f"LOG: [{agent_name}] {message} [{activity}]")
        else:
            print(f"LOG: Unexpected log data format: {log_data}")
    
    print("1. Initializing complete system with RAG integration...")
    
    # Initialize with proper RAG system from main
    try:
        import main
        rag_system = main.rag_system
        rag_query_engine = main.rag_query_engine
        print(f"   ✅ RAG System available: {type(rag_system).__name__ if rag_system else 'None'}")
        print(f"   ✅ RAG Query Engine available: {type(rag_query_engine).__name__ if rag_query_engine else 'None'}")
    except Exception as e:
        print(f"   ⚠️  Could not import from main: {e}")
        rag_system = None
        rag_query_engine = None
    
    orchestrator = await initialize_complete_agent_system(
        rag_system=rag_system,
        rag_query_engine=rag_query_engine,
        log_callback=log_callback
    )
    
    print(f"   ✅ Orchestrator initialized")
    print(f"   ✅ Specialized agents: {list(orchestrator.specialized_agents.keys())}")
    
    print("\n2. Testing complete query processing...")
    test_query = Query(query_text='Quelles mesures sont prises pour la sûreté et la sécurité physique?')
    
    try:
        response = await orchestrator.process_query(test_query)
        
        print(f"\n3. Results:")
        print(f"   Response length: {len(response.content)}")
        print(f"   Sources found: {len(response.sources)}")
        print(f"   Confidence: {response.confidence}")
        print(f"   Agent tools used: {response.metadata.get('tools_used', [])}")
        
        print(f"\n4. Metadata:")
        metadata = response.metadata
        print(f"   Total iterations: {metadata.get('total_iterations', 0)}")
        print(f"   Agents involved: {metadata.get('agents_involved', [])}")
        print(f"   Processing time: {metadata.get('processing_time_ms', 0):.2f}ms")
        
        print(f"\n5. Detailed Logs Captured: {len(detailed_logs)}")
        if detailed_logs:
            print("   Sample detailed logs:")
            for i, log in enumerate(detailed_logs[:5]):
                agent = log.get('agent_name', 'Unknown')
                activity = log.get('activity_type', 'UNKNOWN')
                message = log.get('message', 'No message')[:50]
                print(f"     {i+1}. [{agent}] {activity}: {message}...")
        
        print(f"\n6. Response Preview:")
        preview = response.content[:500] + "..." if len(response.content) > 500 else response.content
        print(preview)
        
        # Test individual agents
        print(f"\n7. Testing individual agents...")
        
        agent_tests = [
            ("document_finder", "Trouve des documents sur la sécurité physique"),
            ("risk_assessment", "Évalue les risques de sécurité physique"),
            ("compliance_analysis", "Analyse la conformité des mesures de sécurité"),
            ("governance_analysis", "Examine la gouvernance de la sécurité physique")
        ]
        
        for agent_id, test_query_text in agent_tests:
            if agent_id in orchestrator.specialized_agents:
                try:
                    agent = orchestrator.specialized_agents[agent_id]
                    test_response = await agent.process_query(Query(query_text=test_query_text))
                    print(f"   ✅ {agent_id}: {len(test_response.content)} chars, {len(test_response.sources)} sources")
                except Exception as e:
                    print(f"   ❌ {agent_id}: Error - {str(e)}")
            else:
                print(f"   ❌ {agent_id}: Not registered")
        
        print(f"\n8. RAG Integration Status:")
        try:
            from agent_framework.integrations.rag_integration import get_rag_integration
            rag_integration = get_rag_integration()
            print(f"   ✅ RAG Integration initialized")
            print(f"   ✅ Has query engine: {rag_integration.query_engine is not None}")
            print(f"   ✅ Has RAG system: {rag_integration.rag_system is not None}")
            
            # Test RAG retrieval
            if rag_integration.rag_system:
                try:
                    rag_results = await rag_integration.retrieve("sécurité physique", top_k=3)
                    print(f"   ✅ RAG retrieval test: {len(rag_results.get('results', []))} results")
                except Exception as e:
                    print(f"   ⚠️  RAG retrieval test failed: {e}")
            
        except Exception as e:
            print(f"   ❌ RAG Integration error: {e}")
        
        return {
            "status": "success",
            "agents_working": len([a for a in agent_tests if orchestrator.specialized_agents.get(a[0])]),
            "total_agents": len(agent_tests),
            "logs_captured": len(detailed_logs),
            "rag_working": rag_integration.rag_system is not None if 'rag_integration' in locals() else False
        }
        
    except Exception as e:
        print(f"\n❌ Complete system test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_complete_system())
    print(f"\n=== FINAL RESULT ===")
    print(json.dumps(result, indent=2)) 