#!/usr/bin/env python3

import requests
import json
import time

# Test the chat endpoint to verify duplication issue is fixed
def test_chat_duplication():
    url = "http://localhost:8090/chat/rag"
    
    payload = {
        "messages": [
            {"role": "user", "content": "quels risques sont considerés comme critiques?"}
        ],
        "stream": True,
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2048,
        "include_context": True,
        "use_agent": True
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Sending test message to check for duplication issues...")
    print(f"Query: {payload['messages'][0]['content']}")
    print("-" * 50)
    
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        
        if response.status_code == 200:
            print("Response received. Processing stream...")
            
            full_content = ""
            token_count = 0
            problematic_patterns = []
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        
                        if data.get('type') == 'token':
                            content = data.get('content', '')
                            full_content += content
                            token_count += 1
                            
                            # Check for duplication patterns in real-time
                            if token_count % 10 == 0:  # Check every 10 tokens
                                # Check for specific duplication patterns
                                patterns_to_check = [
                                    ('internalernal', 'internal_thoughts leakage'),
                                    ('aprèsaprès', 'character-level duplication'),
                                    ('risLes ris', 'word-level duplication'),
                                    ('sontques sont', 'syllable duplication'),
                                    ('context le contexte', 'word overlap duplication'),
                                    ('foure fourni', 'partial word duplication')
                                ]
                                
                                for pattern, description in patterns_to_check:
                                    if pattern in full_content.lower():
                                        problematic_patterns.append((pattern, description))
                        
                        elif data.get('type') == 'end':
                            print(f"\n\nStream ended.")
                            final_message = data.get('message', '')
                            print(f"Final message length: {len(final_message)}")
                            print(f"Collected content length: {len(full_content)}")
                            
                            # Comprehensive duplication check
                            duplication_found = False
                            
                            # Check for internal_thoughts leakage
                            if any(phrase in final_message.lower() for phrase in ['internal_thoughts', 'internalernal', '<internal', '</internal']):
                                print("❌ WARNING: internal_thoughts patterns found in final message!")
                                duplication_found = True
                            
                            # Check for specific patterns from user's example
                            user_patterns = [
                                "d'd'après", "aprèsaprès", "le context le contexte", 
                                "foure fourni", "risles ris", "sontques sont",
                                "considér considérés", "critiques lors critiques",
                                "obti obtiennent", "score total score total"
                            ]
                            
                            found_patterns = []
                            for pattern in user_patterns:
                                if pattern in final_message.lower():
                                    found_patterns.append(pattern)
                                    duplication_found = True
                            
                            if found_patterns:
                                print(f"❌ WARNING: User-reported duplication patterns detected: {found_patterns}")
                            
                            # Check for general repetition patterns
                            words = final_message.split()
                            for i in range(len(words) - 1):
                                if words[i] == words[i + 1] and len(words[i]) > 2:
                                    print(f"❌ WARNING: Consecutive word duplication detected: '{words[i]}'")
                                    duplication_found = True
                                    break
                            
                            # Check for overlapping word patterns
                            for i in range(len(words) - 3):
                                if words[i] == words[i + 2] and words[i + 1] == words[i + 3]:
                                    print(f"❌ WARNING: Overlapping word pattern detected: '{words[i]} {words[i+1]}'")
                                    duplication_found = True
                                    break
                            
                            if problematic_patterns:
                                print(f"❌ WARNING: Real-time patterns detected: {problematic_patterns}")
                                duplication_found = True
                            
                            if not duplication_found:
                                print("✅ No duplication patterns detected - fix appears to be working!")
                            
                            print("\nFinal message:")
                            print("-" * 30)
                            print(final_message)
                            print("-" * 30)
                            break
                            
                        elif data.get('type') == 'processing':
                            if data.get('internal_thoughts'):
                                thoughts_len = len(data.get('internal_thoughts', ''))
                                if thoughts_len % 100 == 0:  # Log every 100 chars
                                    print(f"\n[Internal thoughts: {thoughts_len} chars]", end='')
                        
                        elif data.get('type') == 'error':
                            print(f"\nError: {data.get('message')}")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"\nJSON decode error: {e}")
                        continue
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error during test: {e}")


def test_duplication_cleaning():
    """Test the frontend content cleaning logic with exact patterns from user's example"""
    print("\n" + "="*50)
    print("Testing content cleaning logic...")
    print("="*50)
    
    # Exact test cases from user's example
    test_cases = [
        "s> L'utilisateurL'utilisateur souhaite souhaite comprendre comprendre quels quels types de types de risques risques sont consid sont considérésérés comme critiques comme critiques",
        "D'D'aprèsaprès le context le contexte foure fourni,ni, il semble il semble que la que la classification des classification des risques risques",
        "Les risLes risques sontques sont considér considérés commeés comme critiques lors critiques lorsqu'ilsqu'ils obti obtiennent unennent un score total score total de de 15 à15 à 25 25",
        "dans la dans la matrice matrice de critic de criticité.ité. Ce score Ce score est obt est obtenu enenu en multipliant multipliant les scores les scores",
        "Il estIl est important de important de noter noter que ces que ces risques risques critiques sont critiques sont considér considérésérés comme inaccept inacceptables etables et"
    ]
    
    for test_case in test_cases:
        print(f"\nOriginal: '{test_case[:100]}{'...' if len(test_case) > 100 else ''}'")
        
        # Apply the improved cleaning logic (simulating frontend cleaning)
        cleaned = test_case
        
        # Remove internal thoughts
        cleaned = cleaned.replace('internal_thoughts', '')
        
        # Apply duplication patterns (simulating frontend JS regex)
        
        # Pattern 1: Immediate word duplication "word word" -> "word"
        import re
        cleaned = re.sub(r'(\b\w+)\s+\1\b', r'\1', cleaned)
        
        # Pattern 2: Character-level duplication within words "D'D'après" -> "D'après"  
        cleaned = re.sub(r"(\w+)('\w+)\1\2", r'\1\2', cleaned)
        
        # Pattern 3: Partial word duplication "aprèsaprès" -> "après"
        cleaned = re.sub(r'(\w{3,})\1', r'\1', cleaned)
        
        # Pattern 4: Complex pattern like "Les risLes risques" -> "Les risques"
        cleaned = re.sub(r'(\w{3,})\s+\1(\w+)', r'\1\2', cleaned)
        
        # Pattern 5: Syllable duplication like "sontques sont" -> "sont"
        cleaned = re.sub(r'(\w+)(\w{3,})\s+\1\s+\2', r'\1 \2', cleaned)
        
        # Pattern 6: Number duplication like "15 à15 à 25 25" -> "15 à 25"
        cleaned = re.sub(r'(\d+)\s+à\1\s+à\s+(\d+)\s+\2', r'\1 à \2', cleaned)
        
        # Pattern 7: Phrase duplication "dans la dans la" -> "dans la"
        cleaned = re.sub(r'(\w+\s+\w+)\s+\1', r'\1', cleaned)
        
        # Clean up excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        print(f"Cleaned:  '{cleaned[:100]}{'...' if len(cleaned) > 100 else ''}'")
        
        # Check if cleaning was effective
        if cleaned != test_case:
            print("✅ Content was cleaned successfully")
        else:
            print("❌ No changes made - patterns may need adjustment")
        
        # Check for remaining duplication patterns
        words = cleaned.split()
        has_duplicates = any(i < len(words)-1 and words[i] == words[i+1] for i in range(len(words)))
        if has_duplicates:
            print("⚠️  Still contains duplicate words")
        else:
            print("✅ No obvious duplicate words remain")


if __name__ == "__main__":
    test_chat_duplication()
    test_duplication_cleaning() 