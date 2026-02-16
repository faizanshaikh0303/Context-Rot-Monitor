#!/bin/bash
# Setup script for Context Rot Monitor

echo "🔧 Setting up Context Rot Monitor..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install -q sentence-transformers groq fastapi uvicorn python-dotenv --break-system-packages

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Get your Groq API key from: https://console.groq.com/keys"
echo "2. Create backend/.env file with: GROQ_API_KEY=your_key"
echo "3. Run backend: python backend/main.py"
echo "4. Load Chrome extension from: extension/"
