#!/usr/bin/env python3
"""
Claw-Con.com Automation - Sign up and upvote a post
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
    target_post = "https://www.claw-con.com/post/a4f6bc02-cb20-47e0-937a-d4f9981e703d"
    
    print("🚀 Claw-Con.com Automation - Sign up & Upvote\n")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    username = f"clawcon-bot-{timestamp}"
    password = f"Claw{timestamp}!Secure"
    
    state = {
        "started_at": datetime.now().isoformat(),
        "username": username,
        "password": password,
        "target_post": target_post
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
    
    # Create Browser Use SESSION
    session = browser.create_session()
    session_id = session.get('id')
    live_url = session.get('liveUrl')
    
    state["session_id"] = session_id
    
    print(f"✅ Browser session created: {session_id}")
    print(f"📺 Live view: {live_url}\n")
    
    # Task 1: Sign up
    print("🌐 Creating signup task in session...")
    
    task1_prompt = f"""Navigate to https://www.claw-con.com/ and sign up for a new account using:
- Email: {inbox_id}
- Password: {password}
- Username: {username}

Fill out the signup/registration form completely and submit it. If there is email verification, stop when you reach that step."""
    
    task1_response = browser.create_task(
        task=task1_prompt,
        start_url="https://www.claw-con.com/",
        max_steps=100,
        session_id=session_id,
        llm="browser-use-2.0"
    )
    
    task1_id = task1_response.get('id')
    state["phase1_task_id"] = task1_id
    
    print(f"   Task ID: {task1_id}")
    print(f"   Monitor: https://cloud.browser-use.com/tasks/{task1_id}")
    
    # Wait for signup
    print(f"\n⏳ Waiting for signup to complete...")
    task1_result = browser.wait_for_completion(task1_id, verbose=True)
    
    state["phase1_status"] = "complete" if task1_result.get('isSuccess') else "failed"
    state["phase1_output"] = task1_result.get('output', '')
    
    if not task1_result.get('isSuccess'):
        print(f"\n❌ Phase 1 failed: {task1_result.get('output')}")
        browser.stop_session(session_id)
        save_state(state)
        sys.exit(1)
    
    print(f"✅ Phase 1 complete: Account created")
    
    # Check if verification needed
    output = task1_result.get('output', '').lower()
    needs_verification = 'verif' in output or 'email' in output
    
    if needs_verification:
        # Phase 2: Get verification code
        print(f"\n📧 Phase 2: Polling for verification email\n")
        
        from agentmail import AgentMail
        am_client = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        
        verification_code = None
        verification_link = None
        
        for i in range(20):  # 5 minutes max
            time.sleep(15)
            print(f"   [{i+1}/20] Checking inbox...")
            
            messages = am_client.inboxes.messages.list(inbox_id=inbox_id, limit=5)
            if messages.messages:
                for msg in messages.messages:
                    full_msg = am_client.inboxes.messages.get(inbox_id=inbox_id, message_id=msg.message_id)
                    
                    html = full_msg.html or full_msg.text or ""
                    
                    # Look for verification code
                    code_match = re.search(r'\b(\d{4,6})\b', html)
                    if code_match:
                        verification_code = code_match.group(1)
                        print(f"   ✅ Got code: {verification_code}")
                        break
                    
                    # Look for verification link
                    link_match = re.search(r'(https://[^\s"<>]+verify[^\s"<>]*)', html)
                    if link_match:
                        verification_link = link_match.group(1)
                        print(f"   ✅ Got link: {verification_link}")
                        break
                
                if verification_code or verification_link:
                    break
        
        if not verification_code and not verification_link:
            print(f"\n⚠️  No verification code or link received - continuing anyway")
        else:
            state["verification_code"] = verification_code
            state["verification_link"] = verification_link
            state["phase2_status"] = "complete"
            
            print(f"✅ Phase 2 complete")
            
            # Phase 3: Verify email
            print(f"\n🎯 Phase 3: Verifying email\n")
            
            if verification_link:
                task2_prompt = f"""Navigate to this verification link to verify the email:
{verification_link}

After verification is complete, you should be logged in to claw-con.com."""
            else:
                task2_prompt = f"""Continue on claw-con.com. Enter the verification code: {verification_code}

After email verification is complete, you should be logged in."""
            
            task2_response = browser.create_task(
                task=task2_prompt,
                max_steps=50,
                session_id=session_id,
                llm="browser-use-2.0"
            )
            
            task2_id = task2_response.get('id')
            state["phase3_task_id"] = task2_id
            
            print(f"   Task ID: {task2_id}")
            
            # Wait for verification
            print(f"\n⏳ Waiting for verification...")
            task2_result = browser.wait_for_completion(task2_id, verbose=True)
            
            state["phase3_status"] = "complete" if task2_result.get('isSuccess') else "failed"
            state["phase3_output"] = task2_result.get('output', '')
    
    # Final phase: Upvote the post
    print(f"\n👍 Final Phase: Upvoting post\n")
    
    upvote_prompt = f"""Navigate to this specific post on claw-con.com:
{target_post}

Find and click the upvote button to upvote this post. Confirm the upvote was successful."""
    
    upvote_response = browser.create_task(
        task=upvote_prompt,
        start_url=target_post,
        max_steps=50,
        session_id=session_id,
        llm="browser-use-2.0"
    )
    
    upvote_id = upvote_response.get('id')
    state["upvote_task_id"] = upvote_id
    
    print(f"   Task ID: {upvote_id}")
    print(f"   Monitor: https://cloud.browser-use.com/tasks/{upvote_id}")
    
    # Wait for upvote
    print(f"\n⏳ Waiting for upvote...")
    upvote_result = browser.wait_for_completion(upvote_id, verbose=True)
    
    state["upvote_status"] = "complete" if upvote_result.get('isSuccess') else "failed"
    state["upvote_output"] = upvote_result.get('output', '')
    
    # Cleanup
    try:
        browser.stop_session(session_id)
        print(f"🧹 Session stopped")
    except Exception as e:
        print(f"⚠️  Session cleanup: {e}")
    
    # Save state
    save_state(state)
    
    print(f"\n{'='*60}")
    print(f"🎉 Automation Complete!\n")
    print(f"Account: {inbox_id}")
    print(f"Password: {password}")
    print(f"Post upvoted: {target_post}")
    print(f"💾 Full state saved to clawcon_automation_state.json")
    print(f"{'='*60}")
    
    if not upvote_result.get('isSuccess'):
        print(f"\n⚠️  Upvote may have failed: {upvote_result.get('output')}")
        sys.exit(1)

def save_state(state):
    """Save state to JSON file"""
    with open('clawcon_automation_state.json', 'w') as f:
        json.dump(state, f, indent=2)

if __name__ == '__main__':
    main()
