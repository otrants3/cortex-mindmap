import streamlit as st
import plotly.graph_objects as go
import math

# -------------------------------
# CUSTOM CSS FOR A POLISHED LOOK
# -------------------------------
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        color: #333333;
    }
    .main-title {
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 0.2em;
    }
    .subtitle {
        font-size: 1.2em;
        margin-top: 1em;
        margin-bottom: 0.5em;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# DATA STRUCTURES
# -------------------------------
objectives = {
    "Awareness": {
        "Strategic Imperatives": "Prioritize reach and frequency",
        "KPIs": "Brand Lift, % Reach, Frequency",
        "Core Audiences": "Influencers and early adopters, Interest-based prospecting",
        "Messaging Approach": "Emotional storytelling"
    },
    "Growth": {
        "Strategic Imperatives": "Maximize purchase volume",
        "KPIs": "Customer acquisition costs (CAC), Sales volume",
        "Core Audiences": "Category buyers, Lookalikes",
        "Messaging Approach": "Highlight key value propositions"
    },
    "Profitability": {
        "Strategic Imperatives": "Optimize for high margin products and high LTV consumers",
        "KPIs": "LTV/CAC ratio, Incremental sales lift, Marginal ROI",
        "Core Audiences": "Cart abandoners, 1P CRM segments",
        "Messaging Approach": "Upselling and cross-selling"
    },
    "Buy Rate": {
        "Strategic Imperatives": "Increase purchase frequency",
        "KPIs": "Repeat purchase rate, Customer retention",
        "Core Audiences": "Existing brand buyers, Lapsed brand buyers",
        "Messaging Approach": "Personalized recommendations and loyalty incentives"
    },
    "Household Penetration": {
        "Strategic Imperatives": "Grow the customer base",
        "KPIs": "Household penetration %, New to brand sales",
        "Core Audiences": "Competitor buyers, New life stage consumers",
        "Messaging Approach": "Problem-solution framing to appeal to new users"
    }
}

# -------------------------------
# SIDEBAR: CLIENT INPUTS
# -------------------------------
st.sidebar.header("Client Inputs")
top_priority = st.sidebar.selectbox("Top Priority Objective", list(objectives.keys()))
brand_lifecycle = st.sidebar.selectbox("Brand Lifecycle Stage", ["New", "Growing", "Mature", "Declining"])
industry_type = st.sidebar.selectbox("Industry Type", ["CPG", "Tech", "Finance", "Retail"])
marketing_priorities = st.sidebar.multiselect(
    "Marketing Priorities", 
    ["Increase conversions", "Boost retention", "Improve brand awareness", "Increase sales volume"]
)

# -------------------------------
# HEADER & INSTRUCTIONS
# -------------------------------
st.markdown('<h1 class="main-title">Cortex: Professional Paid Media Strategy Tool</h1>', unsafe_allow_html=True)
st.write("Welcome! Use the sidebar to input your business criteria. Hover over the nodes for details, and use your mouse (or trackpad) to zoom and pan the interactive map. Once satisfied, click on **Download Report** for a detailed strategy summary.")

st.subheader("Your Inputs")
st.write(f"**Top Priority Objective:** {top_priority}")
st.write(f"**Brand Lifecycle Stage:** {brand_lifecycle}")
st.write(f"**Industry Type:** {industry_type}")
st.write(f"**Marketing Priorities:** {', '.join(marketing_priorities) if marketing_priorities else 'None'}")

# -------------------------------
# INTERACTIVE MIND MAP SETUP
# -------------------------------
st.subheader("Interactive Paid Media Strategy Map")

# Parameters for node positioning
R_main = 3      # radius for main nodes from center
R_sub = 1       # radius for sub-nodes (only for top priority)
R_detail = 0.7  # radius for detail nodes from sub-node

center_x, center_y = 0, 0

# Fixed angles (in degrees) for main nodes arranged radially
angles = {
    "Awareness": 90,
    "Growth": 18,
    "Profitability": -54,
    "Buy Rate": -126,
    "Household Penetration": -198  # Equivalent to 162°
}

# -------------------------------
# BUILD THE NODE ARRAYS
# -------------------------------
node_x = []
node_y = []
node_text = []
node_hover = []
node_color = []
node_size = []

# 1. Central Node
node_x.append(center_x)
node_y.append(center_y)
node_text.append("Paid Media Strategy")
node_hover.append("Central Strategy Node")
node_color.append("black")
node_size.append(25)

# 2. Main Nodes for each objective
main_positions = {}   # store (x, y) for each main node
main_angles = {}      # store the assigned angle for each main node

i = 1  # index counter for main nodes
for obj, angle_deg in angles.items():
    angle_rad = math.radians(angle_deg)
    x = center_x + R_main * math.cos(angle_rad)
    y = center_y + R_main * math.sin(angle_rad)
    main_positions[obj] = (x, y)
    main_angles[obj] = angle_deg
    node_x.append(x)
    node_y.append(y)
    node_text.append(obj)
    hover_info = f"{obj}: {objectives[obj]['Strategic Imperatives']}"
    node_hover.append(hover_info)
    # Highlight the top priority node
    if obj == top_priority:
        node_color.append("red")
        node_size.append(20)
    else:
        node_color.append("blue")
        node_size.append(15)
    i += 1

# 3. Sub-Nodes for the top priority objective only
sub_nodes = []  # Will store tuples: (x, y, label, hover_text, base_angle)
if top_priority in main_positions:
    sub_node_labels = ["Strategic Imperatives", "KPIs", "Core Audiences", "Messaging Approach"]
    sub_offsets = [45, -45, 135, -135]  # relative offsets from the main node angle
    main_angle = main_angles[top_priority]
    main_x, main_y = main_positions[top_priority]
    for j, sub_label in enumerate(sub_node_labels):
        sub_angle = main_angle + sub_offsets[j]
        sub_angle_rad = math.radians(sub_angle)
        sx = main_x + R_sub * math.cos(sub_angle_rad)
        sy = main_y + R_sub * math.sin(sub_angle_rad)
        detail_text = objectives[top_priority][sub_label]
        sub_hover = f"{sub_label} for {top_priority}: {detail_text}"
        sub_nodes.append((sx, sy, sub_label, sub_hover, sub_angle))
        node_x.append(sx)
        node_y.append(sy)
        node_text.append(sub_label)
        node_hover.append(sub_hover)
        node_color.append("orange")
        node_size.append(12)

# 4. Detail Nodes branching off each sub-node (only for top priority)
detail_nodes = []
for sub in sub_nodes:
    sx, sy, sub_label, sub_hover, base_angle = sub
    detail_str = objectives[top_priority][sub_label]
    # For KPIs and Core Audiences, split details by comma; else, use the full text.
    if sub_label in ["KPIs", "Core Audiences"]:
        details = [d.strip() for d in detail_str.split(",")]
    else:
        details = [detail_str]
    
    n_details = len(details)
    for idx, detail in enumerate(details):
        delta = (idx - (n_details - 1) / 2) * 15 if n_details > 1 else 0
        detail_angle = base_angle + delta
        detail_angle_rad = math.radians(detail_angle)
        dx = sx + R_detail * math.cos(detail_angle_rad)
        dy = sy + R_detail * math.sin(detail_angle_rad)
        detail_label = detail
        detail_hover = f"{sub_label} Detail: {detail}"
        detail_nodes.append((dx, dy, detail_label, detail_hover))
        node_x.append(dx)
        node_y.append(dy)
        node_text.append(detail_label)
        node_hover.append(detail_hover)
        node_color.append("purple")
        node_size.append(8)

# -------------------------------
# BUILD THE PLOTLY FIGURE
# -------------------------------
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',
    text=node_text,
    textposition="top center",
    marker=dict(color=node_color, size=node_size),
    hovertext=node_hover,
    hoverinfo="text"
))

# Draw lines from the central node to each main node
for obj, pos in main_positions.items():
    fig.add_shape(
        type="line",
        x0=center_x, y0=center_y,
        x1=pos[0], y1=pos[1],
        line=dict(color="lightgrey", width=2)
    )

# Draw lines from the top priority main node to its sub-nodes
if top_priority in main_positions:
    main_pos = main_positions[top_priority]
    for sub in sub_nodes:
        sx, sy, _, _, _ = sub
        fig.add_shape(
            type="line",
            x0=main_pos[0], y0=main_pos[1],
            x1=sx, y1=sy,
            line=dict(color="lightgrey", width=1.5)
        )

# Draw lines from each sub-node to its detail nodes
for sub in sub_nodes:
    sx, sy, sub_label, _, base_angle = sub
    detail_str = objectives[top_priority][sub_label]
    if sub_label in ["KPIs", "Core Audiences"]:
        details = [d.strip() for d in detail_str.split(",")]
    else:
        details = [detail_str]
    n_details = len(details)
    for idx in range(n_details):
        delta = (idx - (n_details - 1) / 2) * 15 if n_details > 1 else 0
        detail_angle = base_angle + delta
        detail_angle_rad = math.radians(detail_angle)
        dx = sx + R_detail * math.cos(detail_angle_rad)
        dy = sy + R_detail * math.sin(detail_angle_rad)
        fig.add_shape(
            type="line",
            x0=sx, y0=sy,
            x1=dx, y1=dy,
            line=dict(color="lightgrey", width=1)
        )

# Enhanced layout: enable panning/zoom and set a clean white background.
fig.update_layout(
    dragmode="pan",
    hovermode="closest",
    margin=dict(l=40, r=40, t=40, b=40),
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="#333333", size=12),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# CASE STUDY & PROFESSIONAL REPORTING
# -------------------------------
st.subheader("Case Study & Benchmarking")
st.write(f"Based on your top priority of **{top_priority}**, here's a placeholder case study:")
st.write("**Case Study:** Our client [Placeholder] achieved remarkable results by aligning their paid media strategy with this objective. Detailed insights and outcomes will be shared soon.")

# Generate a professionally formatted report (Markdown format)
report = f"""
# Cortex Plan Report

**Business Objective:** {top_priority}  
**Brand Lifecycle Stage:** {brand_lifecycle}  
**Industry Type:** {industry_type}  
**Marketing Priorities:** {', '.join(marketing_priorities) if marketing_priorities else 'None'}  

## Strategic Details
- **Strategic Imperatives:** {objectives[top_priority]['Strategic Imperatives']}
- **KPIs:** {objectives[top_priority]['KPIs']}
- **Core Audiences:** {objectives[top_priority]['Core Audiences']}
- **Messaging Approach:** {objectives[top_priority]['Messaging Approach']}

## Case Study
Our client [Placeholder] achieved remarkable results by aligning their paid media strategy with **{top_priority}**. Detailed insights and outcomes will be shared soon.

## Recommendations
- Tailor your messaging to resonate with your key audience segments.
- Optimize channel mix based on performance data.
- Leverage data insights to refine your targeting and creative strategy.
"""

st.download_button(
    label="Download Report",
    data=report,
    file_name="cortex_plan_report.md",
    mime="text/markdown"
)
