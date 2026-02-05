# ClawFarm Quick Start

Get up and running in 5 minutes.

## 1. Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/clawfarm.git
cd clawfarm

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
nano .env  # Add your AgentMail and Browser Use keys
```

## 2. Create Leonardo Accounts

```bash
# Create 3 accounts with API keys
python3 leonardo/create_accounts.py
```

**Output:** `leonardo_parallel_results_*.json` with 3 API keys

**Time:** 2-4 minutes

## 3. Generate Images

```bash
# Generate 100 images (faster for testing)
python3 leonardo/generate_images.py 100
```

**Output:** `leonardo_mass_results_*.json` with 100 image URLs

**Time:** 2-3 minutes

## 4. Build Mosaic

```bash
# Build a small mosaic (10×10 grid)
python3 mosaic/builder.py leonardo_mass_results_*.json "Hello World" 10 10
```

**Output:** `mosaic_*.jpg` high-resolution image

**Time:** 10-20 seconds

## 5. Vote on Claw-Con

```bash
# Cast 10 test votes
python3 clawcon/vote_api.py --count 10 --submission YOUR_SUBMISSION_ID
```

**Time:** ~3 minutes for 10 votes

## Full Pipeline Example

Run everything automatically:

```bash
# Complete mosaic pipeline
python3 mosaic/pipeline.py
```

This will:
1. Create 3 Leonardo accounts
2. Generate 1,200 images  
3. Build final mosaic

**Total time:** ~15-20 minutes

## Troubleshooting

### "Browser Use 429 error"
- Only 3 concurrent sessions allowed
- Wait 1 minute and retry
- Use `single_account.py` instead for reliability

### "Not enough images"
- Lower the grid size or images per key
- Check generation results JSON for failures

### "Magic link not received"
- AgentMail may have delay (up to 60 seconds)
- Check inbox manually at agentmail.to

## Next Steps

- Read full docs in each module's README
- Customize prompts in `leonardo/generate_images.py`
- Experiment with different grid sizes
- Try parallel voting with `clawcon/vote_fast.py`

## Tips

- **AgentMail:** Free tier has rate limits, upgrade for more
- **Browser Use:** Free tier limited, consider paid for production
- **Leonardo:** Each account has ~3,344 tokens (400 images)
- **Voting:** Sequential is slow but 100% reliable

## Example Results

Check `results/` directory for:
- Account creation logs
- Generation results
- Voting summaries
- Final mosaics
