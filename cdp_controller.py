#!/usr/bin/env python3
"""
CDP Browser Controller
Takes over Browser Use session via Chrome DevTools Protocol
"""
import asyncio
import json
import re
from typing import Optional
from playwright.async_api import async_playwright

class CDPController:
    """Control browser via CDP"""
    
    def __init__(self, cdp_url: str):
        self.cdp_url = cdp_url
        self.browser = None
        self.context = None
        self.page = None
    
    async def connect(self):
        """Connect to browser via CDP"""
        playwright = await async_playwright().start()
        
        # Connect to existing browser via CDP
        self.browser = await playwright.chromium.connect_over_cdp(self.cdp_url)
        
        # Get the existing context and page
        contexts = self.browser.contexts
        if contexts:
            self.context = contexts[0]
            pages = self.context.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = await self.context.new_page()
        else:
            print("⚠️ No existing context, creating new one")
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
        
        print(f"✅ Connected to browser via CDP")
        print(f"   Current URL: {self.page.url}")
        return self.page
    
    async def enter_verification_code(self, code: str):
        """Enter verification code on Leonardo.ai"""
        print(f"🔑 Entering verification code: {code}")
        
        # Wait for verification input
        await self.page.wait_for_load_state('networkidle')
        
        # Try common verification input selectors
        selectors = [
            'input[type="text"]',
            'input[placeholder*="code" i]',
            'input[placeholder*="verification" i]',
            'input[name*="code" i]',
            'input[id*="code" i]',
        ]
        
        for selector in selectors:
            try:
                input_field = await self.page.wait_for_selector(selector, timeout=5000)
                if input_field:
                    await input_field.fill(code)
                    print(f"✅ Entered code in {selector}")
                    
                    # Try to find and click submit button
                    submit_selectors = [
                        'button[type="submit"]',
                        'button:has-text("Verify")',
                        'button:has-text("Continue")',
                        'button:has-text("Submit")',
                    ]
                    
                    for submit_sel in submit_selectors:
                        try:
                            submit_btn = await self.page.wait_for_selector(submit_sel, timeout=2000)
                            if submit_btn:
                                await submit_btn.click()
                                print(f"✅ Clicked submit button")
                                break
                        except:
                            continue
                    
                    return True
            except:
                continue
        
        print("⚠️ Could not find verification input field")
        return False
    
    async def navigate_to_api_settings(self):
        """Navigate to API settings page"""
        print("🧭 Navigating to API settings...")
        
        # Wait for page load after verification
        await asyncio.sleep(3)
        await self.page.wait_for_load_state('networkidle')
        
        # Try to find API/settings links
        api_links = [
            'a:has-text("API")',
            'a:has-text("Settings")',
            'a:has-text("Developer")',
            'a[href*="api"]',
            'a[href*="settings"]',
        ]
        
        for link_sel in api_links:
            try:
                link = await self.page.wait_for_selector(link_sel, timeout=3000)
                if link:
                    await link.click()
                    print(f"✅ Clicked: {link_sel}")
                    await self.page.wait_for_load_state('networkidle')
                    break
            except:
                continue
        
        # Alternative: direct navigation
        if 'api' not in self.page.url.lower():
            try:
                await self.page.goto('https://app.leonardo.ai/settings/api')
                await self.page.wait_for_load_state('networkidle')
                print("✅ Navigated directly to API settings")
            except:
                print("⚠️ Could not navigate to API settings")
    
    async def generate_api_key(self) -> Optional[str]:
        """Generate and extract API key"""
        print("🔑 Generating API key...")
        
        # Look for "Generate" or "Create API Key" button
        generate_selectors = [
            'button:has-text("Generate")',
            'button:has-text("Create")',
            'button:has-text("New API Key")',
            'button:has-text("API Key")',
        ]
        
        for gen_sel in generate_selectors:
            try:
                gen_btn = await self.page.wait_for_selector(gen_sel, timeout=5000)
                if gen_btn:
                    await gen_btn.click()
                    print(f"✅ Clicked generate button")
                    await asyncio.sleep(2)
                    break
            except:
                continue
        
        # Extract API key from page
        await asyncio.sleep(2)
        content = await self.page.content()
        
        # Look for UUID-format key
        uuid_pattern = r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
        matches = re.findall(uuid_pattern, content)
        
        if matches:
            api_key = matches[0]
            print(f"✅ Extracted API key: {api_key[:20]}...")
            return api_key
        
        # Try to get from input/textarea
        try:
            key_input = await self.page.query_selector('input[value*="-"]')
            if key_input:
                api_key = await key_input.get_attribute('value')
                if api_key and len(api_key) > 20:
                    print(f"✅ Extracted API key from input: {api_key[:20]}...")
                    return api_key
        except:
            pass
        
        print("⚠️ Could not extract API key")
        return None
    
    async def screenshot(self, filename: str = "screenshot.png"):
        """Take screenshot for debugging"""
        await self.page.screenshot(path=filename)
        print(f"📸 Screenshot saved: {filename}")
    
    async def close(self):
        """Close browser connection"""
        if self.browser:
            await self.browser.close()
            print("✅ Browser connection closed")

async def control_leonardo_verification(cdp_url: str, verification_code: str) -> Optional[str]:
    """
    Main function: Connect to browser, verify email, extract API key
    
    Args:
        cdp_url: Chrome DevTools Protocol URL from Browser Use
        verification_code: 6-digit code from email
    
    Returns:
        API key if successful, None otherwise
    """
    controller = CDPController(cdp_url)
    
    try:
        # Connect to browser
        await controller.connect()
        
        # Enter verification code
        await controller.enter_verification_code(verification_code)
        
        # Navigate to API settings
        await controller.navigate_to_api_settings()
        
        # Generate and extract API key
        api_key = await controller.generate_api_key()
        
        if api_key:
            return api_key
        else:
            # Take screenshot for debugging
            await controller.screenshot("failed_api_extraction.png")
            return None
    
    finally:
        await controller.close()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python cdp_controller.py <cdp_url> <verification_code>")
        sys.exit(1)
    
    cdp_url = sys.argv[1]
    code = sys.argv[2]
    
    api_key = asyncio.run(control_leonardo_verification(cdp_url, code))
    
    if api_key:
        print(f"\n✅ Success! API Key: {api_key}")
    else:
        print("\n❌ Failed to extract API key")
        sys.exit(1)
