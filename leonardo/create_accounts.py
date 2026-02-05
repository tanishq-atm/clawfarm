#!/usr/bin/env python3
"""
Leonardo.ai Parallel Automation - 3 accounts concurrently
"""
import asyncio
import json
import time
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from lib.agentmail_utils import AgentMailClient
from lib.browseruse_utils import BrowserUseClient
from agentmail import AgentMail

async def create_leonardo_account(account_num: int):
    """Create one Leonardo account"""
    print(f"[{account_num}] 🚀 Starting...")
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    username = f"leonardo-bot-{account_num}-{timestamp}"
    password = f"L30Bot{account_num}{timestamp}!Secure"
    
    state = {
        "account_num": account_num,
        "started_at": datetime.now().isoformat(),
        "username": username,
        "password": password,
    }
    
    try:
        # Initialize clients
        agentmail = AgentMailClient()
        browser = BrowserUseClient()
        am_client = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        
        # Create inbox
        print(f"[{account_num}] 📬 Creating inbox...")
        inbox_response = agentmail.create_inbox(username=username)
        inbox_id = f"{username}@agentmail.to"
        state["inbox_id"] = inbox_id
        print(f"[{account_num}] ✅ Inbox: {inbox_id}")
        
        # Create browser session
        print(f"[{account_num}] 🌐 Creating browser session...")
        session = browser.create_session()
        session_id = session.get('id')
        state["session_id"] = session_id
        print(f"[{account_num}] ✅ Session: {session_id[:8]}...")
        
        # Task 1: Signup
        print(f"[{account_num}] 📝 Starting signup...")
        task1_prompt = f"""Navigate to app.leonardo.ai and sign up for a new account using:
- Email: {inbox_id}
- Password: {password}

Fill out the signup form completely and submit it. Stop when you reach the email verification step."""
        
        task1_response = browser.create_task(
            task=task1_prompt,
            start_url="https://app.leonardo.ai",
            max_steps=100,
            session_id=session_id,
            llm="browser-use-2.0"
        )
        
        task1_id = task1_response.get('id')
        
        # Wait for signup (async sleep in loop to not block others)
        print(f"[{account_num}] ⏳ Waiting for signup...")
        max_wait = 300  # 5 minutes
        for i in range(max_wait):
            await asyncio.sleep(1)
            task_status = browser.get_task(task1_id)
            if task_status.get('status') in ['finished', 'failed', 'stopped']:
                break
        
        task1_result = browser.get_task(task1_id)
        
        if not task1_result.get('isSuccess'):
            raise Exception(f"Signup failed: {task1_result.get('output')}")
        
        print(f"[{account_num}] ✅ Signup complete")
        
        # Poll for verification email
        print(f"[{account_num}] 📧 Waiting for verification email...")
        verification_code = None
        
        for attempt in range(20):  # 5 minutes
            await asyncio.sleep(15)
            
            try:
                messages = am_client.inboxes.messages.list(inbox_id=inbox_id, limit=5)
                
                if messages.messages:
                    msg = messages.messages[0]
                    full_msg = am_client.inboxes.messages.get(
                        inbox_id=inbox_id,
                        message_id=msg.message_id
                    )
                    
                    text = (full_msg.text or '') + (full_msg.html or '')
                    
                    # Look for verification code
                    code_match = re.search(r'\b(\d{6})\b', text)
                    if code_match:
                        verification_code = code_match.group(1)
                        break
            except:
                pass
        
        if not verification_code:
            raise Exception("No verification code received")
        
        print(f"[{account_num}] ✅ Got code: {verification_code}")
        
        # Task 2: Enter verification code
        print(f"[{account_num}] 🔑 Entering verification code...")
        task2_prompt = f"""You are in the Leonardo.ai signup flow. Enter the verification code {verification_code} into the verification field and submit it. Then navigate to the user settings or API section to find and extract the API key."""
        
        task2_response = browser.create_task(
            task=task2_prompt,
            max_steps=80,
            session_id=session_id,
            llm="browser-use-2.0"
        )
        
        task2_id = task2_response.get('id')
        
        # Wait for verification
        for i in range(300):
            await asyncio.sleep(1)
            task_status = browser.get_task(task2_id)
            if task_status.get('status') in ['finished', 'failed', 'stopped']:
                break
        
        task2_result = browser.get_task(task2_id)
        
        output_text = task2_result.get('output', '')
        
        # Extract API key from output
        api_key_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', output_text)
        
        if api_key_match:
            api_key = api_key_match.group(1)
            state["api_key"] = api_key
            print(f"[{account_num}] ✅ API KEY: {api_key}")
        else:
            print(f"[{account_num}] ⚠️  No API key found in output")
        
        # Cleanup
        try:
            browser.stop_session(session_id)
        except:
            pass
        
        state["status"] = "success"
        state["completed_at"] = datetime.now().isoformat()
        print(f"[{account_num}] ✅ COMPLETE!")
        
    except Exception as e:
        print(f"[{account_num}] ❌ ERROR: {e}")
        state["status"] = "failed"
        state["error"] = str(e)
        state["failed_at"] = datetime.now().isoformat()
    
    return state

async def main():
    print("\n🚀 Leonardo.ai Parallel Automation - 3 Accounts\n")
    print("="*60 + "\n")
    
    start_time = time.time()
    
    # Run 3 accounts in parallel
    tasks = [create_leonardo_account(i) for i in range(1, 4)]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start_time
    success_count = sum(1 for r in results if r.get('status') == 'success')
    
    print("\n" + "="*60)
    print("🎉 ALL DONE!\n")
    print(f"Total: {len(results)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {len(results) - success_count}")
    print(f"⏱  Time: {elapsed/60:.1f} minutes")
    print("="*60)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"leonardo_parallel_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'results': results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to {output_file}")
    
    # Print API keys
    print("\n🔑 API Keys:")
    for r in results:
        if r.get('api_key'):
            print(f"   {r['inbox_id']}: {r['api_key']}")

if __name__ == '__main__':
    asyncio.run(main())
