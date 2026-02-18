"""
Production Optimization Agent
Optimizes production scheduling and line balancing
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent

class ProductionOptimizationAgent(BaseAgent):
    """Agent specialized in production optimization"""
    
    def __init__(self):
        super().__init__(
            name="Production Optimization Agent",
            role="Optimize production schedules, balance lines, and maximize efficiency"
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze production status with data-driven findings"""
        
        production_data = context.get('production_output', {})
        efficiency = context.get('efficiency', 0)
        defect_rate = context.get('defect_rate', 0)
        energy_consumption = context.get('energy_consumption', 0)
        
        # ====== DATA-DRIVEN PRE-COMPUTATION ======
        
        # Bottleneck detection: line with LOWEST output — DATA-VERIFIED
        if production_data:
            sorted_lines = sorted(production_data.items(), key=lambda x: x[1])
            avg_output = sum(production_data.values()) / len(production_data)
            
            # Bottleneck = lines significantly below average (>10% below)
            bottleneck_threshold = avg_output * 0.9
            data_bottlenecks = [line for line, output in sorted_lines if output < bottleneck_threshold]
            
            # If no line is >10% below average, the lowest output line is the relative bottleneck
            if not data_bottlenecks and sorted_lines:
                data_bottlenecks = [sorted_lines[0][0]]  # Lowest output line
            
            # Balancing: lines that could redirect capacity to help bottleneck
            # These are the higher-output lines (above average)
            data_balancing = [line for line, output in sorted_lines if output > avg_output]
        else:
            sorted_lines = []
            avg_output = 0
            data_bottlenecks = []
            data_balancing = []
        
        # Energy efficiency: output-per-kWh ratio — DATA-CALCULATED
        if energy_consumption > 0 and avg_output > 0:
            output_per_kwh = avg_output / energy_consumption
            # Normalize to 0-100 scale (0.05 units/kWh = 100, 0.02 = 40)
            data_energy_efficiency = min(100, round(output_per_kwh / 0.05 * 100))
        else:
            data_energy_efficiency = 75
        
        # Quality potential based on defect rate — DATA-DERIVED
        if defect_rate <= 1.0:
            data_quality = 'High (defect rate ≤ 1%)'
        elif defect_rate <= 2.0:
            data_quality = f'Medium (defect rate {defect_rate:.2f}%)'
        else:
            data_quality = f'Low (defect rate {defect_rate:.2f}% — needs improvement)'
        
        # Get additional data columns
        active_alerts = context.get('active_alerts', {})
        predicted_kpi = context.get('predicted_kpi_impact', 0)
        kpi_by_line = context.get('kpi_impact_by_line', {})
        existing_recs = context.get('existing_ai_recommendations', {})
        # Master data: line capacities, BOM, scenario impact
        line_master = context.get('line_master', {})
        total_capacity = context.get('total_plant_capacity', 0)
        bom_summary = context.get('bom_summary', {})
        scenario_impact = context.get('scenario_impact', {})
        trigger_event = scenario_impact.get('trigger_event', '')
        trigger_qty = scenario_impact.get('trigger_quantity', 0)

        prompt = f"""Analyze production situation:

Production Output by Line: {production_data}
Overall Efficiency: {efficiency:.1f}%
Average Defect Rate: {defect_rate:.2f}%
Average Energy Consumption: {energy_consumption:.0f} kWh
Scenario: {context.get('scenario', 'Normal')}
{f"TRIGGER EVENT: {trigger_event}" if trigger_event else ""}
{f"Additional units needed: {trigger_qty} ({scenario_impact.get('trigger_suv_type', '')})" if trigger_qty > 0 else ""}

LINE CAPACITIES: {', '.join(f'{k}: {v.get("daily_capacity",0)}/day ({v.get("suv_type","")})' for k,v in line_master.items()) if line_master else 'N/A'}
Total capacity: {total_capacity} units/day
Alerts: {active_alerts if active_alerts else 'None'}
KPI Impact: {predicted_kpi:+.2f}% (by line: {kpi_by_line})

DATA-VERIFIED FACTS:
- Lines sorted by output (lowest first): {[(line, round(out, 0)) for line, out in sorted_lines]}
- Average output across lines: {avg_output:.0f} units
- Bottleneck (lowest output): {data_bottlenecks}
- Energy efficiency score: {data_energy_efficiency}/100

Determine:
1. Specific insights about why the bottleneck line may be underperforming
2. Concrete suggestions for line balancing

Respond in JSON format with keys: bottleneck_insights (string), balancing_suggestions (list)"""
        
        response = self.gemini.generate_json_response(prompt)
        
        # Use DATA-VERIFIED findings
        analysis = {
            'agent': self.name,
            'bottlenecks': data_bottlenecks,  # DATA-VERIFIED (actual lowest output)
            'balancing_opportunities': data_balancing,  # DATA-SORTED
            'energy_efficiency': data_energy_efficiency,  # DATA-CALCULATED
            'quality_potential': data_quality,  # DATA-DERIVED
            'data_verification': {
                'sorted_by_output': [(line, round(out, 0)) for line, out in sorted_lines],
                'avg_output': round(avg_output, 0),
                'bottleneck_line': data_bottlenecks[0] if data_bottlenecks else 'None',
                'lowest_output': round(sorted_lines[0][1], 0) if sorted_lines else 0,
                'highest_output': round(sorted_lines[-1][1], 0) if sorted_lines else 0,
                'energy_efficiency': data_energy_efficiency,
                'defect_rate': round(defect_rate, 2),
            }
        }
        
        self.add_to_memory({'summary': f'Production analysis: {len(analysis["bottlenecks"])} bottlenecks found'})
        
        return analysis
    
    def recommend(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate production optimization recommendations"""
        
        prompt = f"""Based on production analysis:
- Bottlenecks: {analysis.get('bottlenecks', [])}
- Balancing Opportunities: {analysis.get('balancing_opportunities', [])}
- Energy Efficiency: {analysis.get('energy_efficiency', 75)}%

Generate 2-3 production optimization recommendations.

Respond in JSON format as array with: action, priority (1-5), reasoning, expected_impact"""
        
        response = self.gemini.generate_json_response(prompt)
        
        if isinstance(response, dict) and 'error' not in response:
            recommendations = response.get('recommendations', [response])
        elif isinstance(response, list):
            recommendations = response
        else:
            recommendations = [{
                'action': 'Maintain current production schedule',
                'priority': 2,
                'reasoning': 'Production balanced across lines',
                'expected_impact': 'Consistent output'
            }]
        
        return recommendations
