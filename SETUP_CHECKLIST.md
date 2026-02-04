# Setup Checklist - Leonardo.ai Automation v2

Run through this checklist before starting the automation.

## ✅ Prerequisites

### 1. API Keys
- [ ] AgentMail API key from [console.agentmail.to](https://console.agentmail.to)
- [ ] Browser Use API key from [cloud.browser-use.com](https://cloud.browser-use.com)
- [ ] Both keys added to `.env` file

### 2. System Dependencies
- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] pip installed (`pip --version`)
- [ ] ngrok installed (`ngrok version`)
  - Mac: `brew install ngrok`
  - Linux: `snap install ngrok` or download from [ngrok.com](https://ngrok.com/download)
  - Windows: Download from [ngrok.com](https://ngrok.com/download)

### 3. Python Environment
- [ ] Virtual environment created (`python3 -m venv venv`)
- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright browsers installed (`python -m playwright install chromium`)

### 4. Webhook Infrastructure
- [ ] Webhook server running (`python webhook_server.py` in separate terminal)
- [ ] ngrok tunnel active (`ngrok http 5000` in separate terminal)
- [ ] ngrok public URL added to `.env` as `NGROK_URL`
- [ ] Webhook health check passes (`curl http://localhost:5000/health`)

**OR use automated setup:**
```bash
./setup_webhook.sh
# Copy NGROK_URL from output to .env
```

## 🚀 Ready to Run

Once all items are checked, you're ready:

```bash
python leonardo_automation_v2.py
```

## 🔍 Verification

Test each component individually:

```bash
# Test webhook server
curl http://localhost:5000/health

# Test ngrok tunnel
curl http://localhost:4040/api/tunnels

# Test AgentMail connection
python -c "from agentmail_utils import AgentMailClient; print('✅ AgentMail OK')"

# Test Browser Use connection
python -c "from browseruse_utils import BrowserUseClient; client = BrowserUseClient(); print('✅ Browser Use OK')"

# Test CDP/Playwright
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright OK')"
```

## ❌ Troubleshooting

**ngrok not found:**
```bash
# Mac
brew install ngrok

# Linux (snap)
sudo snap install ngrok

# Linux (manual)
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

**Playwright browsers not installed:**
```bash
python -m playwright install chromium
```

**Webhook server won't start (port in use):**
```bash
# Find process on port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port
WEBHOOK_PORT=5001 python webhook_server.py
```

**ngrok authentication required:**
```bash
# Sign up at ngrok.com, get auth token
ngrok config add-authtoken <your_token>
```

## 📊 Expected Timeline

When everything is set up correctly:

1. **Phase 1** (Signup): 2-3 minutes
2. **Phase 2** (Webhook): < 5 seconds  
3. **Phase 3** (CDP): 1-2 minutes

**Total: 5-10 minutes per account**
