#!/usr/bin/env python3
"""
Generate ClawCon lobster image with Leonardo AI
"""
import asyncio
import httpx
import json
import sys
from PIL import Image
import io
from datetime import datetime

async def generate_clawcon(api_key: str):
    """Generate ClawCon lobster conference image"""
    
    # Phoenix 1.0 - best prompt adherence
    model_id = "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3"
    
    print("🦞 Generating ClawCon with Phoenix 1.0...\n")
    
    prompt = "a large conference hall filled with red lobsters attending a tech conference, lobsters sitting at tables with laptops, professional conference setting, modern lighting, ClawCon banner in background, humorous but realistic style, detailed, high quality"
    
    print(f"   Prompt: {prompt}\n")
    
    async with httpx.AsyncClient(timeout=120) as session:
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
                "width": 1024,
                "height": 1024,
                "modelId": model_id,
                "num_inference_steps": 30,
                "guidance_scale": 7
            }
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Generation failed: {response.status_code}")
            print(response.text)
            return None
        
        data = response.json()
        generation_id = data.get("sdGenerationJob", {}).get("generationId")
        
        if not generation_id:
            print("❌ No generation ID received")
            return None
        
        print(f"⏳ Waiting for generation to complete...")
        
        # Poll for completion
        for attempt in range(60):
            await asyncio.sleep(3)
            
            status_resp = await session.get(
                f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                headers={
                    "accept": "application/json",
                    "authorization": f"Bearer {api_key}"
                }
            )
            
            if status_resp.status_code != 200:
                continue
            
            status_data = status_resp.json()
            generation = status_data.get("generations_by_pk", {})
            status = generation.get("status")
            
            if status == "COMPLETE":
                images = generation.get("generated_images", [])
                if images:
                    image_url = images[0].get("url")
                    print(f"✅ Generation complete!\n")
                    
                    # Download image
                    print(f"📥 Downloading image...")
                    img_response = await session.get(image_url)
                    img = Image.open(io.BytesIO(img_response.content))
                    
                    # Save
                    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                    output_file = f"clawcon_{timestamp}.jpg"
                    img.save(output_file, 'JPEG', quality=95)
                    
                    print(f"✅ Saved to: {output_file}")
                    print(f"   Size: {img.width}×{img.height} pixels")
                    return output_file
            
            elif status == "FAILED":
                print("❌ Generation failed")
                return None
        
        print("❌ Timeout waiting for generation")
        return None

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_clawcon.py <results_json>")
        print("\nExample:")
        print("  python3 generate_clawcon.py leonardo_results.json")
        sys.exit(1)
    
    results_file = sys.argv[1]
    
    # Load API key
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data.get('results', [])
    api_key = None
    for r in results:
        if r.get('status') == 'success' and r.get('api_key'):
            api_key = r['api_key']
            break
    
    if not api_key:
        print("❌ No API key found in results")
        sys.exit(1)
    
    print(f"🚀 ClawCon Image Generation\n")
    print("="*60 + "\n")
    
    output_file = await generate_clawcon(api_key)
    
    if output_file:
        print(f"\n🎉 Done! Image saved to: {output_file}")
    else:
        print(f"\n❌ Failed to generate image")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
