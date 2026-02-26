#!/usr/bin/env python3
"""
Test script for Query Expansion functionality in the RegulAIte Agent Framework.

This script demonstrates the query expansion capabilities for GRC-focused searches.
"""

import asyncio
import logging
import sys
import os

# Add the backend path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agent_framework.tools.query_expansion import get_query_expander
from agent_framework.factory import create_rag_agent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_query_expansion():
    """Test the query expansion functionality."""
    print("=" * 60)
    print("Testing Query Expansion for GRC Content")
    print("=" * 60)
    
    # Initialize query expander
    query_expander = get_query_expander()
    
    # Test queries
    test_queries = [
        "security risks in data processing",
        "GDPR compliance requirements",
        "ISO27001 audit findings", 
        "risk assessment methodology",
        "incident response procedures",
        "access control policies",
        "vulnerability management",
        "DORA operational resilience"
    ]
    
    for query in test_queries:
        print(f"\n📝 Original Query: '{query}'")
        print("-" * 50)
        
        try:
            # Test different expansion strategies
            for strategy in ["conservative", "balanced", "comprehensive"]:
                expansion_result = await query_expander.expand_query(
                    query,
                    strategy=strategy,
                    max_expansions=6,
                    include_frameworks=True
                )
                
                print(f"\n🔍 Strategy: {strategy.upper()}")
                print(f"   Expanded Terms: {expansion_result.expanded_terms}")
                print(f"   Framework Terms: {expansion_result.framework_terms}")
                print(f"   Confidence Score: {expansion_result.confidence_score:.2f}")
                
                if expansion_result.synonyms:
                    print(f"   Key Synonyms: {dict(list(expansion_result.synonyms.items())[:2])}")
                    
        except Exception as e:
            print(f"❌ Error expanding query '{query}': {str(e)}")
    
    # Display expansion statistics
    print(f"\n📊 Query Expansion Statistics")
    print("=" * 40)
    stats = query_expander.get_expansion_statistics()
    print(f"Total Expansions: {stats['total_expansions']}")
    print(f"Successful Expansions: {stats['successful_expansions']}")
    print(f"Average Expansion Ratio: {stats['average_expansion_ratio']:.2f}")
    
    if stats['most_expanded_terms']:
        print(f"Most Common Expanded Terms:")
        sorted_terms = sorted(stats['most_expanded_terms'].items(), key=lambda x: x[1], reverse=True)
        for term, count in sorted_terms[:5]:
            print(f"  - {term}: {count}")

async def test_rag_agent_with_expansion():
    """Test RAG agent with query expansion enabled."""
    print(f"\n🤖 Testing RAG Agent with Query Expansion")
    print("=" * 50)
    
    try:
        # Create RAG agent with query expansion enabled
        rag_agent = await create_rag_agent(
            agent_id="test_rag_agent",
            name="Test RAG Agent with Expansion",
            use_query_expansion=True,
            max_sources=5
        )
        
        print("✅ RAG Agent created successfully with query expansion enabled")
        
        # Test query processing (mock query)
        if hasattr(rag_agent, 'retrieval_system') and rag_agent.retrieval_system:
            if hasattr(rag_agent.retrieval_system, 'use_query_expansion'):
                expansion_enabled = rag_agent.retrieval_system.use_query_expansion
                print(f"🔍 Query expansion status: {'ENABLED' if expansion_enabled else 'DISABLED'}")
            else:
                print("⚠️  Query expansion status unknown")
        else:
            print("⚠️  RAG integration not available")
            
    except Exception as e:
        print(f"❌ Error creating RAG agent with expansion: {str(e)}")

async def test_custom_synonyms():
    """Test adding custom synonyms to the query expander."""
    print(f"\n🎯 Testing Custom Synonyms")
    print("=" * 30)
    
    query_expander = get_query_expander()
    
    # Add custom GRC synonyms
    query_expander.add_custom_synonyms("pentest", ["penetration testing", "security testing", "ethical hacking"])
    query_expander.add_framework_mapping("PCI-DSS", ["payment card industry", "card security", "payment processing"])
    
    # Test with custom terms
    test_query = "pentest findings for PCI-DSS compliance"
    
    expansion_result = await query_expander.expand_query(
        test_query,
        strategy="comprehensive",
        max_expansions=8,
        include_frameworks=True
    )
    
    print(f"Query: '{test_query}'")
    print(f"Expanded Terms: {expansion_result.expanded_terms}")
    print(f"Framework Terms: {expansion_result.framework_terms}")
    print(f"Confidence: {expansion_result.confidence_score:.2f}")

if __name__ == "__main__":
    print("🚀 Starting Query Expansion Tests")
    
    async def run_all_tests():
        await test_query_expansion()
        await test_rag_agent_with_expansion()
        await test_custom_synonyms()
        print(f"\n✅ All tests completed!")
    
    # Run the tests
    asyncio.run(run_all_tests()) 