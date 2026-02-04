#!/usr/bin/env python3
"""Create AgentMail inbox for Leonardo.ai signup"""
import os
import json
from dotenv import load_dotenv
from agentmail import AgentMail

load_dotenv()

api_key = os.getenv("AGENTMAIL_API_KEY")
client = AgentMail(api_key=api_key)

# Create inbox with deterministic client_id
inbox = client.inboxes.create(
    username="leonardo-bot",
    client_id="leonardo-signup-2026-02-04"
)

print(f"✅ Created inbox: {inbox.inbox_id}")
print(f"   Display name: {inbox.display_name}")

# Save inbox details for later use
inbox_data = {
    "inbox_id": inbox.inbox_id,
    "username": "leonardo-bot",
    "created_at": str(inbox.created_at),
}

with open('leonardo_inbox.json', 'w') as f:
    json.dump(inbox_data, f, indent=2)

print(f"\n💾 Saved to leonardo_inbox.json")
print(f"\n📧 Use this email for signup: {inbox.inbox_id}")
