# ClawCon Lobster Generator 🦞

Fully autonomous AI pipeline: Create Leonardo account → Generate ClawCon image

## What It Does

**End-to-end automation:**
1. Creates temporary AgentMail inbox
2. Browser automation signs up for Leonardo.ai
3. Extracts API key automatically
4. Generates image: Lobsters attending ClawCon tech conference

**Total time:** ~4 minutes, fully autonomous

---

## Quick Start

**Run the full pipeline:**
```bash
./run_clawcon.sh
```

**What you get:**
- Fresh Leonardo.ai account (3,344 API tokens)
- High-quality AI image: Conference hall full of lobsters with laptops
- Output: `clawcon_TIMESTAMP.jpg` (1024×1024)

---

## Requirements

**Python dependencies:**
```bash
pip install httpx asyncio Pillow python-dotenv agentmail
```

**API Keys (.env):**
```bash
AGENTMAIL_API_KEY=am_...
BROWSERUSE_API_KEY=bu_...
```

Get keys:
- [AgentMail](https://agentmail.to) - Temporary email API
- [Browser-Use](https://browser-use.com) - Browser automation API

---

## Manual Run

**Step by step:**

```bash
# 1. Create Leonardo account
PYTHONPATH=$PWD python3 leonardo/create_accounts.py

# 2. Generate ClawCon image
python3 leonardo/generate_clawcon.py leonardo_parallel_results_*.json
```

---

## How It Works

### Phase 1: Account Creation (~3 min)

**Script:** `leonardo/create_accounts.py`

1. Creates AgentMail temporary inbox
2. Launches Browser-Use session
3. Navigates to leonardo.ai signup
4. Fills form with temporary email
5. Polls inbox for verification code
6. Enters code and completes signup
7. Extracts API key from dashboard
8. Saves to: `leonardo_parallel_results_TIMESTAMP.json`

### Phase 2: Image Generation (~30 sec)

**Script:** `leonardo/generate_clawcon.py`

1. Loads API key from Phase 1 results
2. Calls Leonardo API with prompt:
   - "Conference hall filled with lobsters attending tech conference"
   - Model: Phoenix 1.0 (best prompt adherence)
   - Resolution: 1024×1024
3. Polls for completion
4. Downloads and saves image
5. Output: `clawcon_TIMESTAMP.jpg`

---

## Architecture

```
clawcon/
├── lib/
│   ├── agentmail_utils.py    # AgentMail API wrapper
│   └── browseruse_utils.py   # Browser-Use API wrapper
├── leonardo/
│   ├── create_accounts.py    # Account creation (browser automation)
│   └── generate_clawcon.py   # ClawCon image generation
├── run_clawcon.sh           # Full autonomous pipeline
├── .env                      # API keys
└── README.md                 # This file
```

---

## API Credits

**New Leonardo account includes:**
- 3,344 API tokens (free tier)
- ~418 max images (at 8 tokens/image)
- 10 concurrent API slots

**ClawCon generation uses:**
- ~8 tokens per image
- Plenty remaining for more generations

---

## Example Output

**Prompt:**
> "A large conference hall filled with red lobsters attending a tech conference, lobsters sitting at tables with laptops, professional conference setting, modern lighting, ClawCon banner in background"

**Model:** Phoenix 1.0  
**Result:** Photorealistic conference scene with hundreds of lobsters, ClawCon signage, laptops, professional lighting

---

## Troubleshooting

**"Browser-Use rate limit"**
- Wait 30-60 seconds between account creations
- Script includes automatic 30s stagger

**"No API key found"**
- Check `leonardo_parallel_results_*.json` exists
- Verify account creation completed successfully

**"Generation timeout"**
- Leonardo API may be busy
- Try again in a few minutes

---

## Tech Stack

- **[AgentMail](https://agentmail.to)** - Temporary email API
- **[Browser-Use](https://browser-use.com)** - Browser automation
- **[Leonardo.ai](https://leonardo.ai)** - AI image generation (Phoenix 1.0)
- **Python** - asyncio, httpx, Pillow

---

## Performance

- **Account creation:** 2-3 minutes
- **Image generation:** 30-45 seconds
- **Total:** ~4 minutes end-to-end
- **Success rate:** ~80-90% (browser automation can be flaky)

---

## Notes

- Each run creates a **fresh Leonardo account** (disposable)
- Accounts persist but email is temporary (expires after use)
- API key saved in results JSON (keep if you want to reuse)
- Phoenix 1.0 model has excellent prompt adherence
- Lobster placement/details vary each generation (AI creativity)

---

## License

MIT

---

**Built with [OpenClaw](https://openclaw.ai)** - AI agent framework
