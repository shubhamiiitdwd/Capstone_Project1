"""
Demand Forecasting Agent
Monitors and predicts demand patterns
"""

from typing import Dict, Any, List
import pandas as pd
from src.agents.base_agent import BaseAgent

class DemandForecastingAgent(BaseAgent):
    """Agent specialized in demand forecasting and spike detection"""
    
    def __init__(self):
        super().__init__(
            name="Demand Forecasting Agent",
            role="Monitor demand patterns, predict future demand, and detect anomalies"
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze demand patterns with data-driven spike detection, focused on scenario trigger"""
        
        demand_data = context.get('demand_data', {})
        current_demand = context.get('current_demand', 0)
        peak_demand = context.get('peak_demand', current_demand)
        scenario = context.get('scenario', 'Unknown')
        demand_by_line = context.get('demand_by_line', {})
        
        # ====== DATA-DRIVEN SPIKE DETECTION ======
        avg_demand = demand_data.get('avg_demand', 300)
        std_demand = demand_data.get('std_demand', 50)
        data_spike = self.detect_spike(peak_demand, avg_demand, std_dev=max(std_demand, 30))
        spike_threshold = avg_demand + (2 * max(std_demand, 30))
        
        # Data-driven risk level
        if peak_demand > avg_demand * 1.5:
            data_risk = 'High'
        elif peak_demand > avg_demand * 1.2:
            data_risk = 'Medium'
        else:
            data_risk = 'Low'
        
        # Get scenario-specific impact (pre-computed in context builder)
        scenario_impact = context.get('scenario_impact', {})
        trigger_event = scenario_impact.get('trigger_event', '')
        trigger_qty = scenario_impact.get('trigger_quantity', 0)
        trigger_type = scenario_impact.get('trigger_suv_type', '')
        hr_cap = scenario_impact.get('high_range_capacity_per_day', 190)
        mr_cap = scenario_impact.get('medium_range_capacity_per_day', 345)
        days_full = scenario_impact.get('days_to_fulfill_at_full_capacity', 0)
        days_eff = scenario_impact.get('days_to_fulfill_at_current_utilization', 0)
        mr_impact = scenario_impact.get('medium_range_impact', '')
        
        active_alerts = context.get('active_alerts', {})
        predicted_kpi = context.get('predicted_kpi_impact', 0)
        line_master = context.get('line_master', {})
        total_capacity = context.get('total_plant_capacity', 0)

        line_caps = {k: v.get('daily_capacity', 0) for k, v in line_master.items()} if line_master else {}

        prompt = f"""Analyze the demand situation for this SPECIFIC scenario:

TRIGGER EVENT: {trigger_event}
{f"ADDITIONAL UNITS NEEDED: {trigger_qty} {trigger_type} SUVs" if trigger_qty > 0 else ""}
{f"High Range capacity: {hr_cap} units/day | Days to fulfill: ~{days_full} (full), ~{days_eff} (current utilization)" if trigger_qty > 0 else ""}
{f"Medium Range impact: {mr_impact}" if mr_impact else ""}

Simulation Data Stats:
- Average Demand: {avg_demand:.1f} SUVs | Peak: {peak_demand:.1f} SUVs
- Demand by Line: {demand_by_line}
- Trend: {demand_data.get('trend', 'stable')}

LINE CAPACITIES: {line_caps} (Total: {total_capacity} units/day)
Alerts: {active_alerts if active_alerts else 'None'}

DATA-VERIFIED: Peak ({peak_demand:.1f}) vs Threshold ({spike_threshold:.1f}): {'SPIKE' if data_spike else 'Normal'}. Risk: {data_risk}

Determine:
1. Predicted demand for next 24h
2. Key concerns SPECIFIC to the trigger event ({trigger_event}) — reference capacity constraints
3. Additional insights

Respond in JSON with keys: predicted_demand, concerns (list), insights (string)"""
        
        response = self.gemini.generate_json_response(prompt)
        
        analysis = {
            'agent': self.name,
            'is_spike': data_spike,
            'risk_level': data_risk,
            'predicted_demand': response.get('predicted_demand', peak_demand),
            'concerns': response.get('concerns', []),
            'current_demand': current_demand,
            'peak_demand': peak_demand,
            'demand_by_line': demand_by_line,
            'spike_threshold': spike_threshold,
            'scenario_impact': scenario_impact,
            'total_plant_capacity': total_capacity,
            'line_master': line_master,
            'data_verification': {
                'avg_demand': round(avg_demand, 1),
                'peak_demand': round(peak_demand, 1),
                'std_demand': round(std_demand, 1),
                'threshold': round(spike_threshold, 1),
                'spike_detected': data_spike,
                'risk_level': data_risk,
            }
        }
        
        self.add_to_memory({'summary': f'Analyzed demand: {analysis["risk_level"]} risk', 'result': analysis})
        
        return analysis
    
    def recommend(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate demand-related recommendations focused on the scenario trigger"""
        
        scenario_impact = analysis.get('scenario_impact', {})
        trigger = scenario_impact.get('trigger_event', 'demand situation')
        trigger_qty = scenario_impact.get('trigger_quantity', 0)
        hr_cap = scenario_impact.get('high_range_capacity_per_day', 190)
        total_cap = analysis.get('total_plant_capacity', 535)
        days_eff = scenario_impact.get('days_to_fulfill_at_current_utilization', 0)
        
        prompt = f"""Based on this demand analysis:
- Trigger: {trigger}
{f"- Additional units: {trigger_qty}" if trigger_qty > 0 else ""}
- Risk Level: {analysis.get('risk_level', 'Medium')}
- Current avg demand: {analysis.get('current_demand', 0):.0f} SUVs
{f"- High Range capacity: {hr_cap} units/day, days to fulfill: ~{days_eff}" if trigger_qty > 0 else ""}
- Total plant capacity: {total_cap} units/day (DO NOT exceed this)

Generate 2 actionable recommendations to handle this. Be specific to the trigger event.
IMPORTANT: Do NOT suggest production rates exceeding {total_cap} units/day.

Respond in JSON array with: action, priority (1-5), reasoning, expected_impact"""
        
        response = self.gemini.generate_json_response(prompt)
        
        if isinstance(response, list) and len(response) > 0 and isinstance(response[0], dict):
            recommendations = response
        elif isinstance(response, dict) and 'error' not in response:
            recommendations = response.get('recommendations', [response] if 'action' in response else [])
        else:
            recommendations = []
        
        if not recommendations:
            if trigger_qty > 0:
                recommendations = [{
                    'action': f'Activate overtime on High Range lines to maximize output for the {trigger_qty} unit order (capacity: {hr_cap}/day)',
                    'priority': 5,
                    'reasoning': f"At current capacity of {hr_cap} units/day, fulfilling {trigger_qty} units takes ~{days_eff} days. Overtime can accelerate this.",
                    'expected_impact': f'Reduce fulfillment time from ~{days_eff} days to ~{max(1, days_eff - 0.5):.1f} days'
                }]
            else:
                recommendations = [{
                    'action': f'Monitor demand closely — risk level is {analysis.get("risk_level", "Medium")}',
                    'priority': 3,
                    'reasoning': f"Peak demand ({analysis.get('peak_demand', 0):.0f}) indicates {analysis.get('risk_level', 'Medium')} risk",
                    'expected_impact': 'Better preparedness for demand fluctuations'
                }]
        
        return recommendations
    
    def detect_spike(self, current: float, historical_avg: float, std_dev: float = 50) -> bool:
        """Simple spike detection algorithm"""
        threshold = historical_avg + (2 * std_dev)
        return current > threshold
