"""
Workforce Management Agent
Optimizes workforce allocation and shift scheduling
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent

class WorkforceManagementAgent(BaseAgent):
    """Agent specialized in workforce optimization"""
    
    def __init__(self):
        super().__init__(
            name="Workforce Management Agent",
            role="Optimize workforce allocation, shift scheduling, and worker availability"
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workforce status with data-driven findings"""
        
        worker_data = context.get('worker_availability', {})
        demand = context.get('demand', 0)
        peak_demand = context.get('peak_demand', demand)
        efficiency = context.get('efficiency', 100)
        
        # ====== DATA-DRIVEN PRE-COMPUTATION ======
        target_availability = 92.0  # Plant target for worker availability
        
        # Understaffed: shifts below target
        data_understaffed = [
            f"Shift {shift}" for shift, avail in worker_data.items() 
            if avail < target_availability
        ]
        
        # Utilization score: average availability (data-calculated)
        avg_availability = sum(worker_data.values()) / len(worker_data) if worker_data else 0
        data_utilization = min(100, round(avg_availability))
        
        # Overtime estimation (transparent formula):
        # Step 1: Base overtime from availability gap
        #   Each % below target across all shifts = 0.08 * 8h/shift hours
        total_gap_pct = sum(max(0, target_availability - avail) for avail in worker_data.values())
        base_overtime = total_gap_pct / 100 * 8 * len(worker_data)
        
        # Step 2: Demand pressure multiplier
        #   If peak demand > average demand by >20%, scale overtime by demand ratio
        demand_multiplier = 1.0
        if demand > 0 and peak_demand > demand * 1.2:
            demand_multiplier = min(2.5, peak_demand / demand)
        
        # Step 3: Efficiency gap adds overtime
        #   If production efficiency < 90%, additional overtime needed
        efficiency_overtime = max(0, (90 - efficiency) / 100 * 8) if efficiency < 90 else 0
        
        data_overtime = round(base_overtime * demand_multiplier + efficiency_overtime, 1)
        
        # Get additional data columns
        active_alerts = context.get('active_alerts', {})
        predicted_kpi = context.get('predicted_kpi_impact', 0)
        # Master data: shift details
        shift_master = context.get('shift_master', {})
        total_workers = context.get('total_workers', 0)

        prompt = f"""Analyze workforce situation:

Worker Availability by Shift: {worker_data}
Current Demand: {demand} units
Peak Demand: {peak_demand} units
Production Efficiency: {efficiency}%
Scenario: {context.get('scenario', 'Normal')}

SHIFT DATA: {', '.join(f'{k}: {v.get("workers_assigned",0)} workers, max OT {v.get("max_overtime_hrs",0)}h' for k,v in shift_master.items()) if shift_master else 'N/A'}
Total Workers: {total_workers}
Alerts: {active_alerts if active_alerts else 'None'}
KPI Impact: {predicted_kpi:+.2f}%

DATA-VERIFIED FACTS:
- Target availability: {target_availability}%
- Average availability: {avg_availability:.1f}%
- Shifts below target ({target_availability}%): {data_understaffed if data_understaffed else 'NONE'}
- Data-estimated overtime: {data_overtime} hours (from availability gap + demand pressure)

Determine:
1. Shift optimization opportunities (how to improve worker allocation)
2. Any additional workforce insights

Respond in JSON format with keys: optimization_opportunities (list), insights (string)"""
        
        response = self.gemini.generate_json_response(prompt)
        
        # Use DATA-VERIFIED findings
        analysis = {
            'agent': self.name,
            'understaffed_areas': data_understaffed,  # DATA-VERIFIED
            'overtime_hours': data_overtime,  # DATA-CALCULATED
            'optimization_opportunities': response.get('optimization_opportunities', []),
            'utilization_score': data_utilization,  # DATA-CALCULATED
            'data_verification': {
                'target_availability': target_availability,
                'avg_availability': round(avg_availability, 1),
                'per_shift': {shift: round(avail, 1) for shift, avail in worker_data.items()},
                'total_gap_pct': round(total_gap_pct, 1),
                'base_overtime': round(base_overtime, 1),
                'demand_multiplier': round(demand_multiplier, 2),
                'efficiency_overtime': round(efficiency_overtime, 1),
                'formula': f"OT = ({round(base_overtime,1)}h base × {round(demand_multiplier,2)} demand) + {round(efficiency_overtime,1)}h efficiency = {data_overtime}h",
            }
        }
        
        self.add_to_memory({'summary': f'Workforce analysis: {analysis["utilization_score"]}% utilization'})
        
        return analysis
    
    def recommend(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate workforce recommendations"""
        
        prompt = f"""Based on workforce analysis:
- Understaffed Areas: {analysis.get('understaffed_areas', [])}
- Required Overtime: {analysis.get('overtime_hours', 0)} hours
- Utilization: {analysis.get('utilization_score', 80)}%

Generate 2-3 workforce optimization recommendations.

Respond in JSON format as array with: action, priority (1-5), reasoning, expected_impact"""
        
        response = self.gemini.generate_json_response(prompt)
        
        if isinstance(response, dict) and 'error' not in response:
            recommendations = response.get('recommendations', [response])
        elif isinstance(response, list):
            recommendations = response
        else:
            recommendations = [{
                'action': 'Maintain current shift allocation',
                'priority': 2,
                'reasoning': 'Workforce adequately distributed',
                'expected_impact': 'Stable productivity'
            }]
        
        return recommendations
