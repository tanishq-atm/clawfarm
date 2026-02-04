# Leonardo.ai Automation

Automate Leonardo.ai account creation and API key extraction using AgentMail + Browser Use.

## What It Does

1. **Creates disposable inbox** via AgentMail
2. **Signs up** for Leonardo.ai account using Browser Use automation
3. **Polls email** for verification code
4. **Continues in same browser** to verify email and extract API key

All without touching a real email account.

## Why This Matters

This demonstrates **programmatic email workflows** for AI agents:
- Create unlimited disposable inboxes on demand
- Automate service signups at scale
- Extract verification codes and API keys
- Build "credit farms" from free trial services

## Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Get API Keys

**AgentMail** (programmatic email):
- Sign up at [agentmail.to](https://agentmail.to)
- Get API key from dashboard

**Browser Use** (cloud browser automation):
- Sign up at [browser-use.com](https://browser-use.com)
- Get API key from dashboard

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Usage

```bash
python leonardo_automation.py
```

The script will:
- Create a timestamped inbox (e.g., `leonardo-bot-20260204-123456@agentmail.to`)
- Generate a secure password
- Launch Browser Use automation for signup
- Wait for verification email (polls every 15s)
- Continue in same browser session to verify and extract API key
- Save credentials and API key to `leonardo_automation_state.json`
- Append API key to `.env` as `LEONARDO_API_KEY`

### Expected Timeline

- **Phase 1** (signup): 2-3 minutes
- **Phase 2** (email poll): <30 seconds
- **Phase 3** (verify + extract): 3-5 minutes

**Total**: ~5-10 minutes per account

## Architecture

### Session Continuation (The Key Innovation)

Instead of creating separate browser sessions for each phase:

```python
# ❌ Old approach (wasteful)
task1 = browser.create_task(...)  # New session, signup from scratch
browser.stop_session()
task2 = browser.create_task(...)  # NEW session, login from scratch

# ✅ v3 approach (efficient)
session = browser.create_session()
task1 = browser.create_task(..., session_id=session)  # Signup
# Browser stays open
task2 = browser.create_task(..., session_id=session)  # Continue where left off
```

This reduces API calls by 50% and improves reliability (no need to re-login).

## File Structure

```
leonardo-automation/
├── leonardo_automation.py    # Main automation script
├── agentmail_utils.py        # AgentMail SDK wrapper
├── browseruse_utils.py       # Browser Use API client
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Rate Limits

**Browser Use**: If you hit `429 Too Many Requests`, wait 3-5 minutes. The free tier has rate limits on task creation.

**AgentMail**: No practical limits for inbox creation or message retrieval in testing.

## Output

When successful, you'll get:

```json
{
  "inbox_id": "leonardo-bot-20260204-123456@agentmail.to",
  "password": "L30Bot20260204-123456!Secure",
  "leonardo_api_key": "5cd451b9-798a-472c-a66f-98aaf7cc4622",
  "verification_code": "078283",
  "phase1_status": "complete",
  "phase2_status": "complete",
  "phase3_status": "complete"
}
```

## Use Cases

- **AI agent identity**: Give agents their own email addresses
- **Testing at scale**: Create test accounts without manual email checks
- **Credit farming**: Automate free trial signups for bulk API access
- **Service integration**: Any workflow requiring email verification

## ClawCon Demo

This repo was built for **ClawCon** to showcase AgentMail's capabilities. The pitch:

> "Learn how to use AgentMail's programmatic email API to automate service signups at scale—creating disposable inboxes, retrieving verification codes, and extracting API keys without touching a real email account."

## Troubleshooting

### Browser Use Phase 3 Inconsistency

Sometimes Phase 3 (verification + key extraction) fails with timeout. This is a Browser Use reliability issue, not our code. The same prompt sometimes takes 14 steps (success) or 2 steps (timeout).

**Workaround**: Re-run the script. Phase 1 creates a new inbox each time.

### No Verification Email

If polling times out (5 minutes), check:
1. Leonardo.ai's signup flow hasn't changed
2. Email wasn't caught by spam filters (check AgentMail dashboard)
3. Browser Use task actually completed signup

## Contributing

This is a demo project for ClawCon. Feel free to fork and adapt for other services (Twitter, GitHub, etc.).

## License

MIT
