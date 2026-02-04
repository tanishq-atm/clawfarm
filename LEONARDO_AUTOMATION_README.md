# Leonardo.ai Automation - Quick Reference

Automated Leonardo.ai signup + API key extraction using Browser Use and AgentMail.

## 📋 Files

### Utility Modules (Reusable)
- **`agentmail_utils.py`** - AgentMail API client with email polling functions
- **`browseruse_utils.py`** - Browser Use API client with task control

### Control Scripts
- **`browseruse_control.py`** - Interact with Browser Use tasks
- **`agentmail_utils.py`** - Can run standalone to wait for verification

### Phase Scripts (Run in order)
1. **`phase1_leonardo_signup.sh`** - Launch Browser Use signup task
2. **`phase2_check_email.py`** - Wait for verification email from AgentMail
3. **`phase3_verify_and_get_key.sh`** - Complete verification + get API key

### Data Files (Created during execution)
- `leonardo_credentials.json` - Email, password, task_id
- `verification_link.json` - Verification URL from email
- `leonardo_api_key_response.json` - Final API key result

---

## 🚀 Quick Start

### Phase 1: Sign Up
```bash
./phase1_leonardo_signup.sh
```
Creates Browser Use task to sign up at Leonardo.ai

### Check Task Status
```bash
venv/bin/python browseruse_control.py current
```

### Phase 2: Wait for Email
```bash
venv/bin/python phase2_check_email.py
```
Polls AgentMail inbox for verification email (auto-saves link)

### Phase 3: Complete Verification + Get Key
```bash
./phase3_verify_and_get_key.sh
```
Browser Use clicks verification link, logs in, generates API key

---

## 🛠 Browser Use Task Control

### Check current signup task
```bash
venv/bin/python browseruse_control.py current
```

### Stop a running task
```bash
# Stop current task
venv/bin/python browseruse_control.py stop

# Stop specific task
venv/bin/python browseruse_control.py stop <task-id>
```

### Monitor task live
```bash
venv/bin/python browseruse_control.py monitor
```
Polls every 15s until completion. **Press Ctrl+C to offer stop.**

### List recent tasks
```bash
venv/bin/python browseruse_control.py list
```

---

## 📧 AgentMail Utilities

### Wait for Leonardo verification (standalone)
```bash
venv/bin/python agentmail_utils.py
```
Polls inbox, extracts verification link, saves to `verification_link.json`

### Use in Python scripts
```python
from agentmail_utils import AgentMailClient

client = AgentMailClient()

# Wait for any email from leonardo.ai
message = client.wait_for_email(
    inbox_id="leonardo-bot@agentmail.to",
    from_domain="leonardo.ai",
    timeout_seconds=300
)

# Extract verification link
link = client.find_verification_link(message)
```

---

## 🔧 Python Module Functions

### AgentMailClient

```python
from agentmail_utils import AgentMailClient

client = AgentMailClient(api_key="am_...")

# Create inbox
inbox = client.create_inbox("my-username", client_id="unique-id")

# Get messages
messages = client.get_messages("user@agentmail.to", limit=10)

# Wait for specific email
msg = client.wait_for_email(
    inbox_id="user@agentmail.to",
    from_domain="example.com",
    subject_contains="verify",
    timeout_seconds=300,
    poll_interval=15
)

# Extract links
links = client.extract_links(msg, pattern=r"verify")
verify_link = client.find_verification_link(msg)
```

### BrowserUseClient

```python
from browseruse_utils import BrowserUseClient

client = BrowserUseClient(api_key="bu_...")

# Create task
task = client.create_task(
    task="Go to example.com and click the button",
    llm="browser-use-llm",
    start_url="https://example.com",
    max_steps=50
)

task_id = task['id']

# Check status
status = client.get_task(task_id)

# Stop task
client.stop_task(task_id)

# Wait for completion (polls automatically)
result = client.wait_for_completion(
    task_id,
    timeout_seconds=600,
    poll_interval=15,
    verbose=True
)

# Get final output
output = client.get_task_output(task_id)
```

---

## ⚙️ Configuration

### Environment Variables (.env)
```env
AGENTMAIL_API_KEY=am_your_key_here
BROWSERUSE_API_KEY=bu_your_key_here  # Optional, defaults to hardcoded
```

### Gateway Config (already set)
```bash
openclaw config get skills.entries.browser-use.apiKey
```

---

## 🎯 Example: Custom Automation

```python
from agentmail_utils import AgentMailClient
from browseruse_utils import BrowserUseClient

# Create fresh inbox
mail_client = AgentMailClient()
inbox = mail_client.create_inbox("test-signup-bot")
email = inbox['inbox_id']

# Sign up somewhere
browser_client = BrowserUseClient()
task = browser_client.create_task(
    task=f"Sign up at example.com with email {email}",
    llm="browser-use-llm"
)

# Wait for verification email
print("Waiting for verification email...")
message = mail_client.wait_for_email(
    inbox_id=email,
    from_domain="example.com",
    timeout_seconds=300
)

# Extract link
verify_link = mail_client.find_verification_link(message)

# Complete verification
verify_task = browser_client.create_task(
    task=f"Visit {verify_link} and complete verification",
    start_url=verify_link,
    llm="browser-use-llm"
)

result = browser_client.wait_for_completion(verify_task['id'])
print(result['output'])
```

---

## 📊 Dashboard & Monitoring

- **Browser Use Dashboard:** https://cloud.browser-use.com
- **AgentMail Console:** https://console.agentmail.to
- **Task URL:** `https://cloud.browser-use.com/tasks/<task-id>`

---

## 🚨 Interrupting Tasks

**YES, you can interrupt!**

### Via Control Script (Recommended)
```bash
venv/bin/python browseruse_control.py monitor
# Press Ctrl+C, then type 'y' to stop task
```

### Via API
```bash
venv/bin/python browseruse_control.py stop <task-id>
```

### Via Python
```python
from browseruse_utils import BrowserUseClient
client = BrowserUseClient()
client.stop_task("task-id-here")
```

**Note:** Stopped tasks refund unused time. You're only charged for minutes actually used.

---

## 💡 Tips

1. **Check task progress:** Visit dashboard URL to see live screenshots
2. **Debugging emails:** Print message content if link extraction fails
3. **Timeout tuning:** Adjust `timeout_seconds` and `poll_interval` as needed
4. **Reusable functions:** Import these modules in other automation scripts
5. **Cost control:** Browser Use charges per minute, stop tasks you don't need

---

## 🐛 Troubleshooting

### "No verification email received"
- Check https://console.agentmail.to manually
- Increase timeout in `wait_for_email()` call
- Check spam/promotions equivalent in AgentMail

### "Task stuck"
- Visit dashboard to see screenshots
- Stop task with `browseruse_control.py stop`
- Check if CAPTCHA is blocking (Browser Use usually handles these)

### "Link extraction failed"
- Check `message.get('text')` and `message.get('html')` content
- Update regex patterns in `find_verification_link()`
- Check email in AgentMail console for actual link format

---

## 📚 Further Reading

- AgentMail API: `skills/agentmail/references/API.md`
- Browser Use docs: https://docs.browser-use.com
- Browser Use Cloud API: https://docs.cloud.browser-use.com
