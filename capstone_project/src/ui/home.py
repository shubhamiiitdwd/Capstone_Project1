"""
Home & Overview Page
Focused overview for Use Case 3: Afternoon Line Breakdown
Shows plant status, architecture, and scenario details.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render_home():
    """Render the home/overview page"""
    data_loader = st.session_state.data_loader
    df = st.session_state.working_df

    # ---- Welcome Banner ----
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white;">
        <h1 style="margin:0; font-size:2.2rem;">Intelligent Production Scheduling System</h1>
        <p style="font-size:1.1rem; opacity:0.9; margin-top:0.5rem;">
            AI-powered decision engine for the <b>Pune EV SUV Manufacturing Plant</b>. 
            This system uses a <b>Rule Engine + ML Models + Multi-Agent AI</b> pipeline to 
            detect disruptions, predict risks, and generate actionable recovery plans.
        </p>
        <p style="font-size:0.9rem; opacity:0.7; margin-top:0.3rem;">
            Three scenarios: <b>Demand Spike</b> | <b>Semiconductor Shortage</b> | <b>Line Breakdown</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ---- Architecture Pipeline ----
    st.markdown("### AI Decision Engine Architecture")
    cols = st.columns(5)
    steps = [
        ("📥", "Input Data", "Scenario events +\nMaster data tables\n(1000 records)", "#3498db"),
        ("⚙️", "Rule Engine", "7 deterministic rules\nThreshold checks\nCapacity logic", "#e74c3c"),
        ("🧠", "ML Models", "Breakdown prediction\nDelay risk scoring\nSupplier risk", "#f39c12"),
        ("🤖", "AI Agents", "6 Specialised agents\nAzure OpenAI GPT-5.1\nMulti-agent reasoning", "#9b59b6"),
        ("📋", "Decision Log", "Full traceability\nAudit trail\nExport to CSV/JSON", "#2ecc71"),
    ]
    for col, (icon, title, desc, color) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div style="background: {color}10; border: 2px solid {color}40;
                        border-radius: 12px; padding: 1rem; text-align: center; min-height: 140px;">
                <div style="font-size: 1.8rem;">{icon}</div>
                <div style="font-weight: bold; color: {color}; margin: 0.3rem 0;">{title}</div>
                <div style="font-size: 0.75rem; color: #666; white-space: pre-line;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # ---- Scenario selector and summary ----
    scenario_options = ['Morning_Sudden_Demand_Spike', 'Midday_Semiconductor_Shortage', 'Afternoon_Line_Breakdown']
    available = [s for s in scenario_options if 'Scenario' in df.columns and s in df['Scenario'].unique()]
    if not available:
        available = scenario_options
    selected_scenario = st.selectbox(
        "View Scenario",
        options=available,
        index=2 if 'Afternoon_Line_Breakdown' in available else 0,
        key="home_scenario",
    )

    # Summary of all three scenarios
    if 'Scenario' in df.columns:
        scenario_counts = df['Scenario'].value_counts()
        c1, c2, c3 = st.columns(3)
        for col, (name, label) in zip([c1, c2, c3], [
            ('Morning_Sudden_Demand_Spike', 'UC1: Demand Spike'),
            ('Midday_Semiconductor_Shortage', 'UC2: Semiconductor'),
            ('Afternoon_Line_Breakdown', 'UC3: Line Breakdown'),
        ]):
            with col:
                cnt = scenario_counts.get(name, 0)
                st.metric(label, f"{cnt} records")

    st.markdown("### Scenario Details")

    # Event details from master data (scenario-specific)
    event_map = {
        'Morning_Sudden_Demand_Spike': 'Event_Demand_Spike',
        'Midday_Semiconductor_Shortage': 'Event_Chip_Delay',
        'Afternoon_Line_Breakdown': 'Event_Line_Breakdown',
    }
    event_sheet = event_map.get(selected_scenario, 'Event_Line_Breakdown')
    event_data = data_loader.scenarios.get(event_sheet, pd.DataFrame())
    ev = event_data.iloc[0].to_dict() if not event_data.empty else {}

    scenario_descriptions = {
        'Morning_Sudden_Demand_Spike': 'Europe dealer requests 500 High Range SUVs - 180% demand increase. The system must optimize shifts, inventory, and assembly lines without impacting medium-range production.',
        'Midday_Semiconductor_Shortage': 'Chip supplier reports critical semiconductor shortage - 48hr delay. High Range SUV assembly line affected. The system must generate alternatives: accelerate models, alternate suppliers, swap line sequences.',
        'Afternoon_Line_Breakdown': 'At 3:45 PM during Shift B, a robot on the HighRange assembly line malfunctions. This takes one of the two High Range production lines offline. The system must reallocate production, adjust workforce, check inventory impact, and coordinate a recovery plan.',
    }
    what_happens = scenario_descriptions.get(selected_scenario, ev.get('Description', ''))

    ev_col1, ev_col2 = st.columns([2, 1])
    with ev_col1:
        st.markdown(f"""
        <div style="background: #fff3e0; border-left: 5px solid #ff9800;
                    border-radius: 10px; padding: 1.2rem; margin-bottom: 1rem;">
            <h4 style="margin:0 0 0.5rem;">Scenario Event</h4>
            <table style="width:100%; font-size: 0.9rem;">
                <tr><td style="width:140px; color:#888;"><b>Event ID:</b></td><td>{ev.get('Event_ID', 'EV003')}</td></tr>
                <tr><td style="color:#888;"><b>Description:</b></td><td>{ev.get('Description', 'Robot breakdown on HighRange assembly line')}</td></tr>
                <tr><td style="color:#888;"><b>Impact Areas:</b></td><td>{ev.get('Impact_Areas', 'High Range SUV Production')}</td></tr>
                <tr><td style="color:#888;"><b>Expected Impact:</b></td><td><span style="background:#e74c3c; color:white; padding:2px 8px; border-radius:4px;">{ev.get('Expected_Impact', 'High')}</span></td></tr>
                <tr><td style="color:#888;"><b>Event Date:</b></td><td>{ev.get('Event_Date', '2025-11-05')}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: #e8f4fd; border-radius: 8px; padding: 1rem; font-size: 0.9rem;">
            <b>What happens:</b> {what_happens}
        </div>
        """, unsafe_allow_html=True)

    with ev_col2:
        # Line capacity card
        line_master_df = data_loader.get_master_table('Assembly_Line_Master')
        if not line_master_df.empty:
            st.markdown("**Assembly Line Capacities:**")
            for _, row in line_master_df.iterrows():
                color = '#e74c3c' if 'High' in row['SUV_Type'] else '#3498db'
                st.markdown(f"""
                <div style="background: {color}10; border-left: 3px solid {color};
                            padding: 0.4rem 0.6rem; margin: 0.2rem 0; border-radius: 4px; font-size: 0.85rem;">
                    <b>{row['Line_Name']}</b>: {int(row['Daily_Capacity'])} units/day
                    <span style="color:#888;">({row['SUV_Type']}, OEE {row['OEE_%']:.0f}%)</span>
                </div>
                """, unsafe_allow_html=True)
            total_cap = int(line_master_df['Daily_Capacity'].sum())
            st.markdown(f"**Total Plant Capacity: {total_cap} units/day**")

    st.markdown("---")

    # ---- Plant Performance at a Glance ----
    st.markdown("### Plant Performance at a Glance")

    # Use the selected scenario data
    scenario_df = df[df['Scenario'] == selected_scenario] if 'Scenario' in df.columns else df

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    metrics = [
        (m1, "Records", f"{len(scenario_df):,}", "#3498db"),
        (m2, "Avg Production", f"{scenario_df['Production_Output'].mean():.0f}", "#2ecc71"),
        (m3, "Machine Uptime", f"{scenario_df['Machine_Uptime_%'].mean():.1f}%", "#f39c12"),
        (m4, "Worker Avail.", f"{scenario_df['Worker_Availability_%'].mean():.1f}%", "#9b59b6"),
        (m5, "Defect Rate", f"{scenario_df['Defect_Rate_%'].mean():.2f}%", "#1abc9c"),
        (m6, "Avg KPI Impact", f"+{scenario_df['Predicted_KPI_Impact_%'].mean():.2f}%" if 'Predicted_KPI_Impact_%' in scenario_df.columns else "N/A", "#e74c3c"),
    ]
    for col, (_, label, value, color) in zip([m1, m2, m3, m4, m5, m6], metrics):
        with col:
            st.markdown(f"""
            <div style="background: {color}12; border: 2px solid {color}40;
                        border-radius: 12px; padding: 1rem; text-align: center;">
                <p style="font-size: 0.78rem; color: #888; margin:0;">{label}</p>
                <h2 style="margin: 0.3rem 0; color: {color};">{value}</h2>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # ---- Charts ----
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### Production by Assembly Line ({selected_scenario.replace('_', ' ')})")
        line_data = scenario_df.groupby('Assembly_Line').agg({
            'Production_Output': 'mean',
            'Machine_Uptime_%': 'mean',
        }).reset_index()

        fig = px.bar(
            line_data, x='Assembly_Line', y='Production_Output',
            color='Machine_Uptime_%',
            color_continuous_scale='RdYlGn',
            title='Avg Production Output (color = Machine Uptime %)',
            labels={'Production_Output': 'Avg Units', 'Assembly_Line': 'Line'}
        )
        fig.update_layout(height=380)
        st.plotly_chart(fig, key="home_prod_chart")

    with col2:
        st.markdown("### Shift Performance")
        shift_data = scenario_df.groupby('Shift').agg({
            'Production_Output': 'mean',
            'Worker_Availability_%': 'mean',
        }).reset_index()
        shift_data['Shift_Label'] = shift_data['Shift'].map({
            'A': 'Shift A (Morning)', 'B': 'Shift B (Afternoon)', 'C': 'Shift C (Night)'
        })

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Production', x=shift_data['Shift_Label'],
            y=shift_data['Production_Output'], marker_color='#3498db'
        ))
        fig.add_trace(go.Bar(
            name='Worker Avail %', x=shift_data['Shift_Label'],
            y=shift_data['Worker_Availability_%'], marker_color='#2ecc71'
        ))
        fig.update_layout(barmode='group', title='Production vs Worker Availability', height=380)
        st.plotly_chart(fig, key="home_shift_chart")

    # ---- Data Sources ----
    st.markdown("---")
    st.markdown("### Data Sources")

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("""
        <div style="background: #e8f4fd; border-radius: 10px; padding: 1.2rem; border: 1px solid #bee5eb;">
            <h4 style="margin:0 0 0.5rem;">📊 Simulation Data (Expanded)</h4>
            <p><b>1,000 production records</b> across 3 data splits:</p>
            <ul style="font-size: 0.9rem;">
                <li>Train Data: 500 records</li>
                <li>Validation Data: 300 records</li>
                <li><b>Test Data: 200 records</b> (Use Case 3)</li>
            </ul>
            <p style="font-size:0.82rem; color:#666;">Each record: demand, output, machine health, 
            worker status, inventory, quality, semiconductors, alerts, KPI impact.</p>
        </div>
        """, unsafe_allow_html=True)
    with d2:
        master_count = sum(len(v) for v in data_loader.master_data.values())
        st.markdown(f"""
        <div style="background: #fef9e7; border-radius: 10px; padding: 1.2rem; border: 1px solid #fdebd0;">
            <h4 style="margin:0 0 0.5rem;">📋 Master & Reference Data</h4>
            <p><b>{master_count}+ reference records</b> across 9+ sheets:</p>
            <ul style="font-size: 0.9rem;">
                <li>Assembly Lines (5), Shifts (3), Suppliers (20)</li>
                <li>Inventory (120 items), BOM (50), Machines (30)</li>
                <li>Orders (20), KPI Targets (3), AI Decision Log (10)</li>
            </ul>
            <p style="font-size:0.82rem; color:#666;">Provides context for AI decisions: 
            capacities, lead times, suppliers, order dates.</p>
        </div>
        """, unsafe_allow_html=True)

    # ---- How to use ----
    st.markdown("---")
    st.markdown("""
    <div style="background: #f0f2f6; border-radius: 10px; padding: 1.2rem;">
        <h4 style="margin:0 0 0.5rem;">How to Use</h4>
        <ol style="font-size: 0.9rem;">
            <li>Review the plant overview above to understand the current state.</li>
            <li>Switch to the <b>AI Decision Engine</b> tab.</li>
            <li>Click <b>"Run Full Analysis"</b> to trigger the complete pipeline:
                Rule Engine → ML Models → AI Agents → Decision Log.</li>
            <li>Review results across 6 sub-tabs: Rules, ML, Recommendations, Agents, Decision Log, Raw Data.</li>
            <li>Download the Decision Log (JSON/CSV) for auditing and traceability.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
