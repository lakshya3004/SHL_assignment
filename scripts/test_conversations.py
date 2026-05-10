import asyncio
import sys
import os
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.request_models import ChatRequest, ChatMessage
from app.api.routes.chat import get_orchestrator

async def run_simulations():
    orchestrator = get_orchestrator()
    
    test_cases = [
        {
            "name": "Vague Query (Should Clarify)",
            "message": "I need an assessment for hiring.",
            "history": []
        },
        {
            "name": "Specific Hiring (Should Recommend)",
            "message": "I'm hiring a Java Backend Developer and need to test their technical skills.",
            "history": []
        },
        {
            "name": "Refinement (Preserve Intent)",
            "message": "Also include some personality tests for the same Java role.",
            "history": [
                ChatMessage(role="user", content="I'm hiring a Java Backend Developer."),
                ChatMessage(role="assistant", content="I recommend the SHL Coding test...")
            ]
        },
        {
            "name": "Comparison Query",
            "message": "What is the difference between the OPQ32 and Verify Interactive tests?",
            "history": []
        },
        {
            "name": "Off-topic Query (Should Refuse)",
            "message": "How do I make a pizza?",
            "history": []
        }
    ]
    
    print("\n" + "="*80)
    print("      CONVERSATION ORCHESTRATION TEST SUITE")
    print("="*80)
    
    for case in test_cases:
        print(f"\n🧪 TEST CASE: {case['name']}")
        print(f"USER: {case['message']}")
        print("-" * 40)
        
        request = ChatRequest(message=case['message'], history=case['history'])
        response = await orchestrator.handle_chat(request)
        
        print(f"ASSISTANT: {response.reply}")
        if response.recommendations:
            print(f"RECOMMENDATIONS: {[r.name for r in response.recommendations]}")
        else:
            print("RECOMMENDATIONS: None")
            
    print("\n" + "="*80)

if __name__ == "__main__":
    # Ensure indices are built before running this
    asyncio.run(run_simulations())
