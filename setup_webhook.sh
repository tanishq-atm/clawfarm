#!/bin/bash
# Setup webhook infrastructure

echo "🚀 Setting up webhook infrastructure"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found"
    echo "   Install from: https://ngrok.com/download"
    echo "   Or: brew install ngrok (Mac)"
    echo "   Or: apt install ngrok (Linux)"
    exit 1
fi

echo "✅ ngrok found"
echo ""

# Install Playwright browsers if needed
echo "📦 Installing Playwright browsers..."
python -m playwright install chromium
echo ""

# Start webhook server in background
echo "🌐 Starting webhook server..."
python webhook_server.py &
WEBHOOK_PID=$!
echo "   PID: $WEBHOOK_PID"

# Wait for server to start
sleep 2

# Start ngrok tunnel
echo ""
echo "🌉 Starting ngrok tunnel..."
ngrok http 5000 > /dev/null &
NGROK_PID=$!
echo "   PID: $NGROK_PID"

# Wait for ngrok to start
sleep 3

# Get ngrok public URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Could not get ngrok URL"
    echo "   Check: http://localhost:4040"
    kill $WEBHOOK_PID 2>/dev/null
    kill $NGROK_PID 2>/dev/null
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Webhook Server: http://localhost:5000"
echo "Public URL: $NGROK_URL"
echo "Ngrok Dashboard: http://localhost:4040"
echo ""
echo "Add to .env:"
echo "WEBHOOK_URL=http://localhost:5000"
echo "NGROK_URL=$NGROK_URL"
echo ""
echo "To stop:"
echo "  kill $WEBHOOK_PID  # webhook server"
echo "  kill $NGROK_PID    # ngrok tunnel"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep script running
trap "kill $WEBHOOK_PID $NGROK_PID 2>/dev/null; echo ''; echo 'Stopped.'; exit 0" INT TERM

# Follow webhook server logs
tail -f /dev/null
