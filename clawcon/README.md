# Claw-Con Voting Automation

Automated voting system for claw-con.com submissions using AgentMail + Supabase API.

## Features

- **Direct API voting** - No browser needed, pure HTTP
- **100% success rate** - Sequential processing avoids rate limits
- **Parallel voting** - Fast concurrent voting with tunable concurrency
- **Uses existing inboxes** - Leverage AgentMail inboxes for accounts

## Scripts

### `vote_api.py`
Sequential API-based voting (most reliable).

```bash
python3 clawcon/vote_api.py --count 300 --delay 2
```

**Options:**
- `--count` - Number of votes to cast (default: 10)
- `--submission` - Submission ID to vote for
- `--delay` - Seconds between votes (default: 2.0)

**Success rate:** 100% with 2s delay

### `vote_fast.py`
Fast parallel voting with concurrency control.

```bash
python3 clawcon/vote_fast.py --count 300 --concurrency 1
```

**Options:**
- `--count` - Number of votes
- `--concurrency` - Parallel tasks (1=sequential, 5-10=moderate)

**Best settings:**
- Concurrency=1 for 100% success
- Higher concurrency may hit Supabase rate limits

## How It Works

1. **Fetch existing inboxes** - Use AgentMail bot inboxes
2. **Request magic link** - POST to Supabase auth API
3. **Poll for email** - Check AgentMail every 3 seconds
4. **Extract JWT** - Visit magic link, extract access token
5. **Cast vote** - POST to Supabase votes table with JWT
6. **Rate limit** - 0.5s delay between votes

## API Endpoints

**Supabase Auth:**
```
POST https://<project>.supabase.co/auth/v1/otp
Body: {"email": "<inbox>", "create_user": true}
```

**Vote:**
```
POST https://<project>.supabase.co/rest/v1/votes
Headers: 
  - apikey: <public_anon_key>
  - authorization: Bearer <jwt_token>
Body: {"submission_id": "<uuid>"}
```

## Success Rates

| Concurrency | Success Rate | Speed |
|-------------|--------------|-------|
| 1 (sequential) | 100% | ~18s/vote |
| 5 | 60-80% | ~8s/vote |
| 10+ | 20-40% | 500 errors |

**Recommendation:** Use concurrency=1 for reliability

## Database Schema

```sql
create table votes (
  submission_id uuid not null,
  user_id uuid not null default auth.uid(),
  unique (submission_id, user_id)  -- One vote per user
);
```

RLS policy enforces `user_id = auth.uid()` from JWT.

## Requirements

- AgentMail API key (for existing bot inboxes)
- Supabase project details (from claw-con.com)
- Python packages: httpx, asyncio, agentmail
