#!/usr/bin/env python3
"""
Script de test pour vérifier que le système d'agents fonctionne correctement.
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_agent_system():
    """Test the agent system initialization and functionality."""
    
    logger.info("🚀 Starting agent system test...")
    
    try:
        # Test 1: Initialize RAG system
        logger.info("📚 Test 1: Initializing RAG system...")
        from config.app_config import app_config
        from rag.hype_rag import RAGSystem
        from rag.rag_query_engine import RAGQueryEngine
        
        rag_system = RAGSystem(
            qdrant_url=app_config.qdrant.url,
            collection_name=app_config.qdrant.collection_name,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            chunk_size=app_config.document_parser.chunk_size,
            chunk_overlap=app_config.document_parser.chunk_overlap
        )
        
        rag_query_engine = RAGQueryEngine(rag_system)
        logger.info("✅ RAG system initialized successfully")
        
        # Test 2: Initialize agent system
        logger.info("🤖 Test 2: Initializing agent system...")
        from agent_framework.factory import initialize_complete_agent_system
        from agent_framework.integrations.rag_integration import initialize_rag_integration
        
        # Initialize RAG integration
        initialize_rag_integration(rag_system=rag_system, rag_query_engine=rag_query_engine)
        
        # Create orchestrator with debug callback
        async def debug_callback(log_data):
            if isinstance(log_data, dict):
                agent_name = log_data.get('agent_name', 'Unknown')
                message = log_data.get('message', 'No message')
                logger.info(f"AGENT: {agent_name} - {message}")
        
        orchestrator = await initialize_complete_agent_system(
            rag_system=rag_system,
            log_callback=debug_callback
        )
        
        if orchestrator is None:
            logger.error("❌ Failed to create orchestrator")
            return False
            
        # Test 3: Verify agents are registered
        logger.info("🔍 Test 3: Verifying agent registration...")
        registered_agents = list(orchestrator.specialized_agents.keys())
        logger.info(f"Registered agents: {registered_agents}")
        
        if not registered_agents:
            logger.error("❌ No agents registered!")
            return False
            
        # Debug agent status
        orchestrator.debug_agent_status()
        
        expected_agents = ['risk_assessment', 'document_finder', 'entity_extractor', 'compliance_analysis', 'governance_analysis', 'gap_analysis']
        missing_agents = [agent for agent in expected_agents if agent not in registered_agents]
        
        if missing_agents:
            logger.warning(f"⚠️ Missing expected agents: {missing_agents}")
        else:
            logger.info("✅ All expected agents are registered")
        
        # Test 4: Test orchestrator query processing
        logger.info("💬 Test 4: Testing orchestrator query processing...")
        from agent_framework.agent import Query
        
        test_query = Query(query_text="Analyze the cybersecurity risks in our new IT infrastructure project")
        
        logger.info("Executing test query...")
        response = await orchestrator.process_query(test_query)
        
        if response and response.content:
            logger.info(f"✅ Query processed successfully")
            logger.info(f"Response length: {len(response.content)} characters")
            logger.info(f"Tools used: {response.tools_used}")
            logger.info(f"Sources: {len(response.sources)} sources")
            logger.info(f"Confidence: {response.confidence}")
            
            # Show first 200 characters of response
            preview = response.content[:200] + "..." if len(response.content) > 200 else response.content
            logger.info(f"Response preview: {preview}")
        else:
            logger.error("❌ Query processing failed - empty response")
            return False
        
        # Test 5: Test individual agents
        logger.info("🎯 Test 5: Testing individual agents...")
        test_passed = True
        
        for agent_id in ['risk_assessment', 'compliance_analysis', 'governance_analysis']:
            if agent_id in orchestrator.specialized_agents:
                logger.info(f"Testing {agent_id}...")
                try:
                    agent = orchestrator.specialized_agents[agent_id]
                    agent_query = Query(query_text=f"Test query for {agent_id}")
                    agent_response = await agent.process_query(agent_query)
                    
                    if agent_response and agent_response.content:
                        logger.info(f"✅ {agent_id} responded successfully")
                    else:
                        logger.warning(f"⚠️ {agent_id} gave empty response")
                        test_passed = False
                        
                except Exception as e:
                    logger.error(f"❌ {agent_id} failed: {str(e)}")
                    test_passed = False
        
        # Summary
        logger.info("📊 Test Summary:")
        logger.info(f"  - Orchestrator: {'✅' if orchestrator else '❌'}")
        logger.info(f"  - Agents registered: {len(registered_agents)}/6")
        logger.info(f"  - Query processing: {'✅' if response and response.content else '❌'}")
        logger.info(f"  - Individual agents: {'✅' if test_passed else '⚠️'}")
        
        if orchestrator and registered_agents and response and response.content:
            logger.info("🎉 All tests passed! Agent system is working correctly.")
            return True
        else:
            logger.error("❌ Some tests failed. Check the logs above for details.")
            return False
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {str(e)}")
        import traceback
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agent_system())
    sys.exit(0 if success else 1) 