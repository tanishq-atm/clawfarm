# Photomosaic Builder

Create photomosaics where AI-generated images spell out text when arranged in a grid.

## Features

- **Parallel image download** - Download 1000+ images concurrently
- **Brightness analysis** - Sort images by brightness for optimal contrast
- **Text mask generation** - Render text at high resolution
- **Smart tile placement** - Dark images for text, light images for background

## Scripts

### `builder.py`
Build a photomosaic from generated images.

```bash
python3 mosaic/builder.py leonardo_mass_results_*.json "AgentMail was at ClawCon" 60 20
```

**Arguments:**
- `results_json` - Leonardo generation results file
- `text` - Text to spell out (default: "AgentMail was at ClawCon")
- `width` - Grid width in tiles (default: 60)
- `height` - Grid height in tiles (default: 20)

**Output:** High-resolution mosaic JPEG

### `pipeline.py`
Run the complete pipeline: account creation → generation → mosaic.

```bash
python3 mosaic/pipeline.py
```

**Steps:**
1. Creates 3 Leonardo accounts
2. Generates 1,200 images (400 per account)
3. Builds 60×20 mosaic
4. Saves final JPEG

**Time:** ~15-20 minutes total

## How It Works

1. **Create text mask** - Render text at 4× resolution
2. **Downscale to grid** - Each pixel = one tile position
3. **Brightness analysis** - Sort all images by brightness
4. **Split images** - 50% dark, 50% light
5. **Smart placement:**
   - Text areas (bright in mask) → Dark images
   - Background (dark in mask) → Light images
6. **Assembly** - Paste 512×512 tiles into final grid

## Output Specs

**For 60×20 grid (1,200 images):**
- Resolution: **30,720 × 10,240 pixels** (315 MP)
- Tile size: 512×512 pixels each
- File size: ~20-40 MB JPEG
- Format: High-quality JPEG (95% quality)

## Tips

- **Grid size:** Wider grids = more readable text
- **Text length:** Shorter text = larger letters = more readable
- **Image variety:** More diverse prompts = better visual effect
- **Brightness:** Strong contrast between dark/light images helps

## Requirements

- Pillow (PIL) for image processing
- httpx for parallel downloads
- Generation results JSON with image URLs
