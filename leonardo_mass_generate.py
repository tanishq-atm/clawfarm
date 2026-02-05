#!/usr/bin/env python3
"""
Leonardo Mass Image Generation
Generate 1200 images in parallel (400 per key) - optimized for speed
"""
import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import List, Dict

# Fast generation settings
FAST_MODEL = "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3"  # Leonardo Creative (fast)
IMAGE_SIZE = 512  # Small for speed
NUM_INFERENCE_STEPS = 4  # Minimum for speed (LCM model)
GUIDANCE_SCALE = 1  # Low for speed

# Prompts for variety
DARK_PROMPTS = [
    "dark abstract pattern",
    "black geometric shapes",
    "deep shadows digital art",
    "midnight blue texture",
    "charcoal abstract design",
    "dark purple nebula",
    "black ink splatter",
    "obsidian crystal pattern"
]

LIGHT_PROMPTS = [
    "bright abstract pattern",
    "white geometric shapes",
    "pastel colors digital art",
    "sunny yellow texture",
    "light blue sky pattern",
    "cream colored abstract",
    "bright rainbow colors",
    "golden light rays"
]

async def generate_image(prompt: str, api_key: str, session: httpx.AsyncClient, img_id: int) -> Dict:
    """Generate one image"""
    try:
        # Start generation
        response = await session.post(
            "https://cloud.leonardo.ai/api/rest/v1/generations",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Bearer {api_key}"
            },
            json={
                "prompt": prompt,
                "num_images": 1,
                "width": IMAGE_SIZE,
                "height": IMAGE_SIZE,
                "modelId": FAST_MODEL,
                "num_inference_steps": NUM_INFERENCE_STEPS,
                "guidance_scale": GUIDANCE_SCALE
            },
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            return {"id": img_id, "status": "failed", "error": f"HTTP {response.status_code}"}
        
        data = response.json()
        generation_id = data.get("sdGenerationJob", {}).get("generationId")
        
        if not generation_id:
            return {"id": img_id, "status": "failed", "error": "No generation ID"}
        
        # Poll for completion (fast polling)
        for attempt in range(60):  # 2 minutes max
            await asyncio.sleep(2)
            
            status_resp = await session.get(
                f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                headers={
                    "accept": "application/json",
                    "authorization": f"Bearer {api_key}"
                },
                timeout=30
            )
            
            if status_resp.status_code != 200:
                continue
            
            status_data = status_resp.json()
            generation = status_data.get("generations_by_pk", {})
            status = generation.get("status")
            
            if status == "COMPLETE":
                images = generation.get("generated_images", [])
                if images:
                    return {
                        "id": img_id,
                        "status": "success",
                        "url": images[0].get("url"),
                        "prompt": prompt,
                        "generation_id": generation_id
                    }
            
            elif status == "FAILED":
                return {"id": img_id, "status": "failed", "error": "Generation failed"}
        
        return {"id": img_id, "status": "timeout", "error": "Timeout waiting"}
        
    except Exception as e:
        return {"id": img_id, "status": "failed", "error": str(e)}

async def generate_batch(api_key: str, num_images: int, start_id: int, is_dark: bool) -> List[Dict]:
    """Generate a batch of images with one API key"""
    
    prompts = DARK_PROMPTS if is_dark else LIGHT_PROMPTS
    
    async with httpx.AsyncClient(timeout=60) as session:
        tasks = []
        for i in range(num_images):
            img_id = start_id + i
            prompt = prompts[i % len(prompts)]
            task = generate_image(prompt, api_key, session, img_id)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, dict)]
        return valid_results

async def main_async(api_keys: List[str], images_per_key: int):
    """Generate all images in parallel"""
    
    print(f"\n🚀 Leonardo Mass Generation")
    print(f"   API Keys: {len(api_keys)}")
    print(f"   Images per key: {images_per_key}")
    print(f"   Total images: {len(api_keys) * images_per_key}")
    print(f"   Strategy: {images_per_key//2} dark + {images_per_key//2} light per key\n")
    
    start_time = time.time()
    
    # Launch all batches in parallel
    tasks = []
    img_id = 0
    
    for idx, api_key in enumerate(api_keys):
        # Half dark, half light per key
        half = images_per_key // 2
        
        # Dark batch
        dark_task = generate_batch(api_key, half, img_id, is_dark=True)
        tasks.append(dark_task)
        img_id += half
        
        # Light batch
        light_task = generate_batch(api_key, half, img_id, is_dark=False)
        tasks.append(light_task)
        img_id += half
        
        print(f"[Key {idx+1}] Launching {images_per_key} generations...")
    
    print(f"\n⏳ Waiting for all {len(api_keys) * images_per_key} images...")
    
    all_results = await asyncio.gather(*tasks)
    
    # Flatten results
    results = []
    for batch in all_results:
        results.extend(batch)
    
    elapsed = time.time() - start_time
    success_count = sum(1 for r in results if r.get('status') == 'success')
    
    print(f"\n{'='*60}")
    print(f"✅ Generation complete!")
    print(f"   Success: {success_count}/{len(results)}")
    print(f"   Failed: {len(results) - success_count}")
    print(f"   Time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    print(f"={'='*60}\n")
    
    return results

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 leonardo_mass_generate.py <images_per_key>")
        print("Example: python3 leonardo_mass_generate.py 400")
        sys.exit(1)
    
    images_per_key = int(sys.argv[1])
    
    # Load API keys
    api_keys = [
        "5cd451b9-798a-472c-a66f-98aaf7cc4622",
        "76242b26-d44a-44f6-8807-cb455162dfcb",
        "8918c71a-a6e4-4748-9a44-43f408651adf"
    ]
    
    results = asyncio.run(main_async(api_keys, images_per_key))
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = f"leonardo_mass_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'total': len(results),
            'success': sum(1 for r in results if r.get('status') == 'success'),
            'results': results
        }, f, indent=2)
    
    print(f"💾 Results saved to {output_file}")

if __name__ == '__main__':
    main()
