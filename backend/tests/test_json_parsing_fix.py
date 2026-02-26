#!/usr/bin/env python3
"""
Test script for JSON parsing fix in framework parser.

This script tests the robust JSON extraction function against various edge cases
that can cause parsing errors.
"""

import sys
import os
import json

# Add the backend path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agent_framework.tools.framework_parser import extract_json_from_llm_response

def test_json_extraction():
    """Test the robust JSON extraction function with various edge cases."""
    
    print("Testing JSON Extraction Robustness")
    print("=" * 50)
    
    # Test cases that commonly cause issues
    test_cases = [
        {
            "name": "Valid JSON with extra text after",
            "input": '''{"requirements": [{"id": "1", "title": "test"}]} 

This is some additional text that would cause the original parser to fail.''',
            "expected_keys": ["requirements"]
        },
        {
            "name": "JSON in code block",
            "input": '''Here's the analysis:

```json
{
    "requirements": [
        {"id": "RGPD.1", "title": "Data Protection"}
    ]
}
```

Let me know if you need more details.''',
            "expected_keys": ["requirements"]
        },
        {
            "name": "Nested JSON with extra content",
            "input": '''{"analysis": {"business_impact": {"summary": "High impact"}, "complexity": "medium"}}

Additional explanation text here.''',
            "expected_keys": ["analysis"]
        },
        {
            "name": "JSON with line breaks and formatting",
            "input": '''
{
    "mappings": [
        {
            "source_id": "A.5.1",
            "target_id": "4.1", 
            "mapping_type": "full",
            "confidence": 0.9
        }
    ]
}

End of response.''',
            "expected_keys": ["mappings"]
        },
        {
            "name": "Multiple JSON objects (should take first)",
            "input": '''{"first": "object"} {"second": "object"}''',
            "expected_keys": ["first"]
        },
        {
            "name": "JSON with escaped quotes",
            "input": '''{"description": "This is a \\"test\\" description", "valid": true}''',
            "expected_keys": ["description", "valid"]
        },
        {
            "name": "Empty response",
            "input": "",
            "expected_keys": []
        },
        {
            "name": "No JSON in response",
            "input": "This is just plain text with no JSON structure.",
            "expected_keys": []
        },
        {
            "name": "Invalid JSON with recovery",
            "input": '''{"malformed": json, but we should handle it gracefully}''',
            "expected_keys": []
        },
        {
            "name": "French content with accents",
            "input": '''{"exigences": [{"id": "RGPD.1", "titre": "Protection des données", "description": "Exigence de sécurité"}]}''',
            "expected_keys": ["exigences"]
        }
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            result = extract_json_from_llm_response(test_case["input"])
            
            if test_case["expected_keys"]:
                # Check if expected keys are present
                missing_keys = [key for key in test_case["expected_keys"] if key not in result]
                if missing_keys:
                    print(f"❌ FAILED: Missing expected keys: {missing_keys}")
                    print(f"   Got: {list(result.keys())}")
                    failed += 1
                else:
                    print(f"✅ PASSED: Found expected keys: {test_case['expected_keys']}")
                    print(f"   Result: {json.dumps(result, indent=2)[:100]}...")
                    passed += 1
            else:
                # Expecting empty result
                if not result:
                    print("✅ PASSED: Correctly returned empty result for invalid input")
                    passed += 1
                else:
                    print(f"❌ FAILED: Expected empty result but got: {result}")
                    failed += 1
                    
        except Exception as e:
            print(f"❌ FAILED: Exception occurred: {str(e)}")
            failed += 1
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"Test Results Summary")
    print(f"=" * 50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "N/A")
    
    if failed == 0:
        print("\n🎉 All tests passed! JSON extraction is robust.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the implementation.")
    
    return failed == 0

def test_original_vs_robust():
    """Compare original simple extraction vs robust extraction."""
    print(f"\n🔍 Comparing Original vs Robust Extraction")
    print("=" * 50)
    
    # Problematic input that would fail with original method
    problematic_input = '''{"requirements": [{"id": "RGPD.1", "title": "Data protection"}]}

This extra content would cause "Extra data" JSON parsing error in the original method.
Line 11 column 4 (char 1092) type errors.'''
    
    print("Input that causes original parser to fail:")
    print(problematic_input[:100] + "...")
    
    # Test robust extraction
    try:
        result = extract_json_from_llm_response(problematic_input)
        print(f"\n✅ Robust extraction succeeded:")
        print(f"   Found {len(result.get('requirements', []))} requirements")
        print(f"   Keys: {list(result.keys())}")
        return True
    except Exception as e:
        print(f"\n❌ Robust extraction failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting JSON Parsing Fix Tests")
    
    success1 = test_json_extraction()
    success2 = test_original_vs_robust()
    
    if success1 and success2:
        print(f"\n🎉 All tests completed successfully!")
        print("   The JSON parsing fix should resolve the framework parser errors.")
    else:
        print(f"\n❌ Some tests failed. Please review the implementation.")
        
    print(f"\n💡 The fix addresses the 'Extra data: line 11 column 4' error")
    print("   by using robust JSON extraction with multiple fallback strategies.") 