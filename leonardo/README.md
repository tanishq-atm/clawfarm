# Leonardo.ai Automation

Automated Leonardo.ai account creation and API key extraction using AgentMail + Browser Use.

## Features

- **Parallel account creation** - Create multiple accounts simultaneously
- **Email verification** - Automatic verification code extraction
- **API key extraction** - Automatic API key capture
- **Mass image generation** - Generate hundreds of images in parallel

## Scripts

### `create_accounts.py`
Create 3 Leonardo.ai accounts in parallel.

```bash
python3 leonardo/create_accounts.py
```

**Output:** JSON file with API keys

### `generate_images.py`
Generate hundreds of images using Leonardo API keys.

```bash
python3 leonardo/generate_images.py 400  # 400 images per key
```

**Options:**
- Fast model with minimal inference steps
- Generates both dark and light images for mosaics
- Fully parallel generation

### `single_account.py`
Create a single Leonardo account (sequential, more reliable).

```bash
python3 leonardo/single_account.py
```

## How It Works

1. **Create AgentMail inbox** - Temporary email for signup
2. **Browser Use signup** - Automated form filling on leonardo.ai
3. **Email verification** - Poll inbox for verification code
4. **Extract API key** - Navigate to settings and capture key
5. **Save credentials** - Store in JSON for later use

## API Token Limits

- New accounts: **3,344 API tokens**
- Cost per image: **~8 tokens**
- Max images: **~418 per account**

## Success Rate

- **33-100%** depending on Cloudflare/Browser Use availability
- Browser Use rate limit: ~3 concurrent sessions
- Recommend: Run 3 accounts at a time

## Requirements

- AgentMail API key
- Browser Use API key
- Python packages: httpx, asyncio, python-dotenv, agentmail
