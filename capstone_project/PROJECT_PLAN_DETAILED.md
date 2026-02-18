# Intelligent Production Scheduling System - Detailed Implementation Plan
## AI-Powered Manufacturing Optimization for Pune EV SUV Plant

---

## 📋 TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Project Overview](#project-overview)
3. [System Architecture](#system-architecture)
4. [Multi-LLM Provider Integration](#multi-llm-provider-integration)
5. [Detailed Implementation Phases](#detailed-implementation-phases)
6. [Technology Stack](#technology-stack)
7. [Data Schema & Processing](#data-schema--processing)
8. [Multi-Agent AI System Design](#multi-agent-ai-system-design)
9. [Dashboard & UI Specifications](#dashboard--ui-specifications)
10. [API Specifications](#api-specifications)
11. [Testing Strategy](#testing-strategy)
12. [Deployment Guide](#deployment-guide)
13. [Expected Outcomes](#expected-outcomes)

---

## 🎯 EXECUTIVE SUMMARY

### Project Goal
Build an **Intelligent Production Scheduling System** that combines **Agentic AI** and **Generative AI** to optimize production scheduling for a Pune-based EV SUV manufacturing plant, handling real-time disruptions and maximizing operational efficiency.

### Key Metrics to Achieve
- 📈 **30%** Increased Production Efficiency
- ⏱️ **25%** Reduced Planning Time
- 🔧 **40%** Decreased Downtime
- 💰 **20%** Inventory Cost Savings

### Core Capabilities
- Real-time disruption handling (demand spikes, supply delays, equipment failures)
- Multi-agent collaborative decision-making
- Scenario simulation with multiple LLM providers
- Predictive KPI impact analysis
- Automated workforce and resource optimization

---

## 🏗️ PROJECT OVERVIEW

### Manufacturing Plant Context
- **Location**: Pune, India
- **Product**: EV SUVs (High Range & Medium Range)
- **Assembly Lines**: 5 lines (HighRange_1, HighRange_2, MediumRange_1, MediumRange_2, MediumRange_3)
- **Shifts**: 3 shifts (A, B, C) operating 24/7
- **Components**: Centralized Inventory, Machine Parameters, Shift Management

### Critical Scenarios to Handle

#### Scenario 1: Morning Sudden Demand Spike
- **Trigger**: Europe dealer requests 500 High Range EV SUVs
- **Challenge**: Immediate production planning required
- **AI Expectation**: Optimize shifts, inventory, and assembly lines without impacting medium-range production

#### Scenario 2: Mid-Day Semiconductor Delay
- **Trigger**: Chip shipment delayed by 48 hours
- **Challenge**: High Range SUV assembly line affected
- **AI Expectation**: Generate alternative solutions (accelerate models, alternate suppliers, swap line sequences)

#### Scenario 3: Afternoon Robot Breakdown
- **Trigger**: Assembly line robot malfunction
- **Challenge**: Risk of missing High Range SUV target
- **AI Expectation**: Workload optimization, assembly line swaps, alert notifications to all teams

### Dataset Overview
- **Records**: 500 simulation data points
- **Features**: 16 columns covering demand, inventory, machine status, workforce, production metrics, and AI recommendations
- **Time Period**: Hourly data starting November 2025
- **Scenarios Covered**: All three disruption types with various parameters

---

## 🏛️ SYSTEM ARCHITECTURE

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Web UI     │  │  Dashboard   │  │   Mobile View        │ │
│  │  (React.js)  │  │  (Streamlit) │  │   (Responsive)       │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │   REST API (FastAPI/Flask)                               │  │
│  │   - Authentication & Authorization                        │  │
│  │   - Rate Limiting                                         │  │
│  │   - WebSocket for Real-time Updates                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              LLM PROVIDER MANAGER                       │    │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────────┐  │    │
│  │  │ OpenAI   │  │  Gemini  │  │  Hugging Face       │  │    │
│  │  │  GPT-4   │  │  Flash   │  │  (Llama/Mistral)    │  │    │
│  │  └──────────┘  └──────────┘  └─────────────────────┘  │    │
│  │              [Dynamic Switching Logic]                  │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         MULTI-AGENT ORCHESTRATION SYSTEM               │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │  Master Orchestrator Agent                       │  │    │
│  │  │  - Coordinates all sub-agents                    │  │    │
│  │  │  - Makes holistic decisions                      │  │    │
│  │  │  - Scenario simulation & optimization            │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────┐│    │
│  │  │Demand  │ │Inventor│ │Workforc│ │Machine │ │Supply││    │
│  │  │Forecas │ │y Mgmt  │ │e Mgmt  │ │Mgmt    │ │Chain ││    │
│  │  │t Agent │ │Agent   │ │Agent   │ │Agent   │ │Agent ││    │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └──────┘│    │
│  │  └──────────────────────┬──────────────────────────┘  │    │
│  │                         │                              │    │
│  │  ┌──────────────────────▼──────────────────────────┐  │    │
│  │  │     Production Optimization Agent               │  │    │
│  │  │     - Line balancing & scheduling               │  │    │
│  │  └─────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Database   │  │  Cache Layer │  │   File Storage       │ │
│  │ (PostgreSQL/ │  │   (Redis)    │  │   (Excel/CSV)        │ │
│  │   SQLite)    │  │              │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 MULTI-LLM PROVIDER INTEGRATION

### Overview
The system supports **three LLM providers** with dynamic switching capability, allowing flexibility in cost, performance, and availability.

### Supported Providers

#### 1. **OpenAI (GPT-4 / GPT-4 Turbo)**
- **Pros**: Most advanced reasoning, best for complex multi-agent coordination
- **Cons**: Higher cost, API dependency
- **Use Cases**: Critical scenario planning, complex optimization
- **API**: OpenAI API with function calling

#### 2. **Google Gemini (Gemini Pro / Gemini Flash)**
- **Pros**: Fast inference, good reasoning, multimodal support
- **Cons**: Moderate cost, rate limits
- **Use Cases**: Real-time recommendations, quick scenario analysis
- **API**: Google Generative AI API

#### 3. **Hugging Face (Open Source Models)**
- **Models**: 
  - Llama 3.1 (8B, 70B)
  - Mistral 7B / Mixtral 8x7B
  - Qwen 2.5
- **Pros**: No API costs, full control, privacy
- **Cons**: Requires GPU, slower inference for large models
- **Use Cases**: Offline mode, cost-sensitive deployments
- **Deployment**: Local inference or Hugging Face Inference API

### LLM Provider Manager Architecture

```python
# Conceptual Structure

class LLMProviderManager:
    """
    Manages multiple LLM providers with dynamic switching
    """
    
    providers = {
        'openai': OpenAIProvider(),
        'gemini': GeminiProvider(),
        'huggingface': HuggingFaceProvider()
    }
    
    def __init__(self, default_provider='openai'):
        self.active_provider = default_provider
        self.fallback_order = ['openai', 'gemini', 'huggingface']
        
    def switch_provider(self, provider_name):
        """Switch to a different LLM provider"""
        
    def generate_response(self, prompt, temperature=0.7):
        """Generate response with automatic fallback"""
        
    def get_provider_status(self):
        """Check availability and health of all providers"""
```

### Configuration Structure

```yaml
# config/llm_config.yaml

llm_providers:
  
  openai:
    enabled: true
    api_key: ${OPENAI_API_KEY}
    model: "gpt-4-turbo"
    temperature: 0.7
    max_tokens: 4096
    timeout: 30
    retry_attempts: 3
    
  gemini:
    enabled: true
    api_key: ${GEMINI_API_KEY}
    model: "gemini-1.5-pro"
    temperature: 0.7
    max_tokens: 8192
    timeout: 30
    retry_attempts: 3
    
  huggingface:
    enabled: true
    api_key: ${HUGGINGFACE_API_KEY}  # Optional, for Inference API
    deployment_mode: "local"  # or "api"
    model: "meta-llama/Meta-Llama-3.1-8B-Instruct"
    device: "cuda"  # or "cpu"
    temperature: 0.7
    max_tokens: 4096
    quantization: "4bit"  # For memory efficiency
    
  # Provider Selection Strategy
  selection:
    default: "openai"
    fallback_order: ["openai", "gemini", "huggingface"]
    auto_fallback: true
    
  # Cost Optimization
  cost_optimization:
    enabled: true
    use_cheaper_for_simple_tasks: true
    task_complexity_threshold: 0.5
    provider_cost_ranking: ["huggingface", "gemini", "openai"]
```

### Provider Switching Logic

```python
# Automatic Provider Selection Based on Task

task_to_provider_mapping = {
    # Complex tasks -> GPT-4
    'scenario_simulation': 'openai',
    'multi_agent_coordination': 'openai',
    'complex_optimization': 'openai',
    
    # Moderate tasks -> Gemini
    'recommendation_generation': 'gemini',
    'kpi_prediction': 'gemini',
    'alert_classification': 'gemini',
    
    # Simple tasks -> Hugging Face (cost-effective)
    'text_summarization': 'huggingface',
    'data_extraction': 'huggingface',
    'simple_classification': 'huggingface'
}
```

### Provider-Specific Features

#### OpenAI Integration
```python
# Function Calling for Structured Outputs
functions = [
    {
        "name": "generate_production_schedule",
        "description": "Generate optimized production schedule",
        "parameters": {
            "type": "object",
            "properties": {
                "assembly_line": {"type": "string"},
                "shift": {"type": "string"},
                "recommended_output": {"type": "integer"},
                "kpi_impact": {"type": "number"}
            }
        }
    }
]
```

#### Gemini Integration
```python
# Multimodal Support (future enhancement)
# Can process images of plant floor, equipment status displays
model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content([
    "Analyze this production floor layout",
    image_data
])
```

#### Hugging Face Integration
```python
# Local Inference with Quantization
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    quantization_config=quantization_config,
    device_map="auto"
)
```

### Dashboard Provider Switcher UI

```
┌─────────────────────────────────────────────────────────┐
│  LLM Provider Settings                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Active Provider:  [●] OpenAI   [ ] Gemini   [ ] HF   │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Provider     Status      Latency    Cost/1K      │ │
│  │ OpenAI       ● Online    0.8s       $0.03        │ │
│  │ Gemini       ● Online    0.5s       $0.015       │ │
│  │ HuggingFace  ● Online    1.2s       $0.00        │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Auto-Fallback: [✓] Enabled                            │
│  Cost Optimization: [✓] Enabled                        │
│                                                         │
│  [Switch Provider]  [Test Connection]  [View Logs]     │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 DETAILED IMPLEMENTATION PHASES

### **PHASE 1: PROJECT SETUP & FOUNDATION** (3-4 hours)

#### 1.1 Environment Setup

**Tasks:**
- Create virtual environment with Python 3.10+
- Install core dependencies
- Set up version control (Git)
- Configure development environment

**Deliverables:**
```
capstone_project/
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── config/
│   ├── llm_config.yaml          # LLM provider settings
│   ├── app_config.yaml          # Application settings
│   └── database_config.yaml     # Database configuration
├── data/
│   ├── raw/                     # Raw Excel files
│   ├── processed/               # Processed data
│   └── models/                  # Trained ML models
├── src/
│   ├── __init__.py
│   ├── agents/                  # Multi-agent system
│   ├── api/                     # REST API
│   ├── dashboard/               # Frontend UI
│   ├── llm_providers/           # LLM integrations
│   ├── models/                  # Data models
│   ├── services/                # Business logic
│   └── utils/                   # Helper functions
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   ├── architecture.md
│   ├── api_documentation.md
│   └── user_guide.md
├── notebooks/                    # Jupyter notebooks for analysis
├── scripts/                      # Utility scripts
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
└── README.md
```

#### 1.2 Dependencies Installation

**Core Dependencies:**
```txt
# requirements.txt

# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
flask==3.0.0
streamlit==1.30.0

# LLM Providers
openai==1.10.0
google-generativeai==0.3.2
transformers==4.37.0
torch==2.2.0
accelerate==0.26.0
bitsandbytes==0.42.0

# Data Processing
pandas==2.2.0
numpy==1.26.3
openpyxl==3.1.2
sqlalchemy==2.0.25

# ML & AI
scikit-learn==1.4.0
langchain==0.1.4
langchain-openai==0.0.5
langchain-google-genai==0.0.6

# Visualization
plotly==5.18.0
matplotlib==3.8.2
seaborn==0.13.1

# API & Communication
requests==2.31.0
websockets==12.0
redis==5.0.1

# Utilities
python-dotenv==1.0.1
pydantic==2.5.3
pyyaml==6.0.1
python-multipart==0.0.6

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0

# Deployment
gunicorn==21.2.0
docker==7.0.0
```

#### 1.3 Configuration Files Setup

**Environment Variables (.env):**
```bash
# LLM API Keys
OPENAI_API_KEY=sk-xxx
GEMINI_API_KEY=xxx
HUGGINGFACE_API_KEY=hf_xxx

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/production_db
REDIS_URL=redis://localhost:6379

# Application
APP_ENV=development
DEBUG_MODE=True
SECRET_KEY=your-secret-key

# LLM Settings
DEFAULT_LLM_PROVIDER=openai
ENABLE_AUTO_FALLBACK=True
ENABLE_COST_OPTIMIZATION=True
```

---

### **PHASE 2: DATA PROCESSING & ANALYSIS MODULE** (2-3 hours)

#### 2.1 Data Ingestion Pipeline

**File: `src/data/data_loader.py`**

**Features:**
- Load Excel data with validation
- Handle missing values
- Data type conversions
- Timestamp parsing
- Scenario classification

**Key Functions:**
```python
class DataLoader:
    def load_excel_data(file_path: str) -> pd.DataFrame
    def validate_data(df: pd.DataFrame) -> Dict[str, Any]
    def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame
    def classify_scenarios(df: pd.DataFrame) -> pd.DataFrame
    def save_processed_data(df: pd.DataFrame, output_path: str)
```

**Data Validation Rules:**
- Check for required columns
- Validate data ranges (e.g., percentages 0-100)
- Ensure chronological date ordering
- Verify assembly line and shift codes
- Flag anomalies in production output

#### 2.2 Exploratory Data Analysis (EDA)

**File: `notebooks/01_exploratory_analysis.ipynb`**

**Analysis Components:**

1. **Descriptive Statistics**
   - Mean, median, std dev for all numeric columns
   - Distribution of demand across scenarios
   - Production output patterns by assembly line and shift

2. **Correlation Analysis**
   - Machine uptime vs. production output
   - Worker availability vs. defect rate
   - Inventory status vs. KPI impact
   - Energy consumption vs. production volume

3. **Time Series Analysis**
   - Hourly production trends
   - Shift-wise performance comparison
   - Scenario progression over time

4. **Disruption Pattern Analysis**
   - Alert frequency by scenario type
   - Semiconductor availability impact
   - Machine downtime patterns

5. **KPI Impact Analysis**
   - Predicted vs. actual KPI improvements
   - Recommendation effectiveness
   - Success rate of different AI recommendations

**Visualizations to Generate:**
- Production output heatmap by line and shift
- Defect rate trends over time
- Energy consumption vs. output scatter plot
- Alert status distribution pie chart
- KPI impact histogram
- Scenario comparison box plots

#### 2.3 Feature Engineering

**File: `src/data/feature_engineering.py`**

**New Features to Create:**

1. **Efficiency Metrics**
   - `production_efficiency = (actual_output / demand) * 100`
   - `resource_utilization = (machine_uptime + worker_availability) / 2`
   - `quality_score = 100 - defect_rate`

2. **Trend Indicators**
   - `output_trend = current_output - rolling_avg_output`
   - `demand_volatility = std_dev(demand_last_24h)`
   - `uptime_stability = 1 / std_dev(uptime_last_24h)`

3. **Risk Scores**
   - `supply_risk = f(semiconductor_availability, inventory_status)`
   - `production_risk = f(machine_uptime, worker_availability, defect_rate)`
   - `delay_risk = f(demand, output, inventory)`

4. **Temporal Features**
   - `hour_of_day`, `day_of_week`, `shift_number`
   - `is_peak_demand_period`
   - `time_since_last_alert`

5. **Aggregated Features**
   - `total_plant_output = sum(all_lines_output)`
   - `average_line_efficiency`
   - `total_energy_per_unit = energy_consumption / production_output`

---

### **PHASE 3: MULTI-AGENT AI SYSTEM** (5-6 hours)

#### 3.1 Base Agent Architecture

**File: `src/agents/base_agent.py`**

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from src.llm_providers.llm_manager import LLMProviderManager

class BaseAgent(ABC):
    """
    Abstract base class for all agents
    """
    
    def __init__(self, name: str, llm_manager: LLMProviderManager):
        self.name = name
        self.llm_manager = llm_manager
        self.memory = []  # Conversation history
        self.tools = []   # Agent-specific tools
        
    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the given context and return insights"""
        pass
        
    @abstractmethod
    def recommend(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis"""
        pass
        
    def add_to_memory(self, interaction: Dict[str, Any]):
        """Store interaction in agent memory"""
        self.memory.append(interaction)
        
    def get_memory_context(self, last_n: int = 5) -> str:
        """Retrieve last N interactions for context"""
        return "\n".join([str(m) for m in self.memory[-last_n:]])
```

#### 3.2 Demand Forecasting Agent

**File: `src/agents/demand_agent.py`**

**Responsibilities:**
- Monitor demand patterns from historical data
- Predict future demand using time-series analysis
- Detect demand spikes and anomalies
- Generate early warning alerts

**Key Methods:**
```python
class DemandForecastingAgent(BaseAgent):
    
    def analyze(self, context: Dict) -> Dict:
        """
        Analyze demand patterns and forecast future demand
        
        Returns:
        - current_demand: Current demand across all lines
        - forecasted_demand: Next 24h demand prediction
        - demand_trend: Increasing/Decreasing/Stable
        - anomaly_detected: Boolean flag
        - confidence_level: 0-1 score
        """
        
    def recommend(self, analysis: Dict) -> List[Dict]:
        """
        Generate demand-related recommendations
        
        Recommendations:
        - Prepare for demand spike
        - Reduce production rate
        - Shift inventory allocation
        - Alert planning team
        """
        
    def detect_spike(self, current_demand: int, historical_avg: float) -> bool:
        """Detect if current demand is a spike (>2 std dev)"""
        
    def forecast_next_period(self, historical_data: pd.DataFrame) -> Dict:
        """Use ARIMA/Prophet for demand forecasting"""
```

**LLM Prompt Template:**
```python
DEMAND_ANALYSIS_PROMPT = """
You are a Demand Forecasting Agent for an EV SUV manufacturing plant.

Current Context:
- Current Demand: {current_demand} SUVs
- Historical Average: {historical_avg} SUVs
- Demand Trend: {trend}
- Scenario: {scenario_type}

Recent Demand History:
{demand_history}

Analyze the demand pattern and provide:
1. Is this a demand spike or normal variation?
2. What is the predicted demand for the next 24 hours?
3. What preparation steps should be taken?
4. Risk level (Low/Medium/High)

Provide your analysis in JSON format.
"""
```

#### 3.3 Inventory Management Agent

**File: `src/agents/inventory_agent.py`**

**Responsibilities:**
- Track inventory levels across all lines
- Optimize inventory allocation
- Predict stockout risks
- Suggest reordering points

**Key Methods:**
```python
class InventoryManagementAgent(BaseAgent):
    
    def analyze(self, context: Dict) -> Dict:
        """
        Analyze inventory status
        
        Returns:
        - current_inventory_levels: Dict by assembly line
        - critical_items: List of low-stock items
        - allocation_efficiency: 0-100 score
        - reorder_recommendations: List of items to reorder
        """
        
    def recommend(self, analysis: Dict) -> List[Dict]:
        """
        Generate inventory recommendations
        
        Recommendations:
        - Reallocate inventory from Line X to Line Y
        - Trigger emergency reorder for component Z
        - Reduce inventory holding for overstock items
        """
        
    def calculate_safety_stock(self, demand_volatility: float) -> int:
        """Calculate safety stock level"""
        
    def optimize_allocation(self, demands: Dict, inventory: Dict) -> Dict:
        """Optimize inventory allocation across lines"""
```

#### 3.4 Workforce Management Agent

**File: `src/agents/workforce_agent.py`**

**Responsibilities:**
- Monitor worker availability across shifts
- Optimize shift schedules
- Suggest overtime or shift swaps
- Balance workload across assembly lines

**Key Methods:**
```python
class WorkforceManagementAgent(BaseAgent):
    
    def analyze(self, context: Dict) -> Dict:
        """
        Analyze workforce availability and efficiency
        
        Returns:
        - shift_availability: Dict by shift (A, B, C)
        - understaffed_lines: List of lines needing more workers
        - overtime_requirements: Hours needed
        - skill_gaps: Areas lacking skilled workers
        """
        
    def recommend(self, analysis: Dict) -> List[Dict]:
        """
        Generate workforce recommendations
        
        Recommendations:
        - Move workers from Line X to Line Y
        - Extend Shift A by 2 hours
        - Call in backup workers for Shift B
        - Cross-train workers for flexibility
        """
        
    def calculate_optimal_shift_size(self, production_target: int) -> Dict:
        """Calculate optimal number of workers per shift"""
        
    def suggest_shift_swap(self, current_schedule: Dict, demand: Dict) -> Dict:
        """Suggest shift adjustments based on demand"""
```

#### 3.5 Machine Management Agent

**File: `src/agents/machine_agent.py`**

**Responsibilities:**
- Monitor machine uptime and health
- Predict equipment failures
- Schedule preventive maintenance
- Optimize machine utilization

**Key Methods:**
```python
class MachineManagementAgent(BaseAgent):
    
    def analyze(self, context: Dict) -> Dict:
        """
        Analyze machine status and predict failures
        
        Returns:
        - machine_health_scores: Dict by assembly line
        - failure_predictions: List of at-risk machines
        - maintenance_schedule: Recommended maintenance times
        - uptime_trends: Improving/Declining
        """
        
    def recommend(self, analysis: Dict) -> List[Dict]:
        """
        Generate machine management recommendations
        
        Recommendations:
        - Schedule maintenance for Line X during low-demand shift
        - Replace critical component on Line Y
        - Reduce production rate on Line Z due to wear
        - Alert maintenance team for inspection
        """
        
    def predict_failure(self, uptime_history: List[float]) -> Dict:
        """Predict probability of machine failure"""
        
    def optimize_maintenance_schedule(self, production_schedule: Dict) -> Dict:
        """Schedule maintenance to minimize production impact"""
```

#### 3.6 Supply Chain Management Agent

**File: `src/agents/supply_chain_agent.py`**

**Responsibilities:**
- Track component availability (semiconductors, batteries, etc.)
- Monitor supplier delivery status
- Identify alternative suppliers
- Manage supply chain disruptions

**Key Methods:**
```python
class SupplyChainAgent(BaseAgent):
    
    def analyze(self, context: Dict) -> Dict:
        """
        Analyze supply chain status
        
        Returns:
        - component_availability: Dict by component type
        - delayed_shipments: List of delayed deliveries
        - supplier_reliability: Scores by supplier
        - supply_risk_level: Low/Medium/High
        """
        
    def recommend(self, analysis: Dict) -> List[Dict]:
        """
        Generate supply chain recommendations
        
        Recommendations:
        - Switch to alternative supplier for chips
        - Expedite shipment for critical components
        - Adjust production schedule to match supply
        - Buffer inventory for high-risk components
        """
        
    def find_alternative_suppliers(self, component: str, urgency: str) -> List[Dict]:
        """Find alternative suppliers for a component"""
        
    def estimate_delay_impact(self, delayed_component: str, delay_hours: int) -> Dict:
        """Estimate production impact of supply delay"""
```

#### 3.7 Production Optimization Agent

**File: `src/agents/production_agent.py`**

**Responsibilities:**
- Balance production across assembly lines
- Minimize defect rates and energy consumption
- Maximize throughput and efficiency
- Optimize line sequencing

**Key Methods:**
```python
class ProductionOptimizationAgent(BaseAgent):
    
    def analyze(self, context: Dict) -> Dict:
        """
        Analyze production efficiency
        
        Returns:
        - line_utilization: Dict by assembly line
        - bottleneck_lines: Lines limiting overall output
        - energy_efficiency: kWh per unit produced
        - quality_metrics: Defect rates by line
        """
        
    def recommend(self, analysis: Dict) -> List[Dict]:
        """
        Generate production optimization recommendations
        
        Recommendations:
        - Swap production between lines for better balance
        - Reduce speed on Line X to improve quality
        - Increase output on underutilized Line Y
        - Optimize batch sizes for energy efficiency
        """
        
    def optimize_line_allocation(self, demands: Dict, capacities: Dict) -> Dict:
        """Allocate production optimally across lines"""
        
    def minimize_defect_rate(self, production_params: Dict) -> Dict:
        """Suggest parameters to minimize defects"""
```

#### 3.8 Master Orchestrator Agent

**File: `src/agents/orchestrator.py`**

**Responsibilities:**
- Coordinate all sub-agents
- Make holistic decisions considering all factors
- Simulate multiple scenarios using Gen AI
- Generate comprehensive action plans
- Resolve conflicts between agent recommendations

**Key Methods:**
```python
class MasterOrchestratorAgent(BaseAgent):
    
    def __init__(self, llm_manager: LLMProviderManager):
        super().__init__("Master Orchestrator", llm_manager)
        self.sub_agents = {
            'demand': DemandForecastingAgent(llm_manager),
            'inventory': InventoryManagementAgent(llm_manager),
            'workforce': WorkforceManagementAgent(llm_manager),
            'machine': MachineManagementAgent(llm_manager),
            'supply_chain': SupplyChainAgent(llm_manager),
            'production': ProductionOptimizationAgent(llm_manager)
        }
        
    def analyze(self, context: Dict) -> Dict:
        """
        Coordinate analysis from all sub-agents
        
        Returns:
        - comprehensive_analysis: Aggregated insights
        - conflicting_recommendations: List of conflicts
        - priority_actions: Top 5 critical actions
        - scenario_type: Identified scenario
        """
        
    def recommend(self, analysis: Dict) -> List[Dict]:
        """
        Generate master action plan
        
        Returns:
        - orchestrated_recommendations: Unified action plan
        - execution_sequence: Ordered list of actions
        - expected_kpi_impact: Predicted improvements
        - risk_mitigation: Contingency plans
        """
        
    def simulate_scenarios(self, current_state: Dict, num_scenarios: int) -> List[Dict]:
        """
        Use Generative AI to simulate multiple scenarios
        
        Generate alternative futures based on different actions
        """
        
    def resolve_conflicts(self, recommendations: List[Dict]) -> List[Dict]:
        """
        Resolve conflicting recommendations from sub-agents
        
        Use LLM to reason about trade-offs and priorities
        """
        
    def execute_action_plan(self, action_plan: Dict) -> Dict:
        """
        Coordinate execution of the action plan
        Monitor progress and adjust as needed
        """
```

**Orchestrator LLM Prompt Template:**
```python
ORCHESTRATOR_PROMPT = """
You are the Master Orchestrator Agent coordinating a manufacturing plant's response to a disruption.

Scenario: {scenario_type}
Current Time: {timestamp}

Sub-Agent Reports:
1. Demand Forecasting Agent:
{demand_report}

2. Inventory Management Agent:
{inventory_report}

3. Workforce Management Agent:
{workforce_report}

4. Machine Management Agent:
{machine_report}

5. Supply Chain Agent:
{supply_chain_report}

6. Production Optimization Agent:
{production_report}

Your task:
1. Analyze all reports and identify the critical issues
2. Resolve any conflicting recommendations
3. Create a prioritized action plan with execution sequence
4. Predict the KPI impact of your plan (production efficiency, downtime, costs)
5. Identify risks and create contingency plans

Provide your orchestrated plan in JSON format with the following structure:
{{
  "critical_issues": [...],
  "action_plan": [
    {{
      "action": "...",
      "priority": 1-5,
      "responsible_agent": "...",
      "execution_time": "...",
      "expected_impact": "..."
    }}
  ],
  "kpi_predictions": {{
    "production_efficiency_change": "%",
    "downtime_reduction": "%",
    "cost_impact": "$"
  }},
  "risks": [...],
  "contingency_plans": [...]
}}
"""
```

---

### **PHASE 4: GENERATIVE AI INTEGRATION** (2-3 hours)

#### 4.1 Scenario Simulation Engine

**File: `src/generative_ai/scenario_simulator.py`**

**Purpose:**
Use Generative AI to create multiple "what-if" scenarios and simulate outcomes

**Key Features:**
```python
class ScenarioSimulator:
    
    def generate_alternative_scenarios(
        self, 
        base_scenario: Dict, 
        num_scenarios: int = 5
    ) -> List[Dict]:
        """
        Generate multiple alternative scenarios
        
        Example:
        Base: "Semiconductor delayed by 48h"
        
        Alternatives:
        1. Switch to alternative supplier (delivery in 24h)
        2. Accelerate production of models not needing that chip
        3. Swap assembly lines to continue production
        4. Use buffer inventory from another plant
        5. Negotiate expedited shipping with current supplier
        """
        
    def simulate_scenario_outcome(self, scenario: Dict) -> Dict:
        """
        Simulate the outcome of a given scenario
        
        Returns:
        - production_output: Predicted units produced
        - kpi_impacts: Changes in efficiency, downtime, costs
        - timeline: Hour-by-hour progression
        - success_probability: 0-1 score
        """
        
    def compare_scenarios(self, scenarios: List[Dict]) -> Dict:
        """
        Compare multiple scenarios side-by-side
        
        Returns ranked list with trade-off analysis
        """
```

**Simulation Prompt Template:**
```python
SIMULATION_PROMPT = """
You are a scenario simulation engine for manufacturing operations.

Base Scenario:
{base_scenario_description}

Current Plant State:
- Assembly Lines: {assembly_lines_status}
- Inventory: {inventory_levels}
- Workforce: {workforce_availability}
- Demand: {current_demand}

Generate {num_scenarios} alternative scenarios to handle this situation.
For each scenario, provide:
1. Description of the alternative approach
2. Required actions and resources
3. Timeline for execution
4. Predicted production output
5. KPI impacts (efficiency, downtime, cost)
6. Risk level and potential complications
7. Success probability (0-1)

Format your response as a JSON array of scenarios.
"""
```

#### 4.2 Natural Language Recommendation System

**File: `src/generative_ai/nl_recommender.py`**

**Purpose:**
Convert technical AI recommendations into clear, actionable natural language

**Key Features:**
```python
class NaturalLanguageRecommender:
    
    def generate_executive_summary(self, analysis: Dict) -> str:
        """
        Generate a clear executive summary
        
        Example Output:
        "Critical Alert: Morning Demand Spike Detected
        
        A European dealer has requested 500 High Range EV SUVs, 
        representing a 180% increase from normal demand. 
        
        Our AI system recommends:
        1. Extend Shift A by 3 hours (adds 120 units capacity)
        2. Reallocate 40% of MediumRange_2 line to HighRange production
        3. Call in 15 backup workers with High Range certification
        
        Expected Impact: Meet 92% of demand with 8% overflow to next week
        Downtime: Minimal (<5%)
        Additional Cost: $12,000 (overtime + expedited materials)"
        """
        
    def explain_recommendation(self, recommendation: Dict) -> str:
        """
        Explain the reasoning behind a recommendation
        
        Example:
        "We recommend switching Line 3 to High Range production because:
        - Line 3 currently has 78% excess capacity
        - Workers on Line 3 are certified for High Range models
        - This maintains Medium Range production on other lines
        - Switching time is only 30 minutes vs. 2 hours for other lines"
        """
        
    def generate_alert_message(self, alert: Dict, severity: str) -> str:
        """
        Generate alert messages for different audiences
        (Production Manager, CxO, Line Workers, Logistics Team)
        """
```

#### 4.3 Decision Support System

**File: `src/generative_ai/decision_support.py`**

**Purpose:**
Provide comprehensive decision support with trade-off analysis

**Key Features:**
```python
class DecisionSupportSystem:
    
    def analyze_trade_offs(self, options: List[Dict]) -> Dict:
        """
        Analyze trade-offs between different options
        
        Example:
        Option A: Extend shifts (High cost, high output, worker fatigue)
        Option B: Defer non-urgent orders (Low cost, maintains quality, customer impact)
        Option C: Mix of both (Moderate cost, balanced approach)
        
        Returns comparison matrix with recommendations
        """
        
    def generate_decision_tree(self, scenario: Dict) -> Dict:
        """
        Generate a decision tree for complex scenarios
        
        Shows decision points, alternatives, and outcomes
        """
        
    def create_impact_report(self, decision: Dict) -> Dict:
        """
        Create detailed impact report for a decision
        
        Includes:
        - Production impact
        - Financial impact
        - Quality impact
        - Worker impact
        - Customer satisfaction impact
        - Supply chain impact
        """
```

---

### **PHASE 5: DASHBOARD & UI DEVELOPMENT** (4-5 hours)

#### 5.1 Dashboard Architecture

**Technology Choice:**
- **Primary**: Streamlit (rapid development, Python-native)
- **Alternative**: React.js + FastAPI (more customizable, production-ready)

**Dashboard Structure:**

```
Main Dashboard
├── Header (Logo, Time, Active Scenario, LLM Provider)
├── KPI Cards Row (4 cards)
├── Alert Banner (Critical alerts)
├── Main Content Area
│   ├── Tab 1: Real-Time Monitoring
│   ├── Tab 2: Scenario Management
│   ├── Tab 3: AI Recommendations
│   ├── Tab 4: Workforce & Resources
│   ├── Tab 5: Supply Chain
│   └── Tab 6: Analytics & Reports
└── Footer (System Status, Last Updated)
```

#### 5.2 Tab 1: Real-Time Monitoring

**File: `src/dashboard/pages/monitoring.py`**

**Components:**

1. **Assembly Line Status Panel**
```
┌──────────────────────────────────────────────────────────┐
│  HighRange_1    [●●●●●●●●○○] 85%  ↑ Producing           │
│  HighRange_2    [●●●●●●○○○○] 62%  → Normal               │
│  MediumRange_1  [●●●●●●●●●○] 92%  ↑ High Efficiency      │
│  MediumRange_2  [●●●●●○○○○○] 51%  ⚠ Maintenance Soon     │
│  MediumRange_3  [●●●●●●●●○○] 88%  ↑ Producing           │
└──────────────────────────────────────────────────────────┘
```

2. **KPI Cards**
```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Production  │ │  Efficiency │ │  Downtime   │ │   Defects   │
│    2,847    │ │     87%     │ │    12 min   │ │    1.4%     │
│  units/day  │ │   ↑ +5%     │ │   ↓ -25%    │ │   ↓ -0.3%   │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

3. **Production Timeline Chart**
- Line chart showing hourly production across all lines
- Color-coded by shift (A, B, C)
- Markers for disruption events

4. **Machine Uptime Heatmap**
- Heatmap showing uptime % for each line over time
- Color scale: Green (>90%), Yellow (70-90%), Red (<70%)

5. **Real-Time Alerts Feed**
```
⚠ 14:32 | MediumRange_2 | Maintenance Alert: Uptime dropped to 72%
✓ 14:15 | HighRange_1 | Shift transition completed successfully
⚠ 13:58 | Supply Chain | Semiconductor shipment delayed by 4 hours
```

#### 5.3 Tab 2: Scenario Management

**File: `src/dashboard/pages/scenarios.py`**

**Components:**

1. **Scenario Selector**
```
Current Scenario: [Morning_Sudden_Demand_Spike ▼]

Available Scenarios:
● Morning_Sudden_Demand_Spike (Active)
○ MidDay_Semiconductor_Delay
○ Afternoon_Robot_Breakdown
○ Custom Scenario

[Load Scenario] [Simulate] [Compare]
```

2. **Scenario Details Panel**
```
╔═══════════════════════════════════════════════════════╗
║ Scenario: Morning Sudden Demand Spike                 ║
╠═══════════════════════════════════════════════════════╣
║ Trigger: Europe dealer requests 500 High Range SUVs  ║
║ Time: 08:30 AM                                        ║
║ Affected Lines: HighRange_1, HighRange_2            ║
║ Duration: 8 hours                                     ║
║                                                       ║
║ Impact:                                               ║
║  • Demand increase: 180%                             ║
║  • Required capacity: 500 units                      ║
║  • Current capacity: 280 units                       ║
║  • Capacity gap: 220 units                           ║
╚═══════════════════════════════════════════════════════╝
```

3. **Scenario Comparison Table**
| Metric | Baseline | Scenario 1 | Scenario 2 | Scenario 3 |
|--------|----------|------------|------------|------------|
| Output | 450 | 462 (+2.7%) | 438 (-2.7%) | 471 (+4.7%) |
| Efficiency | 75% | 82% | 71% | 85% |
| Cost | $50K | $58K | $52K | $62K |
| Risk | Low | Medium | Low | High |

4. **Scenario Timeline Visualization**
- Gantt chart showing action sequence
- Dependencies between actions
- Critical path highlighting

#### 5.4 Tab 3: AI Recommendations

**File: `src/dashboard/pages/recommendations.py`**

**Components:**

1. **Recommendation Cards**
```
┌─────────────────────────────────────────────────────────┐
│ 🔴 CRITICAL - Priority 1                                │
├─────────────────────────────────────────────────────────┤
│ Shift Adjustment for High Range Production             │
│                                                         │
│ Recommendation:                                         │
│ Extend Shift A by 3 hours and call in 12 backup       │
│ workers for HighRange_1 and HighRange_2 lines         │
│                                                         │
│ Reasoning:                                              │
│ - Demand spike of 500 units requires 18 hours of      │
│   additional production time                            │
│ - Shift A has highest efficiency (92%)                 │
│ - 12 certified workers available on standby            │
│                                                         │
│ Expected Impact:                                        │
│ • Production: +120 units                               │
│ • KPI Impact: +11.2%                                   │
│ • Additional Cost: $4,800 (overtime)                   │
│ • Success Probability: 89%                             │
│                                                         │
│ [Accept] [Modify] [Reject] [Simulate]                 │
└─────────────────────────────────────────────────────────┘
```

2. **AI Reasoning Explanation**
- Expandable section showing step-by-step reasoning
- References to data points used
- Alternative options considered

3. **Impact Prediction Visualization**
- Before/After comparison charts
- KPI impact breakdown
- Risk assessment meter

4. **Recommendation History**
- Timeline of past recommendations
- Acceptance rate
- Effectiveness scores

#### 5.5 Tab 4: Workforce & Resources

**File: `src/dashboard/pages/workforce.py`**

**Components:**

1. **Shift Schedule Visualization**
```
Time:    00:00        06:00        12:00        18:00      23:59
Shift A: [============================]
Shift B:             [============================]
Shift C:                          [============================]

Worker Availability:
Shift A: ████████░░ 82% (123/150 workers)
Shift B: ██████████ 95% (142/150 workers)
Shift C: ███████░░░ 76% (114/150 workers)
```

2. **Worker Allocation Heatmap**
| Line | Shift A | Shift B | Shift C |
|------|---------|---------|---------|
| HighRange_1 | 28 ✓ | 30 ✓ | 25 ⚠ |
| HighRange_2 | 26 ✓ | 28 ✓ | 24 ⚠ |
| MediumRange_1 | 22 ✓ | 24 ✓ | 20 ✓ |
| MediumRange_2 | 24 ✓ | 26 ✓ | 22 ✓ |
| MediumRange_3 | 23 ✓ | 25 ✓ | 23 ✓ |

3. **Skill Matrix**
- Shows worker certifications by model type
- Identifies skill gaps
- Suggests cross-training opportunities

4. **Resource Utilization Dashboard**
- Machine utilization by line
- Energy consumption trends
- Resource efficiency scores

#### 5.6 Tab 5: Supply Chain

**File: `src/dashboard/pages/supply_chain.py`**

**Components:**

1. **Inventory Levels Dashboard**
```
┌─────────────────────────────────────────────────────┐
│ Component         Current  Required  Status         │
├─────────────────────────────────────────────────────┤
│ Semiconductors      142      200     ⚠ Delayed     │
│ Battery Packs       89       85      ✓ Adequate    │
│ Motors             156      140      ✓ Sufficient  │
│ Chassis Parts      203      180      ✓ Sufficient  │
│ Interior Kits       78       90      ⚠ Low         │
└─────────────────────────────────────────────────────┘
```

2. **Supply Chain Risk Map**
- Visual map showing supplier locations
- Risk indicators by supplier
- Delivery status tracking

3. **Semiconductor Availability Tracker**
```
Current Status: DELAYED
Expected Arrival: +48 hours (Feb 7, 14:00)
Impact: High Range SUV production
Alternative Suppliers: 3 available
  • Supplier B: +24h, +15% cost
  • Supplier C: +36h, +8% cost
  • Supplier D: +72h, -5% cost
```

4. **Supplier Performance Dashboard**
- On-time delivery rates
- Quality scores
- Reliability rankings

#### 5.7 Tab 6: Analytics & Reports

**File: `src/dashboard/pages/analytics.py`**

**Components:**

1. **Historical Performance Trends**
- Production output trends (daily, weekly, monthly)
- Efficiency improvements over time
- Downtime reduction progress

2. **Scenario Effectiveness Analysis**
- Success rate of AI recommendations by scenario type
- Average KPI improvement per scenario
- Cost-benefit analysis

3. **Comparative Analytics**
- Before AI vs. After AI implementation
- Shift-wise performance comparison
- Line-wise efficiency comparison

4. **Report Generator**
```
┌─────────────────────────────────────────────────┐
│ Generate Report                                 │
├─────────────────────────────────────────────────┤
│ Report Type: [Executive Summary ▼]             │
│ Time Period: [Last 7 Days ▼]                   │
│ Include: [✓] KPIs  [✓] Recommendations         │
│          [✓] Scenarios  [ ] Raw Data           │
│ Format: [✓] PDF  [ ] Excel  [ ] PowerPoint     │
│                                                 │
│ [Generate Report] [Schedule Recurring]          │
└─────────────────────────────────────────────────┘
```

5. **KPI Achievement Dashboard**
```
Target vs Actual Performance:

Production Efficiency:
Target: 30% improvement  [████████████████████] 100% ✓
Actual: 32% improvement

Planning Time Reduction:
Target: 25% reduction    [██████████████████░░] 92%
Actual: 23% reduction

Downtime Decrease:
Target: 40% decrease     [████████████████████] 105% ✓
Actual: 42% decrease

Inventory Cost Savings:
Target: 20% savings      [██████████████░░░░░░] 75%
Actual: 15% savings
```

#### 5.8 LLM Provider Settings Panel

**File: `src/dashboard/components/llm_settings.py`**

```
┌─────────────────────────────────────────────────────┐
│  🤖 AI Model Settings                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Active Provider: ● OpenAI  ○ Gemini  ○ Hugging Face│
│                                                     │
│  Provider Status:                                   │
│  ┌───────────────────────────────────────────────┐ │
│  │ Provider      Status    Latency   Cost/1K    │ │
│  │ OpenAI        ● Online  0.8s      $0.030     │ │
│  │ Gemini        ● Online  0.5s      $0.015     │ │
│  │ Hugging Face  ● Online  1.2s      $0.000     │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Advanced Settings:                                 │
│  Temperature: [====●====] 0.7                      │
│  Max Tokens:  [========●] 4096                     │
│                                                     │
│  ☐ Auto-fallback enabled                           │
│  ☐ Cost optimization enabled                       │
│  ☐ Use cheaper models for simple tasks             │
│                                                     │
│  Task-Provider Mapping:                             │
│  Complex scenarios:     [OpenAI ▼]                 │
│  Recommendations:       [Gemini ▼]                 │
│  Simple classification: [Hugging Face ▼]           │
│                                                     │
│  [Save Settings] [Test All Providers] [View Logs]  │
└─────────────────────────────────────────────────────┘
```

---

### **PHASE 6: API DEVELOPMENT** (2-3 hours)

#### 6.1 API Architecture

**Framework: FastAPI**

**File: `src/api/main.py`**

```python
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

app = FastAPI(
    title="Intelligent Production Scheduling API",
    description="AI-powered manufacturing optimization",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 6.2 RESTful Endpoints

**File: `src/api/routes/`**

##### 6.2.1 Scenario Management

```python
# src/api/routes/scenarios.py

@app.get("/api/scenarios")
async def get_all_scenarios() -> List[Dict]:
    """Get list of all available scenarios"""
    
@app.get("/api/scenarios/{scenario_id}")
async def get_scenario_details(scenario_id: str) -> Dict:
    """Get detailed information about a specific scenario"""
    
@app.post("/api/scenarios/simulate")
async def simulate_scenario(scenario: ScenarioRequest) -> Dict:
    """Simulate a scenario and return predicted outcomes"""
    
@app.post("/api/scenarios/compare")
async def compare_scenarios(scenario_ids: List[str]) -> Dict:
    """Compare multiple scenarios side-by-side"""
```

##### 6.2.2 AI Recommendations

```python
# src/api/routes/recommendations.py

@app.get("/api/recommendations/current")
async def get_current_recommendations() -> List[Dict]:
    """Get AI recommendations for current situation"""
    
@app.post("/api/recommendations/generate")
async def generate_recommendations(context: ContextRequest) -> List[Dict]:
    """Generate new recommendations based on context"""
    
@app.put("/api/recommendations/{rec_id}/accept")
async def accept_recommendation(rec_id: str) -> Dict:
    """Accept and execute a recommendation"""
    
@app.put("/api/recommendations/{rec_id}/reject")
async def reject_recommendation(rec_id: str, reason: str) -> Dict:
    """Reject a recommendation with reason"""
    
@app.get("/api/recommendations/history")
async def get_recommendation_history(limit: int = 50) -> List[Dict]:
    """Get historical recommendations and outcomes"""
```

##### 6.2.3 Production Status

```python
# src/api/routes/production.py

@app.get("/api/production/status")
async def get_production_status() -> Dict:
    """Get real-time production status for all lines"""
    
@app.get("/api/production/lines/{line_id}")
async def get_line_status(line_id: str) -> Dict:
    """Get detailed status for a specific assembly line"""
    
@app.get("/api/production/metrics")
async def get_production_metrics(timeframe: str = "24h") -> Dict:
    """Get production metrics and KPIs"""
    
@app.post("/api/production/optimize")
async def optimize_production_schedule(
    demand: Dict, 
    constraints: Dict
) -> Dict:
    """Generate optimized production schedule"""
```

##### 6.2.4 KPI & Analytics

```python
# src/api/routes/analytics.py

@app.get("/api/kpi/current")
async def get_current_kpis() -> Dict:
    """Get current KPI values"""
    
@app.post("/api/kpi/predict")
async def predict_kpi_impact(action: ActionRequest) -> Dict:
    """Predict KPI impact of a proposed action"""
    
@app.get("/api/analytics/trends")
async def get_performance_trends(
    metric: str, 
    period: str = "7d"
) -> Dict:
    """Get performance trends over time"""
    
@app.get("/api/analytics/report")
async def generate_analytics_report(report_type: str) -> Dict:
    """Generate comprehensive analytics report"""
```

##### 6.2.5 Workforce Management

```python
# src/api/routes/workforce.py

@app.get("/api/workforce/availability")
async def get_workforce_availability() -> Dict:
    """Get current workforce availability by shift"""
    
@app.get("/api/workforce/schedule")
async def get_shift_schedule(date: str) -> Dict:
    """Get shift schedule for a specific date"""
    
@app.post("/api/workforce/optimize")
async def optimize_workforce_allocation(
    demand: Dict, 
    current_allocation: Dict
) -> Dict:
    """Generate optimized workforce allocation"""
```

##### 6.2.6 Supply Chain

```python
# src/api/routes/supply_chain.py

@app.get("/api/supply-chain/inventory")
async def get_inventory_status() -> Dict:
    """Get current inventory levels"""
    
@app.get("/api/supply-chain/suppliers")
async def get_supplier_status() -> List[Dict]:
    """Get status of all suppliers"""
    
@app.post("/api/supply-chain/find-alternatives")
async def find_alternative_suppliers(component: str) -> List[Dict]:
    """Find alternative suppliers for a component"""
```

##### 6.2.7 Alerts & Notifications

```python
# src/api/routes/alerts.py

@app.get("/api/alerts/active")
async def get_active_alerts() -> List[Dict]:
    """Get all active alerts"""
    
@app.get("/api/alerts/history")
async def get_alert_history(limit: int = 100) -> List[Dict]:
    """Get historical alerts"""
    
@app.put("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str) -> Dict:
    """Acknowledge an alert"""
```

##### 6.2.8 LLM Provider Management

```python
# src/api/routes/llm_settings.py

@app.get("/api/llm/providers")
async def get_provider_status() -> Dict:
    """Get status of all LLM providers"""
    
@app.put("/api/llm/switch")
async def switch_provider(provider_name: str) -> Dict:
    """Switch to a different LLM provider"""
    
@app.post("/api/llm/test")
async def test_provider_connection(provider_name: str) -> Dict:
    """Test connection to a specific provider"""
    
@app.get("/api/llm/usage")
async def get_usage_statistics() -> Dict:
    """Get LLM usage statistics and costs"""
```

#### 6.3 WebSocket for Real-Time Updates

**File: `src/api/websocket.py`**

```python
@app.websocket("/ws/production")
async def production_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time production updates
    
    Streams:
    - Production output changes
    - Alert notifications
    - KPI updates
    - Recommendation availability
    """
    await websocket.accept()
    
    while True:
        # Send real-time updates
        data = await get_real_time_data()
        await websocket.send_json(data)
        await asyncio.sleep(5)  # Update every 5 seconds
```

#### 6.4 Request/Response Models

**File: `src/api/models.py`**

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ScenarioRequest(BaseModel):
    scenario_type: str
    parameters: Dict[str, Any]
    simulation_duration: int  # hours
    
class ContextRequest(BaseModel):
    timestamp: datetime
    assembly_line_status: Dict[str, float]
    current_demand: Dict[str, int]
    inventory_levels: Dict[str, float]
    workforce_availability: Dict[str, float]
    
class ActionRequest(BaseModel):
    action_type: str
    parameters: Dict[str, Any]
    target_line: Optional[str] = None
    
class RecommendationResponse(BaseModel):
    recommendation_id: str
    priority: int
    action: str
    reasoning: str
    expected_impact: Dict[str, float]
    success_probability: float
    estimated_cost: float
```

---

### **PHASE 7: TESTING STRATEGY** (2-3 hours)

#### 7.1 Unit Testing

**File: `tests/unit/test_agents.py`**

```python
import pytest
from src.agents.demand_agent import DemandForecastingAgent

class TestDemandAgent:
    
    def test_spike_detection(self):
        """Test demand spike detection algorithm"""
        agent = DemandForecastingAgent(llm_manager)
        historical_avg = 300
        current_demand = 500
        assert agent.detect_spike(current_demand, historical_avg) == True
        
    def test_forecast_accuracy(self):
        """Test forecast generation"""
        # Test with known historical data
        # Verify forecast is within acceptable range
```

**Test Coverage:**
- Each agent's core methods
- Data processing functions
- LLM provider switching logic
- Recommendation generation
- KPI calculation

#### 7.2 Integration Testing

**File: `tests/integration/test_multi_agent.py`**

```python
def test_orchestrator_coordination():
    """Test master orchestrator coordinating sub-agents"""
    orchestrator = MasterOrchestratorAgent(llm_manager)
    context = load_test_scenario("morning_spike")
    result = orchestrator.analyze(context)
    
    # Verify all sub-agents were called
    # Verify recommendations are coherent
    # Verify no conflicts in final plan
```

#### 7.3 API Testing

**File: `tests/api/test_endpoints.py`**

```python
from fastapi.testclient import TestClient

def test_get_scenarios():
    """Test scenarios endpoint"""
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

#### 7.4 End-to-End Testing

```python
def test_full_scenario_workflow():
    """
    Test complete workflow:
    1. Load scenario
    2. Generate recommendations
    3. Accept recommendation
    4. Verify KPI impact
    """
```

---

### **PHASE 8: DEPLOYMENT** (2-3 hours)

#### 8.1 Docker Containerization

**File: `docker/Dockerfile`**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/

# Expose ports
EXPOSE 8000 8501

# Start services
CMD ["./start.sh"]
```

**File: `docker/docker-compose.yml`**

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}
    volumes:
      - ./data:/app/data
      
  dashboard:
    build: .
    command: streamlit run src/dashboard/app.py
    ports:
      - "8501:8501"
    depends_on:
      - api
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
      
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=production_db
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 8.2 Deployment Options

##### Option 1: Cloud Deployment (AWS)
- **API**: AWS ECS/Fargate
- **Dashboard**: AWS Amplify or ECS
- **Database**: AWS RDS (PostgreSQL)
- **Cache**: AWS ElastiCache (Redis)
- **Storage**: S3 for data files

##### Option 2: Cloud Deployment (Azure)
- **API**: Azure Container Apps
- **Dashboard**: Azure Web Apps
- **Database**: Azure Database for PostgreSQL
- **Storage**: Azure Blob Storage

##### Option 3: Local/On-Premise
- Docker Compose on server
- Nginx reverse proxy
- SSL certificates (Let's Encrypt)

#### 8.3 CI/CD Pipeline

**File: `.github/workflows/deploy.yml`**

```yaml
name: Deploy Production Scheduling System

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/
          
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t production-scheduler .
        
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deployment commands
```

---

## 📊 TECHNOLOGY STACK SUMMARY

### Backend
- **Python 3.10+**
- **FastAPI** (REST API)
- **WebSockets** (Real-time updates)
- **SQLAlchemy** (ORM)
- **Redis** (Caching)

### AI/ML
- **OpenAI API** (GPT-4)
- **Google Gemini API** (Gemini Pro)
- **Hugging Face Transformers** (Llama, Mistral)
- **LangChain** (Agent framework)
- **PyTorch** (Local inference)

### Data Processing
- **Pandas** (Data manipulation)
- **NumPy** (Numerical computing)
- **Scikit-learn** (ML models)

### Frontend
- **Streamlit** (Dashboard)
- Alternative: **React.js** (Custom UI)
- **Plotly** (Interactive charts)
- **Matplotlib/Seaborn** (Static visualizations)

### Database
- **PostgreSQL** (Primary database)
- **SQLite** (Development)
- **Redis** (Caching & real-time data)

### Deployment
- **Docker** (Containerization)
- **Docker Compose** (Orchestration)
- **Nginx** (Reverse proxy)
- **GitHub Actions** (CI/CD)

---

## 📈 EXPECTED OUTCOMES & KPIs

### Production Efficiency
- **Baseline**: 65%
- **Target**: 85% (+30%)
- **Mechanism**: Optimized line allocation, predictive maintenance, workforce optimization

### Planning Time
- **Baseline**: 4 hours per schedule
- **Target**: 3 hours (-25%)
- **Mechanism**: AI-generated schedules, automated scenario analysis

### Downtime
- **Baseline**: 20 minutes per shift
- **Target**: 12 minutes (-40%)
- **Mechanism**: Predictive maintenance, proactive alerts, quick response

### Inventory Costs
- **Baseline**: $100K per month
- **Target**: $80K (-20%)
- **Mechanism**: Just-in-time optimization, better demand forecasting

---

## 🎯 SUCCESS METRICS

### Technical Metrics
- API response time < 500ms
- Dashboard load time < 2s
- AI recommendation generation < 10s
- System uptime > 99.5%

### Business Metrics
- Recommendation acceptance rate > 75%
- Scenario simulation accuracy > 85%
- User satisfaction score > 4.5/5
- ROI > 200% in first year

---

## 📚 DOCUMENTATION DELIVERABLES

1. **Technical Architecture Document**
   - System design diagrams
   - Data flow diagrams
   - API architecture

2. **API Documentation**
   - OpenAPI/Swagger documentation
   - Endpoint descriptions
   - Request/response examples

3. **User Guide**
   - Dashboard navigation
   - Feature explanations
   - Common workflows

4. **Deployment Guide**
   - Installation instructions
   - Configuration guide
   - Troubleshooting

5. **Developer Guide**
   - Code structure
   - How to extend agents
   - How to add new LLM providers

---

## 🚀 NEXT STEPS

### Immediate Actions:
1. Set up project structure
2. Install dependencies
3. Configure LLM API keys
4. Load and validate dataset

### Phase Execution Order:
1. ✅ Phase 1: Foundation (Done with this plan)
2. 🔄 Phase 2: Data processing
3. 🔄 Phase 3: Multi-agent system
4. 🔄 Phase 4: Generative AI
5. 🔄 Phase 5: Dashboard
6. 🔄 Phase 6: API
7. 🔄 Phase 7: Testing
8. 🔄 Phase 8: Deployment

### Ready to Begin Implementation?
All planning complete. Ready to start building the system!

---

## 📝 NOTES & CONSIDERATIONS

### LLM Provider Selection Guidelines:

**Use OpenAI (GPT-4) for:**
- Complex multi-agent coordination
- Critical scenario planning
- Decision-making with high stakes
- When accuracy is paramount

**Use Gemini for:**
- Real-time recommendations
- Quick scenario analysis
- Moderate complexity tasks
- Cost-performance balance

**Use Hugging Face (Open Source) for:**
- Privacy-sensitive deployments
- Offline mode requirements
- Simple classification tasks
- Cost optimization
- When API limits are reached

### Cost Estimates:
- **OpenAI**: ~$50-100/month (moderate usage)
- **Gemini**: ~$25-50/month (moderate usage)
- **Hugging Face**: Free (local) or ~$10-20/month (API)
- **Infrastructure**: $50-200/month (cloud hosting)

**Total Estimated Monthly Cost**: $135-370

---

## 🎓 LEARNING OUTCOMES

By completing this project, you will learn:
- Multi-agent AI system design
- LLM integration and prompt engineering
- Production scheduling optimization
- Real-time data processing
- Dashboard development
- API design and development
- Containerization and deployment

---

**End of Detailed Plan**

*This document serves as the comprehensive blueprint for the Intelligent Production Scheduling System. Follow each phase systematically for successful implementation.*

**Version**: 1.0  
**Last Updated**: February 5, 2026  
**Author**: AI Capstone Project Team
