#!/usr/bin/env python3
"""
Test script to verify JSON serialization fix
"""
import json

# Simple test of the make_json_serializable function
def make_json_serializable(obj):
    """
    Recursively converts an object into a JSON-serializable format.
    This utility function handles Pydantic models, complex objects, and nested structures.
    """
    if obj is None:
        return None
    
    try:
        # Test if already serializable
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        pass
    
    # Handle different types
    if hasattr(obj, 'model_dump'):
        # Pydantic models - recursively process the dumped data
        return make_json_serializable(obj.model_dump())
    elif hasattr(obj, 'dict'):
        # Other models with dict method
        return make_json_serializable(obj.dict())
    elif isinstance(obj, dict):
        # Dictionary - recursively process values
        result = {}
        for key, value in obj.items():
            result[str(key)] = make_json_serializable(value)
        return result
    elif isinstance(obj, (list, tuple)):
        # List/tuple - recursively process items
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool)):
        # Primitive types
        return obj
    else:
        # Convert to string as fallback
        return str(obj)

# Test cases
test_cases = [
    {"simple": "value"},
    {"nested": {"deep": {"value": 123}}},
    {"mixed": [1, "string", {"nested": True}]},
    {"complex": {"obj": object(), "list": [1, 2, 3]}},
]

print("Testing JSON serialization utility...")
for i, test_case in enumerate(test_cases):
    try:
        result = make_json_serializable(test_case)
        json_str = json.dumps(result)
        print(f"Test {i+1}: PASSED - {len(json_str)} chars")
    except Exception as e:
        print(f"Test {i+1}: FAILED - {e}")

print("All tests completed!") 