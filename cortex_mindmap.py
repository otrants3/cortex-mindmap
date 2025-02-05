import streamlit as st
import plotly.graph_objects as go
import math
import pandas as pd
from fpdf import FPDF
import io
import openai
import os
import datetime

# Load API key from Streamlit secrets (do not display)
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# -------------------------------
# CUSTOM CSS FOR VISUAL APPEAL & POINTER CURSOR ON DROPDOWNS
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
    /* Pointer cursor for dropdowns */
    div[data-baseweb="select"] {
        cursor: pointer;
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

# Vertical channel mix data (each channel's default allocation percentages)
vertical_channel_mix = {
    "Other": {
        "Retail Media": 20, "Paid Search": 20, "Paid Social": 20, "Linear TV": 20,
        "Programmatic Display": 20, "Connected TV": 15, "Livewire Gaming": 5,
        "Online Video": 20, "Affiliate": 10, "Influencer": 10, "Email": 15,
        "OOH/DOOH": 15, "Audio": 10
    },
    "Travel": {
        "Retail Media": 15, "Paid Search": 25, "Paid Social": 25, "Linear TV": 10,
        "Programmatic Display": 20, "Connected TV": 15, "Livewire Gaming": 5,
        "Online Video": 30, "Affiliate": 15, "Influencer": 20, "Email": 15,
        "OOH/DOOH": 10, "Audio": 10
    },
    "CPG": {
        "Retail Media": 30, "Paid Search": 15, "Paid Social": 10, "Linear TV": 35,
        "Programmatic Display": 25, "Connected TV": 20, "Livewire Gaming": 5,
        "Online Video": 15, "Affiliate": 10, "Influencer": 10, "Email": 10,
        "OOH/DOOH": 25, "Audio": 10
    },
    "Finance": {
        "Retail Media": 10, "Paid Search": 35, "Paid Social": 20, "Linear TV": 10,
        "Programmatic Display": 20, "Connected TV": 10, "Livewire Gaming": 0,
        "Online Video": 20, "Affiliate": 10, "Influencer": 15, "Email": 20,
        "OOH/DOOH": 5, "Audio": 15
    },
    "Technology": {
        "Retail Media": 15, "Paid Search": 25, "Paid Social": 30, "Linear TV": 5,
        "Programmatic Display": 25, "Connected TV": 15, "Livewire Gaming": 5,
        "Online Video": 25, "Affiliate": 15, "Influencer": 20, "Email": 15,
        "OOH/DOOH": 5, "Audio": 10
    },
    "Retail": {
        "Retail Media": 35, "Paid Search": 20, "Paid Social": 15, "Linear TV": 30,
        "Programmatic Display": 25, "Connected TV": 20, "Livewire Gaming": 5,
        "Online Video": 20, "Affiliate": 15, "Influencer": 15, "Email": 10,
        "OOH/DOOH": 30, "Audio": 10
    },
    "Healthcare": {
        "Retail Media": 10, "Paid Search": 20, "Paid Social": 20, "Linear TV": 10,
        "Programmatic Display": 20, "Connected TV": 15, "Livewire Gaming": 0,
        "Online Video": 20, "Affiliate": 10, "Influencer": 10, "Email": 20,
        "OOH/DOOH": 10, "Audio": 10
    },
    "Education": {
        "Retail Media": 10, "Paid Search": 15, "Paid Social": 15, "Linear TV": 5,
        "Programmatic Display": 15, "Connected TV": 10, "Livewire Gaming": 0,
        "Online Video": 20, "Affiliate": 10, "Influencer": 5, "Email": 15,
        "OOH/DOOH": 5, "Audio": 5
    },
    "Hospitality": {
        "Retail Media": 20, "Paid Search": 15, "Paid Social": 20, "Linear TV": 15,
        "Programmatic Display": 20, "Connected TV": 20, "Livewire Gaming": 5,
        "Online Video": 25, "Affiliate": 15, "Influencer": 20, "Email": 15,
        "OOH/DOOH": 20, "Audio": 10
    },
    "Automotive": {
        "Retail Media": 25, "Paid Search": 20, "Paid Social": 15, "Linear TV": 25,
        "Programmatic Display": 20, "Connected TV": 20, "Livewire Gaming": 5,
        "Online Video": 20, "Affiliate": 15, "Influencer": 10, "Email": 10,
        "OOH/DOOH": 25, "Audio": 10
    }
}

# -------------------------------
# SIDEBAR: CLIENT INPUTS
# -------------------------------
st.sidebar.header("Client Inputs")

# Business info
brand_name = st.sidebar.text_input("Brand Name", "-")
business_problem = st.sidebar.text_area("Business Problem", "-")
additional_business_info = st.sidebar.text_area("Additional Business Info", "-")

# Investment Range: two number inputs (low-end and high-end) with proper currency formatting
investment_low = st.sidebar.number_input("Investment Range - Low-end ($)", min_value=0, max_value=100000000, value=100000, step=1000, format="%d")
investment_high = st.sidebar.number_input("Investment Range - High-end ($)", min_value=0, max_value=100000000, value=200000, step=1000, format="%d")

# Campaign dates
campaign_start = st.sidebar.date_input("Campaign Start Date", datetime.date.today())
campaign_end = st.sidebar.date_input("Campaign End Date", datetime.date.today() + datetime.timedelta(days=30))

# Client vertical with default "-"
vertical = st.sidebar.selectbox("Client Vertical", ["-","Other", "Travel", "CPG", "Finance", "Technology", "Retail", "Healthcare", "Education", "Hospitality", "Automotive"], index=0)

# Top Priority Objective with default "-"
top_priority = st.sidebar.selectbox("Top Priority Objective", ["-"] + list(objectives.keys()), index=0)

# Brand Lifecycle Stage with default "-"
brand_lifecycle = st.sidebar.selectbox("Brand Lifecycle Stage", ["-", "New", "Growing", "Mature", "Declining"], index=0)

# Marketing Priorities (no default)
marketing_priorities = st.sidebar.multiselect("Marketing Priorities", 
    ["Increase conversions", "Boost retention", "Improve brand awareness", "Increase sales volume"], default=[])

# Creative Formats Available (no default)
creative_formats = st.sidebar.multiselect("Creative Formats Available", 
    ["OLV", "Static Images", "TV", "Interactive", "Audio"], default=[])

# -------------------------------
# MANUAL ALLOCATION ADJUSTMENTS (Right-side)
# -------------------------------
st.sidebar.subheader("Manual Allocation Adjustments")
# Filter allocation based on creative formats
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

def filter_allocation(allocation, creative_formats):
    if creative_formats:
        return {ch: val for ch, val in allocation.items() if any(fmt in creative_formats for fmt in creative_mapping.get(ch, []))}
    else:
        return allocation

filtered_allocation = filter_allocation(vertical_channel_mix.get(vertical, {}), creative_formats)
# We'll allow manual editing of the allocations on the right.
updated_allocation = {}
for ch, val in filtered_allocation.items():
    updated_allocation[ch] = st.sidebar.number_input(f"Allocation for {ch} (%)", min_value=0, max_value=100, value=val, step=1, format="%d")

# Check if total allocation equals 100%
total_alloc = sum(updated_allocation.values())
if total_alloc != 100:
    st.sidebar.warning(f"Total allocation is {total_alloc}%. It should sum to 100%.")

# -------------------------------
# HEADER & SUMMARY OF INPUTS
# -------------------------------
st.markdown('<h1 class="main-title">Cortex: Professional Paid Media Strategy Tool</h1>', unsafe_allow_html=True)
st.write("Use the sidebar to input your business criteria. Adjust channel allocations manually (they should sum to 100%). When ready, click **Run Plan** to generate your tailored strategy. Then, download a detailed PDF report.")

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
st.write(f"**Marketing Priorities:** {', '.join(marketing_priorities) if marketing_priorities else 'None'}")
st.write(f"**Creative Formats Available:** {', '.join(creative_formats) if creative_formats else 'None'}")

# -------------------------------
# INTERACTIVE RADAR CHART (Original vs. Updated)
# -------------------------------
st.subheader("Channel Allocation Comparison")

channels_list = list(filtered_allocation.keys())
original_values = [filtered_allocation[ch] for ch in channels_list]
updated_values = [updated_allocation.get(ch, 0) for ch in channels_list]

radar_fig = go.Figure()

# Original Allocation trace
radar_fig.add_trace(go.Scatterpolar(
    r=original_values,
    theta=channels_list,
    fill='toself',
    fillcolor="rgba(0,37,97,0.3)",  # Secondary color at 30% opacity
    line_color="#002561",
    name='Original Allocation'
))

# Updated Allocation trace
radar_fig.add_trace(go.Scatterpolar(
    r=updated_values,
    theta=channels_list,
    fill='toself',
    fillcolor="rgba(236,21,90,0.3)",  # Primary color at 30% opacity
    line_color="#EC155A",
    name='Updated Allocation'
))

# Adjust the radial axis for a tighter view.
radar_fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, max(100, max(original_values + updated_values))]
        )
    ),
    showlegend=True,
    title=f"Channel Mix for {vertical} Brands"
)

st.plotly_chart(radar_fig, use_container_width=True, config={"editable": True})

# Display allocation comparison as a table.
allocation_df = pd.DataFrame({
    "Channel": channels_list,
    "Original Allocation (%)": original_values,
    "Updated Allocation (%)": updated_values
})
st.subheader("Allocation Table")
st.table(allocation_df)

# -------------------------------
# INVESTMENT BY CHANNEL CALCULATION
# -------------------------------
# Compute the mid-range of investment.
mid_investment = (investment_low + investment_high) / 2
investment_by_channel = {ch: mid_investment * (updated_allocation[ch] / 100) for ch in updated_allocation}
inv_df = pd.DataFrame({
    "Channel": list(investment_by_channel.keys()),
    "Investment ($)": [f"${investment_by_channel[ch]:,.0f}" for ch in investment_by_channel]
})
st.subheader("Investment Allocation by Channel (Mid-Range)")
st.table(inv_df)

# -------------------------------
# SIMPLE CHART OF TOP PRIORITY OBJECTIVE DETAILS (instead of crowded mind map)
# -------------------------------
if top_priority != "-":
    st.subheader("Objective Details")
    details_data = {
        "Attribute": ["Strategic Imperatives", "KPIs", "Core Audiences", "Messaging Approach"],
        "Description": [
            objectives[top_priority]["Strategic Imperatives"],
            objectives[top_priority]["KPIs"],
            objectives[top_priority]["Core Audiences"],
            objectives[top_priority]["Messaging Approach"]
        ]
    }
    details_df = pd.DataFrame(details_data)
    st.table(details_df)
else:
    st.info("Please select a Top Priority Objective to view its details.")

# -------------------------------
# FINAL AI GENERATED PLAN SUMMARY (Unified)
# -------------------------------
st.subheader("Final Plan Summary")

def generate_full_plan(brand_name, business_problem, additional_business_info, vertical, creative_formats,
                       investment_low, investment_high, campaign_start, campaign_end, updated_allocations, base_summary):
    # Read reference content if available.
    reference_content = ""
    if os.path.exists("reference.txt"):
        with open("reference.txt", "r", encoding="utf-8") as f:
            reference_content = f.read()
    
    full_context = (
        f"You are a professional paid media and marketing consultant with deep expertise in the {vertical} vertical and "
        f"Junction 37's strategic approach. Generate a final plan summary that includes two parts: first, a 'TLDR:' section with a one-sentence summary; then an expanded section (2-3 paragraphs) "
        f"with actionable insights, creative recommendations, and 5 specific relevant article/resource links. Tailor your output to the client's inputs below.\n\n"
        f"Brand Name: {brand_name}\n"
        f"Business Problem: {business_problem}\n"
        f"Additional Business Info: {additional_business_info}\n"
        f"Client Vertical: {vertical}\n"
        f"Investment Range: ${investment_low:,} - ${investment_high:,}\n"
        f"Campaign Start Date: {campaign_start}\n"
        f"Campaign End Date: {campaign_end}\n"
        f"Creative Formats Available: {', '.join(creative_formats) if creative_formats else 'None'}\n"
        f"Marketing Priorities: {', '.join(marketing_priorities) if marketing_priorities else 'None'}\n"
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
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Cortex Plan Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Report Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align="C")
    pdf.ln(10)
    
    # Bold section headers for known labels.
    header_labels = [
        "Brand Name:", "Business Problem:", "Additional Business Info:", "Investment Range:", 
        "Campaign Start Date:", "Campaign End Date:", "Top Priority Objective:", 
        "Brand Lifecycle Stage:", "Client Vertical:", "Marketing Priorities:", 
        "Creative Formats Available:", "Strategic Details:", "Recommended Channel Mix", 
        "Updated Channel Allocations:", "Final Plan Summary:", "Case Study:"
    ]
    
    for line in report_text.split('\n'):
        if any(line.startswith(header) for header in header_labels):
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
Marketing Priorities: {', '.join(marketing_priorities) if marketing_priorities else 'None'}
Creative Formats Available: {', '.join(creative_formats) if creative_formats else 'None'}

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
