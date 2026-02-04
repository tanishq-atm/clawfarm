#!/bin/bash
# Run Browser Use task to sign up for Leonardo.ai and get API key

API_KEY="bu_RE73gaEVWynxZNuRjWlyLxQWQTFz2-8vwQNBFdhtauw"
EMAIL="leonardo-bot@agentmail.to"

# The task prompt - tells Browser Use what to do
TASK="Sign up for Leonardo.ai using the email ${EMAIL}. Create a strong password and save it. After signing up, you'll need to verify the email - check ${EMAIL} inbox at https://console.agentmail.to for the verification link and click it. Then log into Leonardo.ai, navigate to the API settings page, generate an API key, and return the API key value."

echo "🚀 Launching Browser Use task..."
echo "📧 Using email: $EMAIL"
echo ""

# Create the task
RESPONSE=$(curl -s -X POST "https://api.browser-use.com/api/v2/tasks" \
  -H "X-Browser-Use-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"task\": \"$TASK\",
    \"llm\": \"browser-use-llm\",
    \"maxSteps\": 150
  }")

echo "Response: $RESPONSE"

# Extract task ID
TASK_ID=$(echo $RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TASK_ID" ]; then
    echo "❌ Failed to create task"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ Task created: $TASK_ID"
echo ""
echo "📊 Monitor at: https://cloud.browser-use.com/tasks/$TASK_ID"
echo ""
echo "⏳ Polling for completion (this may take 5-10 minutes)..."

# Poll for completion
while true; do
    STATUS_RESPONSE=$(curl -s "https://api.browser-use.com/api/v2/tasks/$TASK_ID" \
      -H "X-Browser-Use-API-Key: $API_KEY")
    
    STATUS=$(echo $STATUS_RESPONSE | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    
    echo "   Status: $STATUS"
    
    if [ "$STATUS" = "finished" ] || [ "$STATUS" = "failed" ] || [ "$STATUS" = "stopped" ]; then
        echo ""
        echo "🎉 Task complete!"
        echo ""
        echo "Full response:"
        echo "$STATUS_RESPONSE" | jq '.' 2>/dev/null || echo "$STATUS_RESPONSE"
        break
    fi
    
    sleep 15
done
