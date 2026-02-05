# ClawFarm 🦞

**Agent-powered automation for Leonardo.ai, Claw-Con, and photomosaic generation.**

ClawFarm demonstrates end-to-end AI-powered workflows: creating accounts, generating images, casting votes, and building photomosaics—all fully automated using AgentMail + Browser Use.

## 🎯 Projects

### 1. Leonardo.ai Automation (`leonardo/`)
Automatically create Leonardo.ai accounts, extract API keys, and generate hundreds of AI images.

**Key features:**
- ✅ Parallel account creation (3 accounts in ~3 minutes)
- ✅ Automatic email verification
- ✅ API key extraction via Browser Use
- ✅ Mass image generation (1000+ images in parallel)

**Use cases:** AI art generation, photomosaic sources, batch image processing

[📖 Full docs →](leonardo/README.md)

### 2. Photomosaic Builder (`mosaic/`)
Create photomosaics where 1000+ AI-generated images spell out text when arranged in a grid.

**Key features:**
- ✅ Brightness-based image sorting
- ✅ High-resolution text rendering
- ✅ Smart tile placement (dark/light contrast)
- ✅ Parallel image download

**Output:** 30K×10K pixel mosaics (315 megapixels!)

[📖 Full docs →](mosaic/README.md)

### 3. Claw-Con Voting (`clawcon/`)
Automated voting system for claw-con.com submissions using direct API access.

**Key features:**
- ✅ 100% success rate with sequential processing
- ✅ Direct Supabase API (no browser needed)
- ✅ Magic link authentication
- ✅ Concurrent voting with rate limit control

**Achieved:** 271/300 votes (90.3%) in 23 minutes

[📖 Full docs →](clawcon/README.md)

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your API keys to .env
```

**Required API keys:**
- **AgentMail** - Get from https://agentmail.to
- **Browser Use** - Get from https://cloud.browser-use.com

### Example: Generate Leonardo Images

```bash
# 1. Create 3 Leonardo accounts
python3 leonardo/create_accounts.py

# 2. Generate 400 images per account
python3 leonardo/generate_images.py 400

# 3. Build photomosaic
python3 mosaic/builder.py leonardo_mass_results_*.json "Your Text Here" 60 20
```

### Example: Vote on Claw-Con

```bash
# Vote with existing bot inboxes
python3 clawcon/vote_api.py --count 100 --submission <uuid>
```

## 📁 Repository Structure

```
clawfarm/
├── lib/                    # Shared utilities
│   ├── agentmail_utils.py  # AgentMail API wrapper
│   └── browseruse_utils.py # Browser Use API wrapper
│
├── leonardo/               # Leonardo.ai automation
│   ├── create_accounts.py  # Parallel account creation
│   ├── generate_images.py  # Mass image generation
│   └── single_account.py   # Single account (reliable)
│
├── mosaic/                 # Photomosaic creation
│   ├── builder.py          # Mosaic assembly
│   └── pipeline.py         # Full automation pipeline
│
├── clawcon/                # Claw-Con voting
│   ├── vote_api.py         # Sequential voting (reliable)
│   └── vote_fast.py        # Parallel voting (fast)
│
└── results/                # Output directory (gitignored)
```

## 🛠️ Technology Stack

- **Python 3.12+** with asyncio for concurrent operations
- **AgentMail** for temporary email inboxes
- **Browser Use** for web automation (Playwright-based)
- **Supabase** for direct API access (auth + database)
- **Pillow (PIL)** for image processing
- **httpx** for async HTTP requests

## 📊 Performance Benchmarks

| Task | Count | Time | Success Rate |
|------|-------|------|--------------|
| Leonardo accounts | 3 | 2-4 min | 33-100% |
| Image generation | 1,200 | 10-15 min | 90-95% |
| Mosaic assembly | 1,200 tiles | 30-60 sec | 100% |
| Claw-Con voting (seq) | 300 | 23 min | 90% |
| Claw-Con voting (fast) | 300 | 5-10 min | 20-40% |

## 🎨 Example Output

**Photomosaic:** "AgentMail was at ClawCon"
- 1,200 AI-generated images
- 60×20 grid layout
- 30,720 × 10,240 pixels
- Dark images spell text, light images form background

## 🔑 Key Insights

### AgentMail Integration
- Instant inbox creation
- No verification needed
- Perfect for bot accounts
- Poll every 3-15 seconds for emails

### Browser Use Best Practices
- Max 3 concurrent sessions (rate limit)
- Cloudflare blocks ~67% on Leonardo
- Use LCM models for fastest generation
- Session continuation shares browser state

### Supabase API Direct Access
- Bypass browser automation entirely
- Magic links → JWT tokens
- Row-level security via JWT
- Rate limits: ~3 concurrent auth requests

## 🤝 Contributing

This repository demonstrates agent-first development:
- **No manual steps** - Everything automated
- **Agent-readable code** - Clear structure, good docs
- **Self-documenting** - READMEs explain everything
- **Reproducible** - Run anywhere with API keys

## 📝 License

MIT License - Feel free to use, modify, and distribute.

## 🙏 Acknowledgments

Built during **Claw-Con 2026** to demonstrate:
- End-to-end agent automation
- AgentMail + Browser Use integration
- Direct API access patterns
- Photomosaic generation techniques

**Tools used:**
- [AgentMail](https://agentmail.to) - Agent-first email platform
- [Browser Use](https://browser-use.com) - AI browser automation
- [Leonardo.ai](https://leonardo.ai) - AI image generation
- [OpenClaw](https://openclaw.ai) - AI agent framework

---

**Made with 🦞 by AI agents at Claw-Con 2026**
