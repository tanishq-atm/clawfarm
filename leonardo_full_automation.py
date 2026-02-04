#!/usr/bin/env python3
"""
Leonardo.ai Full Automation
Creates AgentMail inbox → signs up → verifies email → extracts API key
"""
import json
import time
import sys
import os
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import utilities
from agentmail_utils import AgentMailClient
from browseruse_utils import BrowserUseClient

def main():
    print("🚀 Leonardo.ai Full Automation\n")
    print("="*60)
    
    # Initialize state
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    username = f"leonardo-bot-{timestamp}"
    password = f"L30Bot{timestamp}!Secure"
    
    state = {
        "started_at": datetime.utcnow().isoformat(),
        "username": username,
        "password": password,
    }
    
    # Phase 1: Create inbox and sign up
    print("\n📬 Phase 1: Creating inbox and signing up\n")
    
    agentmail = AgentMailClient()
    
    # Create inbox
    inbox_response = agentmail.create_inbox(username=username)
    inbox_id = f"{username}@agentmail.to"
    state["inbox_id"] = inbox_id
    
    print(f"✅ Created inbox: {inbox_id}")
    
    # Browser Use signup
    browser = BrowserUseClient()
    
    task_prompt = f"""Navigate to app.leonardo.ai and sign up for a new account using:
- Email: {inbox_id}
- Password: {password}

Fill out the signup form completely and submit it. Stop when you reach the email verification step (where it asks for a verification code or to check your email)."""
    
    print(f"🌐 Starting Browser Use signup task...")
    
    signup_response = browser.create_task(
        task=task_prompt,
        start_url="https://app.leonardo.ai",
        max_steps=100
    )
    
    task_id = signup_response.get('id')
    state["phase1_task_id"] = task_id
    
    print(f"   Task ID: {task_id}")
    print(f"   Monitor: https://cloud.browser-use.com/tasks/{task_id}")
    
    # Wait for signup completion
    print(f"\n⏳ Waiting for signup to complete...")
    signup_result = browser.wait_for_completion(task_id, verbose=False)
    
    state["phase1_status"] = "complete" if signup_result.get('isSuccess') else "failed"
    state["phase1_output"] = signup_result.get('output', '')
    
    if not signup_result.get('isSuccess'):
        print(f"\n❌ Phase 1 failed: {signup_result.get('output')}")
        save_state(state)
        sys.exit(1)
    
    print(f"✅ Phase 1 complete: Account created")
    
    # Phase 2: Get verification code
    print(f"\n📧 Phase 2: Retrieving verification code\n")
    
    print(f"⏳ Polling {inbox_id} for verification email...")
    
    # Poll for email
    verification_email = agentmail.wait_for_email(
        inbox_id=inbox_id,
        from_domain="leonardo.ai",
        timeout_seconds=300,
        poll_interval=15
    )
    
    if not verification_email:
        print(f"\n❌ No verification email received")
        state["phase2_status"] = "failed"
        save_state(state)
        sys.exit(1)
    
    # Get full email content
    msg_id = verification_email.get('message_id')
    full_email = agentmail.get_messages(inbox_id, limit=1)[0]
    
    # Extract verification code
    # We need to get the full message with .get()
    messages = agentmail.get_messages(inbox_id)
    if messages:
        # AgentMail SDK usage
        from agentmail import AgentMail
        client = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        full_msg = client.inboxes.messages.get(inbox_id=inbox_id, message_id=messages[0].get('message_id'))
        
        html_content = full_msg.html or full_msg.text or ""
        
        # Extract 6-digit code
        code_match = re.search(r'\b(\d{6})\b', html_content)
        
        if not code_match:
            print(f"\n❌ Could not extract verification code from email")
            state["phase2_status"] = "failed"
            save_state(state)
            sys.exit(1)
        
        verification_code = code_match.group(1)
        state["verification_code"] = verification_code
        state["phase2_status"] = "complete"
        
        print(f"✅ Phase 2 complete: Got verification code {verification_code}")
    else:
        print(f"\n❌ No messages found")
        state["phase2_status"] = "failed"
        save_state(state)
        sys.exit(1)
    
    # Phase 3: Verify and get API key
    print(f"\n🔑 Phase 3: Verifying email and generating API key\n")
    
    verify_task = f"""Navigate to app.leonardo.ai and log in with:
- Email: {inbox_id}
- Password: {password}

You should see a verification code input field. Enter the verification code: {verification_code}

After email verification is complete, navigate to the API settings or developer settings page (look in account menu, user settings, or developer section). Generate a new API key. Extract and return the complete API key value."""
    
    print(f"🌐 Starting verification task...")
    
    verify_response = browser.create_task(
        task=verify_task,
        start_url="https://app.leonardo.ai",
        max_steps=150
    )
    
    verify_task_id = verify_response.get('id')
    state["phase3_task_id"] = verify_task_id
    
    print(f"   Task ID: {verify_task_id}")
    print(f"   Monitor: https://cloud.browser-use.com/tasks/{verify_task_id}")
    
    # Wait for verification + key generation
    print(f"\n⏳ Waiting for verification and API key generation...")
    verify_result = browser.wait_for_completion(verify_task_id, verbose=False)
    
    state["phase3_status"] = "complete" if verify_result.get('isSuccess') else "failed"
    state["phase3_output"] = verify_result.get('output', '')
    
    if not verify_result.get('isSuccess'):
        print(f"\n❌ Phase 3 failed: {verify_result.get('output')}")
        save_state(state)
        sys.exit(1)
    
    # Extract API key from output
    output = verify_result.get('output', '')
    
    # Common API key patterns
    api_key_patterns = [
        r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',  # UUID format
        r'(sk-[a-zA-Z0-9]{32,})',  # sk- prefix
        r'(leo_[a-zA-Z0-9]{32,})',  # leo_ prefix
    ]
    
    api_key = None
    for pattern in api_key_patterns:
        match = re.search(pattern, output)
        if match:
            api_key = match.group(1)
            break
    
    if not api_key:
        print(f"\n⚠️  Could not auto-extract API key from output")
        print(f"Output: {output}")
        print(f"\nCheck leonardo_automation_state.json for the raw output")
    else:
        state["leonardo_api_key"] = api_key
        
        # Save to .env
        with open('.env', 'a') as f:
            f.write(f'\nLEONARDO_API_KEY={api_key}\n')
        
        print(f"✅ Phase 3 complete: API key extracted")
        print(f"🔑 API Key: {api_key}")
    
    # Save final state
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
