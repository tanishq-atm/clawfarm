#!/usr/bin/env python3
"""Phase 2: Check AgentMail for Leonardo verification email"""
from agentmail_utils import wait_for_leonardo_verification

if __name__ == '__main__':
    print("🚀 Phase 2: Waiting for Leonardo verification email\n")
    
    link = wait_for_leonardo_verification("leonardo-bot@agentmail.to")
    
    if link:
        print("\n✅ Phase 2 complete!")
        print("   Run: ./phase3_verify_and_get_key.sh")
    else:
        print("\n❌ Failed to get verification email")
        print("   Check manually: https://console.agentmail.to")
        exit(1)
