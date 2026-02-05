#!/usr/bin/env python3
"""
Claw-Con Parallel Scale Test
Tests agent signup + voting at scale for stress testing
"""
import asyncio
import json
import time
import os
import re
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

from agentmail_utils import AgentMailClient
from browseruse_utils import BrowserUseClient

class ClawConBot:
    """Individual bot instance"""
    def __init__(self, bot_id: int, target_post: str):
        self.bot_id = bot_id
        self.target_post = target_post
        self.agentmail = AgentMailClient()
        self.browser = BrowserUseClient()
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.username = f"agent-{bot_id}-{timestamp}"
        self.password = f"Agent{bot_id}{timestamp}!Test"
        self.inbox_id = f"{self.username}@agentmail.to"
        
        self.state = {
            "bot_id": bot_id,
            "started_at": datetime.now().isoformat(),
            "username": self.username,
            "inbox_id": self.inbox_id,
        }
    
    async def run(self) -> Dict:
        """Execute full bot workflow"""
        try:
            print(f"[Bot {self.bot_id}] Starting...")
            
            # Phase 1: Create inbox + session
            self.agentmail.create_inbox(username=self.username)
            session = self.browser.create_session()
            session_id = session.get('id')
            self.state["session_id"] = session_id
            
            print(f"[Bot {self.bot_id}] Session: {session_id}")
            
            # Phase 2: Signup
            signup_prompt = f"""Navigate to https://www.claw-con.com/ and sign up:
- Email: {self.inbox_id}
- Password: {self.password}
- Username: {self.username}

Complete signup. Stop at email verification if required."""
            
            signup_task = self.browser.create_task(
                task=signup_prompt,
                start_url="https://www.claw-con.com/",
                max_steps=80,
                session_id=session_id,
                llm="browser-use-2.0"
            )
            
            signup_result = self.browser.wait_for_completion(
                signup_task['id'], 
                timeout=300,
                verbose=False
            )
            
            if not signup_result.get('isSuccess'):
                raise Exception(f"Signup failed: {signup_result.get('output')}")
            
            self.state["signup"] = "complete"
            print(f"[Bot {self.bot_id}] Signed up")
            
            # Phase 3: Check for verification
            output = signup_result.get('output', '').lower()
            if 'verif' in output or 'email' in output:
                print(f"[Bot {self.bot_id}] Waiting for verification email...")
                
                verification_link = await self._get_verification_link()
                
                if verification_link:
                    self.state["verification_link"] = verification_link
                    
                    verify_task = self.browser.create_task(
                        task=f"Navigate to: {verification_link}",
                        max_steps=30,
                        session_id=session_id,
                        llm="browser-use-2.0"
                    )
                    
                    verify_result = self.browser.wait_for_completion(
                        verify_task['id'],
                        timeout=180,
                        verbose=False
                    )
                    
                    self.state["verification"] = "complete"
                    print(f"[Bot {self.bot_id}] Email verified")
            
            # Phase 4: Upvote
            upvote_task = self.browser.create_task(
                task=f"Navigate to {self.target_post} and upvote it.",
                start_url=self.target_post,
                max_steps=40,
                session_id=session_id,
                llm="browser-use-2.0"
            )
            
            upvote_result = self.browser.wait_for_completion(
                upvote_task['id'],
                timeout=180,
                verbose=False
            )
            
            if not upvote_result.get('isSuccess'):
                raise Exception(f"Upvote failed: {upvote_result.get('output')}")
            
            self.state["upvote"] = "complete"
            print(f"[Bot {self.bot_id}] ✅ Upvoted")
            
            # Cleanup
            try:
                self.browser.stop_session(session_id)
            except:
                pass
            
            self.state["status"] = "success"
            return self.state
            
        except Exception as e:
            print(f"[Bot {self.bot_id}] ❌ Error: {e}")
            self.state["status"] = "failed"
            self.state["error"] = str(e)
            return self.state
    
    async def _get_verification_link(self) -> str:
        """Poll for verification email"""
        from agentmail import AgentMail
        am_client = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        
        for i in range(15):  # 3.75 minutes
            await asyncio.sleep(15)
            
            try:
                messages = am_client.inboxes.messages.list(
                    inbox_id=self.inbox_id, 
                    limit=5
                )
                
                if messages.messages:
                    for msg in messages.messages:
                        full_msg = am_client.inboxes.messages.get(
                            inbox_id=self.inbox_id,
                            message_id=msg.message_id
                        )
                        
                        html = full_msg.html or full_msg.text or ""
                        link_match = re.search(
                            r'(https://[^\s"<>]+verify[^\s"<>]*)',
                            html
                        )
                        
                        if link_match:
                            return link_match.group(1).replace('&amp;', '&')
            except Exception as e:
                print(f"[Bot {self.bot_id}] Email check error: {e}")
        
        return None


async def run_parallel_bots(count: int, target_post: str, batch_size: int = 50):
    """Run multiple bots in parallel with batching"""
    print(f"\n🚀 Starting {count} bots in batches of {batch_size}\n")
    print("="*60)
    
    results = []
    
    # Process in batches to avoid overwhelming APIs
    for batch_start in range(0, count, batch_size):
        batch_end = min(batch_start + batch_size, count)
        batch_num = (batch_start // batch_size) + 1
        
        print(f"\n📦 Batch {batch_num}: Bots {batch_start+1}-{batch_end}")
        print("-"*60)
        
        # Create bot tasks for this batch
        tasks = []
        for i in range(batch_start, batch_end):
            bot = ClawConBot(i + 1, target_post)
            tasks.append(bot.run())
        
        # Run batch concurrently
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        results.extend(batch_results)
        
        # Brief pause between batches
        if batch_end < count:
            print(f"\n⏸  Cooling down 10s before next batch...")
            await asyncio.sleep(10)
    
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Claw-Con Parallel Scale Test')
    parser.add_argument('--count', type=int, default=10, help='Number of bots')
    parser.add_argument('--batch', type=int, default=50, help='Batch size')
    parser.add_argument('--post', type=str, 
                       default='https://www.claw-con.com/post/a4f6bc02-cb20-47e0-937a-d4f9981e703d',
                       help='Target post URL')
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    # Run async workflow
    results = asyncio.run(run_parallel_bots(
        count=args.count,
        target_post=args.post,
        batch_size=args.batch
    ))
    
    elapsed = time.time() - start_time
    
    # Analyze results
    success_count = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'success')
    failed_count = len(results) - success_count
    
    print("\n" + "="*60)
    print("🎉 Test Complete!\n")
    print(f"Total Bots: {len(results)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"⏱  Time: {elapsed:.1f}s ({elapsed/len(results):.1f}s per bot avg)")
    print(f"📊 Success Rate: {100*success_count/len(results):.1f}%")
    print("="*60)
    
    # Save results
    output_file = f"clawcon_test_results_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'config': {
                'count': args.count,
                'batch_size': args.batch,
                'target_post': args.post
            },
            'summary': {
                'total': len(results),
                'success': success_count,
                'failed': failed_count,
                'elapsed_seconds': elapsed,
                'avg_per_bot': elapsed/len(results)
            },
            'results': results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to {output_file}")


if __name__ == '__main__':
    main()
