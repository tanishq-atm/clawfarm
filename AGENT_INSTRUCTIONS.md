# Agent Instructions

**For OpenClaw agents: This repo automates Leonardo.ai account creation and API key extraction.**

## What You Need

1. **AgentMail API key** - Ask your human to get one from https://agentmail.to
2. **Browser Use API key** - Ask your human to get one from https://browser-use.com

## Setup (First Time Only)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file with API keys
cp .env.example .env
# Edit .env and add:
#   AGENTMAIL_API_KEY=am_...
#   BROWSERUSE_API_KEY=bu_...
```

## Running the Automation

```bash
source venv/bin/activate
python leonardo_automation.py
```

**Expected output:**
- Creates disposable inbox at AgentMail
- Signs up for Leonardo.ai account
- Retrieves email verification code
- Verifies email and extracts API key
- Tests API key by generating an image
- Saves credentials to `leonardo_automation_state.json`
- Appends API key to `.env`

**Runtime:** ~3 minutes

## What Gets Created

After successful run, you'll have:

1. **Email account**: `leonardo-bot-TIMESTAMP@agentmail.to`
2. **Password**: Auto-generated secure password
3. **Leonardo API key**: Saved to `.env` and state file
4. **Test image**: Generation started (check Leonardo dashboard)

## Checking Results

```bash
# View the full state
cat leonardo_automation_state.json | python3 -m json.tool

# Get just the API key
grep LEONARDO_API_KEY .env | tail -1
```

## Using the API Key

The Leonardo API key is automatically saved to `.env`. You can use it like:

```python
import os
from dotenv import load_dotenv
import httpx

load_dotenv()
api_key = os.getenv('LEONARDO_API_KEY')

response = httpx.post(
    'https://cloud.leonardo.ai/api/rest/v1/generations',
    headers={'Authorization': f'Bearer {api_key}'},
    json={
        'prompt': 'Your prompt here',
        'modelId': 'b24e16ff-06e3-43eb-8d33-4416c2d75876',
        'width': 512,
        'height': 512
    }
)
```

## Troubleshooting

### Rate Limits
If you see `429 Too Many Requests` from Browser Use, wait 3-5 minutes.

### Missing API Keys
If you get authentication errors, check `.env` has both:
- `AGENTMAIL_API_KEY=am_...`
- `BROWSERUSE_API_KEY=bu_...`

### Task Failures
If Browser Use tasks fail, check:
1. The task URL in output (monitor at browser-use.com)
2. Your Browser Use account has credits/quota
3. You're using `browser-use-2.0` model (default in script)

## Running Multiple Times

Each run creates a NEW account with a unique email. You can run this as many times as you want to create multiple Leonardo accounts and API keys.

## Files Created

- `leonardo_automation_state.json` - Latest run details (overwritten each time)
- `.env` - API keys accumulate here (new LEONARDO_API_KEY appended each run)

## Agent Workflow Example

```python
# 1. Check if setup is done
if not os.path.exists('venv/bin/python'):
    exec('python3 -m venv venv')
    exec('venv/bin/pip install -r requirements.txt')

# 2. Check if .env exists with required keys
load_dotenv()
if not os.getenv('AGENTMAIL_API_KEY') or not os.getenv('BROWSERUSE_API_KEY'):
    print("❌ Missing API keys in .env - ask human to configure")
    exit(1)

# 3. Run automation
exec('venv/bin/python leonardo_automation.py')

# 4. Read results
with open('leonardo_automation_state.json') as f:
    state = json.load(f)
    
print(f"✅ Created account: {state['inbox_id']}")
print(f"🔑 API key: {state['leonardo_api_key']}")
```

## Security Note

The generated Leonardo accounts are real and functional. The API keys have credits and can generate images. Treat them as you would any API credential.

Each account starts with free credits. Once exhausted, you'd need to add payment info or create new accounts.

## What This Demonstrates

This automation shows the **power of programmatic email** (AgentMail):

- ✅ Create disposable inboxes instantly
- ✅ Retrieve verification codes programmatically
- ✅ No manual email interaction needed
- ✅ Fully autonomous agent workflows

Perfect for:
- Service signups at scale
- Testing workflows
- API key extraction
- Credit farming from free trials
