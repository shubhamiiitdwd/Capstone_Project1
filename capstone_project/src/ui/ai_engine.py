"""
AI Decision Engine – Use Case 3 (Afternoon Line Breakdown)
Architecture: INPUT DATA -> Rule Engine + ML Models -> AI Recommendation -> Decision Log
Powered by Azure OpenAI GPT-5.1-chat + Multi-Agent AI orchestration
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

from src.engine.rule_engine import RuleEngine, RuleEngineOutput
from src.engine.ml_models import MLModelManager, MLPredictions
from src.engine.decision_log import DecisionLog


# =====================================================================
# HELPERS
# =====================================================================
def _fmt2(val, pct=False):
    """Format number to 2 decimal places. pct=True appends %."""
    try:
        v = float(val)
        return f"{v:.2f}%" if pct else f"{v:.2f}"
    except (TypeError, ValueError):
        return str(val)


# Breakdown line options: L1, L2, M1, M2, M3 -> master line names
BREAKDOWN_LINE_OPTIONS = [
    ("L1", "HighRange_Line1"),
    ("L2", "HighRange_Line2"),
    ("M1", "MedRange_Line1"),
    ("M2", "MedRange_Line2"),
    ("M3", "MedRange_Line3"),
]


# =====================================================================
# MAIN ENTRY POINT
# =====================================================================
def render_ai_engine():
    """Render the AI Decision Engine page."""
    data_loader = st.session_state.data_loader
    df = st.session_state.working_df

    # --- Page Header ---
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
        <h2 style="margin:0;">AI Decision Engine</h2>
        <p style="margin:0.3rem 0 0; opacity:0.9;">
            Rule Engine + ML Models + Multi-Agent AI &mdash; Architecture: 
            Input Data &rarr; Decision Logic &rarr; AI Recommendation &rarr; Decision Log
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- Glossary (OEE, MTTR, Utilization) ---
    with st.expander("Glossary: OEE, MTTR, Utilization", expanded=False):
        st.markdown("""
- **OEE (Overall Equipment Effectiveness)** = Availability × Performance × Quality. Measures how much of theoretical capacity is actually produced at good quality.
- **MTTR (Mean Time To Repair)** = Expected repair duration in hours when a breakdown occurs. From Assembly_Line_Master.
- **Current_Utilization_%** = Share of line capacity currently in use.

**Mandatory Capacity Formulas (OEE included):**
- Effective_Capacity = Capacity × (OEE / 100)
- Actual_Production = Capacity × (OEE / 100) × (Utilization / 100)
- Spare_Capacity = Capacity × (OEE / 100) × (1 − Utilization / 100)
- Units_Lost_During_Outage = Capacity × (OEE / 100) × (Utilization / 100) × (MTTR / 24)
        """)

    # --- Architecture Flow ---
    _render_architecture_flow()

    st.markdown("---")

    # --- Afternoon Line Breakdown only ---
    selected_scenario = 'Afternoon_Line_Breakdown'
    scenario_df = df[df['Scenario'] == selected_scenario] if 'Scenario' in df.columns else df

    st.markdown(f"""
    <div style="background: #9b59b610; border: 3px solid #9b59b6; border-radius: 12px;
                padding: 1rem; text-align: center; margin-bottom: 1rem;">
        <span style="font-size: 2rem;">🔧</span>
        <span style="background:#9b59b6; color:white; padding:2px 10px; border-radius:8px;
                     font-size:0.8rem; margin-left: 0.5rem;">USE CASE 3</span><br>
        <b style="font-size: 1.1rem;">Afternoon Line Breakdown</b><br>
        <span style="color: #666;">HighRange assembly line robot malfunction at 3:45 PM (Shift B) &mdash; {len(scenario_df)} records</span>
    </div>
    """, unsafe_allow_html=True)

    # Model choice
    model_choice = st.session_state.get('model_choice', 'AzureOpenAI')

    # Breakdown line selector (L1, L2, M1, M2, M3)
    breakdown_line_choice = st.radio(
        "Select breakdown line (single-line breakdown)",
        options=[opt[0] for opt in BREAKDOWN_LINE_OPTIONS],
        index=0,
        key="breakdown_line",
        horizontal=True,
    )
    affected_line = next(m for k, m in BREAKDOWN_LINE_OPTIONS if k == breakdown_line_choice)

    # MTTR override for sensitivity analysis
    mttr_override = None
    mttr_choice = st.radio(
        "MTTR Sensitivity (repair time)",
        options=["Use master data", "2 hours", "24 hours", "48 hours"],
        index=0,
        key="mttr_override",
        horizontal=True,
    )
    if mttr_choice == "2 hours":
        mttr_override = 2.0
    elif mttr_choice == "24 hours":
        mttr_override = 24.0
    elif mttr_choice == "48 hours":
        mttr_override = 48.0

    # --- Run Analysis Button ---
    btn_label = f"Run Full Analysis (Rule Engine + ML + AI Agents)"
    if st.button(btn_label, type="primary", width="stretch", key="run_uc3"):
        _run_full_analysis(selected_scenario, scenario_df, data_loader, model_choice, mttr_override, affected_line)

    # --- Display Results ---
    if st.session_state.get('uc3_analysis'):
        _display_full_results(st.session_state.uc3_analysis, scenario_df)


# =====================================================================
# ARCHITECTURE FLOW VISUALIZATION
# =====================================================================
def _render_architecture_flow():
    """Show the pipeline: Input Data -> Rule Engine -> ML -> AI Rec -> Decision Log"""
    cols = st.columns(5)
    steps = [
        ("📥", "Input Data", "Scenario +\nMaster Data"),
        ("⚙️", "Rule Engine", "Threshold checks\nCapacity logic"),
        ("🧠", "ML Models", "Breakdown pred.\nDelay risk"),
        ("🤖", "AI Agents", "GPT-5.1 Agents\nMulti-agent"),
        ("📋", "Decision Log", "Full traceability\nAudit trail"),
    ]
    for col, (icon, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div style="background: #f8f9fa; border: 2px solid #dee2e6; border-radius: 12px;
                        padding: 0.8rem; text-align: center; min-height: 110px;">
                <div style="font-size: 1.5rem;">{icon}</div>
                <div style="font-weight: bold; font-size: 0.85rem;">{title}</div>
                <div style="font-size: 0.7rem; color: #666; white-space: pre-line;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# =====================================================================
# FULL ANALYSIS PIPELINE
# =====================================================================
def _run_full_analysis(scenario, scenario_df, data_loader, model_choice, mttr_override=None, affected_line=None):
    """Execute: Context Build -> Rule Engine -> ML Models -> AI Agents -> Decision Log"""

    progress = st.progress(0, text="Building context from plant data...")
    status = st.empty()

    try:
        # 1. Build context
        context = _build_context(scenario, scenario_df, data_loader, mttr_override, affected_line)
        progress.progress(0.15, text="Running Rule Engine...")

        # 2. Rule Engine
        rule_engine = RuleEngine()
        rule_output = rule_engine.evaluate(scenario_df, context)
        status.info(f"Rule Engine: {len(rule_output.triggered_rules)} rules triggered. Severity: {rule_output.overall_severity}")
        progress.progress(0.30, text="Running ML Models...")

        # 3. ML Models
        ml_manager = st.session_state.get('ml_manager')
        if ml_manager is None:
            ml_manager = MLModelManager()
            full_df = st.session_state.working_df
            ml_manager.train(full_df)
            st.session_state.ml_manager = ml_manager
        ml_output = ml_manager.predict(scenario_df, context)
        progress.progress(0.45, text="Setting up AI model...")

        # 4. Set active LLM client (Azure OpenAI)
        from src.utils.azure_openai_client import get_azure_openai_client, set_active_llm_client
        try:
            client = get_azure_openai_client()
            set_active_llm_client(client)
        except Exception as e:
            print(f"[WARN] Azure OpenAI client setup: {e}")
        progress.progress(0.55, text="Running Multi-Agent AI Analysis...")

        # 5. Multi-Agent AI Analysis
        from src.agents.crew_agents import run_crew
        crew_result = run_crew(rule_output, ml_output, context)
        progress.progress(0.85, text="Building Decision Log...")

        # 6. Build recommendations from crew result
        recommendations = crew_result.get("recommendations", [])
        # Normalise recommendations to dicts if they're strings
        norm_recs = []
        for r in recommendations:
            if isinstance(r, dict):
                norm_recs.append(r)
            elif isinstance(r, str):
                norm_recs.append({"action": r, "priority": 3, "reasoning": "", "source_agent": "Orchestrator"})
        if not norm_recs:
            norm_recs = [{"action": "Dispatch maintenance for affected line", "priority": 5,
                          "reasoning": "Line breakdown requires immediate attention", "source_agent": "Orchestrator"}]

        # 7. Decision Log
        decision_log = DecisionLog.from_analysis(scenario, rule_output, ml_output, norm_recs, context)
        progress.progress(1.0, text="Analysis complete!")

        # Store everything
        st.session_state.uc3_analysis = {
            "scenario": scenario,
            "context": context,
            "rule_output": rule_output,
            "ml_output": ml_output,
            "crew_result": crew_result,
            "recommendations": norm_recs,
            "decision_log": decision_log,
            "model_used": model_choice,
        }

        status.empty()
        st.success("Full pipeline complete: Rule Engine -> ML Models -> AI Agents -> Decision Log")
        st.rerun()

    except Exception as e:
        progress.empty()
        status.empty()
        st.error(f"Analysis error: {e}")
        import traceback
        with st.expander("Error details"):
            st.code(traceback.format_exc())
    finally:
        from src.utils.azure_openai_client import reset_active_llm_client
        reset_active_llm_client()



# =====================================================================
# CONTEXT BUILDER
# =====================================================================
def _build_context(scenario, scenario_df, data_loader, mttr_override=None, affected_line=None):
    """Build context dict from scenario data + master data."""
    import re

    demand_by_line = {
        line: float(scenario_df[scenario_df['Assembly_Line'] == line]['Demand_SUVs'].mean())
        for line in scenario_df['Assembly_Line'].unique()
    }
    inventory_levels = {
        line: float(scenario_df[scenario_df['Assembly_Line'] == line]['Inventory_Status_%'].mean())
        for line in scenario_df['Assembly_Line'].unique()
    }

    context = {
        'scenario': scenario,
        'timestamp': datetime.now().isoformat(),
        'demand': float(scenario_df['Demand_SUVs'].mean()),
        'current_demand': float(scenario_df['Demand_SUVs'].mean()),
        'peak_demand': float(scenario_df['Demand_SUVs'].max()),
        'demand_by_line': demand_by_line,
        'demand_data': {
            'avg_demand': float(scenario_df['Demand_SUVs'].mean()),
            'max_demand': float(scenario_df['Demand_SUVs'].max()),
            'std_demand': float(scenario_df['Demand_SUVs'].std()),
            'trend': 'increasing' if 'Spike' in scenario else 'declining' if 'Breakdown' in scenario else 'stable',
        },
        'inventory_levels': inventory_levels,
        'worker_availability': {
            shift: float(scenario_df[scenario_df['Shift'] == shift]['Worker_Availability_%'].mean())
            for shift in scenario_df['Shift'].unique()
        },
        'machine_uptime': {
            line: float(scenario_df[scenario_df['Assembly_Line'] == line]['Machine_Uptime_%'].mean())
            for line in scenario_df['Assembly_Line'].unique()
        },
        'production_output': {
            line: float(scenario_df[scenario_df['Assembly_Line'] == line]['Production_Output'].sum())
            for line in scenario_df['Assembly_Line'].unique()
        },
        'efficiency': float(scenario_df['Production_Output'].mean() / max(1, scenario_df['Demand_SUVs'].mean()) * 100),
        'semiconductor_availability': scenario_df['Semiconductor_Availability'].mode().iloc[0] if len(scenario_df) > 0 else 'Available',
        'defect_rate': float(scenario_df['Defect_Rate_%'].mean()),
        'energy_consumption': float(scenario_df['Energy_Consumption_kWh'].mean()),
        'predicted_kpi_impact': float(scenario_df['Predicted_KPI_Impact_%'].mean()) if 'Predicted_KPI_Impact_%' in scenario_df.columns else 0,
        'alert_distribution': scenario_df['Alert_Status'].value_counts().to_dict() if 'Alert_Status' in scenario_df.columns else {},
        'active_alerts': scenario_df[scenario_df['Alert_Status'] != 'None']['Alert_Status'].value_counts().to_dict() if 'Alert_Status' in scenario_df.columns else {},
        'semiconductor_distribution': scenario_df['Semiconductor_Availability'].value_counts().to_dict() if 'Semiconductor_Availability' in scenario_df.columns else {},
    }

    # Load master data
    if data_loader.master_data:
        line_master_df = data_loader.get_master_table('Assembly_Line_Master')
        if not line_master_df.empty:
            context['line_master'] = {
                row['Line_Name']: {
                    'suv_type': row['SUV_Type'], 'daily_capacity': int(row['Daily_Capacity']),
                    'utilization': float(row['Current_Utilization_%']),
                    'oee': float(row['OEE_%']),
                    'mttr_hrs': float(row['MTTR_hrs']), 'mtbf_hrs': float(row['MTBF_hrs']),
                    'robots': int(row['Robots_Count']),
                } for _, row in line_master_df.iterrows()
            }
            context['total_plant_capacity'] = int(line_master_df['Daily_Capacity'].sum())

        shift_master_df = data_loader.get_master_table('Shift_Master')
        if not shift_master_df.empty:
            context['shift_master'] = {
                row['Shift_ID']: {
                    'timing': row['Shift_Timing'],
                    'workers_assigned': int(row['Workers_Assigned']),
                    'skill_level': row['Skill_Level'],
                    'max_overtime_hrs': float(row['Max_Overtime_hrs']),
                    'labor_cost_per_hr': float(row['Labor_Cost_per_hr']),
                } for _, row in shift_master_df.iterrows()
            }
            context['total_workers'] = int(shift_master_df['Workers_Assigned'].sum())

        supplier_df = data_loader.get_master_table('Supplier_Master')
        if not supplier_df.empty:
            context['suppliers'] = [
                {'id': row['Supplier_ID'], 'name': row['Supplier_Name'],
                 'location': row['Location'], 'lead_time_days': int(row['Lead_Time_days']),
                 'reliability': float(row['Reliability_%']),
                 'has_alternate': str(row['Alternate_Supplier'])}
                for _, row in supplier_df.iterrows()
            ]

        kpi_df = data_loader.get_master_table('KPI_Summary')
        if not kpi_df.empty:
            context['kpi_targets'] = kpi_df.to_dict('records')

        inv_master = data_loader.get_master_table('Inventory_Master')
        if not inv_master.empty:
            low_stock = inv_master[inv_master['Current_Stock'] <= inv_master['Reorder_Point']]
            context['inventory_master_summary'] = {
                'total_materials': len(inv_master),
                'low_stock_items': len(low_stock),
                'avg_lead_time_days': round(float(inv_master['Lead_Time_days'].mean()), 1),
            }

        machine_params = data_loader.get_master_table('Machine_Parameters')
        if not machine_params.empty:
            at_risk = machine_params[machine_params['Current_Value'] > machine_params['Threshold']]
            context['machine_params_summary'] = {
                'total_machines': len(machine_params),
                'at_risk_count': len(at_risk),
                'avg_oee': round(float(machine_params['OEE_%'].mean()), 1),
            }

        order_data = data_loader.get_master_table('Order_Data')
        if not order_data.empty:
            context['order_book'] = order_data.to_dict('records')

    # Load event data
    event_map = {
        'Morning_Sudden_Demand_Spike': 'Event_Demand_Spike',
        'Midday_Semiconductor_Shortage': 'Event_Chip_Delay',
        'Afternoon_Line_Breakdown': 'Event_Line_Breakdown',
    }
    event_sheet = event_map.get(scenario, '')
    if event_sheet:
        event_data = data_loader.scenarios.get(event_sheet, pd.DataFrame())
        if not event_data.empty:
            context['event_details'] = event_data.to_dict('records')

    # Scenario impact pre-computation
    line_master = context.get('line_master', {})
    if scenario == 'Afternoon_Line_Breakdown':
        # Use affected_line from UI selection (L1/L2/M1/M2/M3)
        affected_line = affected_line or 'HighRange_Line1'
        description = f'Robot malfunction on {affected_line}'

        def _is_affected(k):
            if k == affected_line:
                return True
            alt = affected_line.replace('_Line', '_')
            return k == alt or k == alt.replace('_', '_Line')

        # Try multiple key formats (Excel may use MedRange_Line1 or MediumRange_Line1)
        line_info = (line_master.get(affected_line, {}) or
                     line_master.get(affected_line.replace('_Line', '_'), {}) or
                     line_master.get(affected_line.replace('MedRange', 'MediumRange'), {}))
        capacity = float(line_info.get('daily_capacity', 100))
        oee = float(line_info.get('oee', 85))
        utilization = float(line_info.get('utilization', 80))
        mttr = mttr_override if mttr_override is not None else float(line_info.get('mttr_hrs', 4))

        # Mandatory formulas (OEE included)
        effective_capacity = capacity * (oee / 100)
        actual_production = capacity * (oee / 100) * (utilization / 100)
        spare_capacity = capacity * (oee / 100) * (1 - utilization / 100)
        actual_units_lost = capacity * (oee / 100) * (utilization / 100) * (mttr / 24)

        # Remaining capacity: use formulas strictly
        # Effective_Capacity = Capacity × (OEE / 100)
        # Spare_Capacity = Capacity × (OEE / 100) × (1 − Utilization / 100)
        def _eff_cap(v):
            return float(v.get('daily_capacity', 0)) * (float(v.get('oee', 85)) / 100)
        def _spare_cap(v):
            return _eff_cap(v) * (1 - float(v.get('utilization', 80)) / 100)

        is_high_range = 'High' in line_info.get('suv_type', '') or 'HighRange' in affected_line
        if is_high_range:
            remaining_full = sum(_eff_cap(v) for k, v in line_master.items()
                               if 'High' in v.get('suv_type', '') and not _is_affected(k))
            remaining_spare = sum(_spare_cap(v) for k, v in line_master.items()
                                if 'High' in v.get('suv_type', '') and not _is_affected(k))
            remaining_label = 'HR'
        else:
            remaining_full = sum(_eff_cap(v) for k, v in line_master.items()
                               if ('Med' in v.get('suv_type', '') or 'Medium' in v.get('suv_type', '')) and not _is_affected(k))
            remaining_spare = sum(_spare_cap(v) for k, v in line_master.items()
                                if ('Med' in v.get('suv_type', '') or 'Medium' in v.get('suv_type', '')) and not _is_affected(k))
            remaining_label = 'MR'

        ev_list = context.get('event_details', [])
        event_date = ev_list[0].get('Event_Date', 'N/A') if ev_list else 'N/A'
        impact_areas = ev_list[0].get('Impact_Areas', 'High Range SUV Production') if ev_list else f'{affected_line} Production'

        context['scenario_impact'] = {
            'trigger_event': description,
            'affected_line': affected_line,
            'event_date': event_date,
            'impact_areas': impact_areas,
            'capacity_lost': capacity,
            'effective_capacity': effective_capacity,
            'actual_production': actual_production,
            'spare_capacity': spare_capacity,
            'utilization_used': utilization,
            'oee_used': oee,
            'formula_explanation': f'Units lost = {capacity} × ({oee}/100) × ({utilization}/100) × ({mttr}/24) = {actual_units_lost:.2f}',
            'actual_units_lost_during_outage': round(actual_units_lost, 2),
            'outage_duration_hours': mttr,
            'remaining_full': remaining_full,
            'remaining_spare': round(remaining_spare, 2),
            'remaining_label': remaining_label,
            'remaining_high_range_capacity': remaining_full if is_high_range else 0,
            'remaining_high_range_spare_capacity': round(remaining_spare, 2) if is_high_range else 0,
            'remaining_medium_range_capacity': remaining_full if not is_high_range else 0,
            'remaining_medium_range_spare_capacity': round(remaining_spare, 2) if not is_high_range else 0,
            'mttr_hrs': mttr,
            'workaround_options': ['Line_Swap', 'Manual_Operation'],
            'medium_range_impact': 'NOT directly affected - separate assembly lines' if is_high_range else 'Directly affected',
            'clarification': f'Line is down for {mttr} hours only (MTTR). Actual units lost = {actual_units_lost:.2f} (using OEE {oee}%, Utilization {utilization}%).',
        }
        # Synthetic event_details for Rule Engine (uses selected affected line)
        context['event_details'] = [{
            'Description': description,
            'Impact_Areas': impact_areas,
            'Event_Date': event_date,
            'Affected_Line': affected_line,
        }]

        # MTTR sensitivity: overtime, semiconductor, delivery impact
        mttr_tier = "short" if mttr <= 4 else "full_day" if mttr <= 24 else "multi_day"
        overtime_required = mttr > 8  # consider overtime if outage > 8h
        if overtime_required:
            overtime_required_reason = (
                f"When MTTR > 8h, units lost ({actual_units_lost:.2f}) exceeds same-day spare capacity ({remaining_spare:.2f} units/day). "
                "Overtime (Max_Overtime_hrs per shift) may add production capacity. "
                "Conversion of OT labor-hrs to extra units is not in master data — use as mitigation when recovery needed before dispatch dates."
            )
        else:
            overtime_required_reason = (
                f"Not required: recovery achievable within same-day spare capacity ({remaining_spare:.2f} units/day). "
                f"Units lost ({actual_units_lost:.2f}) can be absorbed."
            )
        shift_master = context.get('shift_master', {})
        overtime_capacity = {}
        overtime_labor_hrs_total = 0
        overtime_cost_per_hr_total = 0
        for sid, info in shift_master.items():
            workers = info.get('workers_assigned', 0)
            max_ot = info.get('max_overtime_hrs', 0)
            labor_cost = info.get('labor_cost_per_hr', 0)
            overtime_capacity[sid] = {
                'workers_assigned': workers,
                'max_overtime_hrs': max_ot,
                'labor_cost_per_hr': labor_cost,
                'overtime_labor_hrs': workers * max_ot,
            }
            overtime_labor_hrs_total += workers * max_ot
            overtime_cost_per_hr_total += workers * max_ot * labor_cost
        # Semiconductor: relevant when MTTR >= 24h (recovery needs other line to ramp; shortage blocks)
        semiconductor_relevant = mttr >= 24
        semiconductor_reason = (
            "Not relevant: 2h outage, quick recovery. Semiconductor lead times are days."
            if mttr < 12 else
            "Relevant: Recovery needs remaining line to ramp. Semiconductor shortage can block ramp-up."
        )
        semi_dist = context.get('semiconductor_distribution', {})
        semi_shortage = semi_dist.get('Shortage', 0) + semi_dist.get('Delayed', 0)
        semiconductor_risk = semi_shortage / max(1, len(scenario_df)) > 0.3
        # Delivery schedule impact: recovery_days based on SPARE capacity (remaining lines already at utilization)
        remaining_eff = max(remaining_spare, 0.1)  # avoid div by zero
        recovery_days = round(actual_units_lost / remaining_eff, 2) if remaining_eff > 0 else 999
        order_book = context.get('order_book', [])
        orders_at_risk_detail = []
        orders_at_risk_ids = []
        delivery_impact_text = ""
        if mttr <= 4:
            delivery_impact_text = f"Manageable: {actual_units_lost:.2f} units lost, recoverable same day. No delivery impact."
        elif actual_units_lost > 0 and remaining_eff > 0:
            if recovery_days <= 1:
                delivery_impact_text = f"Manageable: ~{recovery_days} day recovery. Low delivery impact. No orders at risk."
            else:
                # Only add orders at risk if dispatch is before recovery_complete + 4 days
                # (orders 4+ days after recovery are safe per executive summary)
                try:
                    ev_dt = pd.to_datetime(event_date) if event_date and str(event_date) != 'N/A' else None
                except Exception:
                    ev_dt = None
                recovery_complete = (ev_dt + timedelta(days=float(recovery_days))) if ev_dt else None
                cutoff_safe = (recovery_complete + timedelta(days=4)) if recovery_complete else None
                for o in sorted(order_book, key=lambda x: str(x.get('Required_Dispatch_Date', ''))):
                    if not cutoff_safe:
                        break
                    try:
                        disp_val = o.get('Required_Dispatch_Date', '')
                        if not disp_val:
                            continue
                        disp_dt = pd.to_datetime(disp_val)
                        if disp_dt < cutoff_safe:
                            orders_at_risk_detail.append({
                                'Order_ID': o.get('Order_ID', ''),
                                'Quantity': o.get('Quantity', 0),
                                'Dispatch_Date': disp_val,
                            })
                    except Exception:
                        continue
                orders_at_risk_ids = [o['Order_ID'] for o in orders_at_risk_detail]
                if recovery_days <= 3:
                    delivery_impact_text = f"Moderate impact: ~{recovery_days} days to recover. Orders due within 2-3 days may slip: {', '.join(orders_at_risk_ids[:3])}." if orders_at_risk_ids else f"Moderate impact: ~{recovery_days} days to recover. No orders at risk (dispatch dates 4+ days after recovery)."
                else:
                    delivery_impact_text = f"High impact: ~{recovery_days} days to recover. Delivery schedule at risk: {', '.join(orders_at_risk_ids[:5])}." if orders_at_risk_ids else f"High impact: ~{recovery_days} days to recover. No orders at risk (dispatch dates 4+ days after recovery)."
        context['mttr_sensitivity'] = {
            'mttr_hrs': mttr,
            'mttr_tier': mttr_tier,
            'units_lost': actual_units_lost,
            'overtime_required': overtime_required,
            'overtime_required_reason': overtime_required_reason,
            'overtime_capacity': overtime_capacity,
            'overtime_labor_hrs_total': overtime_labor_hrs_total,
            'overtime_cost_per_hr_total': overtime_cost_per_hr_total,
            'semiconductor_relevant': semiconductor_relevant,
            'semiconductor_reason': semiconductor_reason,
            'semiconductor_risk': semiconductor_risk,
            'recovery_days': recovery_days,
            'orders_at_risk': orders_at_risk_ids,
            'orders_at_risk_detail': orders_at_risk_detail,
            'delivery_impact': delivery_impact_text,
        }
    elif scenario == 'Morning_Sudden_Demand_Spike':
        peak_demand = float(scenario_df['Demand_SUVs'].max())
        avg_demand = float(scenario_df['Demand_SUVs'].mean())
        total_cap = context.get('total_plant_capacity', 450)
        capacity_gap = max(0, peak_demand - total_cap)
        # High Range capacity (sum of High Range lines) and Medium Range
        lm = context.get('line_master', {})
        hr_cap = sum(v.get('daily_capacity', 0) for k, v in lm.items() if 'High' in v.get('suv_type', ''))
        mr_cap = sum(v.get('daily_capacity', 0) for k, v in lm.items() if 'Med' in v.get('suv_type', '') or 'Medium' in v.get('suv_type', ''))
        order_book = context.get('order_book', [])
        order_total = sum(o.get('Quantity', 0) for o in order_book)
        can_fulfill_500 = (total_cap >= 500 + avg_demand) if avg_demand else (total_cap >= 500)
        context['scenario_impact'] = {
            'trigger_event': 'Europe dealer requests 500 High Range SUVs - 180% demand increase',
            'peak_demand': peak_demand,
            'avg_demand': avg_demand,
            'total_plant_capacity': total_cap,
            'high_range_capacity': hr_cap or 190,
            'medium_range_capacity': mr_cap or 345,
            'capacity_gap': capacity_gap,
            'order_book_total_quantity': order_total,
            'can_fulfill_500_spike': can_fulfill_500,
            'affected_lines': 'HighRange_1, HighRange_2',
            'workaround_options': ['INCREASE_SHIFT', 'Overtime', 'Line reallocation'],
        }
    elif scenario == 'Midday_Semiconductor_Shortage':
        semi_dist = context.get('semiconductor_distribution', {})
        semi_mode = context.get('semiconductor_availability', 'Available')
        context['scenario_impact'] = {
            'trigger_event': 'Chip supplier reports critical semiconductor shortage - 48hr delay',
            'semiconductor_status': semi_mode,
            'semiconductor_distribution': semi_dist,
            'delay_hours': 48,
            'affected_lines': 'High Range SUV production',
            'workaround_options': ['SWITCH_SUPPLIER', 'Expedite shipment', 'Buffer inventory'],
        }
    else:
        context['scenario_impact'] = {'trigger_event': scenario.replace('_', ' ')}

    return context


# =====================================================================
# DISPLAY RESULTS
# =====================================================================
def _display_full_results(analysis, scenario_df):
    """Display the complete analysis pipeline results."""
    st.markdown("---")
    st.markdown("## Analysis Results")

    model_used = analysis.get('model_used', 'Unknown')
    st.markdown(f"""
    <div style="background: #f0f2f6; border-radius: 8px; padding: 0.5rem 1rem; margin-bottom: 1rem;">
        Model: <b>{model_used}</b> | Pipeline: Rule Engine + ML Models + Multi-Agent AI
    </div>
    """, unsafe_allow_html=True)

    # --- Executive Summary ---
    crew_result = analysis.get('crew_result', {})
    exec_summary = crew_result.get('executive_summary', '')
    if exec_summary:
        st.markdown(f"""
        <div style="background: #e8f4fd; border-radius: 10px; padding: 1.2rem;
                    border-left: 5px solid #3498db;">
            <h4 style="margin: 0 0 0.5rem;">Executive Summary</h4>
            {exec_summary}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

    # --- Event Details ---
    context = analysis.get('context', {})
    event_details = context.get('event_details', [])
    si = context.get('scenario_impact', {})
    if event_details or si:
        st.markdown("### Scenario Event")
        if event_details:
            ev = event_details[0]
            description = ev.get('Description', ev.get('Event_Type', 'N/A'))
            affected_area = ev.get('Impact_Areas', ev.get('Affected_Line', si.get('affected_line', 'N/A')))
            impact_level = ev.get('Expected_Impact', ev.get('Impact_Level', 'N/A'))
            event_date = ev.get('Event_Date', 'N/A')
            est_repair = f"{si.get('mttr_hrs', 'N/A')} hours (MTTR from master data)" if si.get('mttr_hrs') else 'N/A'
            workaround = ', '.join(si.get('workaround_options', [])) if si.get('workaround_options') else 'N/A'
            st.markdown(f"""
            <div style="background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px; padding: 1rem;">
                <b>Event:</b> {description}<br>
                <b>Event Date:</b> {si.get('event_date', event_date)} (from Event_Line_Breakdown data)<br>
                <b>Affected Area:</b> {affected_area}<br>
                <b>Affected Line:</b> {si.get('affected_line', 'N/A')}<br>
                <b>Estimated Repair (MTTR):</b> {est_repair}<br>
                <b>Workaround Options:</b> {workaround}<br>
                <b>Impact Level:</b> {impact_level}
            </div>
            """, unsafe_allow_html=True)
        elif si:
            st.info(si.get('trigger_event', ''))

        # Impact table (below scenario event) — formulas: Effective_Capacity, Spare_Capacity, Units_Lost
        if si.get('capacity_lost') or si.get('actual_units_lost_during_outage') is not None:
            rl = si.get('remaining_label', 'HR')
            impact_table = pd.DataFrame([
                {"Metric": "Units Lost (during outage)", "Value": f"{_fmt2(si.get('actual_units_lost_during_outage', 0))} units"},
                {"Metric": "Affected line capacity", "Value": f"{_fmt2(si.get('capacity_lost', 0))} units/day"},
                {"Metric": f"Remaining {rl} (full)", "Value": f"{_fmt2(si.get('remaining_full', si.get('remaining_high_range_capacity', 0)))} units/day"},
                {"Metric": f"Remaining {rl} (spare)", "Value": f"{_fmt2(si.get('remaining_spare', si.get('remaining_high_range_spare_capacity', 0)))} units/day"},
                {"Metric": "Est. Repair (MTTR)", "Value": f"{_fmt2(si.get('mttr_hrs', 0))} hours"},
            ])
            st.dataframe(impact_table, hide_index=True, use_container_width=True)
            st.caption("Formulas: Effective_Capacity = Capacity × (OEE/100); Spare_Capacity = Capacity × (OEE/100) × (1 − Utilization/100); Units_Lost = Capacity × (OEE/100) × (Utilization/100) × (MTTR/24)")

        mttr_sens = context.get('mttr_sensitivity', {})
        if mttr_sens:
            with st.expander("MTTR Sensitivity Analysis", expanded=True):
                st.markdown(f"**Formula:** {si.get('formula_explanation', 'N/A')}")
                ul_val = mttr_sens.get('units_lost', 0)
                rd_val = mttr_sens.get('recovery_days', 0)
                st.markdown(f"**Tier:** {mttr_sens.get('mttr_tier', 'N/A')} | **Units lost:** {_fmt2(ul_val)} | **Recovery days:** ~{_fmt2(rd_val)}")
                st.markdown(f"**Delivery schedule:** {mttr_sens.get('delivery_impact', 'N/A')}")
                st.markdown(f"**Semiconductor relevant?** {mttr_sens.get('semiconductor_relevant', False)} — {mttr_sens.get('semiconductor_reason', '')}")
                st.markdown(f"**Overtime required:** {mttr_sens.get('overtime_required', False)} | **Total OT capacity:** {mttr_sens.get('overtime_labor_hrs_total', 0)} labor-hrs/day")
                if mttr_sens.get('overtime_required') and mttr_sens.get('overtime_required_reason'):
                    st.caption(f"*Why:* {mttr_sens['overtime_required_reason']}")
                orders_at_risk = mttr_sens.get('orders_at_risk', [])
                if orders_at_risk:
                    st.markdown(f"**Orders at risk:** {', '.join(str(x) for x in orders_at_risk[:5])}")
                else:
                    st.markdown("**Orders at risk:** None (recovery achievable before dispatch dates)")
            with st.expander("MTTR Comparison: 2h vs 24h vs 48h", expanded=False):
                util = si.get('utilization_used', 80)
                cap = si.get('capacity_lost', 90)
                oee = si.get('oee_used', 85)
                rem_spare = si.get('remaining_spare', si.get('remaining_high_range_spare_capacity', 15))
                for mh in [2, 24, 48]:
                    ul = round(cap * (oee/100) * (util/100) * (mh/24), 2)
                    rd = round(ul / rem_spare, 2) if rem_spare and rem_spare > 0 else 'N/A'
                    semi = "No" if mh < 12 else "Yes"
                    st.markdown(f"- **MTTR {mh}h:** Units lost={_fmt2(ul)}, Recovery~{rd} days (using spare capacity), Semiconductor relevant={semi}")

    st.markdown("---")

    # --- Tabbed sections ---
    tab_rules, tab_ml, tab_recs, tab_agents, tab_log, tab_data = st.tabs([
        "⚙️ Rule Engine Results",
        "🧠 ML Predictions",
        "📌 Recommendations",
        "🤖 Agent Analysis",
        "📋 Decision Log",
        "📊 Raw Data",
    ])

    with tab_rules:
        _display_rule_engine(analysis['rule_output'])

    with tab_ml:
        _display_ml_predictions(analysis['ml_output'])

    with tab_recs:
        _display_recommendations(analysis['recommendations'], analysis['rule_output'], context)

    with tab_agents:
        _display_agent_outputs(analysis['crew_result'])

    with tab_log:
        _display_decision_log(analysis['decision_log'])

    with tab_data:
        _display_raw_data(scenario_df, context)


# =====================================================================
# RULE ENGINE DISPLAY
# =====================================================================
def _display_rule_engine(rule_output: RuleEngineOutput):
    st.markdown("### Rule Engine / Decision Logic")
    st.markdown("*Deterministic threshold checks evaluated against plant data. No AI guessing.*")

    # Overall severity badge
    sev = rule_output.overall_severity
    sev_color = {'LOW': '#2ecc71', 'MEDIUM': '#f39c12', 'HIGH': '#e74c3c', 'CRITICAL': '#c0392b'}.get(sev, '#95a5a6')
    st.markdown(f"""
    <div style="display:inline-block; background:{sev_color}; color:white; padding:4px 16px;
                border-radius:8px; font-weight:bold; margin-bottom:1rem;">
        Overall Severity: {sev} &mdash; {len(rule_output.triggered_rules)} rules triggered
    </div>
    """, unsafe_allow_html=True)

    # Triggered rules
    if rule_output.triggered_rules:
        st.markdown("#### Triggered Rules")
        for r in rule_output.triggered_rules:
            rc = {'LOW': '#2ecc71', 'MEDIUM': '#f39c12', 'HIGH': '#e74c3c', 'CRITICAL': '#c0392b'}.get(r.severity, '#95a5a6')
            st.markdown(f"""
            <div style="background: {rc}10; border-left: 4px solid {rc}; border-radius: 8px;
                        padding: 0.8rem; margin: 0.5rem 0;">
                <b style="color:{rc};">[{r.severity}] {r.rule_name}</b> &rarr; <code>{r.action}</code><br>
                <span style="font-size:0.9rem;">{r.condition}</span><br>
                <span style="font-size:0.8rem; color:#666;">{r.details}</span>
            </div>
            """, unsafe_allow_html=True)

    # AI Recommendation Logic mapping
    st.markdown("#### AI Recommendation Logic (from architecture)")
    logic_map = [
        ("Demand spike", "Increase shift", "INCREASE_SHIFT" in rule_output.recommended_actions),
        ("Chip delay / shortage", "Switch supplier", "SWITCH_SUPPLIER" in rule_output.recommended_actions),
        ("Low machine health", "Dispatch maintenance", "DISPATCH_MAINTENANCE" in rule_output.recommended_actions),
        ("Overload", "Reallocate line", "REALLOCATE_LINE" in rule_output.recommended_actions),
        ("Low inventory", "Raise supply alert", "RAISE_SUPPLY_ALERT" in rule_output.recommended_actions),
    ]
    for condition, action, fired in logic_map:
        icon = "🔴" if fired else "⚪"
        st.markdown(f"{icon} **{condition}** → {action} {'**(TRIGGERED)**' if fired else ''}")

    # Logic: condition → threshold → actual
    with st.expander("Logic: Condition → Threshold → Actual", expanded=False):
        for r in rule_output.all_results:
            st.markdown(f"**{r.rule_name}** (threshold={r.threshold}, actual={r.actual_value}): {r.condition}")

    # All rules table
    with st.expander("View all evaluated rules", expanded=False):
        rows = []
        for r in rule_output.all_results:
            rows.append({
                "Rule": r.rule_name, "Triggered": "YES" if r.triggered else "no",
                "Severity": r.severity, "Action": r.action,
                "Condition": r.condition[:80],
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


# =====================================================================
# ML PREDICTIONS DISPLAY
# =====================================================================
def _display_ml_predictions(ml_output: MLPredictions):
    st.markdown("### ML Model Predictions")
    st.markdown(f"*Models trained: {'Yes (scikit-learn)' if ml_output.models_trained else 'No (using heuristic fallback)'}*")

    with st.expander("ML Training Summary & How Delay Risk is Used", expanded=False):
        st.markdown("""
**Training Data:** Simulation data from Pune_EV_SUV_Plant_Simulation_Data_Expanded.xlsx (Train + Validation + Test, ~1000 records).

**Breakdown Model:** RandomForestClassifier. Features: Machine_Uptime_%, Worker_Availability_%, Defect_Rate_%, Energy_Consumption_kWh. Target: Alert_Status (Maintenance_Alert vs None). Output: probability per line.

**Delay Model:** GradientBoostingRegressor (or heuristic fallback). Features: Inventory_Status_%, Machine_Uptime_%, Worker_Availability_%, Defect_Rate_%. Target: Predicted_KPI_Impact_%. Formula: risk_score = 1 - (Predicted_KPI_Impact_% / 10), clamped to 0–1. Higher risk = more likely delivery delay.

**Where Used:** Delay risk is passed to Inventory Controller and Supply Chain Monitor agents. It informs semiconductor shortage impact and supplier-switch decisions. Breakdown risk informs Line Health Analyst.
        """)

    st.markdown("**What is Breakdown Prediction?** Probability (0–100%) that an assembly line will trigger a maintenance alert in the near term. Based on Machine_Uptime_%, Worker_Availability_%, Defect_Rate_%, Energy_Consumption. Higher % = higher likelihood of failure; used by Line Health Analyst to prioritise maintenance.")
    st.markdown("**What is Delivery Delay Risk?** Likelihood (0–100%) that delivery schedules will slip due to inventory levels, semiconductor availability, worker availability, or defect rates. Informs Supply Chain and Inventory agents; HIGH risk suggests supplier buffering or expediting.")
    st.markdown("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Breakdown Prediction")
        if ml_output.breakdown_predictions:
            bd_rows = [{"Line": bp.line, "Risk (%)": _fmt2(bp.probability * 100, pct=True), "Level": bp.risk_level,
                       "Factors": ", ".join(bp.contributing_factors) if bp.contributing_factors else "-"}
                      for bp in ml_output.breakdown_predictions]
            st.dataframe(pd.DataFrame(bd_rows), hide_index=True, use_container_width=True)
        else:
            st.info("No breakdown predictions available.")

    with col2:
        st.markdown("#### Delay Risk (per line)")
        if ml_output.delay_predictions:
            dl_rows = [{"Line": dp.line, "Delay Risk (%)": _fmt2(dp.risk_score * 100, pct=True), "Level": dp.risk_level}
                      for dp in ml_output.delay_predictions]
            st.dataframe(pd.DataFrame(dl_rows), hide_index=True, use_container_width=True)
        elif ml_output.delay_prediction:
            dp = ml_output.delay_prediction
            st.dataframe(pd.DataFrame([{"Line": dp.line or "Overall", "Delay Risk (%)": _fmt2(dp.risk_score * 100, pct=True), "Level": dp.risk_level}]), hide_index=True)
        else:
            st.info("No delay predictions available.")

    st.markdown("---")
    st.markdown("#### Supplier Analysis")
    if ml_output.supplier_risks:
        # Top = stable delivery, low delay risk (higher score)
        # High-risk = high delay probability, frequent shortages, longer lead times (lower score)
        sorted_suppliers = sorted(ml_output.supplier_risks, key=lambda s: s.score, reverse=True)
        n = len(sorted_suppliers)
        top_count = max(1, min(n - 1, int(n * 0.6)))  # top 60%, ensure at least 1 in high-risk if n>1
        top_suppliers = sorted_suppliers[:top_count]
        high_risk_suppliers = sorted_suppliers[top_count:] if n > 1 else []

        st.markdown("**Top Suppliers** — Suppliers with stable delivery and low delay risk")
        if top_suppliers:
            top_rows = [{"Supplier": sr.supplier_name, "Score": f"{_fmt2(sr.score)}/100", "Risk": sr.risk_level,
                        "Lead Time (days)": getattr(sr, 'lead_time_days', '-'), "Reliability (%)": _fmt2(getattr(sr, 'reliability', 0), pct=True)}
                       for sr in top_suppliers[:8]]
            st.dataframe(pd.DataFrame(top_rows), hide_index=True, use_container_width=True)
        else:
            st.caption("None identified.")

        st.markdown("")
        st.markdown("**High-Risk Suppliers** — Suppliers with high delay probability, frequent shortages, longer lead times")
        if high_risk_suppliers:
            hr_rows = [{"Supplier": sr.supplier_name, "Score": f"{_fmt2(sr.score)}/100", "Risk": sr.risk_level,
                       "Lead Time (days)": getattr(sr, 'lead_time_days', '-'), "Reliability (%)": _fmt2(getattr(sr, 'reliability', 0), pct=True)}
                      for sr in high_risk_suppliers[:8]]
            st.dataframe(pd.DataFrame(hr_rows), hide_index=True, use_container_width=True)
        else:
            st.caption("None identified.")


# =====================================================================
# RECOMMENDATIONS DISPLAY
# =====================================================================
# KPI action map for Calculation Logic display (matches decision_log._ACTION_KPI_MAP)
_ACTION_KPI_MAP_DISPLAY = {
    "DISPATCH_MAINTENANCE": "Line Downtime: +2-8 hrs; On-time Delivery: -5 to -15%",
    "REALLOCATE_LINE": "On-time Delivery: -3 to -10%; Production Efficiency: -15 to -25%",
    "SWITCH_SUPPLIER": "Lead Time: +2-5 days; Inventory Cost: +5 to +10%",
    "INCREASE_SHIFT": "Overtime Cost: +12 to +18%; Worker Availability: +2 to +5%",
    "RAISE_SUPPLY_ALERT": "Inventory Risk: stockout within 2-4 days if not addressed",
}


def _display_recommendations(recommendations, rule_output, context):
    st.markdown("### Actionable Recommendations")
    kpi = context.get('predicted_kpi_impact', 0)
    st.markdown(f"""
    <div style="background: #e8f4fd; border-radius: 8px; padding: 0.8rem; margin-bottom: 1rem; font-size: 0.85rem;">
        <b>How these were generated:</b><br>
        1. Rule Engine identified {len(rule_output.triggered_rules)} triggered rules<br>
        2. ML models provided breakdown & delay risk scores<br>
        3. AI agents synthesised everything into prioritised actions<br>
        4. KPI baseline from data: <code>Predicted_KPI_Impact_%</code> = <b>{_fmt2(kpi, pct=True)}</b>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("How is priority decided?", expanded=False):
        st.markdown("""
**Priority logic (1 = highest, 5 = lowest):**

- **Priority 1** — Immediate operational risk: Line down, maintenance dispatch, critical repair. Must restore production before recovery planning.
- **Priority 2** — Production recovery: Reallocate lost units to remaining lines, meet dispatch dates.
- **Priority 3** — Supply chain: Supplier switch, semiconductor buffer, expediting. Addresses component availability.
- **Priority 4** — Workforce: Overtime, shift adjustments, availability. Supports recovery capacity.
- **Priority 5** — Preventive: Inspections, health checks, buffers. Reduces future risk.

The Decision Orchestrator orders recommendations by urgency: restore production first, then supply chain and workforce, then preventive actions.""")

    # Calculation Logic expander
    with st.expander("What is KPI & How is it Calculated?", expanded=False):
        st.markdown("""
**KPI (Key Performance Indicator)** measures plant performance: On-time Delivery %, Line Downtime, Overtime Cost, Production Efficiency, etc.

**Calculation sources:**
- *Predicted_KPI_Impact_%*: From simulation data — average predicted % change in KPI for the scenario.
- *KPI_Summary* (master data): Before_Optimization_%, After_Optimization_%, Improvement_% for each KPI.
- *expected_kpi_impact* per action: Derived from rule-action mapping (e.g. DISPATCH_MAINTENANCE → Line Downtime impact) or from simulation improvement when action aligns with data.

**Interpretation:** Positive % = improvement (e.g. +4.65% on-time delivery). Negative % = degradation (e.g. -15% line downtime during outage). Values trace to simulation or master data.""")

    with st.expander("Calculation Logic — KPIs, Overtime, and Factors Considered", expanded=False):
        st.markdown("**KPI Impact Derivation (from rule actions):**")
        for action, impact in _ACTION_KPI_MAP_DISPLAY.items():
            fired = action in rule_output.recommended_actions
            st.markdown(f"- `{action}` → {impact} {'**(triggered)**' if fired else ''}")
        st.markdown("")
        shift_master = context.get('shift_master', {})
        if shift_master:
            st.markdown("**Overtime Factors (from Shift_Master):**")
            for sid, info in shift_master.items():
                st.markdown(f"- **{sid}**: Max_Overtime_hrs = {info.get('max_overtime_hrs', 'N/A')}h, Labor_Cost_per_hr = {info.get('labor_cost_per_hr', 'N/A')}")
        si = context.get('scenario_impact', {})
        if si.get('mttr_hrs') or si.get('actual_units_lost_during_outage'):
            st.markdown("**Scenario Impact (used in recommendations):**")
            st.markdown(f"- MTTR: {si.get('mttr_hrs', 'N/A')} hours | Units lost during outage: {si.get('actual_units_lost_during_outage', 'N/A')}")

    for i, rec in enumerate(recommendations, 1):
        priority = rec.get('priority', 3)
        if isinstance(priority, str):
            try:
                priority = int(priority)
            except ValueError:
                priority = 3
        # Priority 1=highest, 5=lowest; 1-2=HIGH, 3=MEDIUM, 4-5=LOW
        p_color = '#e74c3c' if priority <= 2 else '#f39c12' if priority <= 3 else '#2ecc71'
        p_label = 'HIGH' if priority <= 2 else 'MEDIUM' if priority <= 3 else 'LOW'

        action = rec.get('action', 'Recommended Action')
        reasoning = rec.get('reasoning', rec.get('why', ''))
        source = rec.get('source_agent', rec.get('agent', 'AI Agent'))
        timeline = rec.get('estimated_time', rec.get('timeline', ''))

        st.markdown(f"""
        <div style="background: #f8f9fa; border-left: 5px solid {p_color};
                    border-radius: 8px; padding: 1.2rem; margin: 0.8rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin:0;">#{i} {action}</h4>
                <span style="background: {p_color}; color: white; padding: 2px 10px;
                             border-radius: 12px; font-size: 0.8rem;">{p_label} PRIORITY</span>
            </div>
            <table style="width:100%; margin-top: 0.5rem; font-size: 0.9rem;">
                <tr><td style="width:160px; color:#888;"><b>Source Agent:</b></td><td>{source}</td></tr>
                {'<tr><td style="color:#888;"><b>Why:</b></td><td>' + reasoning + '</td></tr>' if reasoning else ''}
                {'<tr><td style="color:#888;"><b>Timeline:</b></td><td>' + timeline + '</td></tr>' if timeline else ''}
            </table>
        </div>
        """, unsafe_allow_html=True)


# =====================================================================
# AGENT OUTPUTS DISPLAY
# =====================================================================
def _extract_agent_summary(text: str, max_chars: int = 350) -> str:
    """Extract Overview section or first paragraph for quick summary. Strip markdown headers."""
    if not text or not isinstance(text, str):
        return ""
    text = text.strip()
    import re
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    for marker in ["Overview:", "Overview :", "**Overview**", "Summary:", "Summary :", "Executive Summary"]:
        if marker.lower() in text.lower():
            idx = text.lower().find(marker.lower())
            rest = text[idx + len(marker):].strip()
            para = rest.split("\n\n")[0] if "\n\n" in rest else rest.split("\n")[0]
            summary = para.strip()[:max_chars]
            return summary + ("..." if len(para) > max_chars else "")
    first_para = text.split("\n\n")[0].strip() if "\n\n" in text else text.split("\n")[0].strip()
    return first_para[:max_chars] + ("..." if len(first_para) > max_chars else "")


def _display_agent_outputs(crew_result):
    st.markdown("### Multi-Agent Analysis")

    agent_outputs = crew_result.get('agent_outputs', {})
    if not agent_outputs:
        st.info("Agent outputs not available (agents may have used fallback pipeline).")
        # Show the raw result instead
        raw = crew_result.get('raw_result', '')
        if raw:
            st.markdown("#### Integrated Analysis")
            st.markdown(raw)
        justification = crew_result.get('decision_justification', '')
        if justification:
            st.markdown("#### Decision Justification")
            st.markdown(str(justification))
        return

    agent_labels = {
        'line_health': ('⚙️', 'Line Health Analyst'),
        'production': ('🏭', 'Production Planner'),
        'inventory': ('📦', 'Inventory Controller'),
        'workforce': ('👥', 'Workforce Coordinator'),
        'supply_chain': ('🚚', 'Supply Chain Monitor'),
        'orchestrator': ('🎯', 'Decision Orchestrator'),
    }

    for key, output_text in agent_outputs.items():
        if not output_text:
            continue
        icon, label = agent_labels.get(key, ('🤖', key.replace('_', ' ').title()))
        summary = _extract_agent_summary(output_text, max_chars=400) if output_text else ""
        with st.expander(f"{icon} {label}", expanded=(key == 'orchestrator')):
            st.markdown(output_text)
            if summary:
                st.markdown("---")
                st.markdown("**Summary:**")
                st.markdown(summary)


# =====================================================================
# DECISION LOG DISPLAY
# =====================================================================
def _display_decision_log(decision_log: DecisionLog):
    st.markdown("### AI Decision Log")
    st.markdown("*Full traceability: which rules triggered, what thresholds were breached, why each recommendation was selected.*")

    if not decision_log.entries:
        st.info("No decision log entries.")
        return

    # Summary table
    log_df = decision_log.to_dataframe()
    st.dataframe(log_df, hide_index=True, width="stretch")

    # Detailed entries
    for entry in decision_log.entries:
        with st.expander(f"{entry.decision_id}: {entry.recommendation[:80]}"):
            st.markdown(f"**Agent:** {entry.agent_source}")
            st.markdown(f"**Reasoning:** {entry.reasoning}")
            st.markdown(f"**KPI Impact:** {entry.expected_kpi_impact}")

            if entry.thresholds_breached:
                st.markdown("**Thresholds Breached:**")
                for tb in entry.thresholds_breached:
                    st.markdown(f"- {tb}")

            if entry.supporting_indicators:
                st.markdown("**Supporting Indicators:**")
                for si in entry.supporting_indicators:
                    st.markdown(f"- {si}")

            if hasattr(entry, 'logic_trace') and entry.logic_trace:
                st.markdown("**Logic Trace (rules, ML, master data):**")
                for lt in entry.logic_trace:
                    st.markdown(f"- {lt}")

    # Export
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download Decision Log (JSON)",
            decision_log.to_json(),
            file_name=f"decision_log_{decision_log.scenario}_{decision_log.run_id}.json",
            mime="application/json",
        )
    with col2:
        csv = log_df.to_csv(index=False)
        st.download_button(
            "Download Decision Log (CSV)",
            csv,
            file_name=f"decision_log_{decision_log.scenario}_{decision_log.run_id}.csv",
            mime="text/csv",
        )


# =====================================================================
# VALIDATION DISPLAY
# =====================================================================
def _display_validation(validation_report):
    """Display validation report: passed/failed checks and details."""
    if validation_report is None:
        st.info("No validation report available.")
        return

    st.markdown("### Output Validation")
    st.markdown("*Checks that rule outputs, ML outputs, and recommendations are within expected ranges.*")

    overall = validation_report.overall_passed
    color = '#2ecc71' if overall else '#e74c3c'
    st.markdown(f"""
    <div style="display:inline-block; background:{color}; color:white; padding:6px 20px;
                border-radius:8px; font-weight:bold; margin-bottom:1rem;">
        Overall: {'PASSED' if overall else 'FAILED'}
    </div>
    """, unsafe_allow_html=True)

    for c in validation_report.checks:
        icon = "✓" if c.passed else "✗"
        ccolor = '#2ecc71' if c.passed else '#f39c12' if c.severity == 'warning' else '#e74c3c'
        st.markdown(f"""
        <div style="background: {ccolor}15; border-left: 4px solid {ccolor}; border-radius: 6px;
                    padding: 0.6rem; margin: 0.4rem 0;">
            <b>{icon} {c.name}</b> — {c.detail}
        </div>
        """, unsafe_allow_html=True)


# =====================================================================
# RAW DATA DISPLAY
# =====================================================================
def _display_raw_data(scenario_df, context):
    st.markdown("### Raw Data Records")
    st.markdown(f"*{len(scenario_df)} records from this scenario.*")

    # Data Sources and Usage - expandable
    with st.expander("Data Sources and Usage — How Both Data Are Combined", expanded=False):
        st.markdown("""
**This system uses two data sources that are combined in the context builder:**

| Data Source | Tables/Columns | Where Used | Purpose |
|-------------|----------------|------------|---------|
| **Simulation Data** | Demand_SUVs, Production_Output, Machine_Uptime_%, Worker_Availability_%, Inventory_Status_%, Defect_Rate_%, Semiconductor_Availability, Alert_Status, Predicted_KPI_Impact_% | Rule Engine, ML Models, Context | Threshold checks, breakdown/delay prediction, scenario metrics |
| **Master Data** | Assembly_Line_Master (capacity, OEE, MTTR, MTBF) | Rule Engine, Context, Scenario Impact | Capacity lost, repair time, overload check |
| **Master Data** | Shift_Master (workers, Max_Overtime_hrs, Labor_Cost_per_hr) | AI Agents (Workforce), Context | Overtime limits, reallocation |
| **Master Data** | Supplier_Master, Inventory_Master | Rule Engine, ML (supplier risk), AI Agents | Semiconductor risk, reorder decisions |
| **Master Data** | Order_Data | AI Agents (Production) | Prioritize by Required_Dispatch_Date |
| **Master Data** | KPI_Summary | AI Agents (Orchestrator) | Ground KPI impact claims |
| **Event Data** | Event_Line_Breakdown, Event_Demand_Spike, Event_Chip_Delay | Context, Rule Engine | Scenario trigger, affected line |

**Flow:** Scenario records → `_build_context()` merges with master tables → Rule Engine + ML Models + AI Agents receive combined context.
        """)

    display_cols = [
        'Assembly_Line', 'Shift', 'Demand_SUVs', 'Production_Output',
        'Machine_Uptime_%', 'Worker_Availability_%', 'Inventory_Status_%',
        'Defect_Rate_%', 'Semiconductor_Availability', 'Alert_Status',
        'Predicted_KPI_Impact_%',
    ]
    available = [c for c in display_cols if c in scenario_df.columns]
    st.dataframe(scenario_df[available], hide_index=True, width="stretch", height=400)

    # Key metrics (2 decimal places)
    st.markdown("#### Key Metrics Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Machine Uptime", _fmt2(scenario_df['Machine_Uptime_%'].mean(), pct=True))
    with col2:
        st.metric("Avg Worker Avail.", _fmt2(scenario_df['Worker_Availability_%'].mean(), pct=True))
    with col3:
        st.metric("Avg Inventory", _fmt2(scenario_df['Inventory_Status_%'].mean(), pct=True))
    with col4:
        st.metric("Avg Defect Rate", _fmt2(scenario_df['Defect_Rate_%'].mean(), pct=True))

    # Master data reference
    with st.expander("Master Data Reference"):
        line_master = context.get('line_master', {})
        if line_master:
            st.markdown("**Assembly Line Master:**")
            rows = []
            for name, info in line_master.items():
                rows.append({
                    'Line': name, 'Type': info.get('suv_type', ''),
                    'Capacity': f"{info.get('daily_capacity', 0)}/day",
                    'OEE': _fmt2(info.get('oee', 0), pct=True),
                    'MTTR': f"{info.get('mttr_hrs', 0)}h",
                })
            st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

        shift_master = context.get('shift_master', {})
        if shift_master:
            st.markdown("**Shift Master:**")
            rows = []
            for sid, info in shift_master.items():
                rows.append({
                    'Shift': sid, 'Timing': info.get('timing', ''),
                    'Workers': info.get('workers_assigned', 0),
                    'Max OT': f"{info.get('max_overtime_hrs', 0)}h",
                })
            st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
