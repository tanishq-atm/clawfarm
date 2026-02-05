#!/usr/bin/env python3
"""
Claw-Con API-based Voting Bot
Pure HTTP - no browsers, just API calls
"""
import asyncio
import json
import re
import os
import time
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv
import httpx
from agentmail import AgentMail

load_dotenv()


class SupabaseVoter:
    """Direct API voting via Supabase"""
    
    def __init__(self, submission_id: str):
        self.submission_id = submission_id
        self.agentmail = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        
        # Supabase config (from the request you captured)
        self.supabase_url = "https://grhnmffbzheudxajicnf.supabase.co"
        self.apikey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdyaG5tZmZiemhldWR4YWppY25mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwNjA1MzcsImV4cCI6MjA4NTYzNjUzN30.hj2VovmpiT7zABjwaYgVK1iJbkIgT2a8_eWYOkVxKlQ"
    
    async def vote_with_inbox(self, inbox_id: str, account_num: int) -> Dict:
        """Complete flow: signup → magic link → get JWT → vote"""
        
        state = {
            "account_num": account_num,
            "inbox_id": inbox_id,
            "started_at": datetime.now().isoformat()
        }
        
        try:
            print(f"[{account_num}] 📧 Requesting magic link for {inbox_id}")
            
            # Step 1: Request magic link from Supabase
            async with httpx.AsyncClient(timeout=30.0) as client:
                auth_response = await client.post(
                    f"{self.supabase_url}/auth/v1/otp",
                    headers={
                        "apikey": self.apikey,
                        "Content-Type": "application/json"
                    },
                    json={
                        "email": inbox_id,
                        "create_user": True,
                        "data": {}
                    }
                )
                
                if auth_response.status_code not in [200, 201]:
                    raise Exception(f"Magic link request failed: {auth_response.status_code} - {auth_response.text}")
                
                state["magic_link_requested"] = True
                print(f"[{account_num}] ✓ Magic link requested")
            
            # Step 2: Poll AgentMail for the email
            print(f"[{account_num}] 📬 Waiting for email...")
            magic_link = await self._get_magic_link(inbox_id, account_num)
            
            if not magic_link:
                raise Exception("No magic link received")
            
            state["magic_link"] = magic_link
            print(f"[{account_num}] ✓ Got magic link")
            
            # Step 3: Visit magic link to get JWT
            print(f"[{account_num}] 🔑 Getting JWT...")
            jwt_token = await self._get_jwt_from_link(magic_link)
            
            if not jwt_token:
                raise Exception("Failed to get JWT from magic link")
            
            state["jwt_acquired"] = True
            print(f"[{account_num}] ✓ Got JWT")
            
            # Step 4: POST vote with JWT
            print(f"[{account_num}] 🗳️  Casting vote...")
            async with httpx.AsyncClient(timeout=30.0) as client:
                vote_response = await client.post(
                    f"{self.supabase_url}/rest/v1/votes",
                    headers={
                        "apikey": self.apikey,
                        "authorization": f"Bearer {jwt_token}",
                        "Content-Type": "application/json",
                        "Prefer": "return=minimal"
                    },
                    json={
                        "submission_id": self.submission_id
                    }
                )
                
                if vote_response.status_code not in [200, 201]:
                    raise Exception(f"Vote failed: {vote_response.status_code} - {vote_response.text}")
                
                state["vote_cast"] = True
                print(f"[{account_num}] ✅ VOTED!")
            
            state["status"] = "success"
            state["completed_at"] = datetime.now().isoformat()
            return state
            
        except Exception as e:
            print(f"[{account_num}] ❌ Error: {e}")
            state["status"] = "failed"
            state["error"] = str(e)
            state["failed_at"] = datetime.now().isoformat()
            return state
    
    async def _get_magic_link(self, inbox_id: str, account_num: int) -> Optional[str]:
        """Poll AgentMail for magic link email"""
        for i in range(20):  # 5 minutes max
            await asyncio.sleep(15)
            
            try:
                messages = self.agentmail.inboxes.messages.list(
                    inbox_id=inbox_id,
                    limit=5
                )
                
                if messages.messages:
                    msg = messages.messages[0]
                    full_msg = self.agentmail.inboxes.messages.get(
                        inbox_id=inbox_id,
                        message_id=msg.message_id
                    )
                    
                    html = full_msg.html or full_msg.text or ''
                    
                    # Extract magic link (Supabase auth link)
                    patterns = [
                        r'(https://grhnmffbzheudxajicnf\.supabase\.co/auth/v1/verify[^\s"<>]*)',
                        r'(https://[^\s"<>]+/auth/v1/verify[^\s"<>]*)',
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, html, re.IGNORECASE)
                        if match:
                            link = match.group(1)
                            link = link.replace('&amp;', '&')
                            return link
            
            except Exception as e:
                print(f"[{account_num}] Email check error: {e}")
                await asyncio.sleep(5)
        
        return None
    
    async def _get_jwt_from_link(self, magic_link: str) -> Optional[str]:
        """Visit magic link and extract JWT from response/cookies"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(magic_link)
                
                # JWT might be in:
                # 1. URL fragment after redirect
                # 2. Set-Cookie header
                # 3. Response body/JSON
                
                # Check final URL for access_token
                final_url = str(response.url)
                if 'access_token=' in final_url:
                    match = re.search(r'access_token=([^&]+)', final_url)
                    if match:
                        return match.group(1)
                
                # Check if response is JSON with access_token
                try:
                    data = response.json()
                    if 'access_token' in data:
                        return data['access_token']
                except:
                    pass
                
                # Check response text for token
                text = response.text
                match = re.search(r'access_token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9._-]+)', text)
                if match:
                    return match.group(1)
                
                return None
                
        except Exception as e:
            print(f"JWT extraction error: {e}")
            return None


async def run_batch(submission_id: str, inbox_ids: List[str], delay_seconds: float = 2.0) -> List[Dict]:
    """Run voting for multiple inboxes with delays"""
    
    print(f"\n{'='*60}")
    print(f"🗳️  API VOTING - {len(inbox_ids)} accounts")
    print(f"   Submission: {submission_id}")
    print(f"   Delay: {delay_seconds}s between accounts")
    print(f"{'='*60}\n")
    
    voter = SupabaseVoter(submission_id)
    results = []
    
    for i, inbox_id in enumerate(inbox_ids, 1):
        result = await voter.vote_with_inbox(inbox_id, i)
        results.append(result)
        
        # Delay between accounts (except last one)
        if i < len(inbox_ids):
            await asyncio.sleep(delay_seconds)
    
    success_count = sum(1 for r in results if r.get('status') == 'success')
    
    print(f"\n{'='*60}")
    print(f"📊 BATCH COMPLETE")
    print(f"✅ Success: {success_count}/{len(results)}")
    print(f"❌ Failed: {len(results) - success_count}")
    print(f"{'='*60}\n")
    
    return results


def save_results(results: List[Dict], submission_id: str):
    """Save results to JSON"""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"clawcon_api_votes_{timestamp}.json"
    
    success_count = sum(1 for r in results if r.get('status') == 'success')
    
    data = {
        'config': {
            'submission_id': submission_id,
            'timestamp': timestamp,
            'method': 'api_direct'
        },
        'summary': {
            'total': len(results),
            'success': success_count,
            'failed': len(results) - success_count,
            'success_rate': 100 * success_count / len(results) if results else 0
        },
        'results': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Results saved to {output_file}")
    return output_file


async def get_existing_inboxes(limit: int = 1000) -> List[str]:
    """Get list of existing bot inboxes from AgentMail"""
    try:
        from agentmail_utils import AgentMailClient
        client = AgentMailClient()
        inboxes = client.list_inboxes(limit=limit)
        
        # Filter for bot inboxes (created by our automation)
        bot_inboxes = [
            inbox['inbox_id'] 
            for inbox in inboxes 
            if inbox.get('inbox_id', '').startswith('bot-')
        ]
        
        print(f"📬 Found {len(bot_inboxes)} existing bot inboxes")
        return bot_inboxes
        
    except Exception as e:
        print(f"❌ Error fetching inboxes: {e}")
        return []


async def main_async(submission_id: str, count: int, delay: float):
    start_time = time.time()
    
    # Get existing inboxes
    print("🔍 Fetching existing bot inboxes...")
    all_inboxes = await get_existing_inboxes()
    
    if not all_inboxes:
        print("❌ No existing bot inboxes found!")
        return
    
    # Use first N inboxes
    inboxes_to_use = all_inboxes[:count]
    
    print(f"\n📋 Using {len(inboxes_to_use)} inboxes out of {len(all_inboxes)} available")
    
    # Run voting
    results = await run_batch(submission_id, inboxes_to_use, delay)
    
    elapsed = time.time() - start_time
    success_count = sum(1 for r in results if r.get('status') == 'success')
    
    print("\n" + "="*60)
    print("🎉 VOTING COMPLETE!\n")
    print(f"Total Accounts: {len(results)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {len(results) - success_count}")
    print(f"⏱  Time: {elapsed/60:.1f} minutes")
    print(f"📊 Success Rate: {100*success_count/len(results):.1f}%")
    print("="*60)
    
    save_results(results, submission_id)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Claw-Con API Direct Voting Bot')
    parser.add_argument('--count', type=int, default=10, help='Number of votes to cast')
    parser.add_argument('--submission', type=str, 
                       default='a4f6bc02-cb20-47e0-937a-d4f9981e703d',
                       help='Submission ID to vote for')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay in seconds between votes')
    
    args = parser.parse_args()
    
    print(f"\n🎯 API VOTING")
    print(f"   Submission: {args.submission}")
    print(f"   Count: {args.count}")
    print(f"   Delay: {args.delay}s\n")
    
    asyncio.run(main_async(args.submission, args.count, args.delay))


if __name__ == '__main__':
    main()
