import streamlit as st
import plotly.graph_objects as go
import math
import pandas as pd
from fpdf import FPDF
import io
import openai
import os
import datetime
import json

# Load API key from Streamlit Cloud secrets (do not print the full key)
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# -------------------------------
# CUSTOM CSS FOR VISUAL APPEAL & POINTER CURSOR
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

vertical_channel_mix = {
    "Other": {"Retail Media": 20, "Paid Search": 20, "Paid Social": 20, "Linear TV": 20,
              "Programmatic Display": 20, "Connected TV": 15, "Livewire Gaming": 5,
              "Online Video": 20, "Affiliate": 10, "Influencer": 10, "Email": 15,
              "OOH/DOOH": 15, "Audio": 10},
    "Travel": {"Retail Media": 15, "Paid Search": 25, "Paid Social": 25, "Linear TV": 10,
               "Programmatic Display": 20, "Connected TV": 15, "Livewire Gaming": 5,
               "Online Video": 30, "Affiliate": 15, "Influencer": 20, "Email": 15,
               "OOH/DOOH": 10, "Audio": 10},
    "CPG": {"Retail Media": 30, "Paid Search": 15, "Paid Social": 10, "Linear TV": 35,
            "Programmatic Display": 25, "Connected TV": 20, "Livewire Gaming": 5,
            "Online Video": 15, "Affiliate": 10, "Influencer": 10, "Email": 10,
            "OOH/DOOH": 25, "Audio": 10},
    "Finance": {"Retail Media": 10, "Paid Search": 35, "Paid Social": 20, "Linear TV": 10,
                "Programmatic Display": 20, "Connected TV": 10, "Livewire Gaming": 0,
                "Online Video": 20, "Affiliate": 10, "Influencer": 15, "Email": 20,
                "OOH/DOOH": 5, "Audio": 15},
    "Technology": {"Retail Media": 15, "Paid Search": 25, "Paid Social": 30, "Linear TV": 5,
                   "Programmatic Display": 25, "Connected TV": 15, "Livewire Gaming": 5,
                   "Online Video": 25, "Affiliate": 15, "Influencer": 20, "Email": 15,
                   "OOH/DOOH": 5, "Audio": 10},
    "Retail": {"Retail Media": 35, "Paid Search": 20, "Paid Social": 15, "Linear TV": 30,
               "Programmatic Display": 25, "Connected TV": 20, "Livewire Gaming": 5,
               "Online Video": 20, "Affiliate": 15, "Influencer": 15, "Email": 10,
               "OOH/DOOH": 30, "Audio": 10},
    "Healthcare": {"Retail Media": 10, "Paid Search": 20, "Paid Social": 20, "Linear TV": 10,
                   "Programmatic Display": 20, "Connected TV": 15, "Livewire Gaming": 0,
                   "Online Video": 20, "Affiliate": 10, "Influencer": 10, "Email": 20,
                   "OOH/DOOH": 10, "Audio": 10},
    "Education": {"Retail Media": 10, "Paid Search": 15, "Paid Social": 15, "Linear TV": 5,
                  "Programmatic Display": 15, "Connected TV": 10, "Livewire Gaming": 0,
                  "Online Video": 20, "Affiliate": 10, "Influencer": 5, "Email": 15,
                  "OOH/DOOH": 5, "Audio": 5},
    "Hospitality": {"Retail Media": 20, "Paid Search": 15, "Paid Social": 20, "Linear TV": 15,
                    "Programmatic Display": 20, "Connected TV": 20, "Livewire Gaming": 5,
                    "Online Video": 25, "Affiliate": 15, "Influencer": 20, "Email": 15,
                    "OOH/DOOH": 20, "Audio": 10},
    "Automotive": {"Retail Media": 25, "Paid Search": 20, "Paid Social": 15, "Linear TV": 25,
                   "Programmatic Display": 20, "Connected TV": 20, "Livewire Gaming": 5,
                   "Online Video": 20, "Affiliate": 15, "Influencer": 10, "Email": 10,
                   "OOH/DOOH": 25, "Audio": 10}
}

objective_adjustments = {
    "Awareness": {"Paid Social": 1.2, "Online Video": 1.1, "Retail Media": 1.1},
    "Growth": {"Paid Search": 1.2, "Programmatic Display": 1.1, "Online Video": 1.1},
    "Profitability": {"Email": 1.2, "Affiliate": 1.1, "Retail Media": 0.9},
    "Buy Rate": {"Paid Social": 1.1, "Online Video": 1.1, "Retail Media": 1.0},
    "Household Penetration": {"OOH/DOOH": 1.2, "Retail Media": 1.1}
}

def compute_normalized_allocation(vertical, top_priority):
    raw = vertical_channel_mix.get(vertical, {})
    if top_priority != "-" and top_priority in objective_adjustments:
        adjustments = objective_adjustments[top_priority]
        adjusted = {ch: raw[ch] * adjustments.get(ch, 1) for ch in raw}
    else:
        adjusted = raw.copy()
    total = sum(adjusted.values())
    if total > 0:
        normalized = {ch: (val / total) * 100 for ch, val in adjusted.items()}
    else:
        normalized = adjusted
    return normalized

# -------------------------------
# FUNCTION TO GENERATE FLIGHTING PATTERNS VIA AI
# -------------------------------
def generate_flighting_patterns(channels, n_months, vertical, top_priority):
    prompt = (
        f"Generate a JSON object where the keys are the following channel names: {channels}. "
        f"For each channel, output a list of {n_months} integers representing the percentage distribution of that channel's "
        f"investment over {n_months} months for a campaign in the {vertical} vertical with a top priority of {top_priority}. "
        f"Each list must sum to 100 and reflect realistic seasonal fluctuations for this industry. Return only valid JSON."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        result = response.choices[0].message.content.strip()
        patterns = json.loads(result)
        return patterns
    except Exception as e:
        return None

# -------------------------------
# SIDEBAR: CLIENT INPUTS
# -------------------------------
st.sidebar.header("Client Inputs")

brand_name = st.sidebar.text_input("Brand Name", "-")
business_problem = st.sidebar.text_area("Business Problem", "-")
additional_business_info = st.sidebar.text_area("Additional Business Info", "-")

investment_low = st.sidebar.number_input("Investment Range - Low-end ($)", min_value=0, max_value=100000000, value=100000, step=1000, format="%d")
investment_high = st.sidebar.number_input("Investment Range - High-end ($)", min_value=0, max_value=100000000, value=200000, step=1000, format="%d")

campaign_start = st.sidebar.date_input("Campaign Start Date", datetime.date.today())
campaign_end = st.sidebar.date_input("Campaign End Date", datetime.date.today() + datetime.timedelta(days=30))

vertical = st.sidebar.selectbox("Client Vertical", ["-","Other", "Travel", "CPG", "Finance", "Technology", "Retail", "Healthcare", "Education", "Hospitality", "Automotive"], index=0)
top_priority = st.sidebar.selectbox("Top Priority Objective", ["-"] + list(objectives.keys()), index=0)
brand_lifecycle = st.sidebar.selectbox("Brand Lifecycle Stage", ["-", "New", "Growing", "Mature", "Declining"], index=0)
marketing_priorities = st.sidebar.multiselect("Marketing Priorities", ["Increase conversions", "Boost retention", "Improve brand awareness", "Increase sales volume"], default=[])
creative_formats = st.sidebar.multiselect("Creative Formats Available", ["OLV", "Static Images", "TV", "Interactive", "Audio"], default=[])

# -------------------------------
# NORMALIZE DEFAULT ALLOCATION
# -------------------------------
normalized_allocation = compute_normalized_allocation(vertical, top_priority)

# Compute mid-range investment and original investment by channel
mid_investment = (investment_low + investment_high) / 2
original_investment_by_channel = {ch: mid_investment * (normalized_allocation[ch] / 100) for ch in normalized_allocation}

# -------------------------------
# MANUAL ALLOCATION ADJUSTMENTS (User Inputs)
# -------------------------------
if top_priority != "-" and normalized_allocation:
    st.sidebar.subheader("Manual Allocation Adjustments")
    updated_allocation = {}
    for ch, default_val in normalized_allocation.items():
        updated_allocation[ch] = st.sidebar.number_input(f"Allocation for {ch} (%)", min_value=0, max_value=100, value=int(round(default_val)), step=1, format="%d")
else:
    updated_allocation = {}

total_alloc = sum(updated_allocation.values())
if updated_allocation and total_alloc != 100:
    st.sidebar.warning(f"Total allocation is {total_alloc}%. It should sum to 100%.")

if updated_allocation:
    updated_investment_by_channel = {ch: mid_investment * (updated_allocation[ch] / 100) for ch in updated_allocation}
else:
    updated_investment_by_channel = original_investment_by_channel.copy()

# -------------------------------
# SUMMARY OF CLIENT INPUTS
# -------------------------------
st.markdown('<h1 class="main-title">Cortex: Professional Paid Media Strategy Tool</h1>', unsafe_allow_html=True)
st.write("Use the sidebar to input your business criteria and manually adjust channel allocations (which must sum to 100%). When ready, click **Run Plan** (in the sidebar) to generate your tailored strategy. Then, download a detailed PDF report.")

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
# DISPLAY OBJECTIVE DETAILS
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
# PIE CHARTS FOR CHANNEL ALLOCATION
# -------------------------------
st.subheader("Channel Allocation Comparison")
base_colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3',
               '#FF6692', '#B6E880', '#FF97FF', '#FECB52', '#1f77b4', '#ff7f0e']

channels_original = list(normalized_allocation.keys())
colors_original = [base_colors[i % len(base_colors)] for i in range(len(channels_original))]
pie_original = go.Figure(data=[go.Pie(
    labels=channels_original,
    values=list(normalized_allocation.values()),
    marker=dict(colors=colors_original)
)])
pie_original.update_layout(title="Original Allocation (Normalized)")

if updated_allocation:
    channels_updated = list(updated_allocation.keys())
    colors_updated = [base_colors[i % len(base_colors)] for i in range(len(channels_updated))]
    pie_updated = go.Figure(data=[go.Pie(
        labels=channels_updated,
        values=list(updated_allocation.values()),
        marker=dict(colors=colors_updated)
    )])
    pie_updated.update_layout(title="Updated Allocation (Manual)")
else:
    channels_updated = channels_original
    colors_updated = colors_original
    pie_updated = go.Figure(data=[go.Pie(
        labels=channels_updated,
        values=list(normalized_allocation.values()),
        marker=dict(colors=colors_updated)
    )])
    pie_updated.update_layout(title="Updated Allocation (Same as Original)")

st.plotly_chart(pie_original, use_container_width=True)
st.plotly_chart(pie_updated, use_container_width=True)

# -------------------------------
# FLIGHTING LINE GRAPH: DYNAMIC INVESTMENT BY MONTH PER CHANNEL
# -------------------------------
st.subheader("Flighting: Investment by Month")

# Calculate campaign duration in months (approximate)
n_months = ((campaign_end - campaign_start).days // 30) + 1
month_labels = [f"Month {i+1}" for i in range(n_months)]

# Generate flighting patterns via AI
channels_flighting = list(updated_allocation.keys())
flighting_patterns = generate_flighting_patterns(channels_flighting, n_months, vertical, top_priority)
flighting_data = {}
if flighting_patterns is None:
    st.warning("Could not generate dynamic flighting; using uniform distribution.")
    for ch in channels_flighting:
        monthly = updated_investment_by_channel.get(ch, 0) / n_months
        flighting_data[ch] = [monthly] * n_months
else:
    for ch in channels_flighting:
        pattern = flighting_patterns.get(ch)
        if pattern and sum(pattern) == 100:
            flighting_data[ch] = [updated_investment_by_channel.get(ch, 0) * (p / 100) for p in pattern]
        else:
            monthly = updated_investment_by_channel.get(ch, 0) / n_months
            flighting_data[ch] = [monthly] * n_months

flighting_fig = go.Figure()
for ch, investments in flighting_data.items():
    flighting_fig.add_trace(go.Scatter(
        x=month_labels,
        y=investments,
        mode='lines+markers',
        name=ch
    ))
flighting_fig.update_layout(
    title="Monthly Investment by Channel (Dynamic Flighting)",
    xaxis_title="Month",
    yaxis_title="Investment ($)",
    yaxis=dict(tickprefix="$")
)
st.plotly_chart(flighting_fig, use_container_width=True)

# Create a flighting table.
flighting_table = []
for ch in channels_flighting:
    monthly_investments = flighting_data[ch]
    total_channel = sum(monthly_investments)
    flighting_table.append({
        "Channel": ch,
        "Monthly Investment ($)": f"{[f'${m:,.0f}' for m in monthly_investments]}",
        "Total Investment ($)": f"${total_channel:,.0f}"
    })
flighting_df = pd.DataFrame(flighting_table)
st.subheader("Flighting Investment Table")
st.table(flighting_df)

# -------------------------------
# FINAL AI GENERATED PLAN SUMMARY (Unified)
# -------------------------------
st.subheader("Final Plan Summary")

def generate_full_plan(brand_name, business_problem, additional_business_info, vertical, creative_formats,
                       investment_low, investment_high, campaign_start, campaign_end, updated_allocations, base_summary):
    reference_content = ""
    if os.path.exists("reference.txt"):
        with open("reference.txt", "r", encoding="utf-8") as f:
            reference_content = f.read()
    
    full_context = (
        f"You are a professional paid media and marketing consultant with deep expertise in the {vertical} vertical and a strong alignment with Junction 37's approach. "
        f"Generate a final plan summary that includes two parts: first, a 'TLDR:' section with a one-sentence summary; then an expanded analysis (2-3 paragraphs) that includes:\n"
        f"1. Creative Themes: List 3-5 creative themes that align with the target audiences.\n"
        f"2. Key Audiences: List 3 key prospecting audiences and 3 key conversion audiences, with reasoning supported by credible marketing articles.\n"
        f"3. Suggested Flighting: Provide recommendations for how the investment should be distributed over the campaign duration.\n"
        f"Finally, include 5 specific, real, credible marketing article links from sources such as Ad Age, Marketing Land, Adweek, HubSpot Marketing, and Marketing Dive.\n\n"
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
        f"Generate a final plan summary with a TLDR section (one sentence) and an expanded analysis (2-3 paragraphs) that includes all the sections described above."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional paid media and marketing consultant with deep expertise in the client's vertical and a deep understanding of Junction 37's approach."},
                {"role": "user", "content": full_context}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        generated_text = response.choices[0].message.content.strip()
        return generated_text
    except Exception as e:
        return "Error generating AI insight: " + str(e)

if top_priority != "-":
    base_plan_summary = (
        f"Your top priority is {top_priority} for a brand in the {brand_lifecycle} stage operating in the {vertical} vertical. "
        f"Recommended actions include {objectives[top_priority]['Strategic Imperatives'].lower()} and leveraging a channel mix updated based on client inputs."
    )
else:
    base_plan_summary = "No top priority objective selected."

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
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Cortex Plan Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Report Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align="C")
    pdf.ln(10)
    
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
- Strategic Imperatives: {objectives[top_priority]['Strategic Imperatives'] if top_priority != "-" else "N/A"}
- KPIs: {objectives[top_priority]['KPIs'] if top_priority != "-" else "N/A"}
- Core Audiences: {objectives[top_priority]['Core Audiences'] if top_priority != "-" else "N/A"}
- Messaging Approach: {objectives[top_priority]['Messaging Approach'] if top_priority != "-" else "N/A"}

Recommended Channel Mix (for {vertical}):
""" + "\n".join([f"- {channel}: {vertical_channel_mix[vertical][channel]}" for channel in vertical_channel_mix.get(vertical, {})]) + f"""

Updated Channel Allocations:
""" + "\n".join([f"- {channel}: {updated_allocation.get(channel, 0)}" for channel in updated_allocation]) + f"""

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
