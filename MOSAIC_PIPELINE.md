# AgentMail × ClawCon Mosaic Pipeline

## 🎯 Overview

Complete automated pipeline to create a photomosaic spelling **"AgentMail was at ClawCon"** using 1,200 AI-generated images.

## 📋 What It Does

### Phase 1: Account Creation (3-4 minutes)
**Script:** `leonardo_parallel.py`
- Creates 3 Leonardo.ai accounts in parallel
- Each account:
  - Creates AgentMail inbox
  - Signs up on Leonardo via Browser Use
  - Gets verification email
  - Extracts API key
- Output: 3 API keys (each with ~3,344 API tokens)

### Phase 2: Mass Image Generation (10-15 minutes)
**Script:** `leonardo_mass_generate.py`
- Generates 1,200 images total (400 per key)
- **600 dark images** (for text pixels)
- **600 light images** (for background pixels)
- All generated in parallel using fast settings:
  - Model: Leonardo Creative (fastest)
  - Size: 512×512
  - Steps: 4 (minimum for speed)
  - Guidance: 1 (low for speed)
- Output: JSON file with 1,200 image URLs

### Phase 3: Mosaic Assembly (30-60 seconds)
**Script:** `mosaic_builder.py`
- Downloads all 1,200 images in parallel
- Analyzes brightness of each image
- Creates text mask for "AgentMail was at ClawCon"
- Arranges images in 60×20 grid:
  - Dark images → Text areas
  - Light images → Background areas
- Output: `mosaic_TIMESTAMP.jpg` (30,720 × 10,240 pixels)

## 🚀 Running It

### Option 1: Full Pipeline (Automated)
```bash
python3 run_mosaic_pipeline.py
```
This runs all 3 phases automatically.

### Option 2: Step by Step (Manual Control)
```bash
# Step 1: Create accounts
python3 leonardo_parallel.py

# Step 2: Generate images (use API keys from step 1)
python3 leonardo_mass_generate.py 400

# Step 3: Build mosaic (use results file from step 2)
python3 mosaic_builder.py leonardo_mass_results_TIMESTAMP.json
```

## 📊 Expected Results

**Timing:**
- Account creation: 2-4 minutes
- Image generation: 10-15 minutes (1,200 images)
- Mosaic assembly: 30-60 seconds
- **Total: ~15-20 minutes**

**Success Rate:**
- Account creation: 33-100% (Browser Use + Cloudflare variability)
- Image generation: 90-95% (some may timeout)
- Need minimum: ~1,200 successful images for full mosaic

**Output:**
- Final mosaic: ~30 MB JPEG file
- Grid: 60 columns × 20 rows = 1,200 tiles
- Each tile: 512×512 pixels
- Total resolution: 30,720 × 10,240 pixels (315 megapixels!)

## 🔧 Technical Details

**Leonardo API Limits:**
- Free account: 3,344 API tokens
- Cost per image: ~8 tokens
- Max images per account: ~418
- We use: 400 per account (conservative)

**Optimization:**
- Parallel everything (accounts, generations, downloads)
- Fast model with minimal inference steps
- Aggressive async/await throughout
- Brightness-based image sorting for text clarity

## 📁 Files Generated

- `leonardo_parallel_results_*.json` - Account creation results
- `leonardo_mass_results_*.json` - Image generation results  
- `mosaic_*.jpg` - Final photomosaic

## 🎨 How the Mosaic Works

1. Text "AgentMail was at ClawCon" rendered as high-res mask
2. Mask downscaled to 60×20 grid
3. For each grid position:
   - If mask is WHITE (text): Place DARK image
   - If mask is BLACK (background): Place LIGHT image
4. Result: When zoomed out, images form readable text!

## ⚠️ Notes

- Browser Use rate limit: ~3 concurrent sessions (hence parallel accounts work)
- Leonardo rate limit: Very high, 1,200 parallel generations work fine
- Cloudflare may block some account creations (33% historical rate)
- Need good internet connection for 1,200 image downloads

## 🐛 Troubleshooting

**"Not enough images"**
- Lower `images_per_key` in step 2
- Or adjust grid size in step 3

**"Browser Use 429 error"**
- Accounts created too fast, retry individually
- Historical success rate: 1-2 out of 3 accounts

**Mosaic text not readable**
- Try different grid size (wider = more readable)
- Adjust in mosaic_builder.py: `grid_width` and `grid_height`
