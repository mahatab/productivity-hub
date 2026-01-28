#!/bin/bash
# Share Productivity Hub via ngrok tunnel
# Creates a temporary public URL

echo "🌐 Starting Productivity Hub with ngrok tunnel..."
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found!"
    echo ""
    echo "Install ngrok:"
    echo "  brew install ngrok"
    echo "  OR download from: https://ngrok.com/download"
    echo ""
    exit 1
fi

# Check if server is running on 8080
if ! lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  No server running on port 8080"
    echo ""
    echo "Start the server first:"
    echo "  python3 -m http.server 8080"
    echo ""
    exit 1
fi

echo "✅ Server detected on port 8080"
echo "🚀 Creating public tunnel..."
echo ""
echo "📱 Share this URL with anyone to access your dashboard:"
echo "   (URL will appear below)"
echo ""
echo "⚠️  WARNING: Anyone with this URL can access your dashboard!"
echo "   Press Ctrl+C to stop sharing"
echo ""

# Start ngrok tunnel
ngrok http 8080
