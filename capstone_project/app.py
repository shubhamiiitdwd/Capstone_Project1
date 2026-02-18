"""
Intelligent Production Scheduling System
Main Streamlit Application

Use Case 3: Afternoon Line Breakdown
Architecture: Rule Engine + ML Models + Multi-Agent AI + Azure OpenAI GPT-5.1
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="AI Decision Engine - Pune EV SUV Plant",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# IMPORTS
# ============================================================================
from src.data.enhanced_data_loader import EnhancedDataLoader
from src.agents.orchestrator import MasterOrchestratorAgent
from src.utils.azure_openai_client import get_azure_openai_client

# Page renderers
from src.ui.ai_engine import render_ai_engine

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        max-width: 1400px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 16px; font-size: 0.95rem; }
    [data-testid="stMetricValue"] { font-size: 1.5rem; }
    .stDataFrame { border-radius: 8px; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stTextInput label { color: #ffffff !important; }
    header { visibility: hidden; }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
    }
    .streamlit-expanderHeader { font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_system():
    """Initialize all system components"""
    try:
        orchestrator = MasterOrchestratorAgent()
        data_loader = EnhancedDataLoader()
        data_loader.load_all_data()
        data_loader.process_data()
        return orchestrator, data_loader
    except Exception as e:
        st.error(f"System initialization error: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None, None


def init_session_state():
    """Initialize session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.orchestrator = None
        st.session_state.data_loader = None
        st.session_state.working_df = None
        st.session_state.original_df = None
        st.session_state.current_analysis = None
        st.session_state.model_choice = 'AzureOpenAI'
        st.session_state.ml_manager = None


# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    """Render sidebar with model info and plant status"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="margin:0; color: #ffffff;">🏭 EV SUV Plant</h2>
            <p style="margin:0; font-size: 0.85rem; color: #aaa;">AI Decision Engine</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # --- AI Model (Azure OpenAI only) ---
        st.markdown("### 🤖 AI Model")
        try:
            client = get_azure_openai_client()
            info = client.get_model_info()
            st.success(f"Active: {info['model']}")
            st.caption(f"Endpoint: ...{info['endpoint'][-30:]}")
        except Exception as e:
            st.error(f"Azure OpenAI error: {e}")

        st.markdown("---")

        # --- System Status ---
        st.markdown("### 📊 System Status")
        if st.session_state.data_loader:
            stats = st.session_state.data_loader.get_statistics()
            st.metric("Total Records", f"{stats['total_records']:,}")
            st.metric("Assembly Lines", len(stats['assembly_lines']))
            ml_mgr = st.session_state.get('ml_manager')
            if ml_mgr and ml_mgr.trained:
                st.success("ML Models: Trained")
            else:
                st.warning("ML Models: Not trained")

        st.markdown("---")

        # --- Plant Info ---
        st.markdown("### 🏭 Plant Info")
        st.caption("Location: Pune, India")
        st.caption("Product: EV SUVs (High & Medium Range)")
        st.caption("Lines: 5 Assembly Lines")
        st.caption("Shifts: 3 (A, B, C)")
        st.caption("Total Capacity: 535 units/day")

        st.markdown("---")
        st.caption("Built with Streamlit & Multi-Agent AI")
        st.caption(f"Session: {datetime.now().strftime('%H:%M:%S')}")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    init_session_state()

    # Load data if not initialized
    if not st.session_state.initialized:
        with st.spinner("Initializing system — loading data, training ML models..."):
            orchestrator, data_loader = initialize_system()

            if orchestrator and data_loader:
                st.session_state.orchestrator = orchestrator
                st.session_state.data_loader = data_loader
                st.session_state.working_df = data_loader.df.copy()
                st.session_state.original_df = data_loader.df.copy()

                # Train ML models on full simulation data
                try:
                    from src.engine.ml_models import MLModelManager
                    ml_mgr = MLModelManager()
                    ml_mgr.train(data_loader.df)
                    st.session_state.ml_manager = ml_mgr
                except Exception as e:
                    print(f"[WARN] ML model training skipped: {e}")

                st.session_state.initialized = True
            else:
                st.error("Failed to initialize. Check that both Excel files exist.")
                st.stop()

    # Render sidebar
    render_sidebar()

    # --- Main Header ---
    total_records = f"{len(st.session_state.working_df):,}" if st.session_state.working_df is not None else "0"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                padding: 0.8rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;
                display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin:0; color: white; font-size: 1.8rem;">
                🏭 Intelligent Production Scheduling System
            </h1>
            <p style="margin:0; color: #aaa; font-size: 0.9rem;">
                Use Case 3: Afternoon Line Breakdown | Pune EV SUV Plant
            </p>
        </div>
        <div style="text-align: right; color: #aaa; font-size: 0.8rem;">
            <p style="margin:0;">Records: <b style="color:#3498db;">{total_records}</b> | 
               Model: <b style="color:#2ecc71;">Azure OpenAI GPT-5.1</b></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Main Content: AI Decision Engine ---
    try:
        render_ai_engine()
    except Exception as e:
        st.error(f"Error rendering AI Engine: {e}")
        import traceback
        with st.expander("Error details"):
            st.code(traceback.format_exc())

    # --- Footer ---
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem;">
        <p style="margin:0;">
            Powered by Azure OpenAI GPT-5.1 + Multi-Agent AI + Rule Engine + ML Models
        </p>
        <p style="margin:0; font-size: 0.8rem;">
            Capstone Project 2026 | Intelligent Production Scheduling for Pune EV SUV Plant
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
