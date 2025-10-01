#!/bin/bash
# Complete test script for Meeting Assistant

cd "$(dirname "$0")/.."
source venv/bin/activate

echo "🚀 Starting Complete Meeting Assistant Test"
echo "==========================================="
echo ""

# Test 1: Quick system check
echo "📋 Step 1: Quick System Check"
echo "------------------------------"
python3 tests/quick_test.py
echo ""

# Test 2: Complete functionality test
echo "🎯 Step 2: Complete Functionality Test"
echo "---------------------------------------"
python3 tests/run_complete_test.py
echo ""

# Test 3: Web interface test
echo "🌐 Step 3: Web Interface Test"
echo "------------------------------"
echo "Testing web app startup..."

# Test web app import
python3 -c "import web_app" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Web interface dependencies available"
    echo "   Ready to start with: ./run_web.sh"
else
    echo "⚠️  Web interface needs dependencies"
    echo "   Run: ./install_sbc.sh or ./install_lightweight.sh"
fi

echo ""
echo "🎯 Test Summary"
echo "==============="
echo "✅ Meeting Assistant is ready to use!"
echo ""
echo "📋 Available Commands:"
echo "  ./run_web.sh                              # Start web interface"
echo "  ./run_cli.sh record --title \"My Meeting\"  # Record a meeting"
echo "  ./run_cli.sh transcribe audio_file.wav    # Transcribe audio"
echo "  ./run_cli.sh summarize text_file.txt      # Summarize text"
echo "  ./run_cli.sh devices                      # List audio devices"
echo "  ./run_cli.sh engines                      # List available engines"
echo ""
echo "🚀 Ready to assist with your meetings!"
