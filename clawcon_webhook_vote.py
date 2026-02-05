#!/usr/bin/env python3
"""
Claw-Con Webhook-based Voting Bot
Instant email processing via webhooks - complete in 3-5 minutes
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
from flask import Flask, request, jsonify
import threading
from queue import Queue

load_dotenv()


class WebhookVotingSystem:
    """Webhook-based instant voting"""
    
    def __init__(self, submission_id: str):
        self.submission_id = submission_id
        self.agentmail = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))
        self.agentmail_client = AgentMailClient()
        
        # Supabase config
        self.supabase_url = "https://grhnmffbzheudxajicnf.supabase.co"
        self.apikey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdyaG5tZmZiemhldWR4YWppY25mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAwNjA1MzcsImV4cCI6MjA4NTYzNjUzN30.hj2VovmpiT7zABjwaYgVK1iJbkIgT2a8_eWYOkVxKlQ"
        
        # Email queue (webhook → processor)
        self.email_queue = Queue()
        self.pending_inboxes = set()
        self.results = []
        self.vote_semaphore = asyncio.Semaphore(1)  # Serialize votes with delay
        
    async def request_magic_link(self, inbox_id: str) -> bool:
        """Request magic link from Supabase"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
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
                
                return response.status_code in [200, 201]
        except Exception as e:
            print(f"[{inbox_id}] Magic link request failed: {e}")
            return False
    
    async def get_jwt_from_link(self, magic_link: str) -> Optional[str]:
        """Visit magic link and extract JWT"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(magic_link)
                
                # Check final URL for access_token
                final_url = str(response.url)
                if 'access_token=' in final_url:
                    match = re.search(r'access_token=([^&]+)', final_url)
                    if match:
                        return match.group(1)
                
                return None
        except Exception as e:
            print(f"JWT extraction error: {e}")
            return None
    
    async def cast_vote(self, jwt_token: str, inbox_id: str, delay: float = 0.5) -> bool:
        """Cast vote with rate limiting"""
        async with self.vote_semaphore:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
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
                    
                    success = response.status_code in [200, 201]
                    
                    # Delay after vote
                    await asyncio.sleep(delay)
                    
                    return success
            except Exception as e:
                print(f"[{inbox_id}] Vote failed: {e}")
                return False
    
    async def process_email(self, inbox_id: str, email_html: str, account_num: int, delay: float):
        """Process incoming email and vote"""
        state = {
            "account_num": account_num,
            "inbox_id": inbox_id,
            "started_at": datetime.now().isoformat()
        }
        
        try:
            # Extract magic link
            patterns = [
                r'(https://grhnmffbzheudxajicnf\.supabase\.co/auth/v1/verify[^\s"<>]*)',
                r'(https://[^\s"<>]+/auth/v1/verify[^\s"<>]*)',
            ]
            
            magic_link = None
            for pattern in patterns:
                match = re.search(pattern, email_html, re.IGNORECASE)
                if match:
                    magic_link = match.group(1).replace('&amp;', '&')
                    break
            
            if not magic_link:
                raise Exception("No magic link found in email")
            
            state["magic_link"] = magic_link
            
            # Get JWT
            jwt_token = await self.get_jwt_from_link(magic_link)
            if not jwt_token:
                raise Exception("Failed to get JWT")
            
            state["jwt_acquired"] = True
            
            # Cast vote
            vote_success = await self.cast_vote(jwt_token, inbox_id, delay)
            if not vote_success:
                raise Exception("Vote failed")
            
            state["vote_cast"] = True
            state["status"] = "success"
            state["completed_at"] = datetime.now().isoformat()
            
            print(f"[{account_num}] ✅ {inbox_id} - VOTED!")
            
        except Exception as e:
            state["status"] = "failed"
            state["error"] = str(e)
            state["failed_at"] = datetime.now().isoformat()
            print(f"[{account_num}] ❌ {inbox_id} - {e}")
        
        self.results.append(state)
        return state
    
    async def run_parallel_voting(self, inbox_ids: List[str], delay: float):
        """Request all magic links in parallel, process emails as they arrive"""
        
        print(f"\n{'='*60}")
        print(f"🚀 WEBHOOK PARALLEL VOTING")
        print(f"   Inboxes: {len(inbox_ids)}")
        print(f"   Delay: {delay}s between votes")
        print(f"{'='*60}\n")
        
        # Track pending inboxes
        self.pending_inboxes = set(inbox_ids)
        
        # Request all magic links in parallel
        print(f"📤 Requesting {len(inbox_ids)} magic links in parallel...")
        tasks = [self.request_magic_link(inbox_id) for inbox_id in inbox_ids]
        await asyncio.gather(*tasks)
        print(f"✅ All magic links requested\n")
        
        # Process emails as they arrive via queue
        print(f"⏳ Waiting for emails and voting...")
        account_num = 1
        while self.pending_inboxes:
            try:
                # Get email from webhook queue (blocks until available)
                email_data = self.email_queue.get(timeout=300)  # 5 min timeout
                
                inbox_id = email_data['inbox_id']
                email_html = email_data['html']
                
                if inbox_id in self.pending_inboxes:
                    self.pending_inboxes.remove(inbox_id)
                    await self.process_email(inbox_id, email_html, account_num, delay)
                    account_num += 1
                
            except:
                # Timeout - give up on remaining
                print(f"\n⚠️  Timeout waiting for emails. {len(self.pending_inboxes)} inboxes didn't receive emails.")
                break
        
        success_count = sum(1 for r in self.results if r.get('status') == 'success')
        
        print(f"\n{'='*60}")
        print(f"📊 VOTING COMPLETE")
        print(f"✅ Success: {success_count}/{len(self.results)}")
        print(f"❌ Failed: {len(self.results) - success_count}")
        print(f"{'='*60}\n")
        
        return self.results


# Flask webhook server
app = Flask(__name__)
voting_system = None

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive AgentMail webhook"""
    try:
        data = request.json
        
        # Extract inbox_id and email content
        inbox_id = data.get('inbox_id') or data.get('to')
        html = data.get('html') or data.get('body', '')
        
        if inbox_id and html and voting_system:
            # Add to queue for processing
            voting_system.email_queue.put({
                'inbox_id': inbox_id,
                'html': html
            })
            
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


def run_flask(port=5555):
    """Run Flask webhook server"""
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


async def main_async(submission_id: str, count: int, delay: float, webhook_port: int):
    global voting_system
    
    start_time = time.time()
    
    # Start webhook server in background thread
    print("🌐 Starting webhook server...")
    flask_thread = threading.Thread(target=run_flask, args=(webhook_port,), daemon=True)
    flask_thread.start()
    await asyncio.sleep(2)  # Let Flask start
    
    print(f"✅ Webhook server running on http://0.0.0.0:{webhook_port}/webhook\n")
    
    # TODO: Configure AgentMail webhook URL
    # This needs to be done manually or via AgentMail API if available
    print("⚠️  MANUAL STEP REQUIRED:")
    print(f"   Configure AgentMail webhook URL to: http://YOUR_PUBLIC_IP:{webhook_port}/webhook")
    print("   (Use ngrok if you don't have a public IP)\n")
    
    # Get existing inboxes
    print("🔍 Fetching existing bot inboxes...")
    from agentmail_utils import AgentMailClient
    client = AgentMailClient()
    inboxes = client.list_inboxes(limit=1000)
    bot_inboxes = [inbox['inbox_id'] for inbox in inboxes if inbox.get('inbox_id', '').startswith('bot-')]
    
    inboxes_to_use = bot_inboxes[:count]
    print(f"📬 Using {len(inboxes_to_use)} inboxes\n")
    
    # Initialize voting system
    voting_system = WebhookVotingSystem(submission_id)
    
    # Run parallel voting
    results = await voting_system.run_parallel_voting(inboxes_to_use, delay)
    
    elapsed = time.time() - start_time
    success_count = sum(1 for r in results if r.get('status') == 'success')
    
    print("\n" + "="*60)
    print("🎉 COMPLETE!\n")
    print(f"Total: {len(results)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {len(results) - success_count}")
    print(f"⏱  Time: {elapsed/60:.1f} minutes")
    print(f"📊 Success Rate: {100*success_count/len(results):.1f}%")
    print("="*60)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"clawcon_webhook_votes_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'config': {
                'submission_id': submission_id,
                'timestamp': timestamp,
                'method': 'webhook_parallel'
            },
            'summary': {
                'total': len(results),
                'success': success_count,
                'failed': len(results) - success_count,
                'success_rate': 100 * success_count / len(results) if results else 0
            },
            'results': results
        }, f, indent=2)
    
    print(f"💾 Results saved to {output_file}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Claw-Con Webhook Parallel Voting')
    parser.add_argument('--count', type=int, default=300, help='Number of votes')
    parser.add_argument('--submission', type=str, 
                       default='a4f6bc02-cb20-47e0-937a-d4f9981e703d',
                       help='Submission ID')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between votes')
    parser.add_argument('--port', type=int, default=5555, help='Webhook port')
    
    args = parser.parse_args()
    
    asyncio.run(main_async(args.submission, args.count, args.delay, args.port))


if __name__ == '__main__':
    main()
