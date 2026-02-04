#!/usr/bin/env python3
"""Test Leonardo.ai signup with stealth mode to bypass bot detection"""
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

def test_signup_stealth():
    with sync_playwright() as p:
        # Launch with more realistic settings
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        page = context.new_page()
        
        # Apply stealth to hide automation
        stealth = Stealth()
        stealth.apply_stealth(page)
        
        print("🥷 Stealth mode enabled")
        print("🌐 Navigating to Leonardo.ai...")
        
        page.goto('https://app.leonardo.ai/', timeout=30000)
        
        # Wait a bit for any JS to run
        print("⏳ Waiting for page to settle...")
        time.sleep(5)
        
        print("📸 Taking screenshot...")
        page.screenshot(path='leonardo_stealth.png')
        print("   Saved: leonardo_stealth.png")
        
        print(f"\n📄 Page title: {page.title()}")
        print(f"📍 Current URL: {page.url}")
        
        # Check if we got past the checkpoint
        if 'Vercel Security Checkpoint' in page.title():
            print("\n❌ Still blocked by Vercel checkpoint")
            print("   Bot detection is strong on this one.")
        else:
            print("\n✅ Bypassed checkpoint! We're in!")
            
            # Look for signup options
            print("\n🔍 Looking for signup/login options...")
            content = page.content()
            
            # Try to find signup button
            signup_texts = ['sign up', 'create account', 'get started', 'register']
            for text in signup_texts:
                if text.lower() in content.lower():
                    print(f"   Found: '{text}' in page content")
        
        # Check page HTML for clues
        html_snippet = page.content()[:1000]
        print(f"\n📝 First 1000 chars of HTML:")
        print(html_snippet)
        
        browser.close()
        print("\n✅ Test complete!")

if __name__ == '__main__':
    test_signup_stealth()
