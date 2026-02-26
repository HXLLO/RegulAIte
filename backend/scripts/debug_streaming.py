#!/usr/bin/env python3

import requests
import json
import sys

def debug_streaming_response(query="quels risques sont considerés comme critiques?", verbose=False):
    """
    Debug streaming response to check for duplication patterns.
    
    Args:
        query: The query to send to the chat endpoint
        verbose: Whether to show detailed token-by-token output
    """
    url = "http://localhost:8090/chat/rag"
    
    payload = {
        "messages": [{"role": "user", "content": query}],
        "stream": True,
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2048,
        "include_context": True,
        "use_agent": True
    }
    
    headers = {"Content-Type": "application/json"}
    
    print(f"🔍 Debugging streaming response for: '{query}'")
    print("=" * 80)
    
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        
        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return
        
        collected_tokens = []
        internal_thoughts = []
        full_content = ""
        processing_states = []
        errors = []
        
        for line_num, line in enumerate(response.iter_lines(), 1):
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    
                    if data.get('type') == 'token':
                        content = data.get('content', '')
                        collected_tokens.append(content)
                        full_content += content
                        
                        if verbose:
                            print(f"Token {len(collected_tokens):3d}: '{content}'")
                    
                    elif data.get('type') == 'processing':
                        state = data.get('state', '')
                        processing_states.append(state)
                        
                        if verbose and data.get('internal_thoughts'):
                            thoughts = data.get('internal_thoughts', '')
                            internal_thoughts.append(thoughts)
                            print(f"Internal thoughts ({len(thoughts)} chars): {thoughts[:100]}...")
                    
                    elif data.get('type') == 'end':
                        final_message = data.get('message', '')
                        
                        print(f"\n📊 STREAMING ANALYSIS")
                        print(f"   Total tokens received: {len(collected_tokens)}")
                        print(f"   Content length from tokens: {len(full_content)}")
                        print(f"   Final message length: {len(final_message)}")
                        print(f"   Processing states: {len(processing_states)}")
                        
                        # Duplication analysis
                        print(f"\n🔍 DUPLICATION ANALYSIS")
                        
                        # Check for specific patterns
                        duplication_patterns = [
                            ("internal_thoughts", "Internal thoughts leakage"),
                            ("aprèsaprès", "Character duplication"),
                            ("risles ris", "Word overlap"),
                            ("sontques sont", "Syllable duplication"),
                            ("context le contexte", "Word pair duplication")
                        ]
                        
                        found_issues = []
                        for pattern, description in duplication_patterns:
                            if pattern in final_message.lower():
                                found_issues.append(f"   ❌ {description}: '{pattern}' found")
                        
                        # Check for consecutive duplicates
                        words = final_message.split()
                        consecutive_dups = []
                        for i in range(len(words) - 1):
                            if words[i] == words[i + 1] and len(words[i]) > 2:
                                consecutive_dups.append(words[i])
                        
                        if consecutive_dups:
                            found_issues.append(f"   ❌ Consecutive duplicates: {consecutive_dups}")
                        
                        if found_issues:
                            for issue in found_issues:
                                print(issue)
                        else:
                            print("   ✅ No duplication patterns detected")
                        
                        print(f"\n📝 FINAL MESSAGE:")
                        print("-" * 40)
                        print(final_message)
                        print("-" * 40)
                        break
                    
                    elif data.get('type') == 'error':
                        error_msg = data.get('message', 'Unknown error')
                        errors.append(error_msg)
                        print(f"❌ Error: {error_msg}")
                        break
                
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error on line {line_num}: {e}")
                    if verbose:
                        print(f"   Raw line: {line}")
        
        if errors:
            print(f"\n⚠️  ERRORS ENCOUNTERED: {len(errors)}")
            for error in errors:
                print(f"   - {error}")
                
    except Exception as e:
        print(f"❌ Exception during debugging: {e}")


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "quels risques sont considerés comme critiques?"
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    debug_streaming_response(query, verbose) 