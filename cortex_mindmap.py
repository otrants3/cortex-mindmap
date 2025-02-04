import streamlit as st
import plotly.graph_objects as go
import math

# Data structure for objectives and their details
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

# Sidebar: Client Inputs
st.sidebar.header("Client Inputs")
top_priority = st.sidebar.selectbox("Top Priority Objective", list(objectives.keys()))
brand_lifecycle = st.sidebar.selectbox("Brand Lifecycle Stage", ["New", "Growing", "Mature", "Declining"])
industry_type = st.sidebar.selectbox("Industry Type", ["CPG", "Tech", "Finance", "Retail"])
marketing_priorities = st.sidebar.multiselect(
    "Marketing Priorities", 
    ["Increase conversions", "Boost retention", "Improve brand awareness", "Increase sales volume"]
)

# Display Client Selections
st.subheader("Your Inputs")
st.write(f"**Top Priority Objective:** {top_priority}")
st.write(f"**Brand Lifecycle Stage:** {brand_lifecycle}")
st.write(f"**Industry Type:** {industry_type}")
st.write(f"**Marketing Priorities:** {', '.join(marketing_priorities) if marketing_priorities else 'None'}")

# Create the Interactive Mind Map Visualization
st.subheader("Interactive Paid Media Strategy Map")

# Parameters for node positioning
R_main = 3      # Radius for main nodes from center
R_sub = 1       # Radius for sub-nodes from their main node
center_x, center_y = 0, 0

# Define fixed angles (in degrees) for the main nodes so that Awareness is at the top
angles = {
    "Awareness": 90,
    "Growth": 18,
    "Profitability": -54,
    "Buy Rate": -126,
    "Household Penetration": -198  # This is equivalent to 162°
}

# Lists to store node data for plotting
node_x = []
node_y = []
node_text = []
node_hover = []
node_color = []
node_size = []

# Add the central node
node_x.append(center_x)
node_y.append(center_y)
node_text.append("Paid Media Strategy")
node_hover.append("Central Strategy Node")
node_color.append("black")
node_size.append(25)

# Dictionary to store positions of main nodes (to later attach sub-nodes)
main_positions = {}

# Add main objective nodes
for obj, angle_deg in angles.items():
    angle_rad = math.radians(angle_deg)
    x = center_x + R_main * math.cos(angle_rad)
    y = center_y + R_main * math.sin(angle_rad)
    main_positions[obj] = (x, y)
    node_x.append(x)
    node_y.append(y)
    node_text.append(obj)
    # Show a brief detail on hover
    hover_info = f"{obj}: {objectives[obj]['Strategic Imperatives']}"
    node_hover.append(hover_info)
    # Highlight if it’s the top priority
    if obj == top_priority:
        node_color.append("red")
        node_size.append(20)
    else:
        node_color.append("blue")
        node_size.append(15)

# Define sub-node types and offsets (in degrees relative to the main node’s angle)
sub_node_labels = ["Strategic Imperatives", "KPIs", "Core Audiences", "Messaging Approach"]
sub_offsets = [45, -45, 135, -135]

# Add sub-nodes for each main node
for obj, (mx, my) in main_positions.items():
    for i, sub_label in enumerate(sub_node_labels):
        # Offset the sub-node position relative to the main node's angle
        offset_angle_deg = angles[obj] + sub_offsets[i]
        offset_angle_rad = math.radians(offset_angle_deg)
        sx = mx + R_sub * math.cos(offset_angle_rad)
        sy = my + R_sub * math.sin(offset_angle_rad)
        node_x.append(sx)
        node_y.append(sy)
        node_text.append(sub_label)
        detail = objectives[obj][sub_label]
        node_hover.append(f"{sub_label} for {obj}: {detail}")
        # Highlight sub-nodes if the parent is the top priority
        if obj == top_priority:
            node_color.append("orange")
            node_size.append(12)
        else:
            node_color.append("grey")
            node_size.append(10)

# Create the Plotly figure
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

# Add lines from the central node to each main node
for obj, pos in main_positions.items():
    fig.add_shape(
        type="line",
        x0=center_x, y0=center_y,
        x1=pos[0], y1=pos[1],
        line=dict(color="lightgrey", width=2)
    )

# Add lines from each main node to its sub-nodes
# The central node is at index 0, main nodes are next, followed by sub-nodes.
start_index_for_sub = 1 + len(main_positions)
index = start_index_for_sub
for obj, (mx, my) in main_positions.items():
    for i in range(4):
        sx = node_x[index]
        sy = node_y[index]
        fig.add_shape(
            type="line",
            x0=mx, y0=my,
            x1=sx, y1=sy,
            line=dict(color="lightgrey", width=1)
        )
        index += 1

# Hide axis details and set margins
fig.update_layout(
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(l=20, r=20, t=20, b=20),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# Placeholder Case Study & Benchmarking Section
st.subheader("Case Study & Benchmarking")
st.write(f"Based on your top priority of **{top_priority}**, here's a placeholder case study:")
st.write("**Case Study:** Our client [Placeholder] achieved remarkable results by aligning their paid media strategy with this objective. Detailed insights and outcomes will be shared soon.")
