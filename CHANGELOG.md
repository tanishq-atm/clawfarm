# Changelog

All notable changes to ClawFarm will be documented in this file.

## [1.0.0] - 2026-02-04

### 🎨 Repository Reorganization

**Major restructure into production-ready format:**

#### Added
- ✅ Modular structure: `lib/`, `leonardo/`, `mosaic/`, `clawcon/`
- ✅ Comprehensive READMEs for each module
- ✅ `examples/quickstart.md` with step-by-step guide
- ✅ Proper `.gitignore` for secrets and outputs
- ✅ Updated `.env.example` with clear instructions
- ✅ `CONTRIBUTING.md` with development guidelines
- ✅ `lib/__init__.py` for proper package imports

#### Changed
- 📦 Moved utilities to `lib/` (agentmail_utils, browseruse_utils)
- 📦 Organized Leonardo scripts into `leonardo/` module
- 📦 Organized mosaic scripts into `mosaic/` module  
- 📦 Organized voting scripts into `clawcon/` module
- 📝 Updated all imports to use `from lib.*` pattern
- 📝 Rewrote main README.md with clear overview

#### Improved
- 🚀 Better discoverability (clear module structure)
- 📖 Better documentation (READMEs + examples)
- 🔧 Better maintainability (separated concerns)
- 🎯 Better for agents (self-documenting structure)

### 🎯 Leonardo.ai Automation

#### Features
- ✅ Parallel account creation (3 accounts in ~3 min)
- ✅ Automatic email verification via AgentMail
- ✅ API key extraction via Browser Use
- ✅ Mass image generation (1000+ images)
- ✅ Fast generation mode (4 inference steps)

#### Performance
- Success rate: 33-100% (Cloudflare dependent)
- Generation: 10-15 min for 1,200 images
- API tokens: 3,344 per account (~400 images)

### 🖼️ Photomosaic Builder

#### Features
- ✅ Brightness-based image sorting
- ✅ High-resolution text rendering
- ✅ Smart tile placement (dark/light contrast)
- ✅ Parallel image download
- ✅ 60×20 grid support (1,200 tiles)

#### Performance
- Assembly time: 30-60 seconds
- Output: 30,720 × 10,240 pixels (315 MP)
- Format: High-quality JPEG (95%)

### 🗳️ Claw-Con Voting

#### Features
- ✅ Direct API voting (no browser needed)
- ✅ Sequential mode (100% success)
- ✅ Parallel mode (faster, variable success)
- ✅ Magic link authentication
- ✅ Rate limit control

#### Results
- Achieved: 271/300 votes (90.3%) in 23 minutes
- Sequential: 100% success rate
- Parallel (concurrency=1): 90% success

### 🛠️ Infrastructure

#### Tools
- AgentMail for temporary inboxes
- Browser Use for web automation
- Supabase for direct API access
- Pillow for image processing
- httpx for async HTTP

#### Requirements
- Python 3.12+
- asyncio, httpx, python-dotenv
- agentmail, playwright (optional)
- Pillow for mosaics

---

## [Pre-1.0] - Development Phase

Initial development and experimentation:
- Leonardo.ai automation proof-of-concept
- Claw-Con voting scripts
- Various approaches tested (Browser Use, Playwright, API)
- Mosaic generation concept validated

---

## Future Plans

### Potential Features
- [ ] GitHub Actions for CI/CD
- [ ] Docker containerization
- [ ] Rate limit auto-detection
- [ ] Resume failed generations
- [ ] Video mosaic support
- [ ] More voting platforms

### Performance Goals
- Improve Browser Use success rate
- Optimize image generation speed
- Add caching for repeated operations
- Parallel account creation beyond 3

---

**Format:** Based on [Keep a Changelog](https://keepachangelog.com/)
