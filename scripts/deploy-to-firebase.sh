#!/bin/bash
# Auto-deploy to Firebase after updates
# Usage: ./deploy-to-firebase.sh "Optional commit message"

cd "$(dirname "$0")/.."

# Default message
MESSAGE="${1:-Update tasks and jobs}"

echo "🚀 Deploying updates to Firebase..."
echo ""

# Git commit and push (if changes exist)
if ! git diff-index --quiet HEAD --; then
    echo "📝 Committing changes to Git..."
    git add .
    git commit -m "$MESSAGE"
    git push origin main
    echo "✅ Pushed to GitHub"
    echo ""
fi

# Deploy to Firebase
echo "🔥 Deploying to Firebase..."
firebase deploy --only hosting

echo ""
echo "✅ Deployment complete!"
echo "🌐 Live at: https://productivity-hub-mahatab.web.app"
echo ""
