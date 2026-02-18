"""
Supply Chain Management Agent
Tracks component availability and supplier status
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent

class SupplyChainAgent(BaseAgent):
    """Agent specialized in supply chain management"""
    
    def __init__(self):
        super().__init__(
            name="Supply Chain Agent",
            role="Monitor component availability, track suppliers, and manage delays"
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze supply chain status with data-driven risk assessment"""
        
        semiconductor_status = context.get('semiconductor_availability', 'Available')
        scenario = context.get('scenario', 'Normal')
        demand = context.get('demand', 0)
        peak_demand = context.get('peak_demand', demand)
        
        # ====== DATA-DRIVEN RISK ASSESSMENT ======
        # Risk level determined by semiconductor status from actual plant data
        status_lower = str(semiconductor_status).lower()
        if 'shortage' in status_lower or 'critical' in status_lower:
            data_risk = 'High'
        elif 'limited' in status_lower or 'constrained' in status_lower:
            data_risk = 'Medium'
        elif 'available' in status_lower or 'normal' in status_lower:
            data_risk = 'Low'
        else:
            data_risk = 'Medium'  # Unknown status = cautious
        
        # Escalate risk if there's also a demand spike
        is_spike_scenario = 'Spike' in scenario or 'spike' in scenario
        if data_risk == 'Medium' and is_spike_scenario:
            data_risk = 'High'
        
        # Get additional data columns
        active_alerts = context.get('active_alerts', {})
        predicted_kpi = context.get('predicted_kpi_impact', 0)
        semiconductor_dist = context.get('semiconductor_distribution', {})
        event_details = context.get('event_details', [])
        # Master data: actual suppliers and inventory
        suppliers = context.get('suppliers', [])
        inv_summary = context.get('inventory_master_summary', {})
        scenario_impact = context.get('scenario_impact', {})
        trigger_event = scenario_impact.get('trigger_event', '')

        prompt = f"""Analyze supply chain situation:

{f"TRIGGER EVENT: {trigger_event}" if trigger_event else ""}
Semiconductor Status: {semiconductor_status}
Semiconductor Distribution (all records): {semiconductor_dist}
Scenario: {scenario}
Current Demand: {demand} units

TOP SUPPLIERS (use REAL names): {[{'name': s['name'], 'location': s['location'], 'reliability': s['reliability']} for s in suppliers[:5]] if suppliers else 'No data'}
Low stock items: {inv_summary.get('low_stock_items', 0)}, avg lead time: {inv_summary.get('avg_lead_time_days', 'N/A')} days
Alerts: {active_alerts if active_alerts else 'None'}
KPI Impact: {predicted_kpi:+.2f}%

DATA-VERIFIED:
- Semiconductor availability from plant data: {semiconductor_status}
- Semiconductor distribution across records: {semiconductor_dist}
- Data-derived risk level: {data_risk}
- Demand spike present: {is_spike_scenario}

IMPORTANT: Use actual supplier names from the MASTER DATA above (e.g., Tata Autocomp, Hella Electronics, Motherson Sumi) instead of generic "Supplier A/B/C".

Determine:
1. Critical components at risk (specific component types for EV/SUV manufacturing)
2. Impact of potential delays on production
3. Alternative supplier options

Respond in JSON format with keys: critical_components (list), delay_impact (string), alternative_suppliers (list)"""
        
        response = self.gemini.generate_json_response(prompt)
        
        # Use DATA-VERIFIED risk level
        analysis = {
            'agent': self.name,
            'risk_level': data_risk,  # DATA-VERIFIED
            'critical_components': response.get('critical_components', []),
            'delay_impact': response.get('delay_impact', 'Minimal'),
            'alternative_suppliers': response.get('alternative_suppliers', []),
            'data_verification': {
                'semiconductor_status': semiconductor_status,
                'risk_rule': f"'{semiconductor_status}' → {data_risk} risk",
                'demand_spike': is_spike_scenario,
                'risk_escalated': is_spike_scenario and 'Medium' in str(data_risk),
            }
        }
        
        self.add_to_memory({'summary': f'Supply chain risk: {analysis["risk_level"]}'})
        
        return analysis
    
    def recommend(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate supply chain recommendations"""
        
        prompt = f"""Based on supply chain analysis:
- Risk Level: {analysis.get('risk_level', 'Low')}
- Critical Components: {analysis.get('critical_components', [])}
- Delay Impact: {analysis.get('delay_impact', 'Minimal')}

Generate 2-3 supply chain management recommendations.

Respond in JSON format as array with: action, priority (1-5), reasoning, expected_impact"""
        
        response = self.gemini.generate_json_response(prompt)
        
        if isinstance(response, dict) and 'error' not in response:
            recommendations = response.get('recommendations', [response])
        elif isinstance(response, list):
            recommendations = response
        else:
            recommendations = [{
                'action': 'Monitor supplier status',
                'priority': 2,
                'reasoning': 'Supply chain stable',
                'expected_impact': 'Continuous operations'
            }]
        
        return recommendations
