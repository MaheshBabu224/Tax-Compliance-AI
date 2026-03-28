#!/bin/bash

# Tax Compliance AI - Complete Startup Script
# This script sets up and runs the entire application

echo "╔══════════════════════════════════════════════╗"
echo "║   SatyaTax: Tax Compliance AI System         ║"
echo "║        Comprehensive Startup Script         ║"
echo "╚══════════════════════════════════════════════╝"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Create virtual environment if it doesn't exist
echo -e "\n${BLUE}[1/5]${NC} Setting up Python environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Step 2: Activate virtual environment
echo -e "\n${BLUE}[2/5]${NC} Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Step 3: Install dependencies
echo -e "\n${BLUE}[3/5]${NC} Installing dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 4: Generate dataset
echo -e "\n${BLUE}[4/5]${NC} Generating synthetic dataset..."
python generate_dataset.py
echo -e "${GREEN}✓ Dataset generated and model trained${NC}"

# Step 5: Start applications
echo -e "\n${BLUE}[5/5]${NC} Starting applications..."
echo -e "${YELLOW}Starting Backend API (Port 5000)...${NC}"
python backend/api.py &
API_PID=$!

sleep 2

echo -e "${YELLOW}Starting Frontend Dashboard (Port 8501)...${NC}"
streamlit run frontend/dashboard.py

# Cleanup
kill $API_PID 2>/dev/null

echo -e "\n${GREEN}Application shutdown complete${NC}"
