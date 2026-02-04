# Example Agent Conversation

This shows how a human might interact with their OpenClaw agent to use this repo.

---

## Scenario 1: First Time Setup

**Human:**
> I cloned the clawfarm repo to ~/.openclaw/workspace/clawfarm. I've added my AgentMail and Browser Use API keys to the .env file. Can you run the Leonardo automation and get me an API key?

**Agent (reads AGENT_INSTRUCTIONS.md, then):**
> Sure! I'll set up and run the Leonardo automation.
> 
> Setting up virtual environment and dependencies...
> [runs setup commands]
> 
> Running the automation...
> [runs leonardo_automation.py]
> 
> ✅ Success! Created Leonardo account in 2m41s.
> 
> **Results:**
> - Email: leonardo-bot-20260204-141523@agentmail.to
> - API Key: 8f2a4b9c-1d3e-4f5a-9b8c-7e6d5c4b3a2f
> - Test image generated successfully
> 
> The API key has been saved to .env and leonardo_automation_state.json. You can start using it for image generation!

---

## Scenario 2: Generate More Keys

**Human:**
> Can you run it again? I want 3 more Leonardo API keys.

**Agent:**
> Running the automation 3 times to create 3 more accounts...
> 
> **Run 1/3:**
> ✅ leonardo-bot-20260204-142301@agentmail.to
>    Key: 5a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d
> 
> **Run 2/3:**
> ⏳ Waiting 3 minutes (Browser Use rate limit)...
> ✅ leonardo-bot-20260204-142647@agentmail.to
>    Key: 9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c
> 
> **Run 3/3:**
> ⏳ Waiting 3 minutes (Browser Use rate limit)...
> ✅ leonardo-bot-20260204-143012@agentmail.to
>    Key: 2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f
> 
> Done! Created 3 new Leonardo accounts. All API keys saved to .env.

---

## Scenario 3: Agent Troubleshooting

**Human:**
> Run the Leonardo automation for me.

**Agent (checks .env):**
> I found the clawfarm repo, but the .env file is missing API keys. I need:
> 
> 1. **AGENTMAIL_API_KEY** - Get from https://agentmail.to
> 2. **BROWSERUSE_API_KEY** - Get from https://browser-use.com
> 
> Once you have those, I can add them to .env and run the automation.

**Human:**
> Here's my AgentMail key: am_abc123...
> And Browser Use key: bu_xyz789...

**Agent:**
> Thanks! I've added both keys to .env.
> 
> Running the automation now...
> [proceeds with automation]

---

## Scenario 4: Using Generated Keys

**Human:**
> I see you created some Leonardo accounts. Can you use one of those API keys to generate an image of a sunset?

**Agent:**
> Sure! Using the most recent Leonardo API key from .env...
> 
> [reads API key from .env]
> [makes API call to Leonardo]
> 
> ✅ Image generation started!
> - Generation ID: abc-def-ghi-123
> - Prompt: "Beautiful sunset over ocean, vibrant colors, photorealistic"
> - Cost: $0.0105
> - Status: Processing...
> 
> The image should be ready in ~30 seconds. You can view it at:
> https://app.leonardo.ai/generations/abc-def-ghi-123

---

## Scenario 5: Check What Was Created

**Human:**
> How many Leonardo accounts do I have from this automation?

**Agent (checks .env and state files):**
> Looking at .env, I see 4 Leonardo API keys:
> 
> 1. `8f2a4b9c-1d3e-4f5a-9b8c-7e6d5c4b3a2f`
> 2. `5a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d`
> 3. `9f8e7d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c`
> 4. `2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f` (most recent)
> 
> The latest state file shows:
> - Email: leonardo-bot-20260204-143012@agentmail.to
> - Password: [saved in state file]
> - Created: Feb 4, 2026 14:30
> 
> All accounts should have free credits available for image generation.

---

## Key Takeaways

1. **Agent reads AGENT_INSTRUCTIONS.md** to understand what to do
2. **Fully autonomous** - agent handles setup, execution, error handling
3. **Self-documenting** - all info in the repo
4. **Reusable** - can run multiple times for multiple accounts
5. **Agent-friendly** - structured output, clear results

This is the power of **agent-ready repositories**!
