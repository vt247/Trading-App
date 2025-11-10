#!/bin/bash
# Wolf Market Analyzer - Setup Script

echo "🐺 Wolf Market Analyzer - Setup"
echo "================================"

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.9"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "❌ Python 3.9+ required. You have Python $python_version"
    exit 1
fi
echo "✓ Python $python_version detected"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys:"
    echo "   - BINANCE_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - TELEGRAM_BOT_TOKEN (optional)"
fi

# Create directories
echo ""
echo "Creating directories..."
mkdir -p charts data logs
echo "✓ Directories created"

# Make main.py executable
chmod +x main.py

echo ""
echo "================================"
echo "✓ Setup complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate venv: source venv/bin/activate"
echo "3. Run: python main.py --config"
echo ""
echo "Quick start:"
echo "  python main.py --brief              # Daily briefing"
echo "  python main.py --analyze BTC/USDT   # Analyze Bitcoin"
echo "  python main.py --scan               # Scan watchlist"
echo ""
