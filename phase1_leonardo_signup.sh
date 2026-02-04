#!/bin/bash
# Phase 1: Sign up for Leonardo.ai (Browser Use will handle this)

API_KEY="bu_RE73gaEVWynxZNuRjWlyLxQWQTFz2-8vwQNBFdhtauw"
EMAIL="leonardo-bot@agentmail.to"
PASSWORD="L30nard0B0t2026!Secure"

# Simpler task: just sign up
TASK="Go to app.leonardo.ai and sign up for a new account. Use the email '${EMAIL}' and password '${PASSWORD}'. Fill out all required fields. If there are any additional steps like choosing a username, use 'leonardobot'. Complete the signup process as far as you can (you will need to verify email but can't access the inbox)."

echo "🚀 Phase 1: Creating Leonardo.ai account"
echo "📧 Email: $EMAIL"
echo "🔑 Password: $PASSWORD"
echo ""

# Create the task
RESPONSE=$(curl -s -X POST "https://api.browser-use.com/api/v2/tasks" \
  -H "X-Browser-Use-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"task\": $(echo "$TASK" | jq -Rs .),
    \"llm\": \"browser-use-llm\",
    \"maxSteps\": 100,
    \"startUrl\": \"https://app.leonardo.ai\"
  }")

echo "$RESPONSE" | jq '.'

# Extract task ID
TASK_ID=$(echo $RESPONSE | jq -r '.id')

if [ "$TASK_ID" = "null" ] || [ -z "$TASK_ID" ]; then
    echo "❌ Failed to create task"
    exit 1
fi

echo ""
echo "✅ Task ID: $TASK_ID"
echo "📊 Monitor: https://cloud.browser-use.com/tasks/$TASK_ID"
echo ""
echo "💾 Saving credentials..."

# Save credentials for later phases
cat > leonardo_credentials.json <<EOF
{
  "email": "$EMAIL",
  "password": "$PASSWORD",
  "task_id": "$TASK_ID",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "Saved to leonardo_credentials.json"
echo ""
echo "⏳ Task is running... Check the monitor URL to see progress"
echo "   When done, run phase2_check_email.py to get verification link"
