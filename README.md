# Leonardo.ai Automation

Fully automated pipeline to create Leonardo.ai accounts and extract API keys using AgentMail + Browser Use. Zero human intervention from inbox creation to service usage.

## What This Does

1. Creates a disposable email inbox via AgentMail API
2. Uses Browser Use cloud browser to sign up for Leonardo.ai
3. Retrieves verification code from email programmatically
4. Completes email verification and generates API key
5. Validates the API key and returns it ready to use

**Result:** Working Leonardo.ai account with ~3,500 free API tokens in ~50 minutes.

## Prerequisites

- **AgentMail account** - Get API key at [console.agentmail.to](https://console.agentmail.to)
- **Browser Use account** - Get API key at [cloud.browser-use.com](https://cloud.browser-use.com)
- **Python 3.8+**

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/tanishq-atm/clawfarm.git
   cd clawfarm
   ```

2. **Install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   # AGENTMAIL_API_KEY=your_agentmail_key_here
   # BROWSERUSE_API_KEY=your_browser_use_key_here
   ```

## Usage

Run the automation script:

```bash
python leonardo_full_automation.py
```

Or run phases individually:

```bash
# Phase 1: Create account
./phase1_leonardo_signup.sh

# Phase 2: Get verification code from email
python phase2_check_email.py

# Phase 3: Complete verification and extract API key
python phase3_verify_with_code.py
```

## How It Works

### Phase 1: Account Creation
- Creates unique AgentMail inbox: `leonardo-bot-<timestamp>@agentmail.to`
- Launches Browser Use task to autonomously fill Leonardo.ai signup form
- Stops at email verification step

### Phase 2: Email Verification
- Polls AgentMail API for verification email from Leonardo.ai
- Extracts 6-digit verification code from email HTML

### Phase 3: API Key Extraction
- Browser Use enters verification code
- Navigates to API settings in Leonardo.ai dashboard
- Generates new API key and extracts it
- Saves key to `leonardo_automation_state.json` and `.env`

### Validation
- Tests API key with `/me` endpoint
- Confirms account credits and token balance
- Ready for immediate use

## Results

After successful automation you'll have:

- **Working Leonardo.ai account** with credentials in `leonardo_automation_state.json`
- **API key** saved to `.env` as `LEONARDO_API_KEY`
- **Free credits:**
  - 150 subscription tokens
  - 100 GPT tokens
  - 3,344 API tokens
  - 10 concurrent API slots

## Files

- `leonardo_full_automation.py` - All-in-one automation script (recommended)
- `phase1_leonardo_signup.sh` - Account creation only
- `phase2_check_email.py` - Email verification retrieval
- `phase3_verify_with_code.py` - Code entry + API key extraction
- `agentmail_utils.py` - AgentMail API wrapper
- `browseruse_utils.py` - Browser Use API wrapper

## Scaling

Run this N times to get N accounts with N API keys:

```bash
for i in {1..10}; do
  python leonardo_full_automation.py
  sleep 60  # Rate limit between accounts
done
```

Each account includes ~$5 worth of free credits.

## Troubleshooting

**Browser Use task fails:**
- Check Browser Use API key is valid
- Verify you have available Browser Use credits
- Monitor task at: `https://cloud.browser-use.com/tasks/<task_id>`

**No verification email:**
- Check AgentMail inbox at: `https://console.agentmail.to`
- Verify email was sent (may take 1-2 minutes)
- Try re-running phase1 with a new inbox

**API key doesn't work:**
- Ensure `.env` is loaded correctly
- Test key manually: `curl -H "Authorization: Bearer <key>" https://cloud.leonardo.ai/api/rest/v1/me`
- Check `leonardo_automation_state.json` for the raw extracted key

## Use Cases

This automation pattern works for any service with:
- Email-based signup
- Free trials or credits
- API access

**Examples:** OpenAI trials, API providers with free tiers, SaaS products with trials, services with referral bonuses.

## Notes

- **Runtime:** ~50-60 minutes per account (mostly Browser Use execution time)
- **Success rate:** High (handles bot detection automatically via Browser Use)
- **Cost:** AgentMail + Browser Use API usage (both have free tiers)
- **Ethics:** Use responsibly and within Leonardo.ai's Terms of Service

## License

MIT (or whatever GitHub default provides)
