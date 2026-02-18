"""
Multi-Agent AI Analysis for Use Case 3 (Afternoon Line Breakdown)

Uses Azure OpenAI GPT-5.1-chat DIRECTLY via the openai SDK.
Each agent is a specialised prompt function — no CrewAI LLM wrapper needed.

Agents:
  1. Line Health Analyst     – machine uptime, breakdown assessment
  2. Production Planner      – line reallocation, capacity planning
  3. Inventory Controller    – stock impact, reorder needs
  4. Workforce Coordinator   – shift reallocation, overtime
  5. Supply Chain Monitor    – supplier risk, component availability
  6. Decision Orchestrator   – integrates all, generates final plan
"""

from __future__ import annotations

import os
import json
import time
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

from openai import AzureOpenAI
from src.engine.rule_engine import RuleEngineOutput
from src.engine.ml_models import MLPredictions


# ---------------------------------------------------------------------------
# Azure OpenAI client — exactly the pattern you shared
# ---------------------------------------------------------------------------
def _get_client():
    """Create Azure OpenAI client using the direct SDK."""
    endpoint = os.getenv(
        "AZURE_OPENAI_ENDPOINT",
        "https://capstonebatch4-resource.cognitiveservices.azure.com/",
    )
    api_key = os.getenv("AZURE_OPENAI_KEY", "")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    if not api_key:
        raise ValueError("AZURE_OPENAI_KEY not set in .env")

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
    )
    return client


def _get_deployment() -> str:
    return os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.1-chat")


# ---------------------------------------------------------------------------
# Generic agent call (direct SDK — no CrewAI, no litellm)
# ---------------------------------------------------------------------------
def _call_agent(
    client: AzureOpenAI,
    deployment: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 8192,
) -> str:
    """Call Azure OpenAI with a specific agent role."""
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_completion_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"  [Agent] Error: {e}")
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Agent system prompts
# ---------------------------------------------------------------------------
NO_SUGGESTION = " Do NOT ask if the user wants more analysis, additional features, or anything else. Do NOT suggest adding more."

AGENT_SYSTEM_PROMPTS = {
    "line_health": (
        "You are a senior maintenance engineer (Line Health Analyst) at the Pune EV SUV plant. "
        "You monitor OEE, MTTR, MTBF, and sensor data to detect failures early. "
        "Provide structured analysis with specific numbers from the data."
        + NO_SUGGESTION
    ),
    "production": (
        "You are the head of production planning (Production Planner) at the Pune EV SUV plant. "
        "You know every line's capacity, current orders, and decide which lines pick up slack "
        "when another goes offline. Never suggest rates exceeding actual line capacities."
        + NO_SUGGESTION
    ),
    "inventory": (
        "You are the inventory controller at the Pune EV SUV plant. "
        "You manage 120+ items, track safety stock, reorder points, and lead times "
        "for every component. Provide specific stock-level recommendations."
        + NO_SUGGESTION
    ),
    "workforce": (
        "You are the HR operations lead (Workforce Coordinator) at the Pune EV SUV plant. "
        "You manage 320 workers across 3 shifts (A, B, C) and decide overtime, "
        "cross-training, and temporary staffing. Reference actual shift data."
        + NO_SUGGESTION
    ),
    "supply_chain": (
        "You are the supply chain manager at the Pune EV SUV plant. "
        "You manage 20 suppliers, track lead times and reliability scores, "
        "and have alternate supplier contacts. Provide specific supplier recommendations."
        + NO_SUGGESTION
    ),
    "orchestrator": (
        "You are the plant director (Decision Orchestrator) at the Pune EV SUV plant. "
        "You synthesise recommendations from maintenance, production, inventory, "
        "workforce, and supply chain into an executive action plan. "
        "Always respond in valid JSON with keys: executive_summary, recommendations, decision_justification."
        + NO_SUGGESTION
    ),
}


# ---------------------------------------------------------------------------
# Build agent prompts
# ---------------------------------------------------------------------------
def _build_agent_prompts(
    rule_output: RuleEngineOutput,
    ml_output: MLPredictions,
    context: Dict[str, Any],
) -> Dict[str, str]:
    """Build user prompts for each agent with comprehensive master data."""

    rule_summary = rule_output.summary_text()

    ml_breakdown = "\n".join(
        f"  {b.line}: {b.probability*100:.2f}% risk ({b.risk_level})"
        for b in ml_output.breakdown_predictions[:5]
    ) or "No breakdown predictions available."

    # Line-wise delay risk
    if ml_output.delay_predictions:
        ml_delay = "Delay risk per line:\n" + "\n".join(
            f"  {d.line}: {d.risk_score*100:.2f}% ({d.risk_level})"
            for d in ml_output.delay_predictions[:5]
        )
    elif ml_output.delay_prediction:
        dp = ml_output.delay_prediction
        ml_delay = f"Delay risk: {dp.risk_score*100:.2f}% ({dp.risk_level})"
    else:
        ml_delay = "No delay prediction."

    supplier_info = "\n".join(
        f"  {s.supplier_name}: safety score {s.score:.2f}/100 ({s.risk_level})"
        for s in ml_output.supplier_risks[:5]
    ) or "No supplier data."

    event = context.get("event_details", [{}])
    event_str = str(event[0]) if event else "No event data"

    line_master = context.get("line_master", {})
    shift_master = context.get("shift_master", {})
    scenario_impact = context.get("scenario_impact", {})
    impact_str = "\n".join(f"  {k}: {v}" for k, v in scenario_impact.items()) if scenario_impact else "N/A"

    mttr_sensitivity = context.get("mttr_sensitivity", {})
    mttr_str = json.dumps(mttr_sensitivity, indent=2, default=str) if mttr_sensitivity else "N/A"

    # Additional master data for comprehensive prompts
    suppliers = context.get("suppliers", [])
    suppliers_str = json.dumps(suppliers[:10], indent=2, default=str) if suppliers else "No supplier master data."

    inventory_summary = context.get("inventory_master_summary", {})
    inv_summary_str = json.dumps(inventory_summary, indent=2, default=str) if inventory_summary else "No inventory master summary."

    machine_params = context.get("machine_params_summary", {})
    machine_str = json.dumps(machine_params, indent=2, default=str) if machine_params else "No machine parameter data."

    order_book = context.get("order_book", [])
    # Show first 10 orders sorted by dispatch date
    order_str = json.dumps(order_book[:10], indent=2, default=str) if order_book else "No order data."

    kpi_targets = context.get("kpi_targets", [])
    kpi_str = json.dumps(kpi_targets, indent=2, default=str) if kpi_targets else "No KPI targets."

    semiconductor_dist = context.get("semiconductor_distribution", {})
    semi_str = json.dumps(semiconductor_dist, indent=2, default=str) if semiconductor_dist else "N/A"

    scenario = context.get("scenario", "Afternoon_Line_Breakdown")
    data_grounding = "Use ONLY data from the provided context. Every number must trace to simulation or master data. If a value is not in the data, say 'Not in data' and do NOT estimate. Do NOT invent recovery rates for Manual_Operation."
    overview_instruction = "Start with a short Overview (1-2 sentences) explaining what this analysis describes. Then provide the detailed analysis below."

    prompts = {}

    if scenario == "Morning_Sudden_Demand_Spike":
        # Demand spike: Can we fulfill 500? Will we deliver on schedule?
        prompts["line_health"] = f"""Assess line capacity for a DEMAND SPIKE scenario (NOT a breakdown).

SCENARIO: Europe dealer requests 500 High Range SUVs. This is a demand spike, NOT robot breakdown. Do NOT discuss MTTR or outages.

SCENARIO IMPACT:
{impact_str}

LINE MASTER DATA:
{json.dumps(line_master, indent=2, default=str)}

{data_grounding}

Determine: Can the plant fulfill the extra 500 High Range SUVs with current capacity? Use peak_demand, total_plant_capacity, high_range_capacity from scenario impact."""

        prompts["production"] = f"""Create a production plan for a DEMAND SPIKE (500 extra High Range SUVs). NOT a breakdown.

SCENARIO IMPACT:
{impact_str}

ORDER BOOK:
{order_str}

LINE CAPACITIES:
{json.dumps(line_master, indent=2, default=str)}

{data_grounding}

Answer: 1) Can we fulfill the 500? 2) Will we deliver the rest on schedule? Use ONLY numbers from the data."""

        prompts["inventory"] = f"""Check inventory for DEMAND SPIKE scenario (500 extra High Range SUVs).

{impact_str}
{inv_summary_str}
{semi_str}

{data_grounding}

Determine if inventory can support the 500-unit spike. Reference low_stock_items, avg_lead_time_days."""

        prompts["workforce"] = f"""Plan workforce for DEMAND SPIKE (500 extra High Range SUVs). NOT a breakdown.

SHIFT MASTER:
{json.dumps(shift_master, indent=2, default=str)}

WORKER AVAILABILITY: {json.dumps(context.get('worker_availability', {}), indent=2, default=str)}

{impact_str}

{data_grounding}

Determine: Is overtime needed? Reference Max_Overtime_hrs, Labor_Cost_per_hr. Overtime cost = workers × hours × labor_cost_per_hr."""

        prompts["supply_chain"] = f"""Assess supply chain for DEMAND SPIKE (500 extra High Range SUVs).

{suppliers_str}
{semi_str}
{impact_str}

{data_grounding}

Determine if semiconductor/inventory can support the spike."""

    elif scenario == "Midday_Semiconductor_Shortage":
        prompts["line_health"] = f"""Assess line status for SEMICONDUCTOR SHORTAGE scenario (48h chip delay). NOT a breakdown.

{impact_str}
{json.dumps(line_master, indent=2, default=str)}

{data_grounding}

Determine impact of semiconductor shortage on line capacity."""

        prompts["production"] = f"""Plan for SEMICONDUCTOR SHORTAGE (48h delay). NOT a breakdown.

{impact_str}
{order_str}
{json.dumps(line_master, indent=2, default=str)}

{data_grounding}

Determine: How to mitigate 48h semiconductor delay? Line reallocation, alternate models?"""

        prompts["inventory"] = f"""Check inventory for SEMICONDUCTOR SHORTAGE.

{impact_str}
{inv_summary_str}
{semi_str}

{data_grounding}

Determine reorder needs and buffer adequacy."""

        prompts["workforce"] = f"""Plan workforce for SEMICONDUCTOR SHORTAGE.

{json.dumps(shift_master, indent=2, default=str)}
{impact_str}

{data_grounding}"""

        prompts["supply_chain"] = f"""Assess supply chain for SEMICONDUCTOR SHORTAGE (primary scenario).

{suppliers_str}
{semi_str}
{impact_str}

{data_grounding}

Determine: Switch supplier? Expedite? Reference Alternate_Supplier, Lead_Time_days."""

    else:
        # Afternoon_Line_Breakdown (default)
        # 1. Line Health Analyst — needs line master + machine parameters
        affected = scenario_impact.get("affected_line", "assembly line")
        prompts["line_health"] = f"""Assess the {affected} breakdown.

{overview_instruction}

EVENT: {event_str}
RULE ENGINE RESULTS:
{rule_summary}

ML BREAKDOWN PREDICTIONS:
{ml_breakdown}

LINE MASTER DATA (all 5 lines with capacity, OEE, MTTR, MTBF, robots):
{json.dumps(line_master, indent=2, default=str)}

MACHINE PARAMETERS SUMMARY:
{machine_str}

SCENARIO IMPACT (event_date, affected_line, formula_explanation):
{impact_str}

MTTR SENSITIVITY (semiconductor_relevant, semiconductor_reason, delivery_impact):
{mttr_str}

CRITICAL - Recovery uses SPARE capacity, NOT full capacity:
- remaining_high_range_capacity = full capacity of remaining line(s)
- remaining_high_range_spare_capacity = absorbable capacity (remaining lines already run at Current_Utilization_%, so only spare = capacity × (1 - utilization/100) can absorb)
- recovery_days = actual_units_lost_during_outage / remaining_high_range_spare_capacity
- Do NOT use full capacity for recovery — the remaining line is already producing at its utilization level.
For MTTR 2h: semiconductor NOT relevant. For MTTR 24h/48h: semiconductor matters.
{data_grounding}

Determine:
1. Severity (units lost from data)
2. Which lines can absorb — use remaining_high_range_spare_capacity for recovery timeline
3. Immediate maintenance actions

Do NOT invent numbers."""

        # 2. Production Planner
        prompts["production"] = f"""Create a production reallocation plan for the {affected} breakdown.

{overview_instruction}

SCENARIO IMPACT (event_date, affected_line, formula):
{impact_str}

MTTR SENSITIVITY (delivery_impact, orders_at_risk):
{mttr_str}

LINE CAPACITIES:
{json.dumps(line_master, indent=2, default=str)}

ORDER BOOK:
{order_str}

RULE ENGINE:
{rule_summary}

{data_grounding}

Plan: 1) Redistribute to remaining High Range line 2) Recovery timeline = units_lost / remaining_high_range_spare_capacity (NOT full capacity — remaining line already at utilization) 3) Orders at risk (compare Required_Dispatch_Date with event_date + recovery_days). Do NOT invent Manual_Operation recovery rates."""

        # 3. Inventory Controller
        prompts["inventory"] = f"""Check inventory impact of the {affected} breakdown.

{overview_instruction}

ML DELAY PREDICTION: {ml_delay}
RULE ENGINE: {rule_summary}

INVENTORY MASTER SUMMARY:
{inv_summary_str}

SEMICONDUCTOR DISTRIBUTION:
{semi_str}

SCENARIO IMPACT:
{impact_str}

{data_grounding}

Reference total_materials, low_stock_items, avg_lead_time_days. Do NOT invent item counts."""

        # 4. Workforce Coordinator
        prompts["workforce"] = f"""Plan workforce adjustments for the {affected} breakdown.

{overview_instruction}

SHIFT MASTER (Workers_Assigned, Max_Overtime_hrs, Labor_Cost_per_hr):
{json.dumps(shift_master, indent=2, default=str)}

TOTAL WORKERS: {context.get('total_workers', 'N/A')}

WORKER AVAILABILITY:
{json.dumps(context.get('worker_availability', {}), indent=2, default=str)}

MTTR SENSITIVITY (overtime_capacity, overtime_labor_hrs_total, overtime_required_reason):
{mttr_str}

{data_grounding}

Overtime: Use Max_Overtime_hrs per shift. Cost = workers × max_overtime_hrs × labor_cost_per_hr per shift. Total OT cost = sum across shifts. overtime_required_reason explains WHY overtime may be needed (spare capacity vs units lost). Do NOT exceed Max_Overtime_hrs. Conversion of OT labor-hrs to extra units is NOT in master data."""

        # 5. Supply Chain Monitor
        prompts["supply_chain"] = f"""Assess supply chain impact of the {affected} breakdown.

{overview_instruction}

SUPPLIER MASTER:
{suppliers_str}

ML SUPPLIER RISK SCORES:
{supplier_info}

ML DELAY PREDICTION: {ml_delay}

SEMICONDUCTOR DISTRIBUTION:
{semi_str}

MTTR SENSITIVITY (semiconductor_relevant, semiconductor_reason):
{mttr_str}
For MTTR 2h: semiconductor not relevant. For 24h/48h: semiconductor matters.
{data_grounding}

Reference supplier names, lead times, Alternate_Supplier."""

    # 6. Decision Orchestrator (gets all prior agent outputs injected later)
    prompts["orchestrator"] = ""  # Built dynamically after other agents run

    return prompts


def _build_orchestrator_prompt(
    agent_outputs: Dict[str, str],
    rule_summary: str,
    ml_breakdown: str,
    ml_delay: str,
    context: Dict[str, Any] = None,
) -> str:
    """Build the orchestrator prompt with all prior agent outputs."""
    agent_section = ""
    labels = {
        "line_health": "Line Health Analyst",
        "production": "Production Planner",
        "inventory": "Inventory Controller",
        "workforce": "Workforce Coordinator",
        "supply_chain": "Supply Chain Monitor",
    }
    for key, output in agent_outputs.items():
        label = labels.get(key, key)
        agent_section += f"\n--- {label} ---\n{output}\n"

    # Include KPI targets for grounding
    kpi_section = ""
    if context:
        kpi_targets = context.get("kpi_targets", [])
        if kpi_targets:
            kpi_section = f"\nKPI TARGETS (Before vs After Optimization):\n{json.dumps(kpi_targets, indent=2, default=str)}\n"
        predicted_kpi = context.get("predicted_kpi_impact", 0)
        kpi_section += f"\nPredicted KPI Impact from simulation data: {predicted_kpi:+.2f}%\n"

    return f"""Generate the integrated action plan and decision log.

DATA RULE: Use ONLY numbers from the provided context. Every figure must trace to simulation or master data. Do NOT invent values (e.g. "61 semiconductor items" when only low_stock_items count is in data). If a value is not in the data, say "Not in data".

EXECUTIVE SUMMARY: 4-6 sentences, user-friendly. Structure: (1) What happened (event_date, affected_line from Event_Line_Breakdown), (2) Key impact numbers from data, (3) Recovery feasible? (yes/no + reason), (4) Orders at risk if any, (5) Top 2-3 actions. For breakdown: state "If MTTR is Xh: [manageable / delivery impact]".

Synthesise the findings from all specialist agents into:
1. EXECUTIVE SUMMARY (3-4 sentences)
2. TOP 5 PRIORITISED RECOMMENDATIONS — each MUST include: action, priority (1=highest to 5), reasoning, source_agent, estimated_time, and expected_kpi_impact (e.g. "On-time delivery: -5%", "Line downtime: +2 hrs")
   PRIORITY LOGIC: 1 = immediate operational risk (line down, maintenance); 2 = production recovery (reallocate); 3 = supply chain (supplier, semiconductor); 4 = workforce (overtime, shifts); 5 = preventive (inspections, buffers). Order by urgency to restore production first.
3. DECISION JUSTIFICATION (which rules triggered, what thresholds were breached, ML predictions)

SPECIALIST AGENT FINDINGS:
{agent_section}

RULE ENGINE SUMMARY:
{rule_summary}

ML PREDICTIONS:
{ml_breakdown}
{ml_delay}
{kpi_section}

Respond ONLY with valid JSON with keys: executive_summary, recommendations (array of objects with action/priority/reasoning/source_agent/estimated_time/expected_kpi_impact), decision_justification.
Complete ALL 5 recommendations fully — do NOT truncate any field."""


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def run_crew(
    rule_output: RuleEngineOutput,
    ml_output: MLPredictions,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run the full multi-agent analysis using Azure OpenAI directly.
    Falls back to rule-engine-only result if the API call fails.
    """
    try:
        return _run_agents(rule_output, ml_output, context)
    except Exception as e:
        print(f"[AGENTS] Error: {e}")
        return _rule_engine_fallback(rule_output, ml_output, context, str(e))


def _run_agents(
    rule_output: RuleEngineOutput,
    ml_output: MLPredictions,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Run all 6 agents sequentially using the direct Azure OpenAI SDK."""

    client = _get_client()
    deployment = _get_deployment()
    print(f"[AGENTS] Using Azure OpenAI: {deployment}")

    # Build prompts for agents 1-5
    prompts = _build_agent_prompts(rule_output, ml_output, context)

    # Run specialist agents (1-5) sequentially
    agent_order = ["line_health", "production", "inventory", "workforce", "supply_chain"]
    agent_outputs = {}

    for agent_key in agent_order:
        label = agent_key.replace("_", " ").title()
        print(f"  [AGENTS] Running {label}...")
        system_prompt = AGENT_SYSTEM_PROMPTS[agent_key]
        user_prompt = prompts[agent_key]
        output = _call_agent(client, deployment, system_prompt, user_prompt)
        agent_outputs[agent_key] = output
        time.sleep(0.3)  # small pause between calls

    # Build orchestrator prompt with all outputs
    rule_summary = rule_output.summary_text()
    ml_breakdown = "\n".join(
        f"  {b.line}: {b.probability*100:.2f}% risk ({b.risk_level})"
        for b in ml_output.breakdown_predictions[:5]
    ) or "No breakdown predictions."
    if ml_output.delay_predictions:
        ml_delay = "Delay risk per line:\n" + "\n".join(
            f"  {d.line}: {d.risk_score*100:.2f}% ({d.risk_level})"
            for d in ml_output.delay_predictions[:5]
        )
    elif ml_output.delay_prediction:
        dp = ml_output.delay_prediction
        ml_delay = f"Delay risk: {dp.risk_score*100:.2f}% ({dp.risk_level})"
    else:
        ml_delay = "No delay prediction."

    orchestrator_prompt = _build_orchestrator_prompt(
        agent_outputs, rule_summary, ml_breakdown, ml_delay, context
    )

    # Run orchestrator (agent 6)
    print("  [AGENTS] Running Decision Orchestrator...")
    orchestrator_output = _call_agent(
        client, deployment,
        AGENT_SYSTEM_PROMPTS["orchestrator"],
        orchestrator_prompt,
        max_tokens=16384,
    )
    agent_outputs["orchestrator"] = orchestrator_output

    # Parse orchestrator JSON
    parsed = _parse_orchestrator_json(orchestrator_output)

    # Format orchestrator output as readable markdown (like other agents)
    orchestrator_formatted = _format_orchestrator_output(parsed)
    agent_outputs["orchestrator"] = orchestrator_formatted

    print("[AGENTS] All agents complete.")

    return {
        "success": True,
        "executive_summary": parsed.get("executive_summary", ""),
        "recommendations": parsed.get("recommendations", []),
        "decision_justification": parsed.get("decision_justification", ""),
        "agent_outputs": agent_outputs,
        "raw_result": orchestrator_output,
    }


def _format_orchestrator_output(parsed: Dict[str, Any]) -> str:
    """Format parsed orchestrator JSON into readable markdown like other agents."""
    lines = []
    summary = parsed.get("executive_summary", "")
    if summary:
        lines.append("#### Executive Summary")
        lines.append("")
        lines.append(summary)
        lines.append("")

    recs = parsed.get("recommendations", [])
    if recs:
        lines.append("#### Prioritised Recommendations")
        lines.append("")
        for r in recs:
            action = r.get("action", "—")
            priority = r.get("priority", "")
            reasoning = r.get("reasoning", "")
            source = r.get("source_agent", "")
            est_time = r.get("estimated_time", "")
            kpi = r.get("expected_kpi_impact", "")
            lines.append(f"**{priority}. {action}**")
            lines.append(f"- *Source:* {source}")
            lines.append(f"- *Reasoning:* {reasoning}")
            if est_time:
                lines.append(f"- *Estimated time:* {est_time}")
            if kpi:
                lines.append(f"- *Expected KPI impact:* {kpi}")
            lines.append("")

    justification = parsed.get("decision_justification", "")
    if justification:
        lines.append("#### Decision Justification")
        lines.append("")
        lines.append(justification)

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("#### What is KPI & How is it Calculated?")
    lines.append("")
    lines.append("**KPI (Key Performance Indicator)** measures plant performance: On-time Delivery %, Line Downtime, Overtime Cost, Production Efficiency, etc.")
    lines.append("")
    lines.append("**Calculation sources:**")
    lines.append("- *Predicted_KPI_Impact_%*: From simulation data — average predicted % change in KPI for the scenario.")
    lines.append("- *KPI_Summary* (master data): Before_Optimization_%, After_Optimization_%, Improvement_% for each KPI.")
    lines.append("- *expected_kpi_impact* per action: Derived from rule-action mapping (e.g. DISPATCH_MAINTENANCE → Line Downtime impact) or from simulation improvement when action aligns with data.")
    lines.append("")
    lines.append("**Interpretation:** Positive % = improvement (e.g. +4.65% on-time delivery). Negative % = degradation (e.g. -15% line downtime during outage). Values trace to simulation or master data; agents do not invent figures.")

    return "\n".join(lines).strip() if lines else str(parsed)


def _parse_orchestrator_json(text: str) -> Dict[str, Any]:
    """Parse the orchestrator's JSON response."""
    try:
        # Try direct parse first
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Try extracting from markdown code block
    try:
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return json.loads(text[start:end].strip())
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return json.loads(text[start:end].strip())
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    # Fallback: treat entire text as summary
    return {
        "executive_summary": text[:500],
        "recommendations": [],
        "decision_justification": "See agent outputs for details.",
    }


# ---------------------------------------------------------------------------
# Rule-engine-only fallback (if Azure OpenAI is unavailable)
# ---------------------------------------------------------------------------
def _rule_engine_fallback(
    rule_output: RuleEngineOutput,
    ml_output: MLPredictions,
    context: Dict[str, Any],
    error_msg: str = "",
) -> Dict[str, Any]:
    """Return recommendations derived from rules only."""
    print("[AGENTS] Using rule-engine-only fallback")

    recs = []
    for i, r in enumerate(rule_output.triggered_rules[:5]):
        recs.append({
            "action": f"{r.action.replace('_', ' ').title()}: {r.details}",
            "priority": 5 - i,
            "reasoning": r.condition,
            "source_agent": f"Rule Engine ({r.rule_name})",
            "estimated_time": "Immediate" if r.severity == "CRITICAL" else "1-4 hours",
        })

    return {
        "success": True,
        "executive_summary": (
            f"Rule Engine detected {len(rule_output.triggered_rules)} issues "
            f"with overall severity {rule_output.overall_severity}. "
            f"AI agents were unavailable ({error_msg}). "
            f"Actions: {', '.join(rule_output.recommended_actions)}."
        ),
        "recommendations": recs,
        "decision_justification": (
            f"Rules triggered: {rule_output.summary_text()}\n\n"
            f"Note: AI agents were unavailable. "
            f"Recommendations are from the deterministic Rule Engine."
        ),
        "agent_outputs": {},
        "raw_result": f"Rule-engine-only analysis. Error: {error_msg}",
    }
