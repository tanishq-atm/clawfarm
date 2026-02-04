# AgentMail + Browser Use: Leonardo.ai Automation

**Fully automated account creation and API key extraction using programmatic email.**

## What This Demonstrates

The core capability: **Agents can create their own email inboxes and automate email verification workflows** without human intervention.

### The Flow

1. **Create disposable inbox** → `leonardo-bot-xyz@agentmail.to` (AgentMail API)
2. **Sign up for Leonardo.ai** → Fill forms, submit (Browser Use automation)
3. **Retrieve verification code** → Poll inbox, extract 6-digit code (AgentMail API)
4. **Verify email & extract API key** → Continue in same browser session (Browser Use)
5. **Test the API key** → Generate an image to prove it works (Leonardo API)

**Total time: ~3 minutes**

## Why This Matters

### The AgentMail Value Proposition

Traditional email for automation is broken:
- Gmail/Outlook → manual setup, rate limits, security blocks
- Temp email services → unreliable, no API access
- Custom email servers → complex infrastructure

**AgentMail solves this:**
- ✅ Instant inbox creation (no setup)
- ✅ Programmatic access (full API)
- ✅ Unlimited disposable addresses
- ✅ Built for AI agents

### Use Cases

- **Service signups**: Automate account creation at scale
- **Email verification**: Handle confirmation codes programmatically
- **Testing workflows**: Create test accounts without manual email checks
- **AI agent identity**: Give agents their own email addresses
- **Credit farming**: Extract API keys from free trial services

## Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Get API Keys

**AgentMail** → Sign up at [agentmail.to](https://agentmail.to)
- Create account
- Copy API key from dashboard
- Free tier: unlimited inboxes

**Browser Use** → Sign up at [browser-use.com](https://browser-use.com)
- Create account
- Copy API key
- Free tier: generous limits

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and paste your API keys
```

## Usage

```bash
python leonardo_automation.py
```

### What Happens

```
🚀 Leonardo.ai Automation v3 - Session Continuation

📬 Phase 1: Creating inbox and browser session
   ✅ Inbox: leonardo-bot-20260204-060907@agentmail.to
   ✅ Browser session created
   🌐 Signing up for Leonardo.ai...
   ✅ Signup complete → reached verification screen

📧 Phase 2: Polling for verification email
   [1/20] Checking inbox...
   ✅ Got code: 332869

🎯 Phase 3: Verifying email and extracting API key
   🌐 Continuing in same browser...
   ✅ Email verified
   ✅ API key extracted: 76242b26-d44a-44f6-8807-cb455162dfcb

🎨 Phase 4: Testing API key
   ✅ Image generation started!
   
🎉 Complete! (2m38s)
```

## Architecture

### Session Continuation (Key Innovation)

Instead of creating separate browser sessions:

```python
# ❌ Wasteful approach
task1 = browser.create_task(...)  # New session for signup
browser.stop_session()
task2 = browser.create_task(...)  # NEW session for verification

# ✅ Efficient approach
session = browser.create_session()
task1 = browser.create_task(..., session_id=session)  # Signup
# Browser stays open, state persists
task2 = browser.create_task(..., session_id=session)  # Continue
```

**Benefits:**
- 50% fewer API calls
- Faster execution (no re-login)
- More reliable (no state loss)

### Model Selection

Browser Use supports multiple AI models. We use `browser-use-2.0` for best results:

| Model | Result | Speed |
|-------|--------|-------|
| `browser-use-llm` | ❌ Fails | N/A |
| `browser-use-2.0` | ✅ Works | 2m38s |
| `gemini-3-pro-preview` | ⚠️ Slow | >5min |

## Performance

**Measured run (Feb 4, 2026):**
- Phase 1 (Signup): 90 seconds
- Phase 2 (Email): <30 seconds
- Phase 3 (Verify): 60 seconds
- Phase 4 (Test): <5 seconds

**Total: 2 minutes 38 seconds** from zero to working API key.

## Files

```
leonardo-automation/
├── leonardo_automation.py    # Main script (222 lines)
├── agentmail_utils.py        # AgentMail SDK wrapper (254 lines)
├── browseruse_utils.py       # Browser Use client (264 lines)
├── requirements.txt          # Dependencies (agentmail, httpx)
├── .env.example             # API key template
├── .gitignore               # Ignore secrets
└── README.md                # This file
```

**Total: 740 lines of code**

## Output

After a successful run:

```json
{
  "inbox_id": "leonardo-bot-20260204-060907@agentmail.to",
  "password": "L30Bot20260204-060907!Secure",
  "verification_code": "332869",
  "leonardo_api_key": "76242b26-d44a-44f6-8807-cb455162dfcb",
  "image_generation_id": "51fc4817-4460-4657-9725-45dff454edce",
  "phase1_status": "complete",
  "phase2_status": "complete",
  "phase3_status": "complete"
}
```

The API key is also appended to `.env` as `LEONARDO_API_KEY`.

## Adapting to Other Services

This pattern works for **any service with email verification:**

```python
# 1. Create inbox
inbox = agentmail.create_inbox(username="mybot-123")

# 2. Sign up with Browser Use
browser.create_task(
    task=f"Sign up for SERVICE.com with {inbox.email}",
    llm="browser-use-2.0"
)

# 3. Get verification code
messages = agentmail.get_messages(inbox_id)
code = extract_code(messages[0])

# 4. Complete verification
browser.create_task(
    task=f"Enter verification code {code}",
    session_id=same_session  # Key: reuse session!
)
```

**Works for:**
- Twitter/X verification
- GitHub account creation
- OpenAI API signups
- Replicate, Stability AI, etc.

## ClawCon Demo

This repo was built for **ClawCon** to showcase AgentMail's capabilities.

### The Pitch

> "See how AI agents can create their own email addresses, handle verification workflows, and extract API credentials—all without touching a real inbox. AgentMail makes programmatic email trivial: 2 lines of code to create an inbox, 3 lines to retrieve a verification code. No SMTP, no OAuth, no infrastructure. Just an API."

### Live Demo Strategy

1. **Run the script** (takes 2-3 minutes)
2. **Show the live browser** (Browser Use session URL)
3. **Watch it work** (signup → email → verify → API key → image)
4. **Show the credentials** (real working Leonardo API key)

The automation runs end-to-end with zero manual intervention. That's the power of programmable email.

## Troubleshooting

### No Verification Email

If Phase 2 times out (5 minutes):
1. Check Leonardo.ai signup flow hasn't changed
2. Verify Browser Use task completed Phase 1
3. Check AgentMail dashboard for the inbox

### Browser Use 429 Rate Limit

If you hit rate limits, wait 3-5 minutes. Free tier has limits on task creation.

### Task Failures

If Phase 1 or 3 fails:
- Check the Browser Use dashboard for error details
- Ensure you're using `browser-use-2.0` model
- Verify API keys are correct in `.env`

## License

MIT

## Contributing

This is a ClawCon demo project. Feel free to fork and adapt for other services!

**Ideas:**
- Add support for Twitter/GitHub/etc
- Implement webhook support (faster than polling)
- Add image download after generation
- Create a batch mode (spin up N accounts)

---

**Built with:**
- [AgentMail](https://agentmail.to) - Programmatic email for AI agents
- [Browser Use](https://browser-use.com) - Cloud browser automation
- [Leonardo.ai](https://leonardo.ai) - AI image generation
