import streamlit as st
import plotly.graph_objects as go
import json

# Sample data structure for business goals and their connections
data = {
    "Awareness": {
        "Strategic Imperatives": "Prioritize reach and frequency",
        "KPIs": ["Brand Lift", "% Reach", "Frequency"],
        "Core Audiences": ["Influencers and early adopters", "Interest-based prospecting"],
        "Messaging Approach": "Emotional storytelling"
    },
    "Growth": {
        "Strategic Imperatives": "Maximize purchase volume",
        "KPIs": ["Customer acquisition costs (CAC)", "Sales volume"],
        "Core Audiences": ["Category buyers", "Lookalikes"],
        "Messaging Approach": "Highlight key value propositions"
    }
    # Add more objectives as needed
}

# Streamlit UI setup
st.title("Cortex: Interactive Business Planning")
st.write("Select your business objective to explore relevant strategies and metrics.")

# Dropdown for selecting objectives
selected_objective = st.selectbox("Choose Business Objective", list(data.keys()))

# Displaying details based on selection
if selected_objective:
    st.subheader(f"Strategic Approach for {selected_objective}")
    st.write("**Strategic Imperatives:**", data[selected_objective]["Strategic Imperatives"])
    st.write("**KPIs:**", ", ".join(data[selected_objective]["KPIs"]))
    st.write("**Core Audiences:**", ", ".join(data[selected_objective]["Core Audiences"]))
    st.write("**Messaging Approach:**", data[selected_objective]["Messaging Approach"])

    # Mind map visualization
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[0, -1, 1, -1, 1],
        y=[0, 1, 1, -1, -1],
        text=[selected_objective, "Strategic Imperatives", "KPIs", "Core Audiences", "Messaging Approach"],
        mode="text",
    ))
    
    st.plotly_chart(fig, use_container_width=True)