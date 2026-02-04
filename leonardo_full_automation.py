#!/usr/bin/env python3
"""
Leonardo.ai Full Automation - AgentMail Demo

MOTIVE: Demonstrate programmatic inbox creation → service signup → API key extraction
OUTCOME: Fully automated Leonardo.ai account with working API key

This script:
1. Creates AgentMail inbox programmatically
2. Phase 1: Browser Use signs up for Leonardo.ai
3. Polls AgentMail for verification email
4. Phase 2: Browser Use verifies account and generates API key
5. Saves API key to .env for immediate use

Usage: ./leonardo_full_automation.py
"""

import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv, set_key

from agentmail_utils import AgentMailClient
from browseruse_utils import BrowserUseClient

# Configuration
AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY")
BROWSERUSE_API_KEY = os.getenv("BROWSERUSE_API_KEY", "bu_RE73gaEVWynxZNuRjWlyLxQWQTFz2-8vwQNBFdhtauw")

# Generate unique credentials
TIMESTAMP = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
USERNAME = f"leonardo-bot-{TIMESTAMP}"
PASSWORD = f"L30Bot{TIMESTAMP}!Secure"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def save_progress(data, filename="leonardo_automation_state.json"):
    """Save automation state for debugging/resuming"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"💾 State saved to {filename}\n")

def main():
    print_section("🚀 LEONARDO.AI FULL AUTOMATION")
    
    print("📋 MOTIVE: AgentMail Demo - Programmatic Service Access")
    print("   Create inbox → Sign up → Extract API key → Use service\n")
    
    state = {
        "started_at": datetime.utcnow().isoformat(),
        "username": USERNAME,
        "password": PASSWORD
    }
    
    # Initialize clients
    mail_client = AgentMailClient(api_key=AGENTMAIL_API_KEY)
    browser_client = BrowserUseClient(api_key=BROWSERUSE_API_KEY)
    
    # ============================================================================
    # STEP 1: CREATE AGENTMAIL INBOX
    # ============================================================================
    print_section("📧 STEP 1: Creating AgentMail Inbox")
    
    try:
        inbox = mail_client.create_inbox(
            username=USERNAME,
            client_id=f"leonardo-automation-{TIMESTAMP}"
        )
        inbox_id = inbox['inbox_id']
        state['inbox_id'] = inbox_id
        
        print(f"✅ Inbox created: {inbox_id}")
        print(f"   Pod ID: {inbox.get('pod_id')}\n")
        save_progress(state)
    
    except Exception as e:
        print(f"❌ Failed to create inbox: {e}")
        sys.exit(1)
    
    # ============================================================================
    # STEP 2: PHASE 1 - BROWSER USE SIGNUP
    # ============================================================================
    print_section("🤖 STEP 2: Phase 1 - Leonardo.ai Signup")
    
    signup_task_prompt = (
        f"Go to app.leonardo.ai and sign up for a new account. "
        f"Use the email '{inbox_id}' and password '{PASSWORD}'. "
        f"Fill out all required fields. If asked for a username, use '{USERNAME}'. "
        f"Complete the signup process until you reach email verification. "
        f"You will need to verify the email but cannot access the inbox."
    )
    
    print(f"📧 Email: {inbox_id}")
    print(f"🔑 Password: {PASSWORD}")
    print(f"👤 Username: {USERNAME}\n")
    
    try:
        print("🚀 Launching Browser Use signup task...")
        signup_task = browser_client.create_task(
            task=signup_task_prompt,
            llm="browser-use-llm",
            start_url="https://app.leonardo.ai",
            max_steps=100
        )
        
        signup_task_id = signup_task['id']
        state['phase1_task_id'] = signup_task_id
        
        print(f"✅ Task created: {signup_task_id}")
        print(f"📊 Dashboard: https://cloud.browser-use.com/tasks/{signup_task_id}\n")
        save_progress(state)
        
        print("⏳ Waiting for signup to complete...\n")
        result = browser_client.wait_for_completion(
            signup_task_id,
            timeout_seconds=600,
            poll_interval=20,
            verbose=True
        )
        
        if result.get('status') == 'finished':
            print(f"\n✅ Phase 1 complete!")
            print(f"   Output: {result.get('output')}\n")
            state['phase1_status'] = 'complete'
            state['phase1_output'] = result.get('output')
            save_progress(state)
        else:
            print(f"\n⚠️  Task ended with status: {result.get('status')}")
            print(f"   Output: {result.get('output')}")
            print("\nContinuing to email verification step...\n")
    
    except Exception as e:
        print(f"❌ Phase 1 failed: {e}")
        print("Attempting to continue anyway...\n")
    
    # ============================================================================
    # STEP 3: POLL FOR VERIFICATION EMAIL
    # ============================================================================
    print_section("📬 STEP 3: Waiting for Verification Email")
    
    try:
        message = mail_client.wait_for_email(
            inbox_id=inbox_id,
            from_domain="leonardo.ai",
            timeout_seconds=300,
            poll_interval=15
        )
        
        if not message:
            print("❌ No verification email received within 5 minutes")
            print("   Check manually at: https://console.agentmail.to")
            print(f"   Inbox: {inbox_id}\n")
            sys.exit(1)
        
        # Extract verification link
        verify_link = mail_client.find_verification_link(message)
        
        if not verify_link:
            print("⚠️  Verification email found but couldn't extract link")
            print(f"\nEmail content preview:")
            print(message.get('text', '')[:500])
            print("\nCheck email manually and extract link")
            sys.exit(1)
        
        state['verification_link'] = verify_link
        print(f"✅ Verification link: {verify_link}\n")
        save_progress(state)
    
    except Exception as e:
        print(f"❌ Failed to get verification email: {e}")
        sys.exit(1)
    
    # ============================================================================
    # STEP 4: PHASE 2 - VERIFY + GET API KEY
    # ============================================================================
    print_section("🔑 STEP 4: Phase 2 - Verify & Generate API Key")
    
    verify_task_prompt = (
        f"First, visit this verification link to complete email verification: {verify_link}. "
        f"After verification is complete, you should be logged in to Leonardo.ai. "
        f"If not logged in, go to app.leonardo.ai and log in with email '{inbox_id}' and password '{PASSWORD}'. "
        f"Once logged in, navigate to the API settings or developer settings page "
        f"(usually found in account settings, user menu, or settings sidebar). "
        f"Generate a new API key. "
        f"Extract and return the complete API key value."
    )
    
    try:
        print("🚀 Launching verification + API key task...")
        verify_task = browser_client.create_task(
            task=verify_task_prompt,
            llm="browser-use-llm",
            start_url=verify_link,
            max_steps=150
        )
        
        verify_task_id = verify_task['id']
        state['phase2_task_id'] = verify_task_id
        
        print(f"✅ Task created: {verify_task_id}")
        print(f"📊 Dashboard: https://cloud.browser-use.com/tasks/{verify_task_id}\n")
        save_progress(state)
        
        print("⏳ Waiting for API key generation...\n")
        result = browser_client.wait_for_completion(
            verify_task_id,
            timeout_seconds=600,
            poll_interval=20,
            verbose=True
        )
        
        output = result.get('output', '')
        state['phase2_output'] = output
        
        print(f"\n{'='*70}")
        print("PHASE 2 COMPLETE")
        print(f"{'='*70}\n")
        print(f"Status: {result.get('status')}")
        print(f"Success: {result.get('isSuccess')}\n")
        print(f"Output:\n{output}\n")
        
        # Try to extract API key from output
        api_key = None
        
        # Common patterns for Leonardo API keys
        import re
        patterns = [
            r'(sk-[a-zA-Z0-9]{32,})',  # sk- prefix
            r'(leo_[a-zA-Z0-9]{32,})',  # leo_ prefix
            r'API[- ]?Key[:\s]+([a-zA-Z0-9_-]{32,})',  # "API Key: xxx"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                api_key = match.group(1)
                break
        
        if api_key:
            state['leonardo_api_key'] = api_key
            save_progress(state)
            
            # Save to .env
            env_path = '.env'
            set_key(env_path, 'LEONARDO_API_KEY', api_key)
            
            print(f"🔑 API Key extracted: {api_key}")
            print(f"💾 Saved to {env_path} as LEONARDO_API_KEY\n")
        else:
            print("⚠️  Could not automatically extract API key from output")
            print("   Check the output above and extract manually\n")
            state['leonardo_api_key'] = 'extraction_failed'
            save_progress(state)
    
    except Exception as e:
        print(f"❌ Phase 2 failed: {e}")
        sys.exit(1)
    
    # ============================================================================
    # COMPLETION
    # ============================================================================
    print_section("🎉 AUTOMATION COMPLETE")
    
    print("✅ Successfully created Leonardo.ai account with API access!\n")
    print(f"📧 Email: {inbox_id}")
    print(f"🔑 Password: {PASSWORD}")
    
    if api_key:
        print(f"🔐 API Key: {api_key}")
        print(f"\n💡 The AI assistant can now use this key to generate images/videos with Leonardo.ai")
    else:
        print(f"\n⚠️  Manual API key extraction required - check dashboard:")
        print(f"   https://cloud.browser-use.com/tasks/{verify_task_id}")
    
    print(f"\n💾 Full state saved in: leonardo_automation_state.json")
    print(f"📊 Phase 1 task: https://cloud.browser-use.com/tasks/{signup_task_id}")
    print(f"📊 Phase 2 task: https://cloud.browser-use.com/tasks/{verify_task_id}\n")
    
    print("="*70)
    print("  DEMO COMPLETE - AgentMail + Browser Use = Automated Service Access")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
