#!/usr/bin/env python3
"""
Test script to verify the SourceInfo and iteration fixes.
"""
import sys
sys.path.append('backend')

from agent_framework.response_generator import SourceInfo, ResponseGenerator
from agent_framework.orchestrator import IterationContext
from agent_framework.agent import AgentResponse
import asyncio

def test_source_info_creation():
    """Test SourceInfo creation with various scenarios."""
    print("=== Testing SourceInfo Creation ===")
    
    # Test 1: Valid dict with title
    try:
        valid_source = SourceInfo(title="Test Document", url="http://example.com")
        print("✅ Valid source with title: OK")
    except Exception as e:
        print(f"❌ Valid source with title failed: {e}")
    
    # Test 2: Dict without title (should use default)
    try:
        no_title_source = SourceInfo()
        print("✅ Source without title: OK")
    except Exception as e:
        print(f"❌ Source without title failed: {e}")
    
    # Test 3: Dict with empty title (should work)
    try:
        empty_title_source = SourceInfo(title="")
        print("✅ Source with empty title: OK")
    except Exception as e:
        print(f"❌ Source with empty title failed: {e}")
    
    # Test 4: Complex source dict (like from RAG)
    try:
        complex_source = SourceInfo(
            title="Complex Document",
            url="http://example.com/doc",
            snippet="This is a snippet",
            relevance_score=0.85,
            source_type="document"
        )
        print("✅ Complex source: OK")
    except Exception as e:
        print(f"❌ Complex source failed: {e}")

def test_agent_response_sources():
    """Test AgentResponse with various source types."""
    print("\n=== Testing AgentResponse Sources ===")
    
    # Test with mixed source types including None
    try:
        mixed_sources_response = AgentResponse(
            content="Test response content",
            sources=[
                {"title": "Valid Dict Source", "url": "http://example.com"},
                "String Source",
                None,  # Should be filtered out
                {"url": "http://example.com/no-title"},  # Dict without title
                123,  # Number (should convert to string)
            ]
        )
        print("✅ AgentResponse with mixed sources: OK")
        print(f"   Cleaned sources count: {len(mixed_sources_response.sources)}")
        print(f"   Source types: {[type(s).__name__ for s in mixed_sources_response.sources]}")
    except Exception as e:
        print(f"❌ AgentResponse with mixed sources failed: {e}")
    
    # Test with empty sources
    try:
        empty_sources_response = AgentResponse(
            content="Test response content",
            sources=[]
        )
        print("✅ AgentResponse with empty sources: OK")
    except Exception as e:
        print(f"❌ AgentResponse with empty sources failed: {e}")
    
    # Test with None sources only
    try:
        none_sources_response = AgentResponse(
            content="Test response content",
            sources=[None, None, None]
        )
        print("✅ AgentResponse with None sources: OK")
        print(f"   Final sources count: {len(none_sources_response.sources)}")
    except Exception as e:
        print(f"❌ AgentResponse with None sources failed: {e}")

def test_iteration_context():
    """Test the improved iteration logic."""
    print("\n=== Testing Iteration Context ===")
    
    # Test with max_iterations = 2 (new default)
    context = IterationContext()
    print(f"Max iterations: {context.max_iterations}")
    
    # First iteration should be allowed
    should_continue = context.should_continue_iteration()
    print(f"Should continue first iteration: {should_continue}")
    
    # Add an iteration with gaps
    context.add_iteration("test query", {"result": "test"}, ["gap1", "gap2"])
    should_continue = context.should_continue_iteration()
    print(f"Should continue after first iteration with gaps: {should_continue}")
    
    # Add another iteration with same gaps (should stop to avoid loops)
    context.add_iteration("test query 2", {"result": "test2"}, ["gap1", "gap2"])
    should_continue = context.should_continue_iteration()
    print(f"Should continue after repeated gaps: {should_continue}")
    
    # Test without gaps
    context_no_gaps = IterationContext()
    context_no_gaps.add_iteration("test query", {"result": "test"}, [])
    should_continue = context_no_gaps.should_continue_iteration()
    print(f"Should continue with no gaps: {should_continue}")

async def test_response_generator():
    """Test the response generator with problematic sources."""
    print("\n=== Testing Response Generator ===")
    
    generator = ResponseGenerator()
    
    # Create a mock AgentResponse with various source formats
    # Now using the fixed AgentResponse that can handle mixed source types
    mock_response = AgentResponse(
        content="Test response content",
        sources=[
            {"title": "Valid Source", "url": "http://example.com"},
            {"url": "http://example.com/no-title"},  # Missing title
            "String Source",  # String source
            None,  # None source (should be filtered out)
            {"title": "", "snippet": "Empty title source"}  # Empty title
        ]
    )
    
    print(f"AgentResponse created with {len(mock_response.sources)} sources after validation")
    
    # Mock query
    class MockQuery:
        query_text = "Test query"
    
    try:
        formatted = await generator.generate(mock_response, MockQuery())
        print(f"✅ Response generation successful")
        print(f"Sources created: {len(formatted.sources) if formatted.sources else 0}")
        
        if formatted.sources:
            for i, source in enumerate(formatted.sources):
                print(f"  Source {i+1}: title='{source.title}', type={source.source_type}")
                
    except Exception as e:
        print(f"❌ Response generation failed: {e}")

if __name__ == "__main__":
    test_source_info_creation()
    test_agent_response_sources()
    test_iteration_context()
    asyncio.run(test_response_generator())
    print("\n=== Test Complete ===") 