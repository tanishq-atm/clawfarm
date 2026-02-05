#!/usr/bin/env python3
"""
Claw-Con Optimized Sequential Test
Optimized flow: signup → poll email → verify+upvote in single task
"""
import json
import time
import os
import re
import sys
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

from agentmail_utils import AgentMailClient
from browseruse_utils import BrowserUseClient
from agentmail import AgentMail

class ClawConBot:
    """Individual bot instance"""
    def __init__(self, bot_id: int, target_post: str):
        self.bot_id = bot_id
        self.target_post = target_post
        self.agentmail_client = AgentMailClient()
        self.agentmail = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
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
        """Execute optimized bot workflow"""
        try:
            print(f"[Bot {self.bot_id}] 📬 Creating inbox...")
            
            # Step 1: Create inbox FIRST
            self.agentmail_client.create_inbox(username=self.username)
            self.state["inbox_created"] = True
            
            print(f"[Bot {self.bot_id}] 🌐 Creating browser session...")
            
            # Step 2: Create browser session
            session = self.browser.create_session()
            session_id = session.get('id')
            self.state["session_id"] = session_id
            
            print(f"[Bot {self.bot_id}] Session: {session_id[:8]}...")
            
            # Step 3: Sign up and get to verification stage
            print(f"[Bot {self.bot_id}] 📝 Signing up...")
            
            signup_prompt = f"""Navigate to https://www.claw-con.com/ and sign up:
- Email: {self.inbox_id}
- Password: {self.password}
- Username: {self.username}

Fill out the signup form and submit. If email verification is required, stop when you see the verification message or are prompted for a code/link."""
            
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
            
            # Step 4: Check if verification needed
            output = signup_result.get('output', '').lower()
            needs_verification = 'verif' in output or 'email' in output or 'check your email' in output
            
            if needs_verification:
                print(f"[Bot {self.bot_id}] 📧 Polling for verification email...")
                
                # Poll for email
                verification_email = self._get_verification_email()
                
                if not verification_email:
                    raise Exception("No verification email received")
                
                self.state["verification_email_received"] = True
                
                # Extract link and full body
                email_body = verification_email.get('html') or verification_email.get('text', '')
                verification_link = self._extract_verification_link(email_body)
                
                if not verification_link:
                    raise Exception("Could not extract verification link from email")
                
                self.state["verification_link"] = verification_link
                print(f"[Bot {self.bot_id}] ✓ Got verification link")
                
                # Step 5: Single task - verify + upvote
                print(f"[Bot {self.bot_id}] 🎯 Verifying & upvoting...")
                
                combined_prompt = f"""You need to complete email verification and then upvote a post.

STEP 1 - Email Verification:
Navigate to this verification link to verify the email:
{verification_link}

Wait for the verification to complete (you should be logged in).

STEP 2 - Upvote:
After verification is complete, navigate to this post:
{self.target_post}

Find and click the upvote button to upvote this post. Confirm the upvote was successful."""
                
                combined_task = self.browser.create_task(
                    task=combined_prompt,
                    max_steps=60,
                    session_id=session_id,
                    llm="browser-use-2.0"
                )
                
                combined_result = self.browser.wait_for_completion(combined_task['id'])
                
                if not combined_result.get('isSuccess'):
                    raise Exception(f"Verify+upvote failed: {combined_result.get('output')}")
                
                print(f"[Bot {self.bot_id}] ✅ VERIFIED & UPVOTED")
                
            else:
                # No verification needed, just upvote
                print(f"[Bot {self.bot_id}] 👍 No verification needed, upvoting...")
                
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
                
                print(f"[Bot {self.bot_id}] ✅ UPVOTED")
            
            # Cleanup
            try:
                self.browser.stop_session(session_id)
            except:
                pass
            
            self.state["status"] = "success"
            self.state["completed_at"] = datetime.now().isoformat()
            return self.state
            
        except Exception as e:
            print(f"[Bot {self.bot_id}] ❌ Error: {e}")
            self.state["status"] = "failed"
            self.state["error"] = str(e)
            self.state["failed_at"] = datetime.now().isoformat()
            return self.state
    
    def _get_verification_email(self) -> Optional[Dict]:
        """Poll AgentMail API for verification email"""
        for i in range(20):  # 5 minutes max (15s intervals)
            time.sleep(15)
            
            try:
                messages = self.agentmail.inboxes.messages.list(
                    inbox_id=self.inbox_id,
                    limit=5
                )
                
                if messages.messages:
                    # Get the most recent message
                    msg = messages.messages[0]
                    full_msg = self.agentmail.inboxes.messages.get(
                        inbox_id=self.inbox_id,
                        message_id=msg.message_id
                    )
                    
                    # Check if it's a verification email
                    subject = (full_msg.subject or '').lower()
                    html = full_msg.html or full_msg.text or ''
                    
                    if 'verif' in subject or 'verif' in html.lower() or 'confirm' in html.lower():
                        return {
                            'html': full_msg.html,
                            'text': full_msg.text,
                            'subject': full_msg.subject
                        }
            
            except Exception as e:
                print(f"[Bot {self.bot_id}] Email check error: {e}")
                time.sleep(5)
        
        return None
    
    def _extract_verification_link(self, email_body: str) -> Optional[str]:
        """Extract verification link from email body"""
        # Look for verification/confirm links
        patterns = [
            r'(https://[^\s"<>]+verify[^\s"<>]*)',
            r'(https://[^\s"<>]+confirm[^\s"<>]*)',
            r'(https://[^\s"<>]+auth/v1/verify[^\s"<>]*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, email_body, re.IGNORECASE)
            if match:
                link = match.group(1)
                # Clean up HTML entities
                link = link.replace('&amp;', '&')
                link = link.replace('&lt;', '<')
                link = link.replace('&gt;', '>')
                return link
        
        return None


def run_sequential_bots(count: int, target_post: str, delay_seconds: int = 15):
    """Run bots sequentially with delay"""
    print(f"\n🚀 Optimized Sequential Run - {count} bots")
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
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"clawcon_optimized_results_{timestamp}.json"
    
    data = {
        'config': {
            'count': total_count,
            'target_post': target_post,
            'partial': partial,
            'timestamp': timestamp
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
    parser = argparse.ArgumentParser(description='Claw-Con Optimized Sequential Test')
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
