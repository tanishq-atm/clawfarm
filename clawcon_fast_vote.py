#!/usr/bin/env python3
"""
Claw-Con Fast Parallel Voting Bot
Aggressive polling + parallel processing = 5-10 minute completion
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
from agentmail_utils import AgentMailClient

load_dotenv()


class FastVotingSystem:
    """Fast parallel voting with aggressive polling"""
    
    def __init__(self, submission_id: str):
        self.submission_id = submission_id
        self.agentmail = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        
        # Supabase config
        self.supabase_url = "https://grhnmffbzheudxajicnf.supabase.co"
        self.apikey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdyaG5tZmZiemhldWR4YWppY25mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwNjA1MzcsImV4cCI6MjA4NTYzNjUzN30.hj2VovmpiT7zABjwaYgVK1iJbkIgT2a8_eWYOkVxKlQ"
        
        # Rate limiting
        self.vote_lock = asyncio.Lock()
        self.last_vote_time = 0
        self.min_vote_delay = 0.5  # seconds
    
    async def vote_with_inbox(self, inbox_id: str, account_num: int) -> Dict:
        """Complete voting flow for one inbox"""
        state = {
            "account_num": account_num,
            "inbox_id": inbox_id,
            "started_at": datetime.now().isoformat()
        }
        
        try:
            # Step 1: Request magic link
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
                    raise Exception(f"Magic link request failed: {auth_response.status_code}")
            
            # Step 2: Aggressive polling for email (check every 3 seconds, max 60 seconds)
            magic_link = None
            for attempt in range(20):  # 60 seconds max
                await asyncio.sleep(3)
                
                try:
                    messages = self.agentmail.inboxes.messages.list(
                        inbox_id=inbox_id,
                        limit=3
                    )
                    
                    if messages.messages:
                        msg = messages.messages[0]
                        full_msg = self.agentmail.inboxes.messages.get(
                            inbox_id=inbox_id,
                            message_id=msg.message_id
                        )
                        
                        html = full_msg.html or full_msg.text or ''
                        
                        # Extract magic link
                        patterns = [
                            r'(https://grhnmffbzheudxajicnf\.supabase\.co/auth/v1/verify[^\s"<>]*)',
                            r'(https://[^\s"<>]+/auth/v1/verify[^\s"<>]*)',
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, html, re.IGNORECASE)
                            if match:
                                magic_link = match.group(1).replace('&amp;', '&')
                                break
                        
                        if magic_link:
                            break
                except:
                    pass
            
            if not magic_link:
                raise Exception("No magic link received")
            
            # Step 3: Get JWT
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(magic_link)
                
                final_url = str(response.url)
                jwt_token = None
                
                if 'access_token=' in final_url:
                    match = re.search(r'access_token=([^&]+)', final_url)
                    if match:
                        jwt_token = match.group(1)
                
                if not jwt_token:
                    raise Exception("Failed to get JWT")
            
            # Step 4: Cast vote with rate limiting
            async with self.vote_lock:
                # Ensure minimum delay between votes
                now = time.time()
                elapsed = now - self.last_vote_time
                if elapsed < self.min_vote_delay:
                    await asyncio.sleep(self.min_vote_delay - elapsed)
                
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
                        raise Exception(f"Vote failed: {vote_response.status_code}")
                
                self.last_vote_time = time.time()
            
            state["status"] = "success"
            state["completed_at"] = datetime.now().isoformat()
            print(f"[{account_num}] ✅ {inbox_id}")
            
        except Exception as e:
            state["status"] = "failed"
            state["error"] = str(e)
            state["failed_at"] = datetime.now().isoformat()
            print(f"[{account_num}] ❌ {inbox_id} - {e}")
        
        return state
    
    async def run_parallel(self, inbox_ids: List[str], concurrency: int = 50) -> List[Dict]:
        """Run voting in parallel with concurrency limit"""
        
        print(f"\n{'='*60}")
        print(f"🚀 FAST PARALLEL VOTING")
        print(f"   Inboxes: {len(inbox_ids)}")
        print(f"   Concurrency: {concurrency}")
        print(f"   Vote delay: {self.min_vote_delay}s")
        print(f"{'='*60}\n")
        
        # Create tasks for all inboxes
        tasks = []
        for i, inbox_id in enumerate(inbox_ids, 1):
            task = self.vote_with_inbox(inbox_id, i)
            tasks.append(task)
        
        # Run with concurrency limit
        results = []
        for i in range(0, len(tasks), concurrency):
            batch = tasks[i:i+concurrency]
            print(f"\n📦 Processing batch {i//concurrency + 1} ({len(batch)} accounts)...")
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)
        
        success_count = sum(1 for r in results if r.get('status') == 'success')
        
        print(f"\n{'='*60}")
        print(f"📊 COMPLETE")
        print(f"✅ Success: {success_count}/{len(results)}")
        print(f"❌ Failed: {len(results) - success_count}")
        print(f"{'='*60}\n")
        
        return results


async def main_async(submission_id: str, count: int, concurrency: int):
    start_time = time.time()
    
    # Get existing inboxes
    print("🔍 Fetching existing bot inboxes...")
    client = AgentMailClient()
    inboxes = client.list_inboxes(limit=1000)
    bot_inboxes = [inbox['inbox_id'] for inbox in inboxes if inbox.get('inbox_id', '').startswith('bot-')]
    
    inboxes_to_use = bot_inboxes[:count]
    print(f"📬 Using {len(inboxes_to_use)} inboxes\n")
    
    # Run voting
    voter = FastVotingSystem(submission_id)
    results = await voter.run_parallel(inboxes_to_use, concurrency)
    
    elapsed = time.time() - start_time
    success_count = sum(1 for r in results if r.get('status') == 'success')
    
    print("\n" + "="*60)
    print("🎉 ALL DONE!\n")
    print(f"Total: {len(results)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {len(results) - success_count}")
    print(f"⏱  Time: {elapsed/60:.1f} minutes")
    print(f"📊 Success Rate: {100*success_count/len(results):.1f}%")
    print("="*60)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"clawcon_fast_votes_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'config': {
                'submission_id': submission_id,
                'timestamp': timestamp,
                'method': 'fast_parallel',
                'concurrency': concurrency
            },
            'summary': {
                'total': len(results),
                'success': success_count,
                'failed': len(results) - success_count,
                'success_rate': 100 * success_count / len(results) if results else 0
            },
            'results': results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to {output_file}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Claw-Con Fast Parallel Voting')
    parser.add_argument('--count', type=int, default=300, help='Number of votes')
    parser.add_argument('--submission', type=str, 
                       default='a4f6bc02-cb20-47e0-937a-d4f9981e703d',
                       help='Submission ID')
    parser.add_argument('--concurrency', type=int, default=50, help='Parallel tasks')
    
    args = parser.parse_args()
    
    print(f"\n🎯 FAST VOTING")
    print(f"   Submission: {args.submission}")
    print(f"   Count: {args.count}")
    print(f"   Concurrency: {args.concurrency}\n")
    
    asyncio.run(main_async(args.submission, args.count, args.concurrency))


if __name__ == '__main__':
    main()
