#!/usr/bin/env python3
"""
Test script to verify RAG source enrichment is working correctly.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_rag_sources():
    """Test that RAG sources are properly enriched with document metadata."""
    
    try:
        # Import the RAG system
        from main import rag_system
        
        if rag_system is None:
            print("❌ RAG system is not initialized")
            return False
            
        print("✅ RAG system is available")
        
        # Test a simple query
        query = "document test"
        print(f"🔍 Testing query: '{query}'")
        
        # Get RAG results
        results = rag_system.retrieve(query, top_k=3)
        
        if not results:
            print("❌ No results returned from RAG system")
            return False
            
        print(f"✅ Retrieved {len(results)} documents")
        
        # Check if documents have enriched metadata
        success = True
        for i, doc in enumerate(results):
            print(f"\n📄 Document {i+1}:")
            print(f"   Keys: {list(doc.keys())}")
            
            # Check for essential fields
            filename = doc.get('filename')
            original_filename = doc.get('original_filename')
            title = doc.get('title')
            doc_id = doc.get('doc_id')
            
            print(f"   filename: {filename}")
            print(f"   original_filename: {original_filename}")
            print(f"   title: {title}")
            print(f"   doc_id: {doc_id}")
            
            if not (filename or original_filename or title):
                print(f"   ❌ Missing document name information")
                success = False
            else:
                print(f"   ✅ Has document name information")
                
        return success
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run the test."""
    print("🚀 Testing RAG source enrichment...")
    
    # Wait for application startup if needed
    import time
    time.sleep(2)
    
    success = asyncio.run(test_rag_sources())
    
    if success:
        print("\n🎉 RAG source enrichment test PASSED!")
    else:
        print("\n💥 RAG source enrichment test FAILED!")
        
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 