"""
Machine Management Agent
Monitors equipment health and schedules maintenance
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent

class MachineManagementAgent(BaseAgent):
    """Agent specialized in machine health and maintenance"""
    
    def __init__(self):
        super().__init__(
            name="Machine Management Agent",
            role="Monitor machine health, predict failures, and schedule maintenance"
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze machine status with data-driven findings"""
        
        machine_data = context.get('machine_uptime', {})
        
        # ====== DATA-DRIVEN PRE-COMPUTATION ======
        at_risk_threshold = 75.0
        watch_threshold = 85.0
        
        # At-risk machines: data-verified (uptime < 75%)
        data_at_risk = [line for line, uptime in machine_data.items() if uptime < at_risk_threshold]
        data_watch = [line for line, uptime in machine_data.items() if at_risk_threshold <= uptime < watch_threshold]
        data_healthy = [line for line, uptime in machine_data.items() if uptime >= watch_threshold]
        
        # Maintenance priority: sorted by uptime ascending (worst first) — DATA-DRIVEN
        sorted_machines = sorted(machine_data.items(), key=lambda x: x[1])
        data_maintenance_priority = [line for line, _ in sorted_machines]
        
        # Health score: average uptime — DATA-CALCULATED
        avg_uptime = sum(machine_data.values()) / len(machine_data) if machine_data else 0
        data_health_score = min(100, round(avg_uptime))
        
        # Failure risk: based on distance from threshold — DATA-DERIVED
        data_failure_risk = []
        for line, uptime in sorted_machines:
            if uptime < at_risk_threshold:
                data_failure_risk.append(f"{line}: High (uptime {uptime:.1f}% < {at_risk_threshold}%)")
            elif uptime < watch_threshold:
                data_failure_risk.append(f"{line}: Low-Medium (uptime {uptime:.1f}%, monitoring)")
            else:
                data_failure_risk.append(f"{line}: Low (uptime {uptime:.1f}%)")
        
        # Get additional data columns
        active_alerts = context.get('active_alerts', {})
        predicted_kpi = context.get('predicted_kpi_impact', 0)
        # Master data: machine parameters, line master
        machine_params = context.get('machine_params_summary', {})
        line_master = context.get('line_master', {})

        prompt = f"""Analyze machine/equipment status:

Machine Uptime by Line: {machine_data}
Scenario: {context.get('scenario', 'Normal')}

MACHINE DATA: {machine_params.get('at_risk_count', 0)} machines exceeding thresholds out of {machine_params.get('total_machines', 0)}, avg OEE: {machine_params.get('avg_oee', 'N/A')}%
Alerts: {active_alerts if active_alerts else 'None'}
KPI Impact: {predicted_kpi:+.2f}%

DATA-VERIFIED FACTS:
- At-risk machines (uptime < {at_risk_threshold}%): {data_at_risk if data_at_risk else 'NONE'}
- Watch list (uptime {at_risk_threshold}-{watch_threshold}%): {data_watch if data_watch else 'NONE'}
- Healthy (uptime >= {watch_threshold}%): {data_healthy if data_healthy else 'NONE'}
- Maintenance priority (lowest uptime first): {data_maintenance_priority}
- Average uptime: {avg_uptime:.1f}%

Determine:
1. Any additional maintenance insights for the production manager
2. Specific concerns about equipment for this scenario

Respond in JSON format with keys: maintenance_insights (string), scenario_concerns (string)"""
        
        response = self.gemini.generate_json_response(prompt)
        
        # Use DATA-VERIFIED findings
        analysis = {
            'agent': self.name,
            'at_risk_machines': data_at_risk,  # DATA-VERIFIED
            'watch_machines': data_watch,  # DATA-VERIFIED
            'maintenance_priorities': data_maintenance_priority,  # DATA-SORTED by uptime
            'failure_predictions': data_failure_risk,  # DATA-DERIVED
            'health_score': data_health_score,  # DATA-CALCULATED
            'data_verification': {
                'at_risk_threshold': at_risk_threshold,
                'watch_threshold': watch_threshold,
                'avg_uptime': round(avg_uptime, 1),
                'at_risk': data_at_risk,
                'watch': data_watch,
                'healthy': data_healthy,
                'sorted_by_uptime': [(line, round(up, 1)) for line, up in sorted_machines],
            }
        }
        
        self.add_to_memory({'summary': f'Machine health: {analysis["health_score"]}% overall'})
        
        return analysis
    
    def recommend(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate machine management recommendations"""
        
        prompt = f"""Based on machine analysis:
- At-Risk Machines: {analysis.get('at_risk_machines', [])}
- Maintenance Priorities: {analysis.get('maintenance_priorities', [])}
- Health Score: {analysis.get('health_score', 85)}%

Generate 2-3 machine management recommendations.

Respond in JSON format as array with: action, priority (1-5), reasoning, expected_impact"""
        
        response = self.gemini.generate_json_response(prompt)
        
        if isinstance(response, dict) and 'error' not in response:
            recommendations = response.get('recommendations', [response])
        elif isinstance(response, list):
            recommendations = response
        else:
            recommendations = [{
                'action': 'Continue routine maintenance',
                'priority': 2,
                'reasoning': 'Machines operating within normal parameters',
                'expected_impact': 'Sustained uptime'
            }]
        
        return recommendations
