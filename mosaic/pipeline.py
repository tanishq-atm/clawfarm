#!/usr/bin/env python3
"""
Complete Mosaic Pipeline Orchestrator
Runs: Account creation → Mass generation → Mosaic building
"""
import asyncio
import subprocess
import json
import time
from datetime import datetime

def run_command(cmd: list, description: str):
    """Run a command and show progress"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}\n")
    
    start = time.time()
    result = subprocess.run(cmd, capture_output=False, text=True)
    elapsed = time.time() - start
    
    if result.returncode != 0:
        print(f"\n❌ Failed: {description}")
        return False
    
    print(f"\n✅ Complete: {description} ({elapsed:.1f}s)")
    return True

def main():
    print("\n" + "="*60)
    print("🎨 AGENTMAIL × CLAWCON MOSAIC PIPELINE")
    print("="*60)
    print("\nThis will:")
    print("  1. Create 3 Leonardo.ai accounts (parallel)")
    print("  2. Generate 1200 images (400 per account, parallel)")
    print("  3. Build photomosaic spelling 'AgentMail was at ClawCon'")
    print("\nEstimated time: 15-20 minutes")
    print("="*60 + "\n")
    
    input("Press ENTER to start...")
    
    pipeline_start = time.time()
    
    # Step 1: Create Leonardo accounts
    if not run_command(
        ["python3", "leonardo_parallel.py"],
        "Step 1/3: Creating 3 Leonardo accounts"
    ):
        return
    
    # Find the latest results file
    import glob
    results_files = sorted(glob.glob("leonardo_parallel_results_*.json"), reverse=True)
    if not results_files:
        print("❌ No account results found!")
        return
    
    account_results = results_files[0]
    
    # Extract API keys
    with open(account_results, 'r') as f:
        data = json.load(f)
    
    api_keys = [r['api_key'] for r in data['results'] if r.get('status') == 'success' and r.get('api_key')]
    
    print(f"\n✅ Got {len(api_keys)} API keys")
    
    if len(api_keys) < 3:
        print(f"⚠️  Only got {len(api_keys)} keys, continuing anyway...")
    
    # Update leonardo_mass_generate.py with these keys
    with open("leonardo_mass_generate.py", 'r') as f:
        content = f.read()
    
    # Replace API keys list
    keys_str = ",\n        ".join([f'"{k}"' for k in api_keys])
    import re
    content = re.sub(
        r'api_keys = \[.*?\]',
        f'api_keys = [\n        {keys_str}\n    ]',
        content,
        flags=re.DOTALL
    )
    
    with open("leonardo_mass_generate.py", 'w') as f:
        f.write(content)
    
    print(f"✅ Updated generation script with API keys")
    
    # Step 2: Generate images
    images_per_key = 400
    if not run_command(
        ["python3", "leonardo_mass_generate.py", str(images_per_key)],
        f"Step 2/3: Generating {images_per_key * len(api_keys)} images"
    ):
        return
    
    # Find latest mass results
    mass_results = sorted(glob.glob("leonardo_mass_results_*.json"), reverse=True)
    if not mass_results:
        print("❌ No generation results found!")
        return
    
    results_file = mass_results[0]
    
    # Step 3: Build mosaic
    if not run_command(
        ["python3", "mosaic_builder.py", results_file, "AgentMail was at ClawCon", "60", "20"],
        "Step 3/3: Building mosaic"
    ):
        return
    
    pipeline_elapsed = time.time() - pipeline_start
    
    print("\n" + "="*60)
    print("🎉 PIPELINE COMPLETE!")
    print(f"   Total time: {pipeline_elapsed/60:.1f} minutes")
    print("="*60)
    
    # Find the mosaic
    mosaics = sorted(glob.glob("mosaic_*.jpg"), reverse=True)
    if mosaics:
        print(f"\n✅ Mosaic saved to: {mosaics[0]}")
        print(f"   Open it to see 'AgentMail was at ClawCon' spelled in images!\n")

if __name__ == '__main__':
    main()
