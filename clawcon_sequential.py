#!/usr/bin/env python3
"""
Claw-Con Sequential Scale Test
Runs bots one at a time with delay to avoid rate limits
"""
import json
import time
import os
import re
import sys
from datetime import datetime
from typing import Dict
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
    
    def run(self) -> Dict:
        """Execute full bot workflow"""
        try:
            print(f"[Bot {self.bot_id}] Starting...")
            
            # Phase 1: Create inbox + session
            self.agentmail.create_inbox(username=self.username)
            session = self.browser.create_session()
            session_id = session.get('id')
            self.state["session_id"] = session_id
            
            print(f"[Bot {self.bot_id}] Session: {session_id[:8]}...")
            
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
            
            signup_result = self.browser.wait_for_completion(signup_task['id'])
            
            if not signup_result.get('isSuccess'):
                raise Exception(f"Signup failed: {signup_result.get('output')}")
            
            self.state["signup"] = "complete"
            print(f"[Bot {self.bot_id}] ✓ Signed up")
            
            # Phase 3: Check for verification
            output = signup_result.get('output', '').lower()
            if 'verif' in output or 'email' in output:
                print(f"[Bot {self.bot_id}] Checking verification email...")
                
                verification_link = self._get_verification_link()
                
                if verification_link:
                    self.state["verification_link"] = verification_link
                    
                    verify_task = self.browser.create_task(
                        task=f"Navigate to: {verification_link}",
                        max_steps=30,
                        session_id=session_id,
                        llm="browser-use-2.0"
                    )
                    
                    verify_result = self.browser.wait_for_completion(verify_task['id'])
                    
                    self.state["verification"] = "complete"
                    print(f"[Bot {self.bot_id}] ✓ Email verified")
            
            # Phase 4: Upvote
            upvote_task = self.browser.create_task(
                task=f"Navigate to {self.target_post} and upvote it.",
                start_url=self.target_post,
                max_steps=40,
                session_id=session_id,
                llm="browser-use-2.0"
            )
            
            upvote_result = self.browser.wait_for_completion(upvote_task['id'])
            
            if not upvote_result.get('isSuccess'):
                raise Exception(f"Upvote failed: {upvote_result.get('output')}")
            
            self.state["upvote"] = "complete"
            print(f"[Bot {self.bot_id}] ✅ UPVOTED")
            
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
    
    def _get_verification_link(self) -> str:
        """Poll for verification email"""
        from agentmail import AgentMail
        am_client = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        
        for i in range(12):  # 3 minutes
            time.sleep(15)
            
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


def run_sequential_bots(count: int, target_post: str, delay_seconds: int = 15):
    """Run bots sequentially with delay"""
    print(f"\n🚀 Starting {count} bots sequentially")
    print(f"   Delay: {delay_seconds}s between bots")
    print(f"   Estimated time: {count * delay_seconds / 60:.1f} minutes")
    print("="*60 + "\n")
    
    results = []
    success_count = 0
    failed_count = 0
    
    start_time = time.time()
    
    for i in range(count):
        bot = ClawConBot(i + 1, target_post)
        result = bot.run()
        results.append(result)
        
        if result.get('status') == 'success':
            success_count += 1
        else:
            failed_count += 1
        
        # Progress update
        elapsed = time.time() - start_time
        rate = (i + 1) / elapsed if elapsed > 0 else 0
        eta = (count - i - 1) / rate if rate > 0 else 0
        
        print(f"\n📊 Progress: {i+1}/{count} | ✅ {success_count} | ❌ {failed_count} | ETA: {eta/60:.1f}m\n")
        
        # Save intermediate state every 10 bots
        if (i + 1) % 10 == 0:
            save_results(results, count, target_post, partial=True)
        
        # Delay before next bot (except last one)
        if i < count - 1:
            print(f"⏳ Waiting {delay_seconds}s...\n")
            time.sleep(delay_seconds)
    
    return results


def save_results(results, total_count, target_post, partial=False):
    """Save results to JSON file"""
    success_count = sum(1 for r in results if r.get('status') == 'success')
    failed_count = len(results) - success_count
    
    output_file = f"clawcon_sequential_results_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    
    data = {
        'config': {
            'count': total_count,
            'target_post': target_post,
            'partial': partial
        },
        'summary': {
            'total_attempted': len(results),
            'total_planned': total_count,
            'success': success_count,
            'failed': failed_count,
            'success_rate': 100 * success_count / len(results) if results else 0
        },
        'results': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    if not partial:
        print(f"\n💾 Final results saved to {output_file}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Claw-Con Sequential Scale Test')
    parser.add_argument('--count', type=int, default=10, help='Number of bots')
    parser.add_argument('--delay', type=int, default=15, help='Delay between bots (seconds)')
    parser.add_argument('--post', type=str, 
                       default='https://www.claw-con.com/post/a4f6bc02-cb20-47e0-937a-d4f9981e703d',
                       help='Target post URL')
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    # Run bots
    results = run_sequential_bots(
        count=args.count,
        target_post=args.post,
        delay_seconds=args.delay
    )
    
    elapsed = time.time() - start_time
    
    # Analyze results
    success_count = sum(1 for r in results if r.get('status') == 'success')
    failed_count = len(results) - success_count
    
    print("\n" + "="*60)
    print("🎉 Test Complete!\n")
    print(f"Total Bots: {len(results)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"⏱  Time: {elapsed/60:.1f} minutes")
    print(f"📊 Success Rate: {100*success_count/len(results):.1f}%")
    print("="*60)
    
    # Save final results
    save_results(results, args.count, args.post, partial=False)


if __name__ == '__main__':
    main()
