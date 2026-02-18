# Intelligent Production Scheduling System
## AI-Powered Manufacturing Optimization for Pune EV SUV Plant

[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini%20AI-blue)](https://ai.google.dev/)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)](https://streamlit.io/)

## 🎯 Overview

An intelligent production scheduling system that uses Google Gemini AI to optimize manufacturing operations for an EV SUV plant in Pune, India. The system handles real-time disruptions using multi-agent AI coordination.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
The `.env` file is already configured with your Gemini API key.

### 3. Run the Application
```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## 📊 Features

- **Multi-Agent AI System** with 7 specialized agents
- **Real-Time Monitoring** of 5 assembly lines
- **Scenario Management** (Demand Spike, Supply Delay, Equipment Failure)
- **AI Recommendations** with KPI impact predictions
- **Workforce Optimization** across 3 shifts
- **Supply Chain Tracking** with alternative supplier suggestions
- **Interactive Dashboard** with beautiful visualizations

## 🏭 Scenarios Handled

1. **Morning Demand Spike**: 500 High Range SUV order from Europe
2. **Semiconductor Delay**: 48-hour chip shipment delay
3. **Robot Breakdown**: Assembly line equipment failure

## 📈 Expected Outcomes

- 📈 **30%** Increased Production Efficiency
- ⏱️ **25%** Reduced Planning Time
- 🔧 **40%** Decreased Downtime
- 💰 **20%** Inventory Cost Savings

## 🏗️ Architecture

```
Multi-Agent System
├── Master Orchestrator Agent
├── Demand Forecasting Agent
├── Inventory Management Agent
├── Workforce Management Agent
├── Machine Management Agent
├── Supply Chain Agent
└── Production Optimization Agent
```

## 📁 Project Structure

```
capstone_project/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                           # Environment configuration
├── README.md                      # This file
├── src/
│   ├── agents/                    # Multi-agent system
│   ├── data/                      # Data processing
│   ├── utils/                     # Helper functions
│   └── ui/                        # Dashboard components
└── data/
    └── Pune_EV_SUV_Plant_Simulation_Data_Expanded.xlsx
```

## 🤖 AI Model

- **Model**: Google Gemini 1.5 Flash
- **Provider**: Google AI
- **Tier**: Free tier optimized
- **Features**: Function calling, JSON mode, long context

## 📝 License

MIT License - feel free to use for educational purposes.

## 👥 Authors

Capstone Project Team - Neural Newbies

---

**Built with ❤️ using Google Gemini AI**
