#!/usr/bin/env python3
"""Test Leonardo.ai signup page for CAPTCHAs and form structure"""
from playwright.sync_api import sync_playwright
import time

def test_signup_page():
    with sync_playwright() as p:
        # Launch browser (headless for server, set to False to see it)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        print("🌐 Navigating to Leonardo.ai...")
        page.goto('https://app.leonardo.ai/', timeout=30000)
        time.sleep(2)  # Let page settle
        
        print("📸 Taking screenshot...")
        page.screenshot(path='leonardo_landing.png')
        print("   Saved: leonardo_landing.png")
        
        # Look for signup button/link
        print("\n🔍 Looking for signup elements...")
        
        # Common signup selectors
        signup_selectors = [
            'a:has-text("Sign up")',
            'button:has-text("Sign up")',
            'a:has-text("Get Started")',
            'button:has-text("Get Started")',
            '[href*="signup"]',
            '[href*="register"]'
        ]
        
        for selector in signup_selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    print(f"   ✅ Found: {selector}")
                    print(f"      Text: {element.text_content()}")
                    print(f"      Visible: {element.is_visible()}")
            except Exception as e:
                pass
        
        # Get page content snippet
        print("\n📄 Page title:", page.title())
        print("📍 Current URL:", page.url)
        
        # Check for obvious CAPTCHA indicators
        captcha_indicators = ['recaptcha', 'hcaptcha', 'cloudflare', 'turnstile']
        html = page.content().lower()
        
        print("\n🤖 CAPTCHA scan:")
        for indicator in captcha_indicators:
            if indicator in html:
                print(f"   ⚠️  Found: {indicator}")
            else:
                print(f"   ✅ Clear: {indicator}")
        
        browser.close()
        print("\n✅ Test complete!")

if __name__ == '__main__':
    test_signup_page()
