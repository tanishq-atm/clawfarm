#!/bin/bash
# Phase 3: Verify email and generate API key

API_KEY="bu_RE73gaEVWynxZNuRjWlyLxQWQTFz2-8vwQNBFdhtauw"

# Load verification link
if [ ! -f verification_link.json ]; then
    echo "❌ verification_link.json not found"
    echo "   Run phase2_check_email.py first"
    exit 1
fi

VERIFY_LINK=$(cat verification_link.json | jq -r '.link')

echo "🔗 Verification link: $VERIFY_LINK"
echo ""

# Load credentials
EMAIL=$(cat leonardo_credentials.json | jq -r '.email')
PASSWORD=$(cat leonardo_credentials.json | jq -r '.password')

# Task: verify email then get API key
TASK="First, go to this verification link and complete email verification: ${VERIFY_LINK}. After verification is complete, log into Leonardo.ai with email '${EMAIL}' and password '${PASSWORD}'. Then navigate to the API settings or developer settings page (usually in account settings or user menu). Generate a new API key. Extract and return the complete API key value."

echo "🚀 Phase 3: Verifying email + generating API key"
echo ""

# Create the task
RESPONSE=$(curl -s -X POST "https://api.browser-use.com/api/v2/tasks" \
  -H "X-Browser-Use-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"task\": $(echo "$TASK" | jq -Rs .),
    \"llm\": \"browser-use-llm\",
    \"maxSteps\": 150,
    \"startUrl\": \"$VERIFY_LINK\"
  }")

echo "$RESPONSE" | jq '.'

TASK_ID=$(echo $RESPONSE | jq -r '.id')

if [ "$TASK_ID" = "null" ] || [ -z "$TASK_ID" ]; then
    echo "❌ Failed to create task"
    exit 1
fi

echo ""
echo "✅ Task ID: $TASK_ID"
echo "📊 Monitor: https://cloud.browser-use.com/tasks/$TASK_ID"
echo ""
echo "⏳ This may take a few minutes..."
echo ""

# Poll for completion
while true; do
    sleep 20
    
    STATUS_RESPONSE=$(curl -s "https://api.browser-use.com/api/v2/tasks/$TASK_ID" \
      -H "X-Browser-Use-API-Key: $API_KEY")
    
    STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
    
    echo "   Status: $STATUS"
    
    if [ "$STATUS" = "finished" ] || [ "$STATUS" = "failed" ] || [ "$STATUS" = "stopped" ]; then
        echo ""
        echo "🎉 Task complete!"
        echo ""
        
        OUTPUT=$(echo $STATUS_RESPONSE | jq -r '.output')
        IS_SUCCESS=$(echo $STATUS_RESPONSE | jq -r '.isSuccess')
        
        echo "Success: $IS_SUCCESS"
        echo "Output:"
        echo "$OUTPUT"
        echo ""
        
        if [ "$IS_SUCCESS" = "true" ]; then
            # Try to extract API key from output
            if echo "$OUTPUT" | grep -qiE '(api[_-]?key|sk-|leo_)'; then
                echo "🔑 Possible API key found in output!"
                echo ""
                
                # Save the full response
                echo "$STATUS_RESPONSE" | jq '.' > leonardo_api_key_response.json
                echo "💾 Full response saved to: leonardo_api_key_response.json"
            fi
        fi
        
        break
    fi
done
