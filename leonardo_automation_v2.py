#!/usr/bin/env python3
"""
Leonardo.ai Automation v2 - Webhook + CDP Hybrid
Creates AgentMail inbox → Browser Use signup → Webhook notification → CDP takeover
"""
import json
import time
import sys
import os
import re
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import utilities
from agentmail_utils import AgentMailClient
from browseruse_utils import BrowserUseClient
from cdp_controller import control_leonardo_verification

def wait_for_webhook_email(timeout_seconds: int = 300) -> dict:
    """Poll webhook endpoint for email"""
    print(f"⏳ Waiting for webhook email (timeout: {timeout_seconds}s)")
    
    import httpx
    webhook_url = os.getenv('WEBHOOK_URL', 'http://localhost:5000')
    
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            response = httpx.get(f"{webhook_url}/webhook/latest", timeout=5)
            if response.status_code == 200:
                email = response.json()
                print(f"✅ Webhook email received!")
                return email
        except:
            pass
        
        time.sleep(2)
    
    return None

def extract_verification_code(email_data: dict) -> str:
    """Extract 6-digit code from email"""
    html = email_data.get('html', '')
    text = email_data.get('text', '')
    content = html or text
    
    # Look for 6-digit code
    match = re.search(r'\b(\d{6})\b', content)
    if match:
        return match.group(1)
    
    return None

def get_cdp_url_from_browseruse(task_id: str) -> str:
    """Extract CDP URL from Browser Use session"""
    # Browser Use API returns session info with CDP URL
    # Format: ws://host:port/devtools/browser/<id>
    
    client = BrowserUseClient()
    task = client.get_task(task_id)
    
    session_id = task.get('sessionId')
    if not session_id:
        return None
    
    # Browser Use cloud browsers expose CDP on specific endpoints
    # This is the format from their API docs
    cdp_url = f"wss://cloud.browser-use.com/sessions/{session_id}/cdp"
    
    return cdp_url

def main():
    print("🚀 Leonardo.ai Automation v2 (Webhook + CDP)\n")
    print("="*60)
    
    # Check webhook server is running
    webhook_url = os.getenv('WEBHOOK_URL', 'http://localhost:5000')
    print(f"📡 Webhook URL: {webhook_url}")
    
    try:
        import httpx
        health = httpx.get(f"{webhook_url}/health", timeout=5)
        if health.status_code != 200:
            print("❌ Webhook server not running!")
            print("   Start it with: python webhook_server.py")
            sys.exit(1)
        print("✅ Webhook server is healthy\n")
    except:
        print("❌ Cannot reach webhook server!")
        print("   Start it with: python webhook_server.py")
        sys.exit(1)
    
    # Initialize state
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    username = f"leonardo-bot-{timestamp}"
    password = f"L30Bot{timestamp}!Secure"
    
    state = {
        "started_at": datetime.now().isoformat(),
        "username": username,
        "password": password,
    }
    
    # Phase 1: Create inbox and sign up
    print("📬 Phase 1: Creating inbox and signing up\n")
    
    agentmail = AgentMailClient()
    
    # Create inbox
    inbox_response = agentmail.create_inbox(username=username)
    inbox_id = f"{username}@agentmail.to"
    state["inbox_id"] = inbox_id
    
    print(f"✅ Created inbox: {inbox_id}")
    
    # Register webhook for this inbox
    print(f"📡 Registering webhook for incoming emails...")
    
    # Get ngrok public URL
    ngrok_url = os.getenv('NGROK_URL')
    if not ngrok_url:
        print("⚠️  NGROK_URL not set, using localhost (won't work for AgentMail)")
        ngrok_url = webhook_url
    
    webhook_endpoint = f"{ngrok_url}/webhook/agentmail"
    
    try:
        from agentmail import AgentMail
        am_client = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        webhook = am_client.webhooks.create(
            url=webhook_endpoint,
            client_id=f"leonardo-{timestamp}"
        )
        print(f"✅ Webhook registered: {webhook_endpoint}\n")
        state["webhook_id"] = webhook.id
    except Exception as e:
        print(f"⚠️  Webhook registration failed: {e}")
        print("   Continuing anyway (emails will still arrive via polling)\n")
    
    # Browser Use signup
    browser = BrowserUseClient()
    
    task_prompt = f"""Navigate to app.leonardo.ai and sign up for a new account using:
- Email: {inbox_id}
- Password: {password}

Fill out the signup form completely and submit it. Stop when you reach the email verification step (where it asks for a verification code or to check your email).

IMPORTANT: Keep the browser session open after completing signup."""
    
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
    
    # Phase 2: Wait for webhook email
    print(f"\n📧 Phase 2: Waiting for verification email via webhook\n")
    
    email_data = wait_for_webhook_email(timeout_seconds=300)
    
    if not email_data:
        print(f"⏱️  Webhook timeout, falling back to polling...")
        # Fallback to polling if webhook fails
        from agentmail import AgentMail
        am_client = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        
        for i in range(20):
            time.sleep(15)
            messages = am_client.inboxes.messages.list(inbox_id=inbox_id, limit=1)
            if messages.messages:
                msg = messages.messages[0]
                full_msg = am_client.inboxes.messages.get(inbox_id=inbox_id, message_id=msg.message_id)
                email_data = {
                    'html': full_msg.html,
                    'text': full_msg.text,
                    'subject': full_msg.subject,
                    'from': full_msg.from_
                }
                break
    
    if not email_data:
        print(f"\n❌ No verification email received")
        state["phase2_status"] = "failed"
        save_state(state)
        sys.exit(1)
    
    verification_code = extract_verification_code(email_data)
    
    if not verification_code:
        print(f"\n❌ Could not extract verification code")
        state["phase2_status"] = "failed"
        save_state(state)
        sys.exit(1)
    
    state["verification_code"] = verification_code
    state["phase2_status"] = "complete"
    
    print(f"✅ Phase 2 complete: Got verification code {verification_code}")
    
    # Phase 3: CDP takeover
    print(f"\n🎮 Phase 3: Taking over browser via CDP\n")
    
    # Get CDP URL from Browser Use session
    cdp_url = get_cdp_url_from_browseruse(task_id)
    
    if not cdp_url:
        print(f"❌ Could not get CDP URL from Browser Use session")
        state["phase3_status"] = "failed"
        save_state(state)
        sys.exit(1)
    
    print(f"🔗 CDP URL: {cdp_url}")
    
    # Use CDP to complete verification and extract API key
    try:
        api_key = asyncio.run(control_leonardo_verification(cdp_url, verification_code))
        
        if api_key:
            state["leonardo_api_key"] = api_key
            state["phase3_status"] = "complete"
            
            # Save to .env
            with open('.env', 'a') as f:
                f.write(f'\nLEONARDO_API_KEY={api_key}\n')
            
            print(f"✅ Phase 3 complete: API key extracted")
            print(f"🔑 API Key: {api_key}")
        else:
            print(f"❌ Phase 3 failed: Could not extract API key")
            state["phase3_status"] = "failed"
            save_state(state)
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ CDP control failed: {e}")
        state["phase3_status"] = "failed"
        state["phase3_error"] = str(e)
        save_state(state)
        sys.exit(1)
    
    # Save final state
    save_state(state)
    
    print(f"\n{'='*60}")
    print(f"🎉 Automation Complete!\n")
    print(f"Account: {inbox_id}")
    print(f"Password: {password}")
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
