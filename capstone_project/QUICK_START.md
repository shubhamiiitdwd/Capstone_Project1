# 🚀 Quick Start Guide

## Installation & Running the Application

### Option 1: Using Batch Files (Windows - Easiest)

#### Step 1: Install Dependencies
Double-click `install.bat` or run:
```bash
install.bat
```

#### Step 2: Run the Application
Double-click `run.bat` or run:
```bash
run.bat
```

The application will open in your browser at `http://localhost:8501`

---

### Option 2: Manual Installation

#### Step 1: Install Requirements
```bash
pip install -r requirements.txt
```

#### Step 2: Run Streamlit App
```bash
streamlit run app.py
```

---

## 📋 What's Included

✅ **Complete Multi-Agent AI System** with 7 specialized agents:
- Master Orchestrator Agent (coordinates everything)
- Demand Forecasting Agent
- Inventory Management Agent
- Workforce Management Agent
- Machine Management Agent
- Supply Chain Agent
- Production Optimization Agent

✅ **Interactive Dashboard** with:
- Real-time KPI monitoring
- Assembly line status display
- Scenario management
- AI-powered recommendations
- Analytics and visualizations

✅ **Scenario Handling** for:
- Morning Demand Spike
- Semiconductor Delay
- Robot Breakdown

✅ **Powered by Google Gemini 1.5 Flash** (Free Tier)

---

## 🎯 How to Use

### 1. Dashboard Overview
When you first open the app, you'll see:
- **KPI Cards**: Production efficiency, planning time, downtime, inventory costs
- **Assembly Line Status**: Real-time status of all 5 lines
- **Production Charts**: Visualizations of key metrics

### 2. Analyze a Scenario
1. Go to the **"Scenario Management"** tab
2. Select a scenario from the dropdown
3. Click **"Analyze Scenario with AI"**
4. Wait for AI agents to analyze (takes 10-30 seconds)

### 3. View AI Recommendations
After analysis:
- Navigate to the **"AI Recommendations"** tab
- See executive summary
- Review critical issues
- Get prioritized actionable recommendations with KPI impact predictions

### 4. Explore Analytics
- Check the **"Analytics"** tab for:
  - Production trends over time
  - Correlation analysis
  - Quality metrics by line
  - Historical performance

---

## 🔧 Configuration

### API Key
Your Gemini API key is configured in `.env`:
```
GEMINI_API_KEY=AIzaSyAT3YNTPg3R5VztRNNV90wTfcb44bwPgPk
```

### Model Settings
The system uses:
- **Model**: gemini-1.5-flash (fast and free)
- **Temperature**: 0.7 (balanced creativity)
- **Max Tokens**: 8192

---

## 📊 Expected Results

After analyzing scenarios, you'll get:

### Critical Issues Detection
- Demand spikes
- Inventory shortages
- Worker availability problems
- Machine health concerns
- Supply chain risks

### AI Recommendations
Each recommendation includes:
- ⚠️ Priority level (High/Medium/Low)
- 📝 Clear action description
- 🤔 Reasoning/justification
- 📈 Predicted KPI impact
- ⏱️ Estimated execution time
- 👤 Source agent

### Example Recommendation:
```
Priority: 🔴 HIGH
Action: Extend Shift A by 3 hours for HighRange_1 and HighRange_2
Reasoning: Demand spike requires additional production capacity
KPI Impact: +8.5% production efficiency
Time: 2-4 hours
```

---

## 🎨 Dashboard Features

### Real-Time Monitoring
- Live assembly line status
- Color-coded alerts
- Production output tracking
- Machine uptime monitoring
- Worker availability by shift

### Scenario Simulation
- Pre-loaded scenarios from actual plant data
- AI analysis of disruptions
- Multiple recommendation options
- Impact predictions

### Analytics
- Historical trends
- Performance comparisons
- Correlation insights
- Quality metrics

---

## 🐛 Troubleshooting

### Issue: Dependencies not installing
**Solution**: 
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Issue: Gemini API errors
**Solution**: 
- Check your API key in `.env`
- Verify free tier limits (15 requests/minute)
- Wait a few seconds between requests

### Issue: Data file not found
**Solution**: 
- Ensure `Pune_EV_SUV_Plant_Simulation_Data_Expanded.xlsx` is in the project root
- Check the file name matches exactly

### Issue: Import errors
**Solution**:
```bash
# Make sure you're in the project directory
cd C:\Users\HP\Desktop\capstone_project

# Run from project root
streamlit run app.py
```

---

## 🎓 Understanding the System

### Multi-Agent Architecture
The system uses multiple AI agents that work together:

1. **Orchestrator** receives the scenario
2. **Specialized agents** analyze their domains:
   - Demand Agent → forecasts and detects spikes
   - Inventory Agent → checks stock levels
   - Workforce Agent → assesses worker availability
   - Machine Agent → monitors equipment health
   - Supply Chain Agent → tracks component availability
   - Production Agent → optimizes line allocation
3. **Orchestrator** combines all insights
4. **Gemini AI** generates comprehensive recommendations

### Why Gemini 1.5 Flash?
- ✅ **Free tier friendly** (generous limits)
- ✅ **Fast responses** (0.5-1 second)
- ✅ **High quality** reasoning
- ✅ **Long context** (handles complex scenarios)
- ✅ **JSON mode** for structured outputs

---

## 📈 Performance Expectations

### Response Times
- Data loading: < 2 seconds
- Dashboard rendering: < 1 second
- AI scenario analysis: 10-30 seconds (depends on complexity)
- Recommendation generation: 5-10 seconds

### AI Quality
- Accuracy: High (powered by Gemini 1.5)
- Reasoning: Comprehensive and logical
- Recommendations: Actionable and specific
- KPI predictions: Based on historical data patterns

---

## 💡 Tips for Best Results

1. **Let AI analyze fully**: Don't interrupt the analysis process
2. **Try different scenarios**: Each provides unique insights
3. **Review all recommendations**: Lower priority items can be valuable too
4. **Check the reasoning**: Understanding "why" helps with implementation
5. **Use Analytics tab**: Historical context improves decision-making

---

## 🎯 Next Steps

After exploring the dashboard:

1. **Customize scenarios**: Modify the data or add new scenarios
2. **Extend agents**: Add new specialized agents for specific needs
3. **Integrate with real systems**: Connect to actual plant data
4. **Export reports**: Use recommendations for actual planning
5. **Train team**: Show others how AI can optimize operations

---

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Review error messages in the terminal
3. Verify all dependencies are installed
4. Check Gemini API status

---

**Built with ❤️ using Google Gemini AI**

**Capstone Project 2026 | Neural Newbies**
