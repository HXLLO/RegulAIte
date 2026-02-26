#!/usr/bin/env python3
import sys
import asyncio
sys.path.append('/app')

from agent_framework.factory import get_agent_instance

async def test_agent():
    try:
        agent = await get_agent_instance('rag', 'gpt-4')
        print(f'✅ Agent created successfully: {agent.name}')
        print(f'Agent ID: {agent.agent_id}')
        return True
    except Exception as e:
        print(f'❌ Error creating agent: {e}')
        return False

if __name__ == "__main__":
    result = asyncio.run(test_agent())
    sys.exit(0 if result else 1) 