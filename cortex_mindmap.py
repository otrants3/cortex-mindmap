import streamlit as st
import plotly.graph_objects as go
import math
import pandas as pd
from fpdf import FPDF
import io
import openai
import os
import datetime

# Load the API key from Streamlit Cloud secrets.
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# -------------------------------
# CUSTOM CSS FOR A POLISHED LOOK & CURSOR POINTER ON DROPDOWNS
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
    /* Change cursor on select boxes */
    div[data-baseweb="select"] {
        cursor: pointer;
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
# VERTICAL CHANNEL MIX RECOMMENDATIONS (Radar Chart Data)
# -------------------------------
vertical_channel_mix = {
    "Other": {
        "Retail Media": 20,
        "Paid Search": 20,
        "Paid Social": 20,
        "Linear TV": 20,
        "Programmatic Display": 20,
        "Connected TV": 15,
        "Livewire Gaming": 5,
        "Online Video": 20,
        "Affiliate": 10,
        "Influencer": 10,
        "Email": 15,
        "OOH/DOOH": 15,
        "Audio": 10
    },
    "Travel": {
        "Retail Media": 15,
        "Paid Search": 25,
        "Paid Social": 25,
        "Linear TV": 10,
        "Programmatic Display": 20,
        "Connected TV": 15,
        "Livewire Gaming": 5,
        "Online Video": 30,
        "Affiliate": 15,
        "Influencer": 20,
        "Email": 15,
        "OOH/DOOH": 10,
        "Audio": 10
    },
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
    "Finance": {
        "Retail Media": 10,
        "Paid Search": 35,
        "Paid Social": 20,
        "Linear TV": 10,
        "Programmatic Display": 20,
        "Connected TV": 10,
        "Livewire Gaming": 0,
        "Online Video": 20,
        "Affiliate": 10,
        "Influencer": 15,
        "Email": 20,
        "OOH/DOOH": 5,
        "Audio": 15
    },
    "Technology": {
        "Retail Media": 15,
        "Paid Search": 25,
        "Paid Social": 30,
        "Linear TV": 5,
        "Programmatic Display": 25,
        "Connected TV": 15,
        "Livewire Gaming": 5,
        "Online Video": 25,
        "Affiliate": 15,
        "Influencer": 20,
        "Email": 15,
        "OOH/DOOH": 5,
        "Audio": 10
    },
    "Retail": {
        "Retail Media": 35,
        "Paid Search": 20,
        "Paid Social": 15,
        "Linear TV": 30,
        "Programmatic Display": 25,
        "Connected TV": 20,
        "Livewire Gaming": 5,
        "Online Video": 20,
        "Affiliate": 15,
        "Influencer": 15,
        "Email": 10,
        "OOH/DOOH": 30,
        "Audio": 10
    },
    "Healthcare": {
        "Retail Media": 10,
        "Paid Search": 20,
        "Paid Social": 20,
        "Linear TV": 10,
        "Programmatic Display": 20,
        "Connected TV": 15,
        "Livewire Gaming": 0,
        "Online Video": 20,
        "Affiliate": 10,
        "Influencer": 10,
        "Email": 20,
        "OOH/DOOH": 10,
        "Audio": 10
    },
    "Education": {
        "Retail Media": 10,
        "Paid Search": 15,
        "Paid Social": 15,
        "Linear TV": 5,
        "Programmatic Display": 15,
        "Connected TV": 10,
        "Livewire Gaming": 0,
        "Online Video": 20,
        "Affiliate": 10,
        "Influencer": 5,
        "Email": 15,
        "OOH/DOOH": 5,
        "Audio": 5
    },
    "Hospitality": {
        "Retail Media": 20,
        "Paid Search": 15,
        "Paid Social": 20,
        "Linear TV": 15,
        "Programmatic Display": 20,
        "Connected TV": 20,
        "Livewire Gaming": 5,
        "Online Video": 25,
        "Affiliate": 15,
        "Influencer": 20,
        "Email": 15,
        "OOH/DOOH": 20,
        "Audio": 10
    },
    "Automotive": {
        "Retail Media": 25,
        "Paid Search": 20,
        "Paid Social": 15,
        "Linear TV": 25,
        "Programmatic Display": 20,
        "Connected TV": 20,
        "Livewire Gaming": 5,
        "Online Video": 20,
        "Affiliate": 15,
        "Influencer": 10,
        "Email": 10,
        "OOH/DOOH": 25,
        "Audio": 10
    }
}

# -------------------------------
# SIDEBAR: CLIENT INPUTS
# -------------------------------
st.sidebar.header("Client Inputs")

# Business info inputs
brand_name = st.sidebar.text_input("Brand Name", "-")
business_problem = st.sidebar.text_area("Business Problem", "-")
additional_business_info = st.sidebar.text_area("Additional Business Info", "-")

# Investment Range as two number inputs (low-end and high-end)
investment_low = st.sidebar.number_input("Investment Range - Low-end ($)", min_value=0, max_value=100000000, value=100000, step=1000, format="%d")
investment_high = st.sidebar.number_input("Investment Range - High-end ($)", min_value=0, max_value=100000000, value=200000, step=1000, format="%d")

# Campaign dates
campaign_start = st.sidebar.date_input("Campaign Start Date", datetime.date.today())
campaign_end = st.sidebar.date_input("Campaign End Date", datetime.date.today() + datetime.timedelta(days=30))

# Client vertical (with "-" as default)
vertical = st.sidebar.selectbox("Client Vertical", ["-","Other", "Travel", "CPG", "Finance", "Technology", "Retail", "Healthcare", "Education", "Hospitality", "Automotive"], index=0)

# Top Priority Objective (with "-" as default)
top_priority = st.sidebar.selectbox("Top Priority Objective", ["-"] + list(objectives.keys()), index=0)

# Brand Lifecycle Stage (with "-" as default)
brand_lifecycle = st.sidebar.selectbox("Brand Lifecycle Stage", ["-", "New", "Growing", "Mature", "Declining"], index=0)

# Marketing Priorities
marketing_priorities = st.sidebar.multiselect("Marketing Priorities", ["Increase conversions", "Boost retention", "Improve brand awareness", "Increase sales volume"], default=["-"])

# Creative Formats Available
creative_formats = st.sidebar.multiselect("Creative Formats Available", ["OLV", "Static Images", "TV", "Interactive", "Audio"], default=["-"])

# (Note: For dropdowns, a "-" placeholder is included as default.)

# Remove channel allocation sliders; instead, use interactive radar chart editing.
# Create filtered channel allocation based on creative formats.
# Define a mapping from channel names to required creative formats:
creative_mapping = {
    "Retail Media": ["Static Images"],
    "Paid Search": ["Static Images", "OLV", "TV", "Interactive", "Audio"],
    "Paid Social": ["Interactive", "Static Images"],
    "Linear TV": ["TV"],
    "Programmatic Display": ["Static Images"],
    "Connected TV": ["TV"],
    "Livewire Gaming": ["Interactive"],
    "Online Video": ["OLV"],
    "Affiliate": ["Static Images"],
    "Influencer": ["Static Images"],
    "Email": ["Static Images"],
    "OOH/DOOH": ["Static Images"],
    "Audio": ["Audio"]
}

# Filter the original vertical allocation based on creative formats.
if creative_formats and creative_formats != ["-"]:
    filtered_allocation = {ch: val for ch, val in vertical_channel_mix.get(vertical, {}).items() 
                           if any(fmt in creative_formats for fmt in creative_mapping.get(ch, []))}
else:
    filtered_allocation = vertical_channel_mix.get(vertical, {})

# For now, updated_allocation is the same as filtered_allocation.
updated_allocation = filtered_allocation.copy()

# -------------------------------
# HEADER & INSTRUCTIONS
# -------------------------------
st.markdown('<h1 class="main-title">Cortex: Professional Paid Media Strategy Tool</h1>', unsafe_allow_html=True)
st.write("Use the sidebar to input your business criteria. You can click and drag points on the radar chart to adjust channel allocations (ensure they add up to 100%). When ready, click **Run Plan** (in the sidebar) to generate your tailored strategy. Once satisfied, click **Download Report** for a detailed PDF.")

st.subheader("Your Inputs")
st.write(f"**Brand Name:** {brand_name}")
st.write(f"**Business Problem:** {business_problem}")
st.write(f"**Additional Business Info:** {additional_business_info}")
st.write(f"**Investment Range:** ${investment_low:,} – ${investment_high:,}")
st.write(f"**Campaign Start Date:** {campaign_start}")
st.write(f"**Campaign End Date:** {campaign_end}")
st.write(f"**Client Vertical:** {vertical}")
st.write(f"**Top Priority Objective:** {top_priority}")
st.write(f"**Brand Lifecycle Stage:** {brand_lifecycle}")
st.write(f"**Marketing Priorities:** {', '.join(marketing_priorities) if marketing_priorities and marketing_priorities != ['-'] else 'None'}")
st.write(f"**Creative Formats Available:** {', '.join(creative_formats) if creative_formats and creative_formats != ['-'] else 'None'}")

# -------------------------------
# INTERACTIVE MIND MAP SETUP
# -------------------------------
st.subheader("Interactive Paid Media Strategy Map")

R_main = 3      
R_sub = 1       
R_detail = 0.7  
center_x, center_y = 0, 0

angles = {
    "Awareness": 90,
    "Growth": 18,
    "Profitability": -54,
    "Buy Rate": -126,
    "Household Penetration": -198
}

node_x = []
node_y = []
node_text = []
node_hover = []
node_color = []
node_size = []

# Central node
node_x.append(center_x)
node_y.append(center_y)
node_text.append("Paid Media Strategy")
node_hover.append("Central Strategy Node")
node_color.append("black")
node_size.append(25)

# Main nodes for each objective (only show if a valid top_priority is selected)
main_positions = {}
main_angles = {}
if top_priority != "-":
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
        if obj == top_priority:
            node_color.append("#EC155A")
            node_size.append(20)
        else:
            node_color.append("#002561")
            node_size.append(15)
else:
    st.info("Please select a Top Priority Objective.")

# Sub-nodes for the top priority objective
sub_nodes = []
if top_priority != "-" and top_priority in main_positions:
    sub_node_labels = ["Strategic Imperatives", "KPIs", "Core Audiences", "Messaging Approach"]
    sub_offsets = [45, -45, 135, -135]
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

# Detail nodes branching off each sub-node
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

# Connect central node to main nodes
for obj, pos in main_positions.items():
    fig.add_shape(
        type="line",
        x0=center_x, y0=center_y,
        x1=pos[0], y1=pos[1],
        line=dict(color="lightgrey", width=2)
    )

# Connect top priority main node to its sub-nodes
if top_priority != "-" and top_priority in main_positions:
    main_pos = main_positions[top_priority]
    for sub in sub_nodes:
        sx, sy, _, _, _ = sub
        fig.add_shape(
            type="line",
            x0=main_pos[0], y0=main_pos[1],
            x1=sx, y1=sy,
            line=dict(color="lightgrey", width=1.5)
        )

# Connect sub-nodes to detail nodes
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

# Zoom in on the top priority cluster if selected.
if top_priority != "-" and top_priority in main_positions:
    center_focus = main_positions[top_priority]
    st.write("Zooming into the top priority cluster for easier reading.")
    fig.update_layout(
        xaxis=dict(range=[center_focus[0] - 4, center_focus[0] + 4]),
        yaxis=dict(range=[center_focus[1] - 4, center_focus[1] + 4])
    )

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
# RADAR CHART FOR VERTICAL CHANNEL MIX (Original vs. Updated)
# -------------------------------
st.subheader("Channel Allocation Comparison")

# Filter allocations based on creative formats (using our mapping)
def filter_allocation(allocation, creative_formats):
    if creative_formats and creative_formats != ["-"]:
        return {ch: val for ch, val in allocation.items() if any(fmt in creative_formats for fmt in creative_mapping.get(ch, []))}
    else:
        return allocation

creative_mapping = {
    "Retail Media": ["Static Images"],
    "Paid Search": ["Static Images", "OLV", "TV", "Interactive", "Audio"],
    "Paid Social": ["Interactive", "Static Images"],
    "Linear TV": ["TV"],
    "Programmatic Display": ["Static Images"],
    "Connected TV": ["TV"],
    "Livewire Gaming": ["Interactive"],
    "Online Video": ["OLV"],
    "Affiliate": ["Static Images"],
    "Influencer": ["Static Images"],
    "Email": ["Static Images"],
    "OOH/DOOH": ["Static Images"],
    "Audio": ["Audio"]
}

filtered_allocation = filter_allocation(vertical_channel_mix.get(vertical, {}), creative_formats)
# For now, updated_allocation remains the same as filtered_allocation.
updated_allocation = filtered_allocation.copy()

channels_list = list(filtered_allocation.keys())
original_values = [filtered_allocation[ch] for ch in channels_list]
updated_values = [updated_allocation.get(ch, 0) for ch in channels_list]

radar_fig = go.Figure()

radar_fig.add_trace(go.Scatterpolar(
    r=original_values,
    theta=channels_list,
    fill='toself',
    fillcolor="rgba(0,37,97,0.3)",
    line_color="#002561",
    name='Original Allocation'
))

radar_fig.add_trace(go.Scatterpolar(
    r=updated_values,
    theta=channels_list,
    fill='toself',
    fillcolor="rgba(236,21,90,0.3)",
    line_color="#EC155A",
    name='Updated Allocation'
))

radar_fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100]
        )
    ),
    showlegend=True,
    title=f"Channel Mix for {vertical} Brands (Based on Client Inputs)"
)

# Enable editing so that users can drag points (note: capturing updated values may not be fully supported)
st.plotly_chart(radar_fig, use_container_width=True, config={"editable": True})

st.subheader("Allocation Comparison")
allocation_df = pd.DataFrame({
    "Channel": channels_list,
    "Original Allocation": original_values,
    "Updated Allocation": updated_values
})
st.table(allocation_df)

# -------------------------------
# FINAL AI GENERATED PLAN SUMMARY (Unified)
# -------------------------------
st.subheader("Final Plan Summary")

def generate_full_plan(brand_name, business_problem, additional_business_info, vertical, creative_formats, investment_low, investment_high, campaign_start, campaign_end, updated_allocations, base_summary):
    reference_content = ""
    if os.path.exists("reference.txt"):
        with open("reference.txt", "r", encoding="utf-8") as f:
            reference_content = f.read()
    
    full_context = (
        f"You are a professional paid media and marketing consultant with deep expertise in the {vertical} vertical. "
        f"Using Junction 37's framework, generate a final plan summary that includes two parts: first, a 'TLDR:' section with a one-sentence summary; "
        f"then an expanded section (2-3 paragraphs) with actionable insights, creative recommendations, and 5 specific, relevant article/resource links. "
        f"Tailor your output to address the client's business problem, investment range, campaign dates, and available creative formats.\n\n"
        f"Brand Name: {brand_name}\n"
        f"Business Problem: {business_problem}\n"
        f"Additional Business Info: {additional_business_info}\n"
        f"Client Vertical: {vertical}\n"
        f"Investment Range: ${investment_low:,} - ${investment_high:,}\n"
        f"Campaign Start Date: {campaign_start}\n"
        f"Campaign End Date: {campaign_end}\n"
        f"Creative Formats Available: {', '.join(creative_formats) if creative_formats and creative_formats != ['-'] else 'None'}\n"
        f"Marketing Priorities: {', '.join(marketing_priorities) if marketing_priorities and marketing_priorities != ['-'] else 'None'}\n"
        f"Updated Channel Allocations: " + ", ".join([f"{ch}: {updated_allocations[ch]}" for ch in updated_allocations]) + "\n"
        f"Reference Documents: {reference_content}\n\n"
        f"Other Client Inputs:\n"
        f"Top Priority Objective: {top_priority}\n"
        f"Brand Lifecycle Stage: {brand_lifecycle}\n\n"
        f"Base strategy summary: {base_summary}\n\n"
        f"Generate a final plan summary as specified."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional paid media and marketing consultant with expertise in the client's vertical and a deep understanding of Junction 37's approach."},
                {"role": "user", "content": full_context}
            ],
            max_tokens=400,
            temperature=0.7
        )
        generated_text = response.choices[0].message.content.strip()
        return generated_text
    except Exception as e:
        return "Error generating AI insight: " + str(e)

base_plan_summary = (
    f"Your top priority is {top_priority} for a brand in the {brand_lifecycle} stage operating in the {vertical} vertical. "
    f"Recommended actions include {objectives[top_priority]['Strategic Imperatives'].lower()} and leveraging a channel mix updated based on client inputs."
)

if "final_plan" not in st.session_state:
    st.session_state.final_plan = base_plan_summary

# "Run Plan" button in the sidebar (moved to left)
if st.sidebar.button("Run Plan"):
    st.session_state.final_plan = generate_full_plan(
        brand_name, business_problem, additional_business_info, vertical, creative_formats,
        investment_low, investment_high, campaign_start, campaign_end, updated_allocation, base_plan_summary
    )

st.markdown(st.session_state.final_plan)

# -------------------------------
# GENERATE PDF REPORT USING FPDF (Enhanced Formatting)
# -------------------------------
def generate_pdf(report_text):
    pdf = FPDF()
    pdf.add_page()
    # Add header with title and date
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Cortex Plan Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Report Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align="C")
    pdf.ln(10)
    
    # Process each line with bold section headers for lines starting with a known header label.
    for line in report_text.split('\n'):
        # If the line looks like a section header, make it bold.
        if any(line.startswith(header) for header in ["Brand Name:", "Business Problem:", "Additional Business Info:", "Investment Range:", "Campaign Start Date:", "Campaign End Date:", "Top Priority Objective:", "Brand Lifecycle Stage:", "Client Vertical:", "Marketing Priorities:", "Creative Formats Available:", "Strategic Details:", "Recommended Channel Mix", "Updated Channel Allocations:", "Final Plan Summary:", "Case Study:"]):
            pdf.set_font("Arial", "B", 12)
        else:
            pdf.set_font("Arial", "", 12)
        safe_line = line.encode("latin1", "replace").decode("latin1")
        pdf.multi_cell(0, 10, txt=safe_line)
    pdf.ln(5)
    pdf_output_str = pdf.output(dest="S")
    pdf_bytes = pdf_output_str.encode("latin1", "replace")
    return pdf_bytes

report_text = f"""
Cortex Plan Report

Brand Name: {brand_name}
Business Problem: {business_problem}
Additional Business Info: {additional_business_info}
Investment Range: ${investment_low:,} - ${investment_high:,}

Campaign Start Date: {campaign_start}
Campaign End Date: {campaign_end}

Top Priority Objective: {top_priority}
Brand Lifecycle Stage: {brand_lifecycle}
Client Vertical: {vertical}
Marketing Priorities: {', '.join(marketing_priorities) if marketing_priorities and marketing_priorities != ['-'] else 'None'}
Creative Formats Available: {', '.join(creative_formats) if creative_formats and creative_formats != ['-'] else 'None'}

Strategic Details:
- Strategic Imperatives: {objectives[top_priority]['Strategic Imperatives']}
- KPIs: {objectives[top_priority]['KPIs']}
- Core Audiences: {objectives[top_priority]['Core Audiences']}
- Messaging Approach: {objectives[top_priority]['Messaging Approach']}

Recommended Channel Mix (for {vertical}):
""" + "\n".join([f"- {channel}: {vertical_channel_mix[vertical][channel]}" for channel in vertical_channel_mix[vertical].keys()]) + f"""

Updated Channel Allocations:
""" + "\n".join([f"- {channel}: {updated_allocation.get(channel, 0)}" for channel in updated_allocation.keys()]) + f"""

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
