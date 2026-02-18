"""
Inventory Management Agent
Optimizes inventory allocation and tracking
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent

class InventoryManagementAgent(BaseAgent):
    """Agent specialized in inventory management"""
    
    def __init__(self):
        super().__init__(
            name="Inventory Management Agent",
            role="Monitor inventory levels, optimize allocation, and prevent stockouts"
        )
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze inventory status with data-verified findings"""
        
        inventory_levels = context.get('inventory_levels', {})
        demand = context.get('demand', 0)
        
        # ====== DATA-DRIVEN PRE-COMPUTATION (prevents LLM hallucination) ======
        # These are calculated directly from plant data, NOT by the LLM
        actual_critical = [k for k, v in inventory_levels.items() if v < 70]
        actual_at_risk = [k for k, v in inventory_levels.items() if 70 <= v < 80]
        actual_ok = [k for k, v in inventory_levels.items() if v >= 80]
        
        # Also use pre-computed flags from context if available
        ctx_critical = context.get('inventory_critical', actual_critical)
        ctx_at_risk = context.get('inventory_at_risk', actual_at_risk)
        
        # Sort all items by level (lowest first) for reorder priority
        sorted_items = sorted(inventory_levels.items(), key=lambda x: x[1])
        reorder_priority = [item[0] for item in sorted_items]
        
        # Calculate efficiency based on data
        if inventory_levels:
            avg_level = sum(inventory_levels.values()) / len(inventory_levels)
            # Efficiency: how well-distributed inventory is relative to 85% target
            data_efficiency = min(100, int(avg_level / 85 * 100))
        else:
            data_efficiency = 75
        
        # Get additional data columns
        active_alerts = context.get('active_alerts', {})
        predicted_kpi = context.get('predicted_kpi_impact', 0)
        existing_recs = context.get('existing_ai_recommendations', {})
        # Master data: inventory details, BOM, scenario impact
        inv_summary = context.get('inventory_master_summary', {})
        bom_summary = context.get('bom_summary', {})
        scenario_impact = context.get('scenario_impact', {})
        trigger_event = scenario_impact.get('trigger_event', '')
        trigger_qty = scenario_impact.get('trigger_quantity', 0)

        prompt = f"""Analyze inventory situation:

Current Inventory Levels (from plant data): {inventory_levels}
Current Demand: {demand} units
Scenario: {context.get('scenario', 'Normal')}
{f"TRIGGER EVENT: {trigger_event}" if trigger_event else ""}
{f"Additional units needed: {trigger_qty} ({scenario_impact.get('trigger_suv_type', '')})" if trigger_qty > 0 else ""}

INVENTORY MASTER: {inv_summary.get('low_stock_items', 0)} items below reorder point out of {inv_summary.get('total_materials', 0)} total, avg lead time: {inv_summary.get('avg_lead_time_days', 'N/A')} days
BOM: {bom_summary if bom_summary else 'N/A'}
Alerts: {active_alerts if active_alerts else 'None'}
Predicted KPI Impact: {predicted_kpi:+.2f}%

DATA-VERIFIED FACTS (calculated from actual plant data — DO NOT contradict these):
- Items ACTUALLY below 70% (critical): {actual_critical if actual_critical else 'NONE — all items are above 70%'}
- Items between 70-80% (at risk of becoming critical): {actual_at_risk if actual_at_risk else 'NONE'}
- Items above 80% (healthy): {actual_ok if actual_ok else 'NONE'}

IMPORTANT: Only list items as critical_items if they are ACTUALLY below 70% based on the data above.
Items between 70-80% should be listed as stockout_risks, not critical_items.

Determine:
1. Allocation efficiency score (0-100, consider demand vs inventory balance)
2. Stockout risks (items that could run out given current demand)
3. Any additional insights

Respond in JSON format with keys: efficiency_score, stockout_risks (list), additional_insights (string)"""
        
        response = self.gemini.generate_json_response(prompt)
        
        # Use DATA-VERIFIED critical items, NOT LLM output (prevents hallucination)
        analysis = {
            'agent': self.name,
            'critical_items': actual_critical,  # DATA-VERIFIED: only truly below 70%
            'at_risk_items': actual_at_risk,    # DATA-VERIFIED: between 70-80%
            'efficiency_score': response.get('efficiency_score', data_efficiency),
            'stockout_risks': actual_at_risk + actual_critical if (actual_at_risk or actual_critical) else response.get('stockout_risks', []),
            'reorder_priorities': reorder_priority,
            'data_verification': {
                'below_70': actual_critical,
                'between_70_80': actual_at_risk,
                'above_80': actual_ok,
                'avg_inventory': round(avg_level, 1) if inventory_levels else 0,
            }
        }
        
        self.add_to_memory({'summary': f'Inventory analysis: {len(analysis["critical_items"])} critical items'})
        
        return analysis
    
    def recommend(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate inventory recommendations"""
        
        prompt = f"""Based on inventory analysis:
- Critical Items: {analysis.get('critical_items', [])}
- Efficiency Score: {analysis.get('efficiency_score', 75)}
- Stockout Risks: {analysis.get('stockout_risks', [])}

Generate 2-3 inventory management recommendations.

Respond in JSON format as array with: action, priority (1-5), reasoning, expected_impact"""
        
        response = self.gemini.generate_json_response(prompt)
        
        if isinstance(response, dict) and 'error' not in response:
            recommendations = response.get('recommendations', [response])
        elif isinstance(response, list):
            recommendations = response
        else:
            recommendations = [{
                'action': 'Maintain current inventory levels',
                'priority': 2,
                'reasoning': 'Inventory within acceptable range',
                'expected_impact': 'Stable operations'
            }]
        
        return recommendations
