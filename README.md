# ClawFarm 🤖🖼️

Autonomous AI-powered automation demos: Account creation, mass voting, and AI image generation.

## Projects

### 🎨 Leonardo AI Image Generation
**Fully autonomous pipeline:** Create Leonardo account → Generate AI image

**Quick Start:**
```bash
./run_full_demo.sh
```

**What it does:**
1. Creates fresh Leonardo.ai account via browser automation (AgentMail inbox + Browser-Use)
2. Generates single AI image: "AgentMail is at ClawCon"
3. Saves 1024×1024 high-quality image

**Time:** ~3-5 minutes, fully autonomous

**Manual steps:**
```bash
# Phase 1: Create account
PYTHONPATH=$PWD python3 leonardo/create_accounts.py

# Phase 2: Generate single image
python3 leonardo/generate_single.py leonardo_parallel_results_*.json

# Or: Generate 100 images for mosaic
python3 leonardo/generate_images.py 100 leonardo_parallel_results_*.json

# Build mosaic (10×10 grid)
python3 mosaic/builder.py leonardo_mass_results_*.json "AgentMail" 10 10
```

**Model:** Leonardo Creative (`6bef9f1b-29cb-40c7-b9df-32b51c1f67d3`)

---

### 🗳️ Claw-Con Voting Automation
Mass parallel voting automation for Supabase-backed voting systems.

**Results:** 271/300 successful votes (90.3% success rate) at concurrency=1

**Scripts:**
- `clawcon/vote_api.py` - Sequential API voting (reliable)
- `clawcon/vote_fast.py` - Parallel voting (rate-limited by Supabase)

---

## Module Structure

```
clawfarm/
├── lib/                    # Shared utilities
│   ├── agentmail_utils.py # AgentMail API wrapper
│   └── browseruse_utils.py # Browser-Use API wrapper
├── leonardo/              # Leonardo.ai automation
│   ├── create_accounts.py # Account creation (browser automation)
│   ├── generate_images.py # Mass image generation (10 concurrent)
│   └── generate_single.py # Single image generation
├── mosaic/               # Photomosaic builder
│   ├── builder.py       # Brightness-based mosaic assembly
│   └── pipeline.py      # Full pipeline runner
├── clawcon/            # Voting automation
│   ├── vote_api.py    # API-based voting
│   └── vote_fast.py   # Parallel voting
└── examples/          # Usage examples & docs
```

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

**For Claw-Con:**
```bash
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
```

---

## Key Features

✅ **Parallel execution** - Async/await for max throughput  
✅ **Rate limiting** - Semaphores prevent API overload  
✅ **Error handling** - Graceful degradation on failures  
✅ **Modular design** - Reusable utilities in `lib/`  
✅ **Real examples** - Working demos, not just docs

---

## Architecture

**Account Creation Flow:**
1. Create AgentMail temporary inbox
2. Launch Browser-Use session
3. Automate Leonardo signup form
4. Poll inbox for verification code
5. Enter code & extract API key

**Image Generation Flow:**
1. Load API key from results JSON
2. Submit generation requests (10 concurrent)
3. Poll for completion (2s intervals)
4. Download & save images

**Mosaic Assembly:**
1. Calculate brightness for each image
2. Create text mask (black/white)
3. Sort images: darkest → text, lightest → background
4. Assemble grid

---

## Performance

**Account Creation:** 2-3 minutes  
**Image Generation (100):** 1 minute (10 concurrent)  
**Mosaic Assembly:** <30 seconds  

**Total (full pipeline):** ~3.5 minutes ⚡

---

## License

MIT

---

**Built with:**
- [AgentMail](https://agentmail.to) - Temporary email API
- [Browser-Use](https://browser-use.com) - Browser automation API
- [Leonardo.ai](https://leonardo.ai) - AI image generation
- [OpenClaw](https://openclaw.ai) - AI agent framework
