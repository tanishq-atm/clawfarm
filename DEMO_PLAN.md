# Demo Plan: AgentMail Mosaic

## Phase 1: Create 1 Leonardo Account (~5-10 min)
```bash
cd /home/exedev/.openclaw/workspace
PYTHONPATH=/home/exedev/.openclaw/workspace:$PYTHONPATH python3 -u leonardo/create_accounts.py
```

**What happens:**
- Creates 1 AgentMail inbox (e.g., leonardo-bot-1-TIMESTAMP@agentmail.to)
- Opens browser session via Browser-Use API
- Signs up for Leonardo.ai with that email
- Polls inbox for verification code
- Completes verification
- Extracts API key from Leonardo dashboard
- Saves results to: `leonardo_parallel_results_TIMESTAMP.json`

**Expected output:**
- ✅ 1 API key with ~3,344 tokens available

---

## Phase 2: Generate 400 Images (~45-60 min)
```bash
python3 leonardo/generate_images.py 400 leonardo_parallel_results_TIMESTAMP.json
```

**What happens:**
- Loads API key from Phase 1 results
- Generates 400 images in parallel
- Uses fast settings:
  - Model: Leonardo Creative (fast)
  - Size: 512×512 pixels
  - Inference steps: 4 (minimum)
  - Guidance scale: 1 (low)
- Mix of dark and light prompts for contrast
- Token usage: ~3,200 tokens (well under 3,344 limit)
- Saves results to: `leonardo_mass_results_TIMESTAMP.json`

**Expected output:**
- ✅ 400 image URLs ready for mosaic

---

## Phase 3: Build Mosaic (~30 seconds)
```bash
python3 mosaic/builder.py leonardo_mass_results_TIMESTAMP.json "AgentMail" 20 20
```

**What happens:**
- Downloads all 400 images in parallel
- Calculates brightness for each image
- Creates text mask for "AgentMail" on 20×20 grid
- Sorts images: darkest for text pixels, lightest for background
- Assembles final mosaic: 10,240×10,240 pixels
- Saves to: `mosaic_TIMESTAMP.jpg`

**Expected output:**
- ✅ Epic photomosaic spelling "AgentMail"

---

## Total Time: ~50-70 minutes
- Phase 1: 5-10 min (account creation)
- Phase 2: 45-60 min (image generation)
- Phase 3: 30 sec (mosaic assembly)

## Ready to run?
All scripts are prepped and validated. Say GO! 🚀
