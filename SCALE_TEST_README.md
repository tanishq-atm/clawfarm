# Claw-Con Scale Testing

## What This Does

Tests your agent-based platform at scale by creating multiple agent accounts and having them interact with content (signup → verify → upvote).

## Usage

```bash
# Start small - test with 10 agents
python3 clawcon_parallel.py --count 10

# Scale up - 100 agents in batches of 50
python3 clawcon_parallel.py --count 100 --batch 50

# Full scale - 500 agents
python3 clawcon_parallel.py --count 500 --batch 50

# Custom post
python3 clawcon_parallel.py --count 50 --post https://www.claw-con.com/post/YOUR-POST-ID
```

## Parameters

- `--count`: Number of agent accounts to create (default: 10)
- `--batch`: Batch size for concurrent execution (default: 50)
- `--post`: Target post URL (default: your specified post)

## How It Works

**Batching:** Runs agents in batches to avoid overwhelming:
- Browser Use API rate limits
- AgentMail inbox creation limits
- Your site's infrastructure

**Per-Agent Flow:**
1. Create unique AgentMail inbox
2. Create Browser Use session
3. Sign up on claw-con
4. Wait for & click verification email
5. Navigate to post and upvote
6. Clean up session

**Async:** All agents in a batch run concurrently using asyncio.

## What to Watch For

### Browser Use Limits
- Check your Browser Use quota at https://cloud.browser-use.com
- Each agent uses 1 session + 3-4 tasks
- 500 agents ≈ 2000 task credits

### AgentMail Limits
- Free tier: check rate limits
- Each agent needs 1 inbox

### Your Site
- Monitor server load, database connections
- Watch for signup/login rate limiting
- Check email verification load
- Monitor vote count updates

### Expected Timing
- ~20-40s per agent (sequential)
- Batch of 50: ~40-60s total (parallel)
- 500 agents: ~10-15 minutes in 10 batches

## Monitoring

**Live progress:**
```bash
# Watch the script output - shows per-bot status
python3 clawcon_parallel.py --count 100 | tee test.log
```

**Results saved to:**
```
clawcon_test_results_TIMESTAMP.json
```

Contains:
- Success/failure counts
- Timing stats
- Per-bot details (inbox, session ID, errors)

## Troubleshooting

**High failure rate?**
- Reduce batch size (`--batch 25`)
- Add delays between batches (edit script)
- Check Browser Use quota
- Check AgentMail limits
- Check your site's rate limiting

**Slow performance?**
- Increase batch size (up to ~100)
- Check network latency
- Check Browser Use cloud region

**Verification emails not arriving?**
- Check AgentMail webhook config
- Increase polling timeout in script
- Check your site's email sending

## Safety Notes

Since you built the site:
- Test on staging first if you have it
- Start with small counts (10-50)
- Monitor your infrastructure during tests
- Have rollback plan for DB if needed
- Consider adding "test mode" flag to skip emails

## Next Steps

After validating at scale:
- Add rate limiting if needed
- Implement bot detection if desired
- Test other workflows (posts, comments, etc.)
- Benchmark database performance under load
