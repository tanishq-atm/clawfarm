#!/usr/bin/env python3
"""
Claw-Con Playwright Upvote Bot
Simple, fast, local automation - no rate limits!
"""
import asyncio
import json
import re
import os
from datetime import datetime
from typing import Optional, Dict
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page
from agentmail import AgentMail
from agentmail_utils import AgentMailClient

load_dotenv()


class ClawConPlaywrightBot:
    """Playwright-based upvote bot"""
    
    def __init__(self, bot_id: int, target_post: str, headless: bool = True):
        self.bot_id = bot_id
        self.target_post = target_post
        self.headless = headless
        self.agentmail = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        self.agentmail_client = AgentMailClient()
        
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
        """Execute bot workflow"""
        try:
            print(f"[Bot {self.bot_id}] 🚀 Starting...")
            
            # Create inbox
            print(f"[Bot {self.bot_id}] 📬 Creating inbox...")
            self.agentmail_client.create_inbox(username=self.username)
            self.state["inbox_created"] = True
            
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Sign up
                print(f"[Bot {self.bot_id}] 📝 Signing up...")
                await page.goto('https://www.claw-con.com/')
                
                # Click "Sign in" button
                await page.click('button:has-text("Sign in")')
                await page.wait_for_timeout(1000)
                
                # Fill email
                await page.fill('input[type="email"]', self.inbox_id)
                
                # Submit
                await page.click('button:has-text("Send magic link")')
                await page.wait_for_timeout(2000)
                
                self.state["signup"] = "complete"
                print(f"[Bot {self.bot_id}] ✓ Magic link requested")
                
                # Wait for verification email
                print(f"[Bot {self.bot_id}] 📧 Polling for magic link...")
                verification_link = await self._get_verification_link()
                
                if not verification_link:
                    raise Exception("No magic link received")
                
                self.state["verification_link"] = verification_link
                print(f"[Bot {self.bot_id}] ✓ Got magic link")
                
                # Click verification link (logs us in)
                print(f"[Bot {self.bot_id}] 🔗 Clicking magic link...")
                await page.goto(verification_link)
                await page.wait_for_timeout(3000)
                
                # Navigate to target post
                print(f"[Bot {self.bot_id}] 🎯 Navigating to post...")
                await page.goto(self.target_post)
                await page.wait_for_timeout(2000)
                
                # Find and click upvote button
                print(f"[Bot {self.bot_id}] 👍 Upvoting...")
                upvote_button = page.locator('button:has-text("▲"), button:has-text("⬆"), .upvote, button.hn-upvote')
                await upvote_button.first.click()
                await page.wait_for_timeout(1000)
                
                print(f"[Bot {self.bot_id}] ✅ UPVOTED!")
                
                await browser.close()
            
            self.state["status"] = "success"
            self.state["completed_at"] = datetime.now().isoformat()
            return self.state
            
        except Exception as e:
            print(f"[Bot {self.bot_id}] ❌ Error: {e}")
            self.state["status"] = "failed"
            self.state["error"] = str(e)
            self.state["failed_at"] = datetime.now().isoformat()
            return self.state
    
    async def _get_verification_link(self) -> Optional[str]:
        """Poll AgentMail for verification email"""
        for i in range(20):  # 5 minutes max
            await asyncio.sleep(15)
            
            try:
                messages = self.agentmail.inboxes.messages.list(
                    inbox_id=self.inbox_id,
                    limit=5
                )
                
                if messages.messages:
                    msg = messages.messages[0]
                    full_msg = self.agentmail.inboxes.messages.get(
                        inbox_id=self.inbox_id,
                        message_id=msg.message_id
                    )
                    
                    html = full_msg.html or full_msg.text or ''
                    
                    # Extract link
                    patterns = [
                        r'(https://[^\s"<>]+claw-con\.com[^\s"<>]*)',
                        r'(https://[^\s"<>]+verify[^\s"<>]*)',
                        r'(https://[^\s"<>]+auth/v1/verify[^\s"<>]*)',
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, html, re.IGNORECASE)
                        if match:
                            link = match.group(1)
                            link = link.replace('&amp;', '&')
                            return link
            
            except Exception as e:
                print(f"[Bot {self.bot_id}] Email check error: {e}")
                await asyncio.sleep(5)
        
        return None


async def run_parallel_bots(count: int, target_post: str, headless: bool = True):
    """Run multiple bots in parallel"""
    print(f"\n🚀 Playwright Parallel Run - {count} bots")
    print(f"   Mode: {'Headless' if headless else 'Visible'}")
    print(f"   All bots run concurrently")
    print("="*60 + "\n")
    
    # Create and run all bots concurrently
    tasks = []
    for i in range(count):
        bot = ClawConPlaywrightBot(i + 1, target_post, headless=headless)
        tasks.append(bot.run())
    
    print(f"✅ All {count} bots started\n")
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions
    valid_results = [r for r in results if isinstance(r, dict)]
    
    return valid_results


def save_results(results, total_count, target_post):
    """Save results to JSON"""
    success_count = sum(1 for r in results if r.get('status') == 'success')
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"clawcon_playwright_results_{timestamp}.json"
    
    data = {
        'config': {
            'count': total_count,
            'target_post': target_post,
            'timestamp': timestamp,
            'method': 'playwright'
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
    
    print(f"\n💾 Results saved to {output_file}")
    return output_file


async def main_async(count: int, target_post: str, headless: bool):
    import time
    start_time = time.time()
    
    results = await run_parallel_bots(count, target_post, headless)
    
    elapsed = time.time() - start_time
    success_count = sum(1 for r in results if r.get('status') == 'success')
    
    print("\n" + "="*60)
    print("🎉 Test Complete!\n")
    print(f"Total Bots: {len(results)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {len(results) - success_count}")
    print(f"⏱  Time: {elapsed/60:.1f} minutes")
    print(f"📊 Success Rate: {100*success_count/len(results):.1f}%")
    print("="*60)
    
    save_results(results, count, target_post)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Claw-Con Playwright Upvote Bot')
    parser.add_argument('--count', type=int, default=15, help='Number of bots')
    parser.add_argument('--post', type=str, 
                       default='https://www.claw-con.com/post/a4f6bc02-cb20-47e0-937a-d4f9981e703d',
                       help='Target post URL')
    parser.add_argument('--visible', action='store_true', help='Run with visible browsers (not headless)')
    
    args = parser.parse_args()
    
    asyncio.run(main_async(args.count, args.post, headless=not args.visible))


if __name__ == '__main__':
    main()
