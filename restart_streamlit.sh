#!/bin/bash

echo "🔄 Restarting Streamlit with fresh imports..."

# Step 1: Kill existing Streamlit process
echo "1️⃣ Stopping Streamlit..."
pkill -f "streamlit run app.py"
sleep 2

# Step 2: Clear Python cache
echo "2️⃣ Clearing Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Step 3: Verify imports work
echo "3️⃣ Verifying imports..."
python -c "from src.analyzer import RiskTriageEngine; print('✓ RiskTriageEngine import successful')" || {
    echo "❌ Import failed! Check src/analyzer.py"
    exit 1
}

# Step 4: Restart Streamlit
echo "4️⃣ Starting Streamlit..."
streamlit run app.py

echo "✅ Done!"
