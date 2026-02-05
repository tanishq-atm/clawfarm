#!/usr/bin/env python3
"""
Mosaic Builder
Takes 1200 images and arranges them to spell "AgentMail was at ClawCon"
"""
import json
import sys
import asyncio
import httpx
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

async def download_image(url: str, session: httpx.AsyncClient) -> Image.Image:
    """Download one image"""
    try:
        response = await session.get(url, timeout=30)
        return Image.open(io.BytesIO(response.content))
    except:
        # Return blank on error
        return Image.new('RGB', (512, 512), color='gray')

async def download_all_images(image_urls: list) -> list:
    """Download all images in parallel"""
    print(f"📥 Downloading {len(image_urls)} images...")
    
    async with httpx.AsyncClient() as session:
        tasks = [download_image(url, session) for url in image_urls]
        images = await asyncio.gather(*tasks)
    
    print(f"✅ Downloaded {len(images)} images")
    return images

def calculate_brightness(img: Image.Image) -> float:
    """Calculate average brightness of image"""
    grayscale = img.convert('L')
    pixels = list(grayscale.getdata())
    return sum(pixels) / len(pixels)

def create_text_mask(text: str, grid_width: int, grid_height: int, tile_size: int) -> Image.Image:
    """Create a black/white mask where white = text, black = background"""
    
    # Create high-res mask first
    scale = 4
    mask_width = grid_width * tile_size * scale
    mask_height = grid_height * tile_size * scale
    
    mask = Image.new('L', (mask_width, mask_height), color=0)  # Black bg
    draw = ImageDraw.Draw(mask)
    
    # Try to use a good font, fallback to default
    try:
        font_size = int(mask_height * 0.15)  # ~15% of height
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Draw text in white
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (mask_width - text_width) // 2
    y = (mask_height - text_height) // 2
    
    draw.text((x, y), text, fill=255, font=font)  # White text
    
    # Downscale to grid size
    mask = mask.resize((grid_width, grid_height), Image.LANCZOS)
    
    return mask

def build_mosaic(images: list, text: str, grid_width: int, grid_height: int) -> Image.Image:
    """Build the photomosaic"""
    
    print(f"\n🎨 Building mosaic...")
    print(f"   Text: '{text}'")
    print(f"   Grid: {grid_width}×{grid_height}")
    print(f"   Total tiles: {grid_width * grid_height}")
    
    tile_size = 512
    
    # Calculate brightness for all images
    print(f"   Analyzing image brightness...")
    brightnesses = [(i, calculate_brightness(img)) for i, img in enumerate(images)]
    brightnesses.sort(key=lambda x: x[1])  # Sort by brightness
    
    # Split into dark and light
    mid = len(brightnesses) // 2
    dark_images = [images[i] for i, _ in brightnesses[:mid]]
    light_images = [images[i] for i, _ in brightnesses[mid:]]
    
    print(f"   Dark images: {len(dark_images)}")
    print(f"   Light images: {len(light_images)}")
    
    # Create text mask
    print(f"   Creating text mask...")
    mask = create_text_mask(text, grid_width, grid_height, tile_size)
    
    # Build mosaic
    print(f"   Assembling mosaic...")
    mosaic = Image.new('RGB', (grid_width * tile_size, grid_height * tile_size))
    
    dark_idx = 0
    light_idx = 0
    
    for y in range(grid_height):
        for x in range(grid_width):
            # Check if this position should be text (bright in mask) or background (dark in mask)
            mask_value = mask.getpixel((x, y))
            
            # If mask is bright (>128), this is TEXT area - use DARK image
            # If mask is dark (<128), this is BACKGROUND - use LIGHT image
            if mask_value > 128:
                # Text area - use dark image
                img = dark_images[dark_idx % len(dark_images)]
                dark_idx += 1
            else:
                # Background - use light image
                img = light_images[light_idx % len(light_images)]
                light_idx += 1
            
            # Paste tile
            mosaic.paste(img.resize((tile_size, tile_size)), (x * tile_size, y * tile_size))
    
    print(f"✅ Mosaic complete!")
    return mosaic

async def main_async(results_file: str, text: str, grid_width: int, grid_height: int):
    """Build mosaic from generation results"""
    
    print(f"\n🖼️  Mosaic Builder")
    print(f"={'='*60}\n")
    
    # Load results
    print(f"📂 Loading results from {results_file}...")
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    # Get successful image URLs
    image_urls = [r['url'] for r in data['results'] if r.get('status') == 'success' and r.get('url')]
    
    print(f"✅ Found {len(image_urls)} successful images")
    
    # Check if we have enough
    needed = grid_width * grid_height
    if len(image_urls) < needed:
        print(f"❌ Not enough images! Need {needed}, have {len(image_urls)}")
        sys.exit(1)
    
    # Use only what we need
    image_urls = image_urls[:needed]
    
    # Download images
    images = await download_all_images(image_urls)
    
    # Build mosaic
    mosaic = build_mosaic(images, text, grid_width, grid_height)
    
    # Save
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"mosaic_{timestamp}.jpg"
    
    print(f"\n💾 Saving mosaic...")
    mosaic.save(output_file, 'JPEG', quality=95, optimize=True)
    
    print(f"✅ Saved to {output_file}")
    print(f"   Size: {mosaic.width}×{mosaic.height} pixels")
    print(f"\n🎉 Done!\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 mosaic_builder.py <results_json> [text] [width] [height]")
        print("\nExample:")
        print("  python3 mosaic_builder.py leonardo_mass_results.json")
        print("  python3 mosaic_builder.py leonardo_mass_results.json 'AgentMail at ClawCon' 60 20")
        sys.exit(1)
    
    results_file = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "AgentMail was at ClawCon"
    grid_width = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    grid_height = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    
    asyncio.run(main_async(results_file, text, grid_width, grid_height))

if __name__ == '__main__':
    main()
