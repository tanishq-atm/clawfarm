#!/usr/bin/env python3
"""
Leonardo.ai Image Generation
Use our API keys to generate AI images
"""
import httpx
import json
import time
import sys

# API keys we collected
API_KEYS = [
    "5cd451b9-798a-472c-a66f-98aaf7cc4622",
    "76242b26-d44a-44f6-8807-cb455162dfcb",
    "8918c71a-a6e4-4748-9a44-43f408651adf",
    "12ee030c-4dab-4dc5-8980-1d9075e8ad87",
    "148f0637-d878-4506-9d64-4671a8708969"
]

def generate_image(prompt: str, api_key: str):
    """Generate an image using Leonardo API"""
    
    print(f"🎨 Generating image...")
    print(f"   Prompt: {prompt}")
    print(f"   API Key: {api_key[:8]}...\n")
    
    # Leonardo API endpoint
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "prompt": prompt,
        "num_images": 1,
        "width": 512,
        "height": 512,
        "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",  # Leonardo Creative
        "guidance_scale": 7
    }
    
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        generation_id = data.get("sdGenerationJob", {}).get("generationId")
        
        if not generation_id:
            print(f"❌ No generation ID returned")
            return None
        
        print(f"✅ Generation started: {generation_id}")
        print(f"   Waiting for completion...")
        
        # Poll for completion
        status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
        
        for i in range(60):  # 2 minutes max
            time.sleep(2)
            
            status_response = httpx.get(status_url, headers=headers, timeout=30)
            status_response.raise_for_status()
            
            status_data = status_response.json()
            generation = status_data.get("generations_by_pk", {})
            status = generation.get("status")
            
            if status == "COMPLETE":
                images = generation.get("generated_images", [])
                if images:
                    image_url = images[0].get("url")
                    print(f"\n✅ Image generated!")
                    print(f"   URL: {image_url}")
                    
                    return {
                        "generation_id": generation_id,
                        "image_url": image_url,
                        "prompt": prompt
                    }
            
            elif status == "FAILED":
                print(f"❌ Generation failed")
                return None
        
        print(f"⏱️  Timeout waiting for generation")
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 leonardo_generate.py '<prompt>'")
        print("\nExample:")
        print("  python3 leonardo_generate.py 'a robot eating pizza in space'")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    print("\n🎨 Leonardo.ai Image Generation")
    print("="*60 + "\n")
    
    # Try first available API key
    api_key = API_KEYS[0]
    
    result = generate_image(prompt, api_key)
    
    if result:
        # Save result
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_file = f"leonardo_generation_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 Result saved to {output_file}")
    else:
        print("\n❌ Generation failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
