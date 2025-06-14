#!/bin/bash
# Push ProStudio to GitHub

cd /home/golde/prostudio

# Initialize git if not already done
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit: ProStudio zero-cost deployment"
fi

# Create the repository using gh CLI
gh repo create ProStudio --public --description "ProStudio Content Generation Platform - Zero Cost Deployment" --source=. --push

echo "✅ ProStudio pushed to GitHub!"
echo "Repository URL: https://github.com/nsfwhubinfo/ProStudio"