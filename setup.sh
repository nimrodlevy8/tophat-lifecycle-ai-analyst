#!/bin/bash
# Setup script for BigQuery AI Agent

echo "🚀 BigQuery AI Agent Setup"
echo "================================"

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env exists
echo ""
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your credentials:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - GCP_PROJECT_ID"
    echo "   - GOOGLE_APPLICATION_CREDENTIALS"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the agent:"
echo "   python3 bigquery_agent.py"
echo ""
echo "4. Or try the examples:"
echo "   python3 example_queries.py"
echo ""
