#!/usr/bin/env python3
"""
Claw-Con Batched Upvote Bot
Efficient browser pooling - 10 browsers, multiple accounts per browser
"""
import asyncio
import json
import re
import os
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, BrowserContext
from agentmail import AgentMail
from agentmail_utils import AgentMailClient

load_dotenv()


class BrowserPool:
    """Manages a pool of browsers for efficient upvoting"""
    
    def __init__(self, pool_size: int, target_post: str, headless: bool = True):
        self.pool_size = pool_size
        self.target_post = target_post
        self.headless = headless
        self.agentmail = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        self.agentmail_client = AgentMailClient()
        self.browsers: List[Browser] = []
        self.playwright = None
        
    async def initialize(self):
        """Launch browser pool"""
        print(f"🚀 Launching {self.pool_size} browsers...")
        self.playwright = await async_playwright().start()
        
        for i in range(self.pool_size):
            browser = await self.playwright.chromium.launch(headless=self.headless)
            self.browsers.append(browser)
            print(f"   Browser {i+1}/{self.pool_size} ready")
        
        print(f"✅ Browser pool initialized\n")
    
    async def cleanup(self):
        """Close all browsers"""
        print("\n🧹 Cleaning up browsers...")
        for browser in self.browsers:
            await browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def process_account(self, browser: Browser, account_num: int) -> Dict:
        """Process one account through signup → verify → upvote"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        username = f"bot-{account_num}-{timestamp}"
        inbox_id = f"{username}@agentmail.to"
        
        state = {
            "account_num": account_num,
            "username": username,
            "inbox_id": inbox_id,
            "started_at": datetime.now().isoformat()
        }
        
        try:
            # Create inbox
            self.agentmail_client.create_inbox(username=username)
            state["inbox_created"] = True
            
            # New context for this account
            context = await browser.new_context()
            page = await context.new_page()
            
            # Sign up
            await page.goto('https://www.claw-con.com/', timeout=30000)
            await page.wait_for_timeout(1000)
            
            # Click sign in (use .first since there are multiple sign in buttons)
            sign_in_btn = page.locator('button:has-text("Sign in")').first
            await sign_in_btn.click(timeout=10000)
            await page.wait_for_timeout(1500)
            
            # Fill email
            email_input = page.locator('input[type="email"]')
            await email_input.fill(inbox_id)
            await page.wait_for_timeout(500)
            
            # Submit
            magic_link_btn = page.locator('button:has-text("Send magic link")')
            await magic_link_btn.click()
            await page.wait_for_timeout(2000)
            
            state["signup"] = "complete"
            
            # Wait for verification email
            verification_link = await self._get_verification_link(inbox_id, account_num)
            
            if not verification_link:
                raise Exception("No magic link received")
            
            state["verification_link"] = verification_link
            
            # Click verification link
            await page.goto(verification_link, timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Navigate to post
            await page.goto(self.target_post, timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Find upvote button - try multiple selectors
            upvote_selectors = [
                'button:has-text("▲")',
                'button:has-text("⬆")',
                '.upvote',
                'button.hn-upvote',
                'td.hn-vote button',
                'button[aria-label*="vote" i]'
            ]
            
            clicked = False
            for selector in upvote_selectors:
                try:
                    btn = page.locator(selector).first
                    if await btn.count() > 0:
                        await btn.click(timeout=5000)
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                raise Exception("Could not find upvote button")
            
            await page.wait_for_timeout(1000)
            
            await context.close()
            
            state["status"] = "success"
            state["completed_at"] = datetime.now().isoformat()
            return state
            
        except Exception as e:
            state["status"] = "failed"
            state["error"] = str(e)
            state["failed_at"] = datetime.now().isoformat()
            return state
    
    async def _get_verification_link(self, inbox_id: str, account_num: int) -> Optional[str]:
        """Poll AgentMail for verification email"""
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
                print(f"[Account {account_num}] Email check error: {e}")
                await asyncio.sleep(5)
        
        return None
    
    async def run_batch(self, batch_size: int, batch_num: int = 1) -> List[Dict]:
        """Run a batch of accounts across browser pool"""
        print(f"\n{'='*60}")
        print(f"📦 BATCH {batch_num} - {batch_size} accounts")
        print(f"{'='*60}\n")
        
        results = []
        tasks = []
        
        # Distribute accounts across browsers
        accounts_per_browser = batch_size // self.pool_size
        extra_accounts = batch_size % self.pool_size
        
        account_num = (batch_num - 1) * batch_size + 1
        
        for browser_idx, browser in enumerate(self.browsers):
            # How many accounts for this browser?
            count = accounts_per_browser + (1 if browser_idx < extra_accounts else 0)
            
            print(f"🌐 Browser {browser_idx+1}: handling {count} accounts")
            
            # Process accounts sequentially within each browser
            for i in range(count):
                task = self.process_account(browser, account_num)
                tasks.append(task)
                account_num += 1
        
        print(f"\n⏳ Processing {len(tasks)} accounts...\n")
        
        # Run all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, dict)]
        
        success_count = sum(1 for r in valid_results if r.get('status') == 'success')
        
        print(f"\n{'='*60}")
        print(f"📊 BATCH {batch_num} COMPLETE")
        print(f"✅ Success: {success_count}/{len(valid_results)}")
        print(f"❌ Failed: {len(valid_results) - success_count}")
        print(f"{'='*60}\n")
        
        return valid_results


def save_results(all_results, config):
    """Save all results to JSON"""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"clawcon_batched_results_{timestamp}.json"
    
    success_count = sum(1 for r in all_results if r.get('status') == 'success')
    
    data = {
        'config': config,
        'summary': {
            'total': len(all_results),
            'success': success_count,
            'failed': len(all_results) - success_count,
            'success_rate': 100 * success_count / len(all_results) if all_results else 0
        },
        'results': all_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Results saved to {output_file}")
    return output_file


async def main_async(browser_count: int, accounts_per_batch: int, num_batches: int, target_post: str, headless: bool):
    import time
    start_time = time.time()
    
    pool = BrowserPool(browser_count, target_post, headless)
    await pool.initialize()
    
    all_results = []
    
    try:
        for batch_num in range(1, num_batches + 1):
            batch_results = await pool.run_batch(accounts_per_batch, batch_num)
            all_results.extend(batch_results)
            
            # Show running total
            total_success = sum(1 for r in all_results if r.get('status') == 'success')
            print(f"\n🎯 RUNNING TOTAL: {total_success} successful upvotes\n")
            
            # Brief pause between batches
            if batch_num < num_batches:
                print("⏸️  Pausing 10s before next batch...\n")
                await asyncio.sleep(10)
    
    finally:
        await pool.cleanup()
    
    elapsed = time.time() - start_time
    success_count = sum(1 for r in all_results if r.get('status') == 'success')
    
    print("\n" + "="*60)
    print("🎉 ALL BATCHES COMPLETE!\n")
    print(f"Total Accounts: {len(all_results)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {len(all_results) - success_count}")
    print(f"⏱  Time: {elapsed/60:.1f} minutes")
    print(f"📊 Success Rate: {100*success_count/len(all_results):.1f}%")
    print("="*60)
    
    config = {
        'browser_count': browser_count,
        'accounts_per_batch': accounts_per_batch,
        'num_batches': num_batches,
        'target_post': target_post,
        'timestamp': datetime.now().isoformat()
    }
    
    save_results(all_results, config)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Claw-Con Batched Upvote Bot')
    parser.add_argument('--browsers', type=int, default=10, help='Number of browsers in pool')
    parser.add_argument('--batch-size', type=int, default=100, help='Accounts per batch')
    parser.add_argument('--batches', type=int, default=11, help='Number of batches to run')
    parser.add_argument('--post', type=str, 
                       default='https://www.claw-con.com/post/a4f6bc02-cb20-47e0-937a-d4f9981e703d',
                       help='Target post URL')
    parser.add_argument('--visible', action='store_true', help='Run with visible browsers')
    
    args = parser.parse_args()
    
    total_accounts = args.batch_size * args.batches
    print(f"\n🎯 TARGET: {total_accounts} upvotes")
    print(f"   {args.browsers} browsers × {args.batch_size} accounts/batch × {args.batches} batches\n")
    
    asyncio.run(main_async(
        args.browsers,
        args.batch_size,
        args.batches,
        args.post,
        headless=not args.visible
    ))


if __name__ == '__main__':
    main()
