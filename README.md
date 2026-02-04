# Leonardo.ai Automation with AgentMail

Fully automated Leonardo.ai account creation and API key extraction using programmatic email.

## What It Does

Creates a Leonardo.ai account, retrieves the email verification code, completes verification, extracts the API key, and tests it by generating an image. All autonomous—no manual email interaction.

**Runtime:** ~3 minutes

## Quick Start

### For AI Agents

Read [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md) for complete setup and usage instructions.

### For Humans

```bash
# 1. Clone and navigate
git clone https://github.com/tanishq-atm/clawfarm.git
cd clawfarm

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
# Edit .env and add:
#   AGENTMAIL_API_KEY=am_your_key_here
#   BROWSERUSE_API_KEY=bu_your_key_here

# 4. Run
python leonardo_automation.py
```

## Get API Keys

- **AgentMail**: https://agentmail.to (programmatic email)
- **Browser Use**: https://browser-use.com (cloud browser automation)

## What Gets Created

After successful run:
- Disposable email account at AgentMail
- Leonardo.ai account (verified)
- Leonardo API key (saved to `.env` and `leonardo_automation_state.json`)
- Test image generation (proves the key works)

## Output Example

```json
{
  "inbox_id": "leonardo-bot-20260204-123456@agentmail.to",
  "password": "L30Bot20260204-123456!Secure",
  "leonardo_api_key": "abc-def-123-456",
  "verification_code": "123456",
  "image_generation_id": "xyz-789",
  "phase1_status": "complete",
  "phase2_status": "complete",
  "phase3_status": "complete"
}
```

## How It Works

1. **Creates inbox** via AgentMail API
2. **Signs up** for Leonardo using Browser Use (cloud browser automation)
3. **Polls inbox** for verification code
4. **Verifies email** in the same browser session
5. **Extracts API key** from Leonardo dashboard
6. **Tests key** by generating an image

## Use Cases

- Automate service signups requiring email verification
- Extract API keys from free trial services
- Create test accounts programmatically
- Give AI agents their own email identities

## Files

- `leonardo_automation.py` - Main automation script
- `agentmail_utils.py` - AgentMail API wrapper
- `browseruse_utils.py` - Browser Use API client
- `AGENT_INSTRUCTIONS.md` - Setup guide for AI agents
- `EXAMPLE_CONVERSATION.md` - Example agent interactions
- `requirements.txt` - Python dependencies

## Adapting for Other Services

This pattern works for any service with email verification:

```python
# 1. Create inbox
inbox = agentmail.create_inbox(username="mybot-123")

# 2. Sign up with browser automation
browser.create_task(
    task=f"Sign up for SERVICE.com with {inbox.email}",
    llm="browser-use-2.0"
)

# 3. Get verification code from email
messages = agentmail.get_messages(inbox_id)
code = extract_code(messages[0])

# 4. Complete verification in same session
browser.create_task(
    task=f"Enter code {code} and complete signup",
    session_id=same_session
)
```

Works for: Twitter/X, GitHub, OpenAI, Replicate, Stability AI, etc.

## Troubleshooting

**Missing API keys:** Check `.env` has `AGENTMAIL_API_KEY` and `BROWSERUSE_API_KEY`

**Rate limits:** Browser Use free tier has limits. Wait 3-5 minutes if you hit 429 errors.

**Task failures:** Check Browser Use dashboard for error details. Ensure you have available credits.

## License

MIT
