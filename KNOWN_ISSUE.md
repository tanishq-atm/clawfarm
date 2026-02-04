# Known Issue: CDP Connection

**Potential blocker:** Browser Use may not expose CDP endpoints publicly.

The v2 script assumes we can connect to:
```
wss://cloud.browser-use.com/sessions/{sessionId}/cdp
```

But this endpoint might not exist. Browser Use's business model is to abstract away the browser - they may intentionally NOT expose CDP for direct control.

## Fallback Plan

If CDP connection fails during test:

1. **Option A:** Use Browser Use for entire flow (like v1, but with better prompts)
2. **Option B:** Check Browser Use docs for CDP access
3. **Option C:** Demo the architecture conceptually without live CDP

The webhook + CDP architecture is still valid for:
- Self-hosted browsers (Browserless, PlaywrightCloud with CDP exposed)
- Local selenium/playwright with CDP enabled
- Services that explicitly expose CDP endpoints

## For ClawCon Demo

Emphasize the **architecture pattern** rather than this specific implementation:
> "Hybrid approach: Specialized tools for specialized tasks. Browser Use for bot detection, CDP for precision control, webhooks for real-time notifications."

Even if this exact flow doesn't work, the pattern is sound.
