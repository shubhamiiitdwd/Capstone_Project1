"""
Master Orchestrator Agent
Coordinates all specialized agents and makes holistic decisions
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.agents.demand_agent import DemandForecastingAgent
from src.agents.inventory_agent import InventoryManagementAgent
from src.agents.workforce_agent import WorkforceManagementAgent
from src.agents.machine_agent import MachineManagementAgent
from src.agents.supply_chain_agent import SupplyChainAgent
from src.agents.production_agent import ProductionOptimizationAgent

class MasterOrchestratorAgent(BaseAgent):
    """Master agent coordinating all sub-agents"""
    
    def __init__(self):
        super().__init__(
            name="Master Orchestrator Agent",
            role="Coordinate all agents, resolve conflicts, and generate comprehensive action plans"
        )
        
        # Initialize all sub-agents
        self.sub_agents = {
            'demand': DemandForecastingAgent(),
            'inventory': InventoryManagementAgent(),
            'workforce': WorkforceManagementAgent(),
            'machine': MachineManagementAgent(),
            'supply_chain': SupplyChainAgent(),
            'production': ProductionOptimizationAgent()
        }
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate analysis from all sub-agents"""
        
        print(f"\n[ORCHESTRATOR] {self.name} coordinating analysis...")
        
        # Collect analyses from all agents
        agent_analyses = {}
        
        for agent_name, agent in self.sub_agents.items():
            try:
                print(f"  +-- {agent.name} analyzing...")
                analysis = agent.analyze(context)
                agent_analyses[agent_name] = analysis
            except Exception as e:
                print(f"  +-- {agent.name} error: {e}")
                agent_analyses[agent_name] = {'error': str(e)}
        
        # Consolidate findings
        consolidated = {
            'scenario': context.get('scenario', 'Unknown'),
            'timestamp': context.get('timestamp', 'N/A'),
            'agent_analyses': agent_analyses,
            'critical_issues': self._identify_critical_issues(agent_analyses),
            'overall_risk': self._calculate_overall_risk(agent_analyses),
            # Pass through key data fields for downstream use
            'predicted_kpi_impact': context.get('predicted_kpi_impact', 0),
            'kpi_impact_by_line': context.get('kpi_impact_by_line', {}),
            'alert_distribution': context.get('alert_distribution', {}),
            'active_alerts': context.get('active_alerts', {}),
            'existing_ai_recommendations': context.get('existing_ai_recommendations', {}),
            'event_details': context.get('event_details', []),
            'kpi_targets': context.get('kpi_targets', []),
            'scenario_description': context.get('scenario_description', ''),
            # Scenario-specific impact analysis (pre-computed, not LLM-generated)
            'scenario_impact': context.get('scenario_impact', {}),
            # Master data references
            'line_master': context.get('line_master', {}),
            'shift_master': context.get('shift_master', {}),
            'total_plant_capacity': context.get('total_plant_capacity', 0),
            'total_workers': context.get('total_workers', 0),
            'order_book': context.get('order_book', []),
            'high_range_order_book': context.get('high_range_order_book', 0),
            'medium_range_order_book': context.get('medium_range_order_book', 0),
            'suppliers': context.get('suppliers', []),
            'ai_decision_history': context.get('ai_decision_history', []),
        }
        
        print(f"  \\-- Analysis complete. Risk Level: {consolidated['overall_risk']}")
        
        return consolidated
    
    def recommend(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive orchestrated recommendations"""
        
        print(f"\n[RECOMMEND] {self.name} generating recommendations...")
        
        # Collect recommendations from all agents
        all_recommendations = []
        
        for agent_name, agent in self.sub_agents.items():
            try:
                agent_analysis = analysis['agent_analyses'].get(agent_name, {})
                if agent_analysis and 'error' not in agent_analysis:
                    recommendations = agent.recommend(agent_analysis)
                    for rec in recommendations:
                        rec['source_agent'] = agent.name
                        all_recommendations.append(rec)
            except Exception as e:
                print(f"  +-- Error from {agent.name}: {e}")
        
        # Orchestrate and prioritize recommendations
        orchestrated = self._orchestrate_recommendations(
            all_recommendations, 
            analysis
        )
        
        print(f"  \\-- Generated {len(orchestrated)} prioritized recommendations")
        
        return orchestrated
    
    def _identify_critical_issues(self, agent_analyses: Dict[str, Any]) -> List[str]:
        """Identify critical issues from agent analyses"""
        issues = []
        
        # Check demand spike
        demand_analysis = agent_analyses.get('demand', {})
        if demand_analysis.get('is_spike'):
            issues.append(f"[ALERT] Demand Spike Detected: {demand_analysis.get('risk_level', 'Medium')} Risk")
        
        # Check inventory
        inventory_analysis = agent_analyses.get('inventory', {})
        critical_items = inventory_analysis.get('critical_items', [])
        if len(critical_items) > 0:
            issues.append(f"[INVENTORY] {len(critical_items)} Critical Inventory Items")
        
        # Check workforce
        workforce_analysis = agent_analyses.get('workforce', {})
        if workforce_analysis.get('overtime_hours', 0) > 4:
            issues.append(f"[WORKFORCE] High Overtime Required: {workforce_analysis.get('overtime_hours')} hours")
        
        # Check machines
        machine_analysis = agent_analyses.get('machine', {})
        at_risk = machine_analysis.get('at_risk_machines', [])
        if len(at_risk) > 0:
            issues.append(f"[MACHINES] {len(at_risk)} Machines At Risk")
        
        # Check supply chain
        supply_analysis = agent_analyses.get('supply_chain', {})
        if supply_analysis.get('risk_level') in ['High', 'Medium']:
            issues.append(f"[SUPPLY] Supply Chain Risk: {supply_analysis.get('risk_level')}")
        
        return issues if issues else ["[OK] No Critical Issues Detected"]
    
    def _calculate_overall_risk(self, agent_analyses: Dict[str, Any]) -> str:
        """Calculate overall risk level"""
        risk_scores = {
            'Low': 1,
            'Medium': 2,
            'High': 3
        }
        
        total_score = 0
        count = 0
        
        # Aggregate risk from various analyses
        demand = agent_analyses.get('demand', {})
        if demand.get('risk_level'):
            total_score += risk_scores.get(demand['risk_level'], 1)
            count += 1
        
        supply = agent_analyses.get('supply_chain', {})
        if supply.get('risk_level'):
            total_score += risk_scores.get(supply['risk_level'], 1)
            count += 1
        
        if count == 0:
            return 'Low'
        
        avg_score = total_score / count
        
        if avg_score >= 2.5:
            return 'High'
        elif avg_score >= 1.5:
            return 'Medium'
        else:
            return 'Low'
    
    def _orchestrate_recommendations(
        self, 
        recommendations: List[Dict[str, Any]], 
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Orchestrate and prioritize recommendations using data + LLM refinement"""
        
        if not recommendations:
            return [{
                'action': 'Continue Normal Operations',
                'priority': 1,
                'reasoning': 'All systems operating within normal parameters',
                'expected_impact': 'Stable production',
                'source_agent': 'Master Orchestrator'
            }]
        
        # Sort by priority
        recommendations.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        # Take top 5 recommendations
        top_recommendations = recommendations[:5]
        
        # ====== SCENARIO IMPACT DATA (pre-computed in context builder) ======
        scenario_impact = analysis.get('scenario_impact', {})
        trigger_qty = scenario_impact.get('trigger_quantity', 0)
        trigger_type = scenario_impact.get('trigger_suv_type', '')
        trigger_event = scenario_impact.get('trigger_event', '')
        hr_capacity = scenario_impact.get('high_range_capacity_per_day', 190)
        mr_capacity = scenario_impact.get('medium_range_capacity_per_day', 345)
        total_capacity = analysis.get('total_plant_capacity', hr_capacity + mr_capacity)
        
        # ====== DATA-DRIVEN KPI IMPACT CALCULATION ======
        data_kpi_impact = analysis.get('predicted_kpi_impact', 4.0)
        shift_master = analysis.get('shift_master', {})
        suppliers = analysis.get('suppliers', [])

        total_priority = sum(r.get('priority', 3) for r in top_recommendations)
        if total_priority == 0:
            total_priority = 1

        for rec in top_recommendations:
            p = rec.get('priority', 3)
            rec['kpi_impact'] = f"+{abs(data_kpi_impact) * p / total_priority:.1f}%"
            rec['kpi_impact_formula'] = f"Data KPI ({data_kpi_impact:+.2f}%) × priority ({p}) ÷ total priority ({total_priority})"

        # ====== DATA-DRIVEN TIMELINE ESTIMATION ======
        max_overtime = 2  # default
        if shift_master:
            max_overtime = max(s.get('max_overtime_hrs', 2) for s in shift_master.values())
        
        for rec in top_recommendations:
            source = str(rec.get('source_agent', '')).lower()
            action = str(rec.get('action', '')).lower()
            
            if 'demand' in source or 'shift' in action or 'overtime' in action or 'production' in action:
                rec['estimated_time'] = f"{max(1, max_overtime)}-{max(2, max_overtime*2)} hours (based on shift max overtime: {max_overtime}h)"
            elif 'inventory' in source or 'stock' in action or 'reorder' in action:
                rec['estimated_time'] = "1-2 days (avg lead time from Inventory_Master: ~5 days, safety stock adjustment faster)"
            elif 'supply' in source or 'supplier' in action:
                if suppliers:
                    avg_supplier_lead = sum(s.get('lead_time_days', 5) for s in suppliers[:5]) / min(5, len(suppliers))
                    rec['estimated_time'] = f"1-2 weeks (avg supplier lead time: {avg_supplier_lead:.0f} days)"
                else:
                    rec['estimated_time'] = "1-2 weeks (supplier evaluation needed)"
            elif 'machine' in source or 'maintenance' in action:
                rec['estimated_time'] = "2-8 hours (based on MTTR from Assembly_Line_Master)"
            elif 'workforce' in source or 'worker' in action:
                rec['estimated_time'] = f"1-4 hours (shift change: next rotation per Shift_Master)"
            else:
                rec['estimated_time'] = "2-4 hours"

        # ====== LLM REFINEMENT — scenario-focused, capacity-constrained ======
        try:
            # Build a FOCUSED prompt with the TRIGGER EVENT, not all orders
            constraints_str = "\n".join(f"  - {c}" for c in scenario_impact.get('key_constraints', []))
            
            prompt = f"""You are the Master Orchestrator for the Pune EV SUV manufacturing plant.

TRIGGER EVENT: {trigger_event}
{f"ADDITIONAL UNITS NEEDED: {trigger_qty} {trigger_type} SUVs" if trigger_qty > 0 else ""}

PLANT CAPACITY CONSTRAINTS (HARD LIMITS — do NOT suggest exceeding these):
- High Range lines: {hr_capacity} units/day (2 lines)
- Medium Range lines: {mr_capacity} units/day (3 lines)
- Total plant capacity: {total_capacity} units/day
{constraints_str}

Medium Range impact: {scenario_impact.get('medium_range_impact', 'Assess based on scenario')}

Critical Issues: {analysis.get('critical_issues', [])}
Overall Risk: {analysis.get('overall_risk', 'Medium')}

Agent Recommendations to refine:
{self._format_recommendations(top_recommendations)}

INSTRUCTIONS:
1. Refine each recommendation to be SPECIFIC to the trigger event (e.g., "500 High Range SUVs")
2. NEVER suggest production rates exceeding plant capacity ({total_capacity} units/day total)
3. Reference actual line capacities, overtime limits, and scenario constraints
4. Make reasoning actionable for a production manager

Respond in JSON as an array with: action, priority (keep original), reasoning, source_agent (keep original)"""
            
            response = self.gemini.generate_json_response(prompt)
            
            if isinstance(response, list) and len(response) > 0:
                for i, refined in enumerate(response[:len(top_recommendations)]):
                    if isinstance(refined, dict):
                        if 'action' in refined:
                            top_recommendations[i]['action'] = refined['action']
                        if 'reasoning' in refined:
                            top_recommendations[i]['reasoning'] = refined['reasoning']
                
        except Exception as e:
            print(f"  +-- LLM refinement error (non-critical): {e}")

        return top_recommendations
    
    def _format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations for prompt"""
        formatted = ""
        for i, rec in enumerate(recommendations, 1):
            formatted += f"\n{i}. {rec.get('action', 'Unknown action')}"
            formatted += f"\n   Priority: {rec.get('priority', 0)}"
            formatted += f"\n   From: {rec.get('source_agent', 'Unknown')}"
            formatted += f"\n   Reasoning: {rec.get('reasoning', 'N/A')}\n"
        return formatted
    
    def simulate_scenario(self, scenario: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a specific scenario"""
        
        print(f"\n[SCENARIO] Simulating scenario: {scenario}")
        
        # Update context with scenario
        context['scenario'] = scenario
        
        # Run analysis
        analysis = self.analyze(context)
        
        # Generate recommendations
        recommendations = self.recommend(analysis)
        
        # Generate executive summary
        summary = self._generate_executive_summary(scenario, analysis, recommendations)
        
        return {
            'scenario': scenario,
            'analysis': analysis,
            'recommendations': recommendations,
            'summary': summary
        }
    
    def _generate_executive_summary(
        self, 
        scenario: str, 
        analysis: Dict[str, Any], 
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate executive summary focused on the specific trigger event"""
        
        try:
            scenario_impact = analysis.get('scenario_impact', {})
            trigger_event = scenario_impact.get('trigger_event', scenario)
            trigger_qty = scenario_impact.get('trigger_quantity', 0)
            hr_cap = scenario_impact.get('high_range_capacity_per_day', 190)
            mr_cap = scenario_impact.get('medium_range_capacity_per_day', 345)
            days_full = scenario_impact.get('days_to_fulfill_at_full_capacity', 0)
            days_eff = scenario_impact.get('days_to_fulfill_at_current_utilization', 0)
            mr_impact = scenario_impact.get('medium_range_impact', '')
            constraints = scenario_impact.get('key_constraints', [])
            
            prompt = f"""Generate a concise executive summary for manufacturing leadership (3-4 sentences).

TRIGGER EVENT: {trigger_event}
{f"Additional units needed: {trigger_qty} units" if trigger_qty > 0 else ""}
{f"High Range capacity: {hr_cap} units/day | Days to fulfill: ~{days_full} days (full capacity), ~{days_eff} days (current utilization)" if trigger_qty > 0 else ""}
Medium Range impact: {mr_impact}

Overall Risk: {analysis.get('overall_risk', 'Medium')}
Critical Issues: {analysis.get('critical_issues', [])}
Supply chain status: Semiconductor {analysis.get('agent_analyses', {}).get('supply_chain', {}).get('risk_level', 'Unknown')} risk
Active alerts: {analysis.get('active_alerts', {})}
KPI Impact from data: {analysis.get('predicted_kpi_impact', 0):+.2f}%
Key constraints: {constraints}

Top 3 Recommendations:
{self._format_recommendations(recommendations[:3])}

RULES:
- Focus on the SPECIFIC trigger event, not total order book
- Reference actual capacity numbers and days to fulfill
- State whether Medium Range production is affected
- Mention key risks (supply chain, inventory, etc.)
- Reference the {analysis.get('predicted_kpi_impact', 0):+.2f}% KPI improvement baseline
- Keep it professional and actionable"""
            
            summary = self.gemini.generate_response(prompt)
            return summary
        except Exception as e:
            return f"Scenario {scenario} detected. {len(recommendations)} recommendations generated. Risk level: {analysis.get('overall_risk', 'Medium')}."
