# Leonardo.ai Automation

**Session-based automation** using AgentMail + Browser Use session continuation for reliable service signup automation.

## What This Does

**v3 Architecture (Session Continuation):**
1. Creates disposable email inbox via AgentMail API
2. Creates Browser Use **session** (not just a task)
3. Task 1 in session: AI signs up for Leonardo.ai, stops at verification
4. Polls email for verification code (< 30 seconds)
5. Task 2 in **same session**: AI enters code, navigates to API settings, extracts key
6. Browser stays open between tasks - maintains login state

**Result:** Working Leonardo.ai account with ~3,500 free API tokens in ~5-10 minutes.

**Success Rate:** ~30-50% (Cloudflare CAPTCHA blocks some attempts - this is the reality of automated signups).

## Why This Approach?

**vs. Creating New Task Each Phase:**
- ❌ New task = new browser = lost login state
- ✅ Session continuation = same browser = stays logged in

**vs. One Giant Task:**
- ❌ Single task can't wait for external input (email)
- ✅ Two tasks in one session = pause for email, continue seamlessly

**vs. Manual:**
- ❌ Manual verification requires human intervention  
- ✅ AI agent handles verification automatically in same browser

## Architecture

```
┌─────────────┐
│ AgentMail   │  1. Create inbox
│  API        │
└─────────────┘

┌─────────────────────────────────────────┐
│ Browser Use Session (ONE browser)       │
│                                          │
│  Task 1:                                 │
│  2. Navigate to leonardo.ai              │
│  3. Fill signup form                     │
│  4. Stop at verification screen          │
│     ⏸️  Browser stays open               │
│                                          │
│  [Poll email - outside browser]          │
│  5. Check AgentMail for verification code│
│  6. Extract 6-digit code                 │
│                                          │
│  Task 2: (SAME browser!)                 │
│  7. Enter verification code              │
│  8. Navigate to API settings             │
│  9. Generate API key                     │
│ 10. Extract and return key               │
└─────────────────────────────────────────┘
```

## Prerequisites

- **AgentMail account** - Get API key at [console.agentmail.to](https://console.agentmail.to)
- **Browser Use account** - Get API key at [cloud.browser-use.com](https://cloud.browser-use.com)
- **ngrok** - For webhook tunnel: [ngrok.com/download](https://ngrok.com/download)
- **Python 3.8+**

## Setup

### 1. Clone and Install

```bash
git clone https://github.com/tanishq-atm/clawfarm.git
cd clawfarm

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium
```

### 2. Configure Environment

```bash
cp .env.example .env

# Edit .env and add:
# AGENTMAIL_API_KEY=your_agentmail_key_here
# BROWSERUSE_API_KEY=your_browser_use_key_here
# WEBHOOK_URL=http://localhost:5000
# NGROK_URL=  # Will be set by setup script
```

### 3. Start Webhook Infrastructure

**Option A: Automated Setup**
```bash
./setup_webhook.sh
```

This starts:
- Webhook server on port 5000
- ngrok tunnel (public URL for AgentMail)
- Displays URLs and PIDs

**Option B: Manual Setup**
```bash
# Terminal 1: Start webhook server
python webhook_server.py

# Terminal 2: Start ngrok tunnel
ngrok http 5000

# Copy the ngrok URL (https://xxx.ngrok.io) and add to .env:
# NGROK_URL=https://xxx.ngrok.io
```

## Usage

### Run Full Automation (v3 - Recommended)

```bash
python leonardo_automation_v3.py
```

**What happens:**
1. Creates AgentMail inbox
2. Registers webhook for instant notifications
3. Browser Use signs up for Leonardo.ai
4. Webhook receives verification email (real-time)
5. CDP connects to browser session
6. AI agent enters code + extracts API key
7. Key saved to `.env` and state file

### Run Individual Phases (Legacy)

```bash
# Phase 1: Create account (Browser Use)
./phase1_leonardo_signup.sh

# Phase 2: Get verification code (polling fallback)
python phase2_check_email.py

# Phase 3: CDP takeover
python cdp_controller.py <cdp_url> <verification_code>
```

## How It Works

### Phase 1: Account Creation (Browser Use)
- Creates unique inbox: `leonardo-bot-<timestamp>@agentmail.to`
- Registers webhook endpoint with AgentMail
- Browser Use autonomously fills signup form
- Stops at email verification (browser stays open)

### Phase 2: Real-Time Email (Webhook)
- AgentMail sends verification email to webhook
- Webhook server receives POST request instantly
- Extracts 6-digit verification code
- No polling, no delays

### Phase 3: CDP Takeover (Playwright)
- Connects to Browser Use session via CDP URL
- Locates verification code input field
- Fills code and clicks submit
- Navigates to API settings
- Generates new API key
- Extracts key via regex or DOM query

### Validation
- Tests API key with `/me` endpoint
- Confirms account credits
- Saves to `.env` for immediate use

## Files

**v2 (Hybrid Architecture):**
- `leonardo_automation_v2.py` - Main automation with webhook + CDP
- `webhook_server.py` - Flask server for AgentMail webhooks
- `cdp_controller.py` - Playwright CDP browser control
- `setup_webhook.sh` - One-command webhook infrastructure setup

**v1 (Legacy):**
- `leonardo_full_automation.py` - Polling-based approach (slower)
- `phase1_leonardo_signup.sh` - Account creation only
- `phase2_check_email.py` - Email polling
- `phase3_verify_with_code.py` - Browser Use verification

**Utilities:**
- `agentmail_utils.py` - AgentMail API wrapper
- `browseruse_utils.py` - Browser Use API wrapper

## Troubleshooting

**Webhook not receiving emails:**
- Check ngrok is running: `http://localhost:4040`
- Verify ngrok URL in `.env` matches webhook registration
- Test webhook: `curl http://localhost:5000/health`

**CDP connection fails:**
- Browser Use session must stay open after Phase 1
- Check CDP URL format: `wss://cloud.browser-use.com/sessions/{id}/cdp`
- Ensure Playwright installed: `python -m playwright install`

**Verification code input not found:**
- Take screenshot: `cdp_controller.py` saves to `failed_api_extraction.png`
- Check Browser Use dashboard for session state
- May need to adjust selectors in `cdp_controller.py`

**API key extraction fails:**
- Verify navigation to API settings page
- Check if key generation requires additional steps
- Inspect page source for key format (UUID vs other)

## Scaling

Run multiple accounts in parallel:

```bash
# Each instance gets unique inbox + Browser Use session
for i in {1..5}; do
  python leonardo_automation_v2.py &
  sleep 120  # Stagger starts
done

wait
echo "All accounts created!"
```

Each account includes ~$5 worth of free credits → 10 accounts = $50 in API credits.

## Performance

**v2 (Webhook + CDP):**
- Phase 1 (Signup): ~2-3 min
- Phase 2 (Webhook): < 5 sec
- Phase 3 (CDP): ~1-2 min
- **Total: ~5-10 min**

**v1 (Polling + Browser Use):**
- Phase 1: ~2-3 min
- Phase 2: ~30 sec - 5 min (polling)
- Phase 3: ~3-5 min (or fails)
- **Total: ~10-15 min (50% failure rate)**

## Use Cases

This pattern works for **any service** with:
- Email-based signup
- Email verification step
- API access or credentials to extract

**Examples:**
- OpenAI trial credits
- Cloud provider free tiers
- API services with free quotas
- SaaS products with trial periods
- Referral bonus programs

## Architecture Notes

**Why Webhook + CDP?**
- **Webhooks**: Production-ready, instant, scalable
- **CDP**: Precise control when Browser Use struggles
- **Hybrid**: Best of both worlds

**When to use each:**
- **Browser Use**: Bot detection bypass (login pages, CAPTCHAs)
- **CDP**: Precision tasks (form filling, navigation, extraction)
- **Webhooks**: Real-time notifications (vs. polling)

**Lessons Learned:**
- Browser Use can fail on complex multi-step flows
- Polling is inefficient for production systems
- CDP gives you full Playwright control over cloud browsers
- Hybrid approach combines strengths of each tool

## Ethics & Legal

- Use responsibly and within Leonardo.ai's Terms of Service
- Respect rate limits and usage policies
- Don't abuse free trial systems
- This is for educational/demonstration purposes

## License

MIT
