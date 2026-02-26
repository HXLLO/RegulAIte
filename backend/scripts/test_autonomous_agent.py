#!/usr/bin/env python3
import sys
import asyncio
import json
sys.path.append('/app')

from agent_framework.integrations.chat_integration import get_chat_integration

async def test_autonomous_agent():
    try:
        # Get chat integration
        chat_integration = get_chat_integration()
        print('✅ Chat integration initialized')
        
        # Prepare test request
        request_data = {
            "messages": [
                {"role": "user", "content": "What are the key requirements for GDPR compliance?"}
            ],
            "model": "gpt-4",
            "session_id": "test_session",
            "include_context": True,
            "response_format": "markdown"
        }
        
        # Test autonomous processing
        print('🤖 Testing autonomous agent...')
        response = await chat_integration.process_chat_request(request_data)
        
        if response.get("error"):
            print(f'❌ Agent error: {response.get("message")}')
            return False
        
        print('✅ Autonomous agent responded successfully!')
        print(f'Agent used: {response.get("agent_used")}')
        print(f'Context used: {response.get("context_used")}')
        print(f'Message length: {len(response.get("message", ""))} characters')
        print('\n📝 Response content:')
        print('=' * 80)
        print(response.get("message", ""))
        print('=' * 80)
        
        return True
        
    except Exception as e:
        print(f'❌ Error testing autonomous agent: {e}')
        return False

if __name__ == "__main__":
    result = asyncio.run(test_autonomous_agent())
    sys.exit(0 if result else 1) 