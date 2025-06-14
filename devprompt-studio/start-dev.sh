#!/bin/bash
# Start development server

echo "Starting DevPrompt Studio development server..."
echo "Server will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Set environment variables
export NODE_ENV=development

# Start the development server
npm run dev