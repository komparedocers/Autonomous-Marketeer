#!/bin/bash

# Autonomous Marketeer Setup Script
# This script initializes the environment for first-time setup

echo "========================================="
echo "  Autonomous Marketeer - Setup"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "✓ Creating .env file from .env.example..."
    cp .env.example .env
    echo "  .env file created successfully!"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "========================================="
echo "  Configuration"
echo "========================================="
echo ""
echo "The system is configured with the following defaults:"
echo ""
echo "  LLM Provider: Local (Mistral-7B)"
echo "  API Gateway:  http://localhost:8080"
echo "  Dashboard:    http://localhost:5173"
echo "  Analytics:    http://localhost:8086"
echo "  Attribution:  http://localhost:8085"
echo ""
echo "Default Login:"
echo "  Email:    admin@demo.com"
echo "  Password: demo123"
echo ""
echo "========================================="
echo "  Optional Configuration"
echo "========================================="
echo ""
echo "To enable OpenAI (optional):"
echo "  1. Edit .env file"
echo "  2. Set OPENAI_ENABLED=true"
echo "  3. Add your OPENAI_API_KEY=sk-..."
echo ""
echo "========================================="
echo "  Starting Services"
echo "========================================="
echo ""
echo "Run the following command to start all services:"
echo ""
echo "  docker-compose up --build"
echo ""
echo "Or in detached mode:"
echo ""
echo "  docker-compose up -d --build"
echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
