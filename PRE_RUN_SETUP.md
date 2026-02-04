# Pre-Run Setup for Test

**Before you say "go", I need to:**

## 1. Install ngrok (if not already)
```bash
# Mac
brew install ngrok

# Or download directly
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

## 2. Start webhook infrastructure
```bash
# Terminal 1: Webhook server
python webhook_server.py

# Terminal 2: ngrok tunnel
ngrok http 5000

# Copy the ngrok URL from Terminal 2 output
```

## 3. Add ngrok URL to .env
```bash
# Add this line to .env:
NGROK_URL=https://xxxx.ngrok.io
```

## OR use automated script:
```bash
./setup_webhook.sh
# It will output the NGROK_URL to add to .env
```

## When ready:
- Webhook server running: `curl http://localhost:5000/health`
- ngrok tunnel active: Check http://localhost:4040
- NGROK_URL in .env
- Then say "go" and I'll run: `python leonardo_automation_v2.py`
