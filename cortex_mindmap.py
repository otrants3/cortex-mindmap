import streamlit as st
import plotly.graph_objects as go
import math
from fpdf import FPDF
import io
import openai

# Load the API key from Streamlit Cloud secrets.
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# Optional: DEBUG message (shows first 4 characters only)
st.write(f"API Key loaded: {openai.api_key[:4]}...")

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
# DATA STRUCTURES FOR OBJECTIVES
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
# EXPANDED CHANNEL MIX RECOMMENDATIONS (Radar Chart Data)
# -------------------------------
channel_mix = {
    "CPG": {
        "Retail Media": 30,
        "Paid Search": 15,
        "Paid Social": 10,
        "Linear TV": 35,
        "Programmatic Display": 25,
        "Connected TV": 20,
        "Livewire Gaming": 5,
        "Online Video": 15,
        "Affiliate": 10,
        "Influencer": 10,
        "Email": 10,
        "OOH/DOOH": 25,
        "Audio": 10
    },
    "DTC": {
        "Retail Media": 10,
        "Paid Search": 30,
        "Paid Social": 35,
        "Linear TV": 5,
        "Programmatic Display": 30,
        "Connected TV": 10,
        "Livewire Gaming": 10,
        "Online Video": 25,
        "Affiliate": 15,
        "Influencer": 25,
        "Email": 25,
        "OOH/DOOH": 5,
        "Audio": 10
    },
    "Hybrid": {
        "Retail Media": 20,
        "Paid Search": 25,
        "Paid Social": 25,
        "Linear TV": 15,
        "Programmatic Display": 20,
        "Connected TV": 15,
        "Livewire Gaming": 10,
        "Online Video": 20,
        "Affiliate": 15,
        "Influencer": 15,
        "Email": 20,
        "OOH/DOOH": 15,
        "Audio": 10
    }
}

# -------------------------------
# RECOMMENDATION MAPPING BASED ON LIFECYCLE & INDUSTRY
# -------------------------------
recommendation_mapping = {
    ("New", "CPG"): "For a new CPG brand, building awareness via digital and social channels is critical.",
    ("New", "DTC"): "For a new DTC brand, focus on rapid awareness and testing direct response channels.",
    ("New", "Hybrid"): "For a new Hybrid brand, a balanced approach to both awareness and conversion is key.",
    ("Growing", "CPG"): "For a growing CPG brand, scaling with a mix of digital and traditional media can drive results.",
    ("Growing", "DTC"): "For a growing DTC brand, customer acquisition and retention should be prioritized.",
    ("Growing", "Hybrid"): "For a growing Hybrid brand, investing in both brand and performance strategies is recommended.",
    ("Mature", "CPG"): "For a mature CPG brand, profitability and efficiency in media spend become essential.",
    ("Mature", "DTC"): "For a mature DTC brand, optimizing targeting and leveraging data insights is crucial.",
    ("Mature", "Hybrid"): "For a mature Hybrid brand, a refined mix of retention and performance marketing is advisable.",
    ("Declining", "CPG"): "For a declining CPG brand, revitalizing the brand with innovative campaigns is key.",
    ("Declining", "DTC"): "For a declining DTC brand, re-engaging customers and creative re-positioning are critical.",
    ("Declining", "Hybrid"): "For a declining Hybrid brand, a strategic overhaul combining both brand and performance efforts is recommended."
}

# -------------------------------
# ADDITIONAL RECOMMENDATIONS BASED ON MARKETING PRIORITIES
# -------------------------------
marketing_priority_recs = {
    "Increase conversions": "Optimize landing pages and retargeting campaigns to boost conversion rates.",
    "Boost retention": "Invest in loyalty programs, personalized email campaigns, and re-engagement strategies.",
    "Improve brand awareness": "Leverage influencer partnerships, social media, and display advertising to raise visibility.",
    "Increase sales volume": "Utilize targeted promotions, upselling, and cross-selling tactics to drive sales."
}

# -------------------------------
# NEW: SUGGESTED OBJECTIVE BASED ON BRAND LIFECYCLE
# -------------------------------
lifecycle_suggested = {
    "New": "Awareness",
    "Growing": "Growth",
    "Mature": "Profitability",
    "Declining": "Household Penetration"
}

# -------------------------------
# SIDEBAR: CLIENT INPUTS
# -------------------------------
st.sidebar.header("Client Inputs")

# New fields for business info
brand_name = st.sidebar.text_input("Brand Name", "Enter the brand name here...")
business_problem = st.sidebar.text_area("Business Problem", "Describe the business problem you are trying to solve...")
additional_business_info = st.sidebar.text_area("Additional Business Info", "Enter any additional info about the brand or strategy here...")

# Existing fields
top_priority = st.sidebar.selectbox("Top Priority Objective", list(objectives.keys()))
brand_lifecycle = st.sidebar.selectbox("Brand Lifecycle Stage", ["New", "Growing", "Mature", "Declining"])
industry_type = st.sidebar.selectbox("Industry Type", ["CPG", "DTC", "Hybrid"])
marketing_priorities = st.sidebar.multiselect(
    "Marketing Priorities", 
    ["Increase conversions", "Boost retention", "Improve brand awareness", "Increase sales volume"]
)

# -------------------------------
# HEADER & INSTRUCTIONS
# -------------------------------
st.markdown('<h1 class="main-title">Cortex: Professional Paid Media Strategy Tool</h1>', unsafe_allow_html=True)
st.write("Welcome! Use the sidebar to input your business criteria. Hover over the nodes for details, and use your mouse to zoom/pan the interactive map. Once satisfied, click **Download Report** for a detailed strategy summary.")

st.subheader("Your Inputs")
st.write(f"**Brand Name:** {brand_name}")
st.write(f"**Business Problem:** {business_problem}")
st.write(f"**Additional Business Info:** {additional_business_info}")
st.write(f"**Top Priority Objective:** {top_priority}")
st.write(f"**Brand Lifecycle Stage:** {brand_lifecycle}")
st.write(f"**Industry Type:** {industry_type}")
st.write(f"**Marketing Priorities:** {', '.join(marketing_priorities) if marketing_priorities else 'None'}")

# -------------------------------
# INTERACTIVE MIND MAP SETUP
# -------------------------------
st.subheader("Interactive Paid Media Strategy Map")

# Parameters for node positioning
R_main = 3      # Radius for main nodes from center
R_sub = 1       # Radius for sub-nodes (only for top priority)
R_detail = 0.7  # Radius for detail nodes from sub-node

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
    # Use Junction 37 colors: top priority uses #EC155A, others use #002561
    if obj == top_priority:
        node_color.append("#EC155A")
        node_size.append(20)
    else:
        node_color.append("#002561")
        node_size.append(15)

# 3. Sub-Nodes for the top priority objective only
sub_nodes = []  # tuples: (x, y, label, hover_text, base_angle)
if top_priority in main_positions:
    sub_node_labels = ["Strategic Imperatives", "KPIs", "Core Audiences", "Messaging Approach"]
    sub_offsets = [45, -45, 135, -135]  # offsets relative to the main node's angle
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
        node_color.append("#EC155A")
        node_size.append(12)

# 4. Detail Nodes branching off each sub-node (only for top priority)
for sub in sub_nodes:
    sx, sy, sub_label, sub_hover, base_angle = sub
    detail_str = objectives[top_priority][sub_label]
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
        node_x.append(dx)
        node_y.append(dy)
        node_text.append(detail_label)
        node_hover.append(detail_hover)
        node_color.append("purple")
        node_size.append(8)

# -------------------------------
# BUILD THE PLOTLY FIGURE (MIND MAP)
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

# Highlight suggested objective based on brand lifecycle (if different from selected top priority)
suggested_obj = lifecycle_suggested.get(brand_lifecycle)
if suggested_obj and suggested_obj in main_positions and suggested_obj != top_priority:
    pos = main_positions[suggested_obj]
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=pos[0]-0.3, y0=pos[1]-0.3,
        x1=pos[0]+0.3, y1=pos[1]+0.3,
        line=dict(color="green", width=2, dash="dot")
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
# SUPPLEMENTARY VISUALIZATION: RADAR CHART FOR CHANNEL MIX
# -------------------------------
st.subheader("Recommended Channel Mix")
channels = list(channel_mix[industry_type].keys())
values = list(channel_mix[industry_type].values())

radar_fig = go.Figure()

radar_fig.add_trace(go.Scatterpolar(
    r=values,
    theta=channels,
    fill='toself',
    fillcolor="rgba(0,37,97,0.3)",  # #002561 at 30% opacity
    line_color="#EC155A",
    name='Channel Mix'
))

radar_fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 40]
        )
    ),
    showlegend=False,
    title=f"Channel Mix for {industry_type} Brands ({brand_lifecycle} Stage)"
)

st.plotly_chart(radar_fig, use_container_width=True)

# -------------------------------
# FINAL AI GENERATED PLAN SUMMARY
# -------------------------------
st.subheader("Final Plan Summary")

# Create a function to generate the final plan summary using the new inputs.
def generate_full_plan(brand_name, business_problem, additional_business_info, base_summary):
    prompt = (
        f"You are a professional paid media and marketing consultant. Using Junction 37's expertise, "
        f"generate a concise, professional final plan summary in a single paragraph. Include actionable insights and "
        f"relevant links to articles or resources that address the client's needs. Use the following client inputs:\n\n"
        f"Brand Name: {brand_name}\n"
        f"Business Problem: {business_problem}\n"
        f"Additional Business Info: {additional_business_info}\n"
        f"Top Priority Objective: {top_priority}\n"
        f"Brand Lifecycle Stage: {brand_lifecycle}\n"
        f"Industry Type: {industry_type}\n"
        f"Marketing Priorities: {', '.join(marketing_priorities) if marketing_priorities else 'None'}\n\n"
        f"Base strategy summary: {base_summary}\n\n"
        f"Generate a final plan summary as a single, coherent paragraph."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional media strategy consultant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.7
        )
        generated_text = response.choices[0].message.content.strip()
        return generated_text
    except Exception as e:
        return "Error generating AI insight: " + str(e)

# Prepare a base summary (this can be a simple concatenation of the key inputs)
base_plan_summary = (
    f"Your top priority is {top_priority} for a brand in the {brand_lifecycle} stage operating in the {industry_type} sector. "
    f"Recommended actions include: {objectives[top_priority]['Strategic Imperatives'].lower()} and leveraging a channel mix that "
    f"focuses on key areas such as {', '.join(channels)}."
)

# Use a button to trigger AI generation (and update session state accordingly)
if "final_plan" not in st.session_state:
    st.session_state.final_plan = base_plan_summary  # default summary

if st.button("Update Final Plan"):
    st.session_state.final_plan = generate_full_plan(brand_name, business_problem, additional_business_info, base_plan_summary)

st.markdown(st.session_state.final_plan)

# -------------------------------
# GENERATE PDF REPORT USING FPDF
# -------------------------------
def generate_pdf(report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Process each line, encoding with replacement for unsupported characters.
    for line in report_text.split('\n'):
        safe_line = line.encode("latin1", "replace").decode("latin1")
        pdf.multi_cell(0, 10, txt=safe_line)
    pdf_output_str = pdf.output(dest="S")
    pdf_bytes = pdf_output_str.encode("latin1", "replace")
    return pdf_bytes

report_text = f"""
Cortex Plan Report

Brand Name: {brand_name}
Business Problem: {business_problem}
Additional Business Info: {additional_business_info}

Top Priority Objective: {top_priority}
Brand Lifecycle Stage: {brand_lifecycle}
Industry Type: {industry_type}
Marketing Priorities: {', '.join(marketing_priorities) if marketing_priorities else 'None'}

Strategic Details:
- Strategic Imperatives: {objectives[top_priority]['Strategic Imperatives']}
- KPIs: {objectives[top_priority]['KPIs']}
- Core Audiences: {objectives[top_priority]['Core Audiences']}
- Messaging Approach: {objectives[top_priority]['Messaging Approach']}

Recommended Channel Mix (for {industry_type}):
""" + "\n".join([f"- {channel}: {value}" for channel, value in channel_mix[industry_type].items()]) + f"""

Final Plan Summary:
{st.session_state.final_plan}

Case Study:
Our client [Placeholder] achieved remarkable results by aligning their paid media strategy with {top_priority}.
"""

pdf_data = generate_pdf(report_text)

st.download_button(
    label="Download PDF Report",
    data=pdf_data,
    file_name="cortex_plan_report.pdf",
    mime="application/pdf"
)
