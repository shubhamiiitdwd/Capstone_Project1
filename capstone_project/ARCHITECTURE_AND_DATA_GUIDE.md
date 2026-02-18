# AI Decision Engine — Architecture & Data Guide

**A plain-language guide for technical and non-technical readers**

This document explains how the Intelligent Production Scheduling System works: what data it uses, where that data comes from, and how each component (Rule Engine, ML Models, AI Agents) makes decisions. No prior technical knowledge is required for the main sections.

---

## Table of Contents

1. [What Problem Does This System Solve?](#1-what-problem-does-this-system-solve)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Data Sources — Scenario vs Master](#3-data-sources--scenario-vs-master)
4. [Where Each Data Type Is Used](#4-where-each-data-type-is-used)
5. [The 7-Step Pipeline (Step by Step)](#5-the-7-step-pipeline-step-by-step)
6. [Rule Engine — How It Works](#6-rule-engine--how-it-works)
7. [ML Models — Math and Logic](#7-ml-models--math-and-logic)
8. [AI Agents — How They Collaborate](#8-ai-agents--how-they-collaborate)
9. [Decision Log — Traceability](#9-decision-log--traceability)
10. [File Map — Where to Find What](#10-file-map--where-to-find-what)

---

## 1. What Problem Does This System Solve?

**Use Case 3: Afternoon Line Breakdown**

Imagine a car factory in Pune that builds electric SUVs. One afternoon at 3:45 PM, a robot on the HighRange assembly line breaks down. Production stops on that line. The plant manager needs to decide:

- How urgent is the repair?
- Where can we move production to compensate?
- Do we have enough parts (inventory) to support the new plan?
- Do we need to bring in extra workers or overtime?
- Are any suppliers at risk of causing further delays?

This system answers these questions by combining:

1. **Strict rules** (e.g., "If machine uptime &lt; 75%, dispatch maintenance")
2. **Predictive models** (e.g., "Line 2 has 54% risk of breakdown")
3. **AI reasoning** (e.g., "Given the rules and predictions, here are the top 5 actions")

Everything is logged so decisions can be audited later.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INPUT DATA (2 Excel Files)                             │
│  Pune_EV_SUV_Plant_Simulation_Data_Expanded.xlsx  +  Pune_EV_SUV_Plant_...  │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: BUILD CONTEXT                                                       │
│  Combine scenario data (200 records) + master data (lines, shifts, orders)  │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: RULE ENGINE (Deterministic — No AI)                                 │
│  Check: Machine uptime, line breakdown, inventory, workforce, semiconductors │
│  Output: "Rule X fired: Machine_Uptime = 62% < 75% → DISPATCH_MAINTENANCE"   │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: ML MODELS (Predictions)                                             │
│  - Breakdown risk per line (e.g., HighRange_2: 54%)                           │
│  - Delay risk (e.g., 63% due to inventory + semiconductor)                  │
│  - Supplier safety scores (e.g., Motherson Sumi: 89/100)                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: AI AGENTS (6 Specialists + 1 Orchestrator)                           │
│  Each agent gets rules + ML + master data → calls Azure OpenAI GPT-5.1       │
│  Agents: Line Health, Production, Inventory, Workforce, Supply Chain,        │
│          Decision Orchestrator (combines all)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: DECISION LOG (Audit Trail)                                          │
│  Each recommendation linked to: rules triggered, thresholds breached,       │
│  ML predictions, KPI impact, agent source                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Sources — Scenario vs Master

The system uses **two Excel files** and keeps two kinds of data clearly separate:

### Scenario Data (What Happened)

| Source | File | Sheet(s) | Records | Purpose |
|--------|------|----------|---------|---------|
| **Simulation** | Pune_EV_SUV_Plant_Simulation_Data_Expanded.xlsx | Train_Data, Validation_Data, Test_Data | 1000 total | Hourly production records: demand, uptime, inventory, defects, alerts |
| **Event** | Pune_EV_SUV_Plant_Simulation_Data.xlsx | Event_Line_Breakdown | 1 | Describes the breakdown: "Robot breakdown on HighRange_Line2", impact area, expected impact |

**Scenario data tells us:** What is happening right now (e.g., 200 records for "Afternoon Line Breakdown").

### Master Data (Reference / Static)

| Source | File | Sheet(s) | Records | Purpose |
|--------|------|----------|---------|---------|
| **Lines** | Pune_EV_SUV_Plant_Simulation_Data.xlsx | Assembly_Line_Master | 5 | Each line: capacity, OEE, MTTR, MTBF, robots |
| **Shifts** | Same | Shift_Master | 3 | Each shift: timing, workers, overtime, skill level |
| **Suppliers** | Same | Supplier_Master | 20 | Each supplier: name, location, lead time, reliability |
| **Inventory** | Same | Inventory_Master | 120 | Each material: reorder point, safety stock, lead time |
| **Orders** | Same | Order_Data | 20 | Pending orders: quantity, region, dispatch date |
| **Machines** | Same | Machine_Parameters | 30 | Machine sensors: threshold, current value, OEE |
| **KPI Targets** | Same | KPI_Summary | 3 | On-time delivery, downtime, overtime targets |

**Master data tells us:** What are the fixed facts (capacities, lead times, targets).

---

## 4. Where Each Data Type Is Used

### Scenario Data Usage

| Data | Column(s) | Where Used | Purpose |
|------|-----------|------------|---------|
| **Simulation** | Assembly_Line, Shift, Demand_SUVs, Production_Output | Rule Engine | Demand spike, inventory, workforce checks |
| **Simulation** | Machine_Uptime_%, Worker_Availability_%, Inventory_Status_% | Rule Engine | Threshold checks (uptime &lt; 75%, workers &lt; 92%) |
| **Simulation** | Semiconductor_Availability | Rule Engine | Semiconductor risk (Delayed/Shortage) |
| **Simulation** | Alert_Status | ML Models | Train breakdown predictor (Maintenance_Alert = breakdown proxy) |
| **Simulation** | Predicted_KPI_Impact_% | ML Models | Train delay predictor |
| **Simulation** | Machine_Uptime_%, Defect_Rate_%, Energy_Consumption_kWh | ML Models | Features for breakdown prediction |
| **Simulation** | Inventory_Status_%, Semiconductor_Availability | ML Models | Features for delay prediction |
| **Event** | Description, Impact_Areas, Expected_Impact | Rule Engine, Context | Identify affected line (HighRange_Line2), impact level |

### Master Data Usage

| Sheet | Fields Used | Where Used | Purpose |
|-------|-------------|------------|---------|
| **Assembly_Line_Master** | Line_Name, Daily_Capacity, OEE_%, MTTR_hrs, MTBF_hrs, Robots_Count, Current_Utilization_% | Rule Engine, AI Agents, Scenario Impact | Capacity lost, repair time (MTTR), overload check |
| **Shift_Master** | Shift_ID, Shift_Timing, Workers_Assigned, Skill_Level, Max_Overtime_hrs, Labor_Cost_per_hr | AI Agents (Workforce), Orchestrator | Overtime limits, worker reallocation |
| **Supplier_Master** | Supplier_Name, Location, Lead_Time_days, Reliability_%, Alternate_Supplier | ML (supplier risk), AI Agents (Supply Chain) | Supplier risk score, expedite recommendations |
| **Inventory_Master** | (summary: total_materials, low_stock_items, avg_lead_time_days) | AI Agents (Inventory) | Context for reorder decisions |
| **Order_Data** | Order_ID, Region, SUV_Type, Quantity, Order_Date, Required_Dispatch_Date | AI Agents (Production) | Prioritize orders by dispatch date |
| **Machine_Parameters** | (summary: total_machines, at_risk_count, avg_oee) | AI Agents (Line Health) | Machine health context |
| **KPI_Summary** | KPI, Before_Optimization_%, After_Optimization_%, Improvement_% | AI Agents (Orchestrator) | Ground KPI impact claims |

---

## 5. The 7-Step Pipeline (Step by Step)

When you click **"Run Full Analysis"** in the AI Decision Engine:

| Step | Name | What Happens | Input | Output |
|------|------|--------------|-------|--------|
| 1 | **Build Context** | Combines 200 scenario records + 9 master tables into one `context` dict | scenario_df, data_loader | `context` (dict with line_master, shift_master, suppliers, order_book, etc.) |
| 2 | **Rule Engine** | Runs 7 rules (machine health, breakdown, demand spike, inventory, semiconductor, overload, workforce) | scenario_df, context | `rule_output` (triggered rules, severity, actions) |
| 3 | **ML Models** | Predicts breakdown risk per line, delay risk, supplier scores | scenario_df, context | `ml_output` (breakdown probabilities, delay %, supplier list) |
| 4 | **AI Client Setup** | Connects to Azure OpenAI GPT-5.1 | .env credentials | Client ready |
| 5 | **AI Agents** | 6 agents run in sequence, each calls Azure OpenAI with rules + ML + master data | rule_output, ml_output, context | `crew_result` (executive summary, 5 recommendations) |
| 6 | **Normalize Recommendations** | Converts AI output to standard format | crew_result | `norm_recs` (list of dicts with action, priority, reasoning) |
| 7 | **Decision Log** | Builds traceable log: each recommendation linked to rules, ML, KPI impact | rule_output, ml_output, norm_recs | `decision_log` (entries for export/audit) |

---

## 6. Rule Engine — How It Works

The Rule Engine uses **fixed thresholds** — no AI, no guessing. If a condition is met, the rule fires.

### Rules and Thresholds

| Rule | Condition | Threshold | Action | Severity |
|------|-----------|-----------|--------|----------|
| **Low Machine Health** | Machine_Uptime_% for any line | &lt; 75% | DISPATCH_MAINTENANCE | HIGH |
| **Line Breakdown Detected** | Event has "breakdown" or "malfunction" | — | DISPATCH_MAINTENANCE | CRITICAL |
| **Line Reallocation Required** | Same event (line offline) | — | REALLOCATE_LINE | HIGH |
| **Demand Spike** | Peak demand &gt; avg + 2×std | sigma = 2 | INCREASE_SHIFT | HIGH |
| **Low Inventory** | Inventory_Status_% for any line | &lt; 70% | RAISE_SUPPLY_ALERT | HIGH |
| **Semiconductor Supply Risk** | Semiconductor = Shortage or &gt;30% records delayed | 30% | SWITCH_SUPPLIER | HIGH |
| **Line Overload** | Line utilization from master &gt; 95% | 95% | REALLOCATE_LINE | HIGH |
| **Workforce Below Target** | Worker_Availability_% per shift | &lt; 92% | INCREASE_SHIFT | MEDIUM |

### Data Used by Each Rule

- **Machine health:** `scenario_df` (Machine_Uptime_% per line)
- **Line breakdown:** `context['event_details']` (Description, Impact_Areas), `context['line_master']` (MTTR)
- **Demand spike:** `scenario_df` (Demand_SUVs mean, std, max)
- **Inventory:** `scenario_df` (Inventory_Status_% per line)
- **Semiconductor:** `scenario_df` (Semiconductor_Availability mode, shortage count)
- **Overload:** `context['line_master']` (Current_Utilization_%, Daily_Capacity)
- **Workforce:** `scenario_df` (Worker_Availability_% per shift)

---

## 7. ML Models — Math and Logic

### Model 1: Breakdown Prediction

**Goal:** Estimate the probability (0–100%) that each assembly line will need maintenance in the next few hours.

**Training:**
- **Input features:** Machine_Uptime_%, Worker_Availability_%, Defect_Rate_%, Energy_Consumption_kWh (from simulation)
- **Target:** 1 if Alert_Status = "Maintenance_Alert", else 0
- **Algorithm:** Random Forest (100 trees, max depth 5)
- **Training data:** All 1000 simulation records

**Prediction:**
- For each line, average the feature values across that line’s records
- Model outputs probability P(breakdown)
- Risk: HIGH if P &gt; 60%, MEDIUM if P &gt; 30%, else LOW

**Fallback (if model not trained):**  
`probability = (100 - Machine_Uptime_%) / 50` (clamped to 0–1).

---

### Model 2: Delay Prediction

**Goal:** Estimate delivery delay risk (0–100%).

**Training:**
- **Input features:** Inventory_Status_%, Machine_Uptime_%, Worker_Availability_%, Defect_Rate_%
- **Target:** Predicted_KPI_Impact_% (from simulation)
- **Algorithm:** Gradient Boosting Regressor (80 trees, max depth 4)

**Prediction:**
- Predict KPI impact from scenario averages
- Convert to risk: `risk_score = 1 - (kpi_impact / 10)` (clamped 0–1)
- Risk: HIGH if score &gt; 0.6, MEDIUM if &gt; 0.3, else LOW

**Fallback:**  
Base 0.2 + 0.3 if inventory &lt; 75% + 0.3 if semiconductor = Shortage (or 0.15 if Delayed).

---

### Model 3: Supplier Risk Scoring

**Goal:** Safety score 0–100 for each supplier (higher = safer).

**Method:** Heuristic (no ML training)

**Formula:**
```
score = Reliability_% - (Lead_Time_days × 1.5)
score = clamp(score, 0, 100)
```
- **Reliability_%, Lead_Time_days** from Supplier_Master
- Risk: LOW if score ≥ 80, MEDIUM if ≥ 60, else HIGH

---

## 8. AI Agents — How They Collaborate

All 6 agents use **Azure OpenAI GPT-5.1-chat**. Each agent gets a system prompt (role) and a user prompt (data + task).

### Agent Flow

```
Line Health Analyst   →  Production Planner  →  Inventory Controller
        ↓                        ↓                        ↓
Workforce Coordinator  →  Supply Chain Monitor  →  Decision Orchestrator
                                                          ↓
                                            Final 5 recommendations (JSON)
```

### What Each Agent Receives

| Agent | Scenario Data | Master Data | Rule Output | ML Output |
|-------|---------------|-------------|-------------|-----------|
| **Line Health** | Event, ML breakdown | line_master, machine_params_summary | rule_summary | breakdown predictions |
| **Production** | scenario_impact | line_master, **order_book** | rule_summary | — |
| **Inventory** | semiconductor_dist | **inventory_master_summary** | rule_summary | delay prediction |
| **Workforce** | worker_availability | **shift_master** | rule_summary | — |
| **Supply Chain** | semiconductor_dist | **suppliers** | rule_summary | supplier_risks, delay |
| **Orchestrator** | — | **kpi_targets** | rule_summary | breakdown, delay |

### Orchestrator Output

The Orchestrator returns JSON with:

- `executive_summary` — Short summary (3–4 sentences)
- `recommendations` — Array of 5 items: action, priority, reasoning, source_agent, estimated_time, expected_kpi_impact
- `decision_justification` — How rules and ML support the recommendations

---

## 9. Decision Log — Traceability

Each recommendation in the Decision Log is linked to:

- **Rules triggered** — Only rules relevant to that recommendation (not all rules)
- **Thresholds breached** — Human-readable conditions (e.g., "Machine_Uptime_% = 62% < 75%")
- **ML predictions** — Breakdown/delay/supplier data used for that recommendation
- **Supporting indicators** — Which rules and ML outputs support the decision
- **KPI impact** — From orchestrator or derived from rule action (e.g., DISPATCH_MAINTENANCE → "Line Downtime: +2–8 hrs")

Export formats: JSON and CSV.

---

## 10. File Map — Where to Find What

| File | Responsibility |
|------|----------------|
| **src/data/enhanced_data_loader.py** | Loads simulation + master + event data from Excel |
| **src/ui/ai_engine.py** | `_build_context()` — Builds context from scenario + master; `_run_full_analysis()` — Runs the 7-step pipeline |
| **src/engine/rule_engine.py** | All 7 rules and threshold logic |
| **src/engine/ml_models.py** | Breakdown model, delay model, supplier risk heuristic |
| **src/agents/crew_agents.py** | 6 agents + orchestrator, prompts, Azure OpenAI calls |
| **src/engine/decision_log.py** | Decision log structure, per-entry filtering, KPI derivation |
| **app.py** | App entry, sidebar, tabs, ML training at startup |

---

## Quick Reference: Data Flow Diagram

```
Excel 1 (Expanded)          Excel 2 (Main)
Train/Val/Test (1000)       Assembly_Line_Master (5)
       │                    Shift_Master (3)
       │                    Supplier_Master (20)
       │                    Inventory_Master (120)
       │                    Order_Data (20)
       │                    Machine_Parameters (30)
       │                    KPI_Summary (3)
       │                    Event_Line_Breakdown (1)
       │                              │
       └──────────────┬───────────────┘
                      ▼
              EnhancedDataLoader
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   scenario_df    master_data   event_details
   (200 rows)     (9 tables)   (1 event)
        │             │             │
        └─────────────┼─────────────┘
                      ▼
              _build_context()
                      │
                      ▼
               context (dict)
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   Rule Engine    ML Models    AI Agents
        │             │             │
        └─────────────┼─────────────┘
                      ▼
              Decision Log
```

---

*Document version: 1.0 | Capstone Project 2026 | Pune EV SUV Plant*
