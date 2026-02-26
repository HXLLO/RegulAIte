import asyncio
import sys
import json
sys.path.append('/app')

from agent_framework.integrations.llm_integration import get_llm_client
from agent_framework.orchestrator import OrchestratorAgent

async def simple_test():
    print("Testing orchestrator analysis...")
    llm = get_llm_client()
    orc = OrchestratorAgent(llm)
    
    res = await orc._analyze_request('Quelles mesures sont prises pour la sûreté et la sécurité physique?')
    
    print("Analysis result:")
    print(json.dumps(res, indent=2))
    
    print(f"Has sequence_execution: {'sequence_execution' in res}")
    print(f"Sequence length: {len(res.get('sequence_execution', []))}")
    
    seq = res.get('sequence_execution', [])
    if seq:
        print("Sequence steps:")
        for step in seq:
            print(f"  Step {step.get('etape', 0)}: {step.get('action', 'Unknown')} -> {step.get('agent', 'Unknown')}")
    else:
        print("NO EXECUTION SEQUENCE - This is the problem!")

asyncio.run(simple_test()) 