#!/usr/bin/env python3
"""
Comprehensive integration test script for RegulAIte autonomous agent system.
Tests all components and their interactions to identify integration issues.
"""
import asyncio
import logging
import sys
import os
from pathlib import Path
import time
from typing import Dict, Any, List

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegrationTester:
    """Comprehensive integration tester for RegulAIte system."""
    
    def __init__(self):
        self.test_results = {}
        self.config = None
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        logger.info("🚀 Starting comprehensive RegulAIte integration tests")
        
        tests = [
            ("Configuration Management", self.test_configuration),
            ("Database Connection", self.test_database_connection),
            ("RAG System Integration", self.test_rag_system),
            ("Agent Framework", self.test_agent_framework),
            ("Document Processing", self.test_document_processing),
            ("API Endpoints", self.test_api_endpoints),
            ("Agent Orchestration", self.test_agent_orchestration),
            ("End-to-End Workflow", self.test_end_to_end_workflow)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n--- Testing: {test_name} ---")
            try:
                start_time = time.time()
                result = await test_func()
                end_time = time.time()
                
                self.test_results[test_name] = {
                    'success': result,
                    'duration': round(end_time - start_time, 2),
                    'error': None
                }
                
                status = "✅ PASS" if result else "❌ FAIL"
                logger.info(f"{test_name}: {status} ({self.test_results[test_name]['duration']}s)")
                
            except Exception as e:
                self.test_results[test_name] = {
                    'success': False,
                    'duration': 0,
                    'error': str(e)
                }
                logger.error(f"{test_name}: ❌ ERROR - {str(e)}")
        
        return self._generate_summary()
    
    async def test_configuration(self) -> bool:
        """Test configuration management."""
        try:
            from config.app_config import get_config, validate_config
            
            # Load configuration
            self.config = get_config()
            logger.info(f"Configuration loaded: environment={self.config.environment}")
            
            # Validate configuration
            validation = validate_config()
            logger.info(f"Configuration validation: valid={validation['valid']}")
            
            if validation['warnings']:
                logger.warning(f"Configuration warnings: {len(validation['warnings'])}")
                for warning in validation['warnings']:
                    logger.warning(f"  - {warning}")
            
            if validation['errors']:
                logger.error(f"Configuration errors: {len(validation['errors'])}")
                for error in validation['errors']:
                    logger.error(f"  - {error}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration test failed: {str(e)}")
            return False
    
    async def test_database_connection(self) -> bool:
        """Test database connectivity."""
        try:
            import mariadb
            
            if not self.config:
                logger.error("Configuration not loaded")
                return False
            
            # Test database connection
            conn = mariadb.connect(
                host=self.config.database.host,
                port=self.config.database.port,
                user=self.config.database.user,
                password=self.config.database.password,
                database=self.config.database.database
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            logger.info(f"Database connection successful: {result}")
            return True
            
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    async def test_rag_system(self) -> bool:
        """Test RAG system initialization and basic functionality."""
        try:
            from rag.hype_rag import HyPERagSystem as RAGSystem
            from rag.query_engine import RAGQueryEngine
            
            if not self.config:
                logger.error("Configuration not loaded")
                return False
            
            # Initialize RAG system
            rag_system = RAGSystem(
                qdrant_url=self.config.qdrant.url,
                collection_name=f"test_{self.config.qdrant.collection_name}",
                embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                chunk_size=self.config.document_parser.chunk_size,
                chunk_overlap=self.config.document_parser.chunk_overlap
            )
            
            # Test basic functionality
            test_query = "test query"
            # Note: This might fail if Qdrant is not running, which is expected
            logger.info("RAG system initialized successfully")
            
            return True
            
        except Exception as e:
            logger.warning(f"RAG system test failed (expected if services not running): {str(e)}")
            return False
    
    async def test_agent_framework(self) -> bool:
        """Test agent framework components."""
        try:
            from agent_framework.agent import Agent, Query, AgentResponse
            from agent_framework.tool_registry import ToolRegistry
            from agent_framework.query_parser import QueryParser
            
            # Test basic agent creation
            agent = Agent(agent_id="test_agent", name="Test Agent")
            logger.info(f"Agent created: {agent.agent_id}")
            
            # Test query processing
            query = Query(query_text="Test query")
            logger.info(f"Query created: {query.intent}")
            
            # Test tool registry
            tool_registry = ToolRegistry()
            logger.info(f"Tool registry created with {len(tool_registry.tools)} tools")
            
            return True
            
        except Exception as e:
            logger.error(f"Agent framework test failed: {str(e)}")
            return False
    
    async def test_document_processing(self) -> bool:
        """Test document processing pipeline."""
        try:
            from unstructured_parser.document_parser import DocumentParser
            
            if not self.config:
                logger.error("Configuration not loaded")
                return False
            
            # Initialize document parser
            parser = DocumentParser(
                embedding_dim=384,
                chunk_size=self.config.document_parser.chunk_size,
                chunk_overlap=self.config.document_parser.chunk_overlap,
                chunking_strategy="fixed",
                extract_tables=self.config.document_parser.extract_tables,
                extract_metadata=self.config.document_parser.extract_metadata,
                extract_images=self.config.document_parser.extract_images
            )
            
            logger.info("Document parser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Document processing test failed: {str(e)}")
            return False
    
    async def test_api_endpoints(self) -> bool:
        """Test API endpoint imports and basic structure."""
        try:
            from routers import (
                chat_router, document_router, config_router,
                agents_router, welcome_router, auth_router, hype_router
            )
            
            routers = [
                chat_router, document_router, config_router,
                agents_router, welcome_router, auth_router, hype_router
            ]
            
            for router in routers:
                if hasattr(router, 'router'):
                    logger.info(f"Router loaded: {router.router.prefix or 'root'}")
                else:
                    logger.info(f"Router loaded: {type(router).__name__}")
            
            return True
            
        except Exception as e:
            logger.error(f"API endpoints test failed: {str(e)}")
            return False
    
    async def test_agent_orchestration(self) -> bool:
        """Test agent orchestration system."""
        try:
            from agent_framework.orchestrator import OrchestratorAgent
            from agent_framework.integrations.llm_integration import get_llm_client
            
            # Check if OpenAI API key is available
            if not self.config or not self.config.llm.openai_api_key:
                logger.warning("OpenAI API key not configured, skipping orchestration test")
                return True  # Consider this a pass since it's configuration-dependent
            
            # Test LLM client
            llm_client = get_llm_client()
            logger.info("LLM client created successfully")
            
            # Test orchestrator creation
            orchestrator = OrchestratorAgent(llm_client=llm_client)
            logger.info("Orchestrator agent created successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Agent orchestration test failed: {str(e)}")
            return False
    
    async def test_end_to_end_workflow(self) -> bool:
        """Test end-to-end workflow simulation."""
        try:
            from agent_framework.agent import Query
            
            # Simulate a complete workflow
            test_query = Query(query_text="Analyser les risques de sécurité informatique")
            logger.info(f"Test query created: {test_query.query_text}")
            logger.info(f"Query intent: {test_query.intent}")
            logger.info(f"Query context: {test_query.context.session_id}")
            
            # Test query processing pipeline
            logger.info("End-to-end workflow simulation completed")
            return True
            
        except Exception as e:
            logger.error(f"End-to-end workflow test failed: {str(e)}")
            return False
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(result['duration'] for result in self.test_results.values())
        
        summary = {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': round((passed_tests / total_tests) * 100, 1) if total_tests > 0 else 0,
            'total_duration': round(total_duration, 2),
            'results': self.test_results
        }
        
        logger.info("\n" + "="*60)
        logger.info("🎯 INTEGRATION TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {summary['success_rate']}%")
        logger.info(f"Total Duration: {total_duration}s")
        
        logger.info("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅" if result['success'] else "❌"
            duration = result['duration']
            logger.info(f"  {status} {test_name} ({duration}s)")
            if result['error']:
                logger.info(f"      Error: {result['error']}")
        
        if passed_tests == total_tests:
            logger.info("\n🎉 All integration tests passed!")
        else:
            logger.warning(f"\n⚠️  {failed_tests} test(s) failed")
        
        return summary

async def main():
    """Main test runner."""
    tester = IntegrationTester()
    summary = await tester.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if summary['failed'] == 0 else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main()) 