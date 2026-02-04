# Prompt Analysis - What's Wrong

## Current Task 2 Prompt (v3)
```
You are on the Leonardo.ai verification page. Enter the verification code: {code}

After verification is complete, navigate to the API settings or developer settings page (look in account menu, user settings, or developer section). Generate a new API key. Extract and return the complete API key value.
```

## Problem
**Assumes context:** "You are on the Leonardo.ai verification page"

But Browser Use tasks don't share memory. Task 2 agent:
- Doesn't know what Task 1 did
- Doesn't remember being on a verification page
- Starts fresh, just sees the browser state

## What Actually Works (from earlier successful run)
```
Navigate to app.leonardo.ai and log in with:
- Email: leonardo-bot-20260204-034244@agentmail.to
- Password: L30Bot20260204-034244!Secure

You should see a verification code input field. Enter the verification code: 623535

After email verification is complete, navigate to the API settings or developer settings page (look in account menu, user settings, or developer section). Generate a new API key. Extract and return the complete API key value.
```

Key difference: **Tells it what to DO, not where it IS**

## Better Task 2 Prompt
```
The browser is currently on Leonardo.ai. Complete the signup process by entering this verification code: {code}

Once verification succeeds, navigate to the account settings, find the API or Developer section, generate a new API key, and return the key value.
```

Or even simpler:
```
Continue the Leonardo.ai signup. Enter verification code: {code}. Then go to API settings and generate a new API key. Return the key.
```

## The Real Issue
Browser Use sessions preserve **browser state** (cookies, URL, logged-in status) but **NOT task memory**. Each task is a new agent that just sees the current browser state.

Task 2 should:
1. Observe current state (it'll see the verification page)
2. Be told what to do next (enter code X)
3. Continue from there

Not:
1. Assume it knows where it is
2. Be told what page it's on
