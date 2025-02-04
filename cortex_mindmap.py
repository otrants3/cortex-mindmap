import streamlit as st
import plotly.graph_objects as go

# Sample data structure for business objectives
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
}

# Sample case studies mapping (objective, industry) to case study text
case_studies = {
    ("Awareness", "CPG"): "Example: Company A increased brand lift by 20% with targeted influencer marketing.",
    ("Growth", "Tech"): "Example: Company B achieved a 15% sales increase with performance marketing.",
    ("Awareness", "Tech"): "Example: Company C boosted online engagement by 25% via digital campaigns.",
    ("Growth", "CPG"): "Example: Company D reduced CAC by 10% through optimized ad spend."
}

# Color mapping for business objectives
color_map = {
    "Awareness": "blue",
    "Growth": "green"
}

# Sidebar: Custom Client Inputs
st.sidebar.header("Client Inputs")
business_objective = st.sidebar.selectbox("Business Objective", list(data.keys()))
brand_lifecycle = st.sidebar.selectbox("Brand Lifecycle Stage", ["New", "Growing", "Mature", "Declining"])
industry_type = st.sidebar.selectbox("Industry Type", ["CPG", "Tech", "Finance", "Retail"])
marketing_priorities = st.sidebar.multiselect(
    "Marketing Priorities", 
    ["Increase conversions", "Boost retention", "Improve brand awareness", "Increase sales volume"]
)

# Main Title & Intro
st.title("Cortex: Interactive Business Planning")
st.write("Explore tailored strategies and insights based on your business inputs.")

# Display Client Selections
st.subheader("Your Selections")
st.write(f"**Business Objective:** {business_objective}")
st.write(f"**Brand Lifecycle Stage:** {brand_lifecycle}")
st.write(f"**Industry Type:** {industry_type}")
st.write("**Marketing Priorities:**", ", ".join(marketing_priorities) if marketing_priorities else "None selected")

# Expanders for Strategy Details
st.subheader(f"Strategic Approach for {business_objective}")
with st.expander("Strategic Imperatives"):
    st.write(data[business_objective]["Strategic Imperatives"])
with st.expander("KPIs"):
    st.write(", ".join(data[business_objective]["KPIs"]))
with st.expander("Core Audiences"):
    st.write(", ".join(data[business_objective]["Core Audiences"]))
with st.expander("Messaging Approach"):
    st.write(data[business_objective]["Messaging Approach"])

# Interactive Mind Map Visualization
st.subheader("Interactive Mind Map")
fig = go.Figure()

# Define coordinates for each node (central node and four branches)
nodes = {
    business_objective: (0, 0),
    "Strategic Imperatives": (-1, 1),
    "KPIs": (1, 1),
    "Core Audiences": (-1, -1),
    "Messaging Approach": (1, -1)
}

# Create lists for coordinates, text, and colors
node_x = [coord[0] for coord in nodes.values()]
node_y = [coord[1] for coord in nodes.values()]
node_text = list(nodes.keys())
node_colors = []
for text in node_text:
    if text == business_objective:
        node_colors.append(color_map.get(business_objective, "black"))
    else:
        node_colors.append("grey")

# Plot the nodes
fig.add_trace(go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',
    marker=dict(size=20, color=node_colors),
    text=node_text,
    textposition="bottom center"
))

# Draw lines connecting the central objective to the other nodes
center = nodes[business_objective]
for node, coord in nodes.items():
    if node != business_objective:
        fig.add_shape(type="line",
                      x0=center[0], y0=center[1],
                      x1=coord[0], y1=coord[1],
                      line=dict(color="lightgrey", width=2))

# Hide axes and set layout margins
fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# Display Case Study based on objective and industry
st.subheader("Case Study & Benchmarking")
case_key = (business_objective, industry_type)
case_text = case_studies.get(case_key, "No specific case study available for these selections. Explore our other campaigns for similar insights.")
st.write(case_text)

# Backend Recommendations based on Marketing Priorities
st.subheader("Recommendations")
recommendations = []
if "Increase conversions" in marketing_priorities:
    recommendations.append("Optimize your website and landing pages to drive conversions.")
if "Boost retention" in marketing_priorities:
    recommendations.append("Invest in customer loyalty programs and retention strategies.")
if "Improve brand awareness" in marketing_priorities:
    recommendations.append("Focus on broad-reaching campaigns and influencer collaborations.")
if "Increase sales volume" in marketing_priorities:
    recommendations.append("Leverage performance marketing and targeted promotions.")

if recommendations:
    for rec in recommendations:
        st.write(f"- {rec}")
else:
    st.write("No specific recommendations. Consider exploring our full range of strategies.")

# Generate a Report Summary for Download
st.subheader("Export Your Cortex Plan")
report = f"""
Cortex Plan Report

Business Objective: {business_objective}
Brand Lifecycle Stage: {brand_lifecycle}
Industry Type: {industry_type}
Marketing Priorities: {", ".join(marketing_priorities) if marketing_priorities else "None"}

Strategic Imperatives: {data[business_objective]['Strategic Imperatives']}
KPIs: {", ".join(data[business_objective]['KPIs'])}
Core Audiences: {", ".join(data[business_objective]['Core Audiences'])}
Messaging Approach: {data[business_objective]['Messaging Approach']}

Case Study: {case_text}

Recommendations:
"""
for rec in recommendations:
    report += f"- {rec}\n"

st.download_button(label="Download Report", data=report, file_name="cortex_plan_report.txt", mime="text/plain")
