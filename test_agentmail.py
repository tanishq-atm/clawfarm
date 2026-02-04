#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from agentmail import AgentMail

# Load .env
load_dotenv()

api_key = os.getenv("AGENTMAIL_API_KEY")
if not api_key:
    print("❌ AGENTMAIL_API_KEY not found in .env")
    exit(1)

# Test connection
try:
    client = AgentMail(api_key=api_key)
    inboxes = client.inboxes.list(limit=5)
    print(f"✅ Connected! Found {len(inboxes.inboxes)} inbox(es):")
    for inbox in inboxes.inboxes:
        print(f"  - {inbox.inbox_id}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
