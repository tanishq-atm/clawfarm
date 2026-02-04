#!/usr/bin/env python3
"""Phase 3: Enter verification code and generate API key using Browser Use"""
import json
import time
import sys
from browseruse_utils import BrowserUseClient

def main():
    # Load state
    with open('leonardo_automation_state.json', 'r') as f:
        state = json.load(f)
    
    email = state['inbox_id']
    password = state['password']
    code = state.get('verification_code')
    
    if not code:
        print("❌ No verification code in state")
        print("   Run phase2 first to get the code")
        sys.exit(1)
    
    print("🚀 Phase 3: Verifying email + generating API key\n")
    print(f"Email: {email}")
    print(f"Verification code: {code}")
    print()
    
    # Create Browser Use task
    client = BrowserUseClient()
    
    task = f"""Navigate to app.leonardo.ai and log in with:
- Email: {email}
- Password: {password}

You should see a verification code input field. Enter the verification code: {code}

After email verification is complete, navigate to the API settings or developer settings page (look in account menu, user settings, or developer section). Generate a new API key. Extract and return the complete API key value."""
    
    print(f"📋 Task: {task[:200]}...\n")
    
    response = client.create_task(
        task=task,
        start_url="https://app.leonardo.ai",
        max_steps=150
    )
    
    task_id = response.get('id')
    if not task_id:
        print(f"❌ Failed to create task: {response}")
        sys.exit(1)
    
    print(f"✅ Task created: {task_id}")
    print(f"📊 Monitor: https://cloud.browser-use.com/tasks/{task_id}\n")
    print("⏳ Waiting for completion (this may take a few minutes)...\n")
    
    # Poll for completion
    result = client.wait_for_completion(task_id, poll_interval=20)
    
    print("\n🎉 Task complete!")
    print(f"Success: {result['isSuccess']}")
    print(f"Output: {result['output']}\n")
    
    # Save to state
    state['phase3_task_id'] = task_id
    state['phase3_status'] = 'complete' if result['isSuccess'] else 'failed'
    state['phase3_output'] = result['output']
    
    # Try to extract API key from output
    import re
    api_key_patterns = [
        r'(sk-[a-zA-Z0-9]{32,})',  # Common API key format
        r'(leo_[a-zA-Z0-9]{32,})',  # Leonardo-specific
        r'api[_-]?key[:\s]+([a-zA-Z0-9_-]{20,})',  # Generic
    ]
    
    for pattern in api_key_patterns:
        match = re.search(pattern, result['output'], re.IGNORECASE)
        if match:
            api_key = match.group(1)
            state['leonardo_api_key'] = api_key
            print(f"🔑 Extracted API key: {api_key[:20]}...\n")
            break
    
    # Save state
    with open('leonardo_automation_state.json', 'w') as f:
        json.dump(state, f, indent=2)
    
    # Save full response
    with open('leonardo_api_key_response.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("💾 Saved state to leonardo_automation_state.json")
    print("💾 Saved response to leonardo_api_key_response.json")
    
    if result['isSuccess']:
        print("\n✅ Phase 3 complete!")
        if 'leonardo_api_key' in state:
            print(f"🎯 API Key ready: {state['leonardo_api_key']}")
    else:
        print("\n❌ Phase 3 failed")
        print("   Check leonardo_api_key_response.json for details")
        sys.exit(1)

if __name__ == '__main__':
    main()
