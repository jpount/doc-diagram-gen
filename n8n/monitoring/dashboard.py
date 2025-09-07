#!/usr/bin/env python3
"""
Simple Monitoring Dashboard for n8n Documentation Framework
Optional component - can be disabled in docker-compose
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import httpx
import asyncio
from pathlib import Path
import time

st.set_page_config(
    page_title="Documentation Framework Monitor",
    page_icon="📊",
    layout="wide"
)

# API Configuration
API_URL = "http://doc-framework-api:8100"

def get_session_status(session_id: str = None):
    """Get current session status from API"""
    try:
        if session_id:
            response = httpx.get(f"{API_URL}/n8n/status/{session_id}", timeout=5.0)
        else:
            # Try to get latest session from context
            context_dir = Path("/app/output/context")
            if context_dir.exists():
                session_file = context_dir / "session-progress.json"
                if session_file.exists():
                    with open(session_file) as f:
                        data = json.load(f)
                        session_id = data.get("session_id")
                        if session_id:
                            response = httpx.get(f"{API_URL}/n8n/status/{session_id}", timeout=5.0)
                        else:
                            return None
                else:
                    return None
            else:
                return None
        
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to get status: {e}")
        return None

def main():
    st.title("📊 Documentation Framework Monitor")
    st.markdown("Real-time monitoring for n8n workflow execution")
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        # Session ID input
        session_id = st.text_input("Session ID", placeholder="Enter session ID or leave blank for latest")
        
        # Refresh interval
        refresh_interval = st.slider("Refresh Interval (seconds)", 1, 30, 5)
        
        # Auto-refresh checkbox
        auto_refresh = st.checkbox("Auto Refresh", value=True)
        
        if auto_refresh:
            st.empty()  # Placeholder for refresh countdown
    
    # Main content area
    col1, col2, col3, col4 = st.columns(4)
    
    # Get status
    status = get_session_status(session_id)
    
    if status and status.get("success", True):
        # Display metrics
        with col1:
            st.metric("Progress", f"{status.get('progress_percentage', 0):.1f}%")
        
        with col2:
            completed = len(status.get('agents', {}).get('completed', []))
            st.metric("Completed Agents", completed)
        
        with col3:
            running = len(status.get('agents', {}).get('running', []))
            st.metric("Running Agents", running)
        
        with col4:
            failed = len(status.get('agents', {}).get('failed', []))
            st.metric("Failed Agents", failed, delta_color="inverse")
        
        # Progress bar
        st.progress(status.get('progress_percentage', 0) / 100)
        
        # Agent status details
        st.subheader("Agent Status")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Completed", "Running", "Pending", "Failed"])
        
        with tab1:
            completed_agents = status.get('agents', {}).get('completed', [])
            if completed_agents:
                st.success(f"✅ {len(completed_agents)} agents completed")
                for agent in completed_agents:
                    st.write(f"• {agent}")
            else:
                st.info("No agents completed yet")
        
        with tab2:
            running_agents = status.get('agents', {}).get('running', [])
            if running_agents:
                st.warning(f"🔄 {len(running_agents)} agents running")
                for agent in running_agents:
                    st.write(f"• {agent}")
            else:
                st.info("No agents currently running")
        
        with tab3:
            pending_agents = status.get('agents', {}).get('pending', [])
            if pending_agents:
                st.info(f"⏳ {len(pending_agents)} agents pending")
                for agent in pending_agents:
                    st.write(f"• {agent}")
            else:
                st.info("No agents pending")
        
        with tab4:
            failed_agents = status.get('agents', {}).get('failed', [])
            if failed_agents:
                st.error(f"❌ {len(failed_agents)} agents failed")
                for agent in failed_agents:
                    st.write(f"• {agent}")
            else:
                st.success("No failed agents")
        
        # Workflow visualization
        st.subheader("Workflow Progress")
        
        # Create a simple progress chart
        all_agents = (
            status.get('agents', {}).get('completed', []) +
            status.get('agents', {}).get('running', []) +
            status.get('agents', {}).get('pending', []) +
            status.get('agents', {}).get('failed', [])
        )
        
        if all_agents:
            # Create dataframe for visualization
            agent_data = []
            for agent in all_agents:
                if agent in status.get('agents', {}).get('completed', []):
                    agent_status = 'Completed'
                    color = 'green'
                elif agent in status.get('agents', {}).get('running', []):
                    agent_status = 'Running'
                    color = 'orange'
                elif agent in status.get('agents', {}).get('failed', []):
                    agent_status = 'Failed'
                    color = 'red'
                else:
                    agent_status = 'Pending'
                    color = 'gray'
                
                agent_data.append({
                    'Agent': agent,
                    'Status': agent_status,
                    'Color': color
                })
            
            df = pd.DataFrame(agent_data)
            
            # Create horizontal bar chart
            fig = px.bar(df, x='Status', color='Status',
                        color_discrete_map={
                            'Completed': 'green',
                            'Running': 'orange',
                            'Pending': 'lightgray',
                            'Failed': 'red'
                        },
                        title="Agent Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Session information
        st.subheader("Session Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Session ID:** {status.get('session_id', 'N/A')}")
            st.write(f"**Phase:** {status.get('phase', 'N/A')}")
        
        with col2:
            st.write(f"**Last Updated:** {status.get('last_updated', 'N/A')}")
            if status.get('is_complete'):
                st.success("✅ Workflow Complete!")
            else:
                st.info("🔄 Workflow in progress...")
        
    else:
        st.warning("No active session found or unable to connect to API")
        st.info("Make sure the n8n workflow is running and the API server is accessible")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()