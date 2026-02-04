#!/usr/bin/env python3
"""
Leonardo.ai Automation v3 - Session Continuation (The Right Way)
Creates session → Task 1 signup → Poll email → Task 2 verification in SAME browser
"""
import json
import time
import sys
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from agentmail_utils import AgentMailClient
from browseruse_utils import BrowserUseClient

def main():
    print("🚀 Leonardo.ai Automation v3 - Session Continuation\n")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    username = f"leonardo-bot-{timestamp}"
    password = f"L30Bot{timestamp}!Secure"
    
    state = {
        "started_at": datetime.now().isoformat(),
        "username": username,
        "password": password,
    }
    
    # Initialize clients
    agentmail = AgentMailClient()
    browser = BrowserUseClient()
    
    # Create inbox
    print("📬 Phase 1: Creating inbox and browser session\n")
    
    inbox_response = agentmail.create_inbox(username=username)
    inbox_id = f"{username}@agentmail.to"
    state["inbox_id"] = inbox_id
    
    print(f"✅ Inbox created: {inbox_id}")
    
    # Create Browser Use SESSION (not task yet)
    session = browser.create_session()
    session_id = session.get('id')
    live_url = session.get('liveUrl')
    
    state["session_id"] = session_id
    
    print(f"✅ Browser session created: {session_id}")
    print(f"📺 Live view: {live_url}\n")
    
    # Task 1: Signup in that session
    print("🌐 Creating signup task in session...")
    
    task1_prompt = f"""Navigate to app.leonardo.ai and sign up for a new account using:
- Email: {inbox_id}
- Password: {password}

Fill out the signup form completely and submit it. Stop when you reach the email verification step (where it asks for a verification code)."""
    
    task1_response = browser.create_task(
        task=task1_prompt,
        start_url="https://app.leonardo.ai",
        max_steps=100,
        session_id=session_id,  # Use the session!
        llm="browser-use-2.0"  # Latest optimized Browser Use model
    )
    
    task1_id = task1_response.get('id')
    state["phase1_task_id"] = task1_id
    
    print(f"   Task ID: {task1_id}")
    print(f"   Monitor: https://cloud.browser-use.com/tasks/{task1_id}")
    
    # Wait for signup
    print(f"\n⏳ Waiting for signup to complete...")
    task1_result = browser.wait_for_completion(task1_id, verbose=False)
    
    state["phase1_status"] = "complete" if task1_result.get('isSuccess') else "failed"
    state["phase1_output"] = task1_result.get('output', '')
    
    if not task1_result.get('isSuccess'):
        print(f"\n❌ Phase 1 failed: {task1_result.get('output')}")
        browser.stop_session(session_id)
        save_state(state)
        sys.exit(1)
    
    print(f"✅ Phase 1 complete: Account created (browser still open)")
    
    # Phase 2: Get verification code
    print(f"\n📧 Phase 2: Polling for verification email\n")
    
    from agentmail import AgentMail
    am_client = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
    
    verification_code = None
    
    for i in range(20):  # 5 minutes max
        time.sleep(15)
        print(f"   [{i+1}/20] Checking inbox...")
        
        messages = am_client.inboxes.messages.list(inbox_id=inbox_id, limit=1)
        if messages.messages:
            msg = messages.messages[0]
            full_msg = am_client.inboxes.messages.get(inbox_id=inbox_id, message_id=msg.message_id)
            
            html = full_msg.html or full_msg.text or ""
            code_match = re.search(r'\b(\d{6})\b', html)
            
            if code_match:
                verification_code = code_match.group(1)
                print(f"   ✅ Got code: {verification_code}")
                break
    
    if not verification_code:
        print(f"\n❌ No verification code received")
        browser.stop_session(session_id)
        state["phase2_status"] = "failed"
        save_state(state)
        sys.exit(1)
    
    state["verification_code"] = verification_code
    state["phase2_status"] = "complete"
    
    print(f"✅ Phase 2 complete: Got verification code {verification_code}")
    
    # Phase 3: Continue in SAME browser
    print(f"\n🎯 Phase 3: Continuing in same browser session\n")
    
    task2_prompt = f"""Continue on app.leonardo.ai. You are completing signup for:
- Email: {inbox_id}
- Password: {password}

You should see a verification code input field. Enter the verification code: {verification_code}

After email verification is complete, navigate to the API settings or developer settings page (look in account menu, user settings, or developer section). Generate a new API key. Extract and return the complete API key value."""
    
    print(f"🌐 Creating verification task in same session...")
    
    task2_response = browser.create_task(
        task=task2_prompt,
        max_steps=150,
        session_id=session_id,  # SAME SESSION!
        llm="browser-use-2.0"  # Latest optimized Browser Use model
    )
    
    task2_id = task2_response.get('id')
    state["phase3_task_id"] = task2_id
    
    print(f"   Task ID: {task2_id}")
    print(f"   Monitor: https://cloud.browser-use.com/tasks/{task2_id}")
    
    # Wait for verification + key extraction
    print(f"\n⏳ Waiting for verification and API key generation...")
    task2_result = browser.wait_for_completion(task2_id, verbose=False)
    
    state["phase3_status"] = "complete" if task2_result.get('isSuccess') else "failed"
    state["phase3_output"] = task2_result.get('output', '')
    
    # Try to stop session (may auto-close)
    try:
        browser.stop_session(session_id)
        print(f"🧹 Session stopped")
    except Exception as e:
        print(f"⚠️  Session cleanup: {e} (may have auto-closed)")
    
    if not task2_result.get('isSuccess'):
        print(f"\n❌ Phase 3 failed: {task2_result.get('output')}")
        save_state(state)
        sys.exit(1)
    
    # Extract API key
    output = task2_result.get('output', '')
    
    api_key_patterns = [
        r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
        r'(sk-[a-zA-Z0-9]{32,})',
        r'(leo_[a-zA-Z0-9]{32,})',
    ]
    
    api_key = None
    for pattern in api_key_patterns:
        match = re.search(pattern, output)
        if match:
            api_key = match.group(1)
            break
    
    if not api_key:
        print(f"\n⚠️  Could not auto-extract API key")
        print(f"Output: {output}")
    else:
        state["leonardo_api_key"] = api_key
        
        # Save to .env
        with open('.env', 'a') as f:
            f.write(f'\nLEONARDO_API_KEY={api_key}\n')
        
        print(f"✅ Phase 3 complete: API key extracted")
        print(f"🔑 API Key: {api_key}")
        
        # Phase 4: Test the API key by generating an image
        print(f"\n🎨 Phase 4: Testing API key with image generation\n")
        
        import httpx
        try:
            response = httpx.post(
                'https://cloud.leonardo.ai/api/rest/v1/generations',
                headers={'Authorization': f'Bearer {api_key}'},
                json={
                    'prompt': 'A cute robot mascot holding an envelope, digital art, vibrant colors',
                    'modelId': 'b24e16ff-06e3-43eb-8d33-4416c2d75876',  # Leonardo Kino XL
                    'width': 512,
                    'height': 512,
                    'num_images': 1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generation_id = result.get('sdGenerationJob', {}).get('generationId')
                state["image_generation_id"] = generation_id
                print(f"✅ Image generation started!")
                print(f"   Generation ID: {generation_id}")
                print(f"   Cost: {result.get('sdGenerationJob', {}).get('cost', {}).get('amount', 'N/A')} USD")
            else:
                print(f"⚠️  Image generation failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"⚠️  Image generation error: {e}")
    
    # Save state
    save_state(state)
    
    print(f"\n{'='*60}")
    print(f"🎉 Automation Complete!\n")
    print(f"Account: {inbox_id}")
    print(f"Password: {password}")
    if api_key:
        print(f"API Key: {api_key}")
        print(f"\n💾 API key saved to .env as LEONARDO_API_KEY")
    print(f"💾 Full state saved to leonardo_automation_state.json")
    print(f"{'='*60}")

def save_state(state):
    """Save state to JSON file"""
    with open('leonardo_automation_state.json', 'w') as f:
        json.dump(state, f, indent=2)

if __name__ == '__main__':
    main()
