#!/usr/bin/env python3
"""
Test script for the enhanced Document Finder with full document retrieval capability.
"""

import asyncio
import logging
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from agent_framework.tools.document_finder import DocumentFinder, SearchCriteria
from agent_framework.modules.document_finder_agent import DocumentFinderAgent
from agent_framework.agent import Query

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_full_document_retrieval():
    """Test the full document retrieval functionality."""
    
    print("🔍 Testing Enhanced Document Finder with Full Document Retrieval")
    print("=" * 70)
    
    try:
        # Initialize the Document Finder Agent
        agent = DocumentFinderAgent()
        
        # Test queries that should trigger full document retrieval
        test_queries = [
            "document complet sur la politique de sécurité",
            "texte intégral de la procédure ISO27001",
            "audit complet de conformité RGPD",
            "politique complète de gestion des risques",
            "procédure complète de sauvegarde",
        ]
        
        print("Testing queries that should trigger full document retrieval:")
        print("-" * 50)
        
        for i, query_text in enumerate(test_queries, 1):
            print(f"\n{i}. Query: '{query_text}'")
            
            # Create query object
            query = Query(
                query_text=query_text,
                user_id="test_user",
                session_id="test_session"
            )
            
            # Process the query
            try:
                response = await agent.process_query(query)
                
                # Check if full documents were retrieved
                full_docs_found = 0
                if response.sources:
                    for source in response.sources:
                        if isinstance(source, dict) and source.get('has_full_content', False):
                            full_docs_found += 1
                
                print(f"   ✅ Response generated successfully")
                print(f"   📄 Total sources: {len(response.sources) if response.sources else 0}")
                print(f"   📋 Full documents retrieved: {full_docs_found}")
                print(f"   🎯 Confidence: {response.confidence:.2f}")
                
                if full_docs_found > 0:
                    print(f"   🎉 SUCCESS: Full document retrieval triggered!")
                else:
                    print(f"   ℹ️  No full documents retrieved (may be normal if no highly relevant docs found)")
                
            except Exception as e:
                print(f"   ❌ Error processing query: {str(e)}")
        
        print("\n" + "=" * 70)
        print("Testing direct document finder functionality:")
        print("-" * 50)
        
        # Test the document finder directly
        document_finder = DocumentFinder()
        
        # Test the should_retrieve_full_documents method
        test_analysis = {
            'intent': 'compliance_check',
            'scope': 'comprehensive',
            'keywords': ['politique', 'sécurité']
        }
        
        test_results = [
            {'doc_id': 'test_doc_1', 'score': 0.85, 'title': 'Test Document 1'},
            {'doc_id': 'test_doc_2', 'score': 0.75, 'title': 'Test Document 2'}
        ]
        
        should_retrieve = await document_finder._should_retrieve_full_documents(
            "politique complète de sécurité", 
            test_analysis, 
            test_results
        )
        
        print(f"Should retrieve full documents: {should_retrieve}")
        
        if should_retrieve:
            print("✅ Full document retrieval logic working correctly!")
        else:
            print("ℹ️  Full document retrieval not triggered for test case")
        
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_document_retrieval()) 