#!/usr/bin/env python3
"""AgentMail utility functions for Leonardo.ai automation"""
import os
import json
import time
import re
from typing import Optional, Dict, List
from dotenv import load_dotenv
import httpx

load_dotenv()

class AgentMailClient:
    """Simple AgentMail API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AGENTMAIL_API_KEY")
        self.base_url = "https://api.agentmail.to/v0"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def create_inbox(self, username: str, client_id: Optional[str] = None) -> Dict:
        """Create a new inbox"""
        payload = {"username": username}
        if client_id:
            payload["client_id"] = client_id
        
        response = httpx.post(
            f"{self.base_url}/inboxes",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def list_inboxes(self, limit: int = 10) -> List[Dict]:
        """List all inboxes"""
        response = httpx.get(
            f"{self.base_url}/inboxes",
            headers=self.headers,
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json().get("inboxes", [])
    
    def get_messages(self, inbox_id: str, limit: int = 10) -> List[Dict]:
        """Get messages for an inbox"""
        response = httpx.get(
            f"{self.base_url}/inboxes/{inbox_id}/messages",
            headers=self.headers,
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json().get("messages", [])
    
    def wait_for_email(
        self, 
        inbox_id: str, 
        from_domain: str = None,
        subject_contains: str = None,
        timeout_seconds: int = 300,
        poll_interval: int = 15
    ) -> Optional[Dict]:
        """
        Poll inbox until email matching criteria arrives
        
        Args:
            inbox_id: Email address to check
            from_domain: Filter by sender domain (e.g., 'leonardo.ai')
            subject_contains: Filter by subject keywords
            timeout_seconds: Max time to wait (default 5 min)
            poll_interval: Seconds between checks (default 15s)
        
        Returns:
            First matching message dict, or None if timeout
        """
        max_attempts = timeout_seconds // poll_interval
        
        print(f"📬 Waiting for email at {inbox_id}")
        if from_domain:
            print(f"   From domain: *@{from_domain}")
        if subject_contains:
            print(f"   Subject contains: '{subject_contains}'")
        print(f"   Timeout: {timeout_seconds}s ({max_attempts} attempts)\n")
        
        for attempt in range(1, max_attempts + 1):
            print(f"⏳ Attempt {attempt}/{max_attempts}...", end=" ")
            
            try:
                messages = self.get_messages(inbox_id)
                print(f"{len(messages)} message(s)")
                
                for msg in messages:
                    # Extract sender
                    from_field = msg.get("from", "")
                    # from_field is a string like "Leonardo Ai <contact@leonardo.ai>"
                    if isinstance(from_field, str):
                        from_email = from_field
                    elif isinstance(from_field, list) and from_field:
                        from_email = from_field[0].get("email", "") if isinstance(from_field[0], dict) else str(from_field[0])
                    else:
                        from_email = ""
                    
                    # Extract subject
                    subject = msg.get("subject", "")
                    
                    # Check filters
                    domain_match = True
                    if from_domain:
                        domain_match = from_domain.lower() in from_email.lower()
                    
                    subject_match = True
                    if subject_contains:
                        subject_match = subject_contains.lower() in subject.lower()
                    
                    if domain_match and subject_match:
                        print(f"\n✅ Match found!")
                        print(f"   From: {from_email}")
                        print(f"   Subject: {subject}\n")
                        return msg
                
                if attempt < max_attempts:
                    time.sleep(poll_interval)
            
            except Exception as e:
                print(f"❌ Error: {e}")
                if attempt < max_attempts:
                    time.sleep(poll_interval)
        
        print(f"\n⏱️ Timeout: No matching email after {timeout_seconds}s")
        return None
    
    def extract_links(self, message: Dict, pattern: str = None) -> List[str]:
        """
        Extract URLs from email message
        
        Args:
            message: Message dict from get_messages()
            pattern: Optional regex pattern to filter URLs
        
        Returns:
            List of URLs found in email
        """
        text = message.get("text", "")
        html = message.get("html", "")
        content = html or text
        
        # Basic URL extraction
        url_pattern = r'https?://[^\s<>"\'\)]+(?:[^\s<>"\'\)]|(?=\s*$))'
        urls = re.findall(url_pattern, content, re.IGNORECASE)
        
        # Filter by pattern if provided
        if pattern:
            urls = [url for url in urls if re.search(pattern, url, re.IGNORECASE)]
        
        # Clean up common trailing chars
        cleaned = []
        for url in urls:
            url = url.rstrip('.,;:!?)')
            cleaned.append(url)
        
        return cleaned
    
    def find_verification_link(self, message: Dict) -> Optional[str]:
        """
        Extract verification/confirmation link from message
        
        Common patterns for verification emails
        """
        patterns = [
            r'verify',
            r'confirm',
            r'activation',
            r'validate',
            r'authenticate'
        ]
        
        for pattern in patterns:
            links = self.extract_links(message, pattern)
            if links:
                return links[0]  # Return first match
        
        # Fallback: return first leonardo.ai link
        links = self.extract_links(message, r'leonardo\.ai')
        return links[0] if links else None


def load_credentials(filename: str = "leonardo_credentials.json") -> Dict:
    """Load saved credentials from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)


def save_credentials(data: Dict, filename: str = "leonardo_credentials.json"):
    """Save credentials to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def save_verification_link(link: str, message: Dict, filename: str = "verification_link.json"):
    """Save verification link and metadata"""
    data = {
        "link": link,
        "subject": message.get("subject", ""),
        "from": message.get("from", [{}])[0].get("email", ""),
        "found_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"💾 Saved to {filename}")


# Example usage functions
def wait_for_leonardo_verification(inbox_id: str = "leonardo-bot@agentmail.to") -> Optional[str]:
    """
    Convenience function: wait for Leonardo verification email and return link
    """
    client = AgentMailClient()
    
    # Wait for email from Leonardo
    message = client.wait_for_email(
        inbox_id=inbox_id,
        from_domain="leonardo.ai",
        timeout_seconds=300
    )
    
    if not message:
        return None
    
    # Extract verification link
    link = client.find_verification_link(message)
    
    if link:
        print(f"🔗 Verification link: {link}\n")
        save_verification_link(link, message)
        return link
    else:
        print("⚠️ No verification link found in email")
        # Print email preview for debugging
        text = message.get("text", "")[:500]
        print(f"\nEmail preview:\n{text}\n")
        return None


if __name__ == '__main__':
    # When run directly, wait for Leonardo verification
    print("🚀 AgentMail Utils - Leonardo Verification Mode\n")
    link = wait_for_leonardo_verification()
    
    if link:
        print("✅ Ready for Phase 3!")
        print("   Run: ./phase3_verify_and_get_key.sh")
    else:
        print("❌ No verification email received")
        print("   Check manually at: https://console.agentmail.to")
