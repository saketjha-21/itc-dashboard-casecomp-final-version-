import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from fpdf import FPDF
import random
from datetime import date, timedelta

# ==============================================================================
# --- 1. PAGE CONFIGURATION & AESTHETICS ---
# ==============================================================================
st.set_page_config(layout="wide", page_title="Kily Agentic AI Engine for ITC",
                   page_icon="https://www.itcportal.com/assets/images/favicon.ico")

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #040810;
        color: #FAFAFA;
    }
    .st-emotion-cache-1d391kg {
        background-color: rgba(38, 39, 48, 0.2);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    .st-emotion-cache-1avcm0n {
        background: linear-gradient(145deg, #1f2c3e, #0a1018);
        border-radius: 12px;
        padding: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    .stPlotlyChart {
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.03);
        padding: 10px;
    }
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #00A86B;
        background-color: transparent;
        color: #00A86B;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #00A86B;
        color: #FFFFFF;
        box-shadow: 0 0 15px #00A86B;
    }
    .stDownloadButton>button {
        border: 1px solid #4B8BBE;
        color: #4B8BBE;
    }
    .stDownloadButton>button:hover {
        background-color: #4B8BBE;
        color: #FFFFFF;
        box-shadow: 0 0 15px #4B8BBE;
    }

    /* --- NEW: CSS FOR AMPLIFIED KPI CARDS --- */
    div[data-testid="stMetric"] {
        background-color: rgba(38, 39, 48, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    div[data-testid="stMetric"] > div:nth-child(2) { /* The KPI value */
        font-size: 2.25rem;
        font-weight: bold;
    }
    div[data-testid="stMetric"] > label { /* The KPI label */
        font-size: 1.1rem;
        font-weight: 500;
        text-transform: uppercase;
        color: #a0a0a0;
    }
    /* --- END NEW CSS --- */

    .agent-log {
        background-color: #1a1a2e;
        color: #e0e0e0;
        font-family: 'Courier New', Courier, monospace;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #4a4a70;
    }
    .agent-log .log-line { margin-bottom: 5px; }
    .agent-log .log-time { color: #8c8ca0; }
    .agent-log .agent-name { font-weight: bold; }
    .agent-log .agent-orchestrator { color: #57a6ff; }
    .agent-log .agent-budget { color: #ffca57; }
    .agent-log .agent-creative { color: #a277ff; }
    .agent-log .agent-bidding { color: #ff77a8; }
    .agent-log .agent-status { color: #20c997; }
    .log-container-blue {
        background-color: #1f2c3e;
        border-left: 5px solid #3b82f6;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .log-container-red {
        background-color: #3e1f1f;
        border-left: 5px solid #f63b3b;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .log-container-yellow {
        background-color: #3e3a1f;
        border-left: 5px solid #f6c83b;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .log-container-green {
        background-color: #1f3e2c;
        border-left: 5px solid #3bf68a;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 2. COMPETITOR MAPPING ---
# ==============================================================================
COMPETITOR_MAPPING = {
    "Sunfeast": {"name": "Britannia", "sku": "Bourbon"},
    "Bingo!": {"name": "Lay's", "sku": "Classic Salted"},
    "YiPPee!": {"name": "Maggi", "sku": "2-Minute Noodles"},
    "Aashirvaad": {"name": "Pillsbury", "sku": "Chakki Fresh Atta"},
    "B Natural": {"name": "Tropicana", "sku": "100% Mixed Fruit Juice"},
    "ITC Master Chef": {"name": "McCain", "sku": "Smiles"}
}


# ==============================================================================
# --- 3. DATA GENERATION ENGINE (STABLE) ---
# ==============================================================================
@st.cache_data(ttl=3600)
def generate_synthetic_data(is_kily_activated: bool):
    brands_skus = {
        "Aashirvaad": ["Select Atta", "Multigrain Atta", "Iodized Salt", "Turmeric Powder", "Organic Tur Dal",
                       "Gulab Jamun Mix"],
        "Sunfeast": ["Dark Fantasy Choco Fills", "Mom's Magic Cashew", "Farmlite Oats & Almonds",
                     "Bounce Cream Biscuit", "Marie Light"],
        "YiPPee!": ["Magic Masala Noodles", "Power Up Atta Noodles", "Creamy Pasta"],
        "Bingo!": ["Mad Angles", "Tedhe Medhe", "Original Style Potato Chips"],
        "B Natural": ["Mixed Fruit Juice", "Guava Juice", "Tender Coconut Water"],
        "ITC Master Chef": ["Classic Aloo Tikki", "Chilli Garlic Potato Shots", "Chicken Nuggets"]
    }
    platforms = ["Blinkit", "Zepto", "Swiggy Instamart", "Flipkart", "Amazon"]
    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Kolkata"]
    dayparts = ["Breakfast", "Lunch", "Snacks", "Dinner"]

    config = {
        "old_way": {"roas_mean": 1.8, "roas_std": 0.8, "oos_prob": 0.10, "cvr_lift": 0.0,
                    "content_score_range": (4, 7)},
        "kily_way": {"roas_mean": 2.8, "roas_std": 0.4, "oos_prob": 0.005, "cvr_lift": 0.15,
                     "content_score_range": (8, 11)}
    }
    mode = "kily_way" if is_kily_activated else "old_way"

    data = []
    date_range = pd.to_datetime(pd.date_range(end=pd.Timestamp.now(), periods=30))

    for date in date_range:
        daily_volatility = np.random.uniform(0.85, 1.15)
        for brand, skus in brands_skus.items():
            for sku in skus:
                for platform in platforms:
                    for city in cities:
                        for daypart in dayparts:
                            base_roas = np.random.normal(config[mode]["roas_mean"], config[mode]["roas_std"])
                            spend = np.random.uniform(500, 5000) * daily_volatility
                            base_cvr = np.random.uniform(0.02, 0.10)
                            effective_cvr = base_cvr * (1 + config[mode]["cvr_lift"])
                            impressions = np.random.randint(2500, 40000)
                            clicks = int(impressions * np.random.uniform(0.005, 0.05))
                            conversions = int(clicks * effective_cvr)
                            noise = np.random.normal(0, 0.15)
                            roas = max(0.5, base_roas + noise)
                            direct_sales = spend * roas
                            is_oos = np.random.choice([True, False],
                                                      p=[config[mode]["oos_prob"], 1 - config[mode]["oos_prob"]])
                            content_score = np.random.randint(*config[mode]["content_score_range"])
                            data.append(
                                [date, brand, sku, platform, city, daypart, spend, impressions, clicks, conversions,
                                 direct_sales, roas, is_oos, content_score])
    columns = ["Date", "Brand", "SKU", "Platform", "City", "Daypart", "Spend", "Impressions", "Clicks", "Conversions",
               "Direct Sales", "ROAS", "Is OOS", "Content Score"]
    return pd.DataFrame(data, columns=columns)


# ==============================================================================
# --- 4. PDF GENERATION UTILITY (MODIFIED) ---
# ==============================================================================
def create_pdf_summary(kpis_kily, kpis_old):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, "Kily Agentic AI Engine: Performance Brief", 0, 1, 'C')
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 8, f"Report for ITC Foods | Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "1. Executive Summary", 0, 1, 'L')
    pdf.set_font("Arial", '', 11)
    uplift = (kpis_kily['roas'] / kpis_old['roas'] - 1) * 100 if kpis_old['roas'] > 0 else 0
    revenue_gain = kpis_kily['sales'] - kpis_old['sales']
    summary_text = f"Activation of the Kily Agentic AI Engine resulted in a transformative impact on performance marketing over the last 30 days. The engine delivered a {uplift:.1f}% improvement in blended ROAS, generating an additional Rs. {revenue_gain:,.0f} in incremental revenue. This was achieved through autonomous, real-time optimization across more than 40,000 campaign variables, validating the shift from manual oversight to an agentic framework."
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Top-Line Impact Analysis", 0, 1, 'L')
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(80, 8, "Metric", 1, 0, 'C', 1)
    pdf.cell(35, 8, "Baseline (Manual)", 1, 0, 'C', 1)
    pdf.cell(35, 8, "Kily Engine (Active)", 1, 0, 'C', 1)
    pdf.cell(35, 8, "Impact", 1, 1, 'C', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(80, 8, "Total Direct Sales (Rs.)", 1, 0, 'L')
    pdf.cell(35, 8, f"{kpis_old['sales']:,.0f}", 1, 0, 'R')
    pdf.cell(35, 8, f"{kpis_kily['sales']:,.0f}", 1, 0, 'R')
    pdf.set_font("Arial", 'B', 10);
    pdf.set_text_color(0, 128, 0)
    pdf.cell(35, 8, f"+{revenue_gain:,.0f}", 1, 1, 'R');
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.cell(80, 8, "Blended ROAS", 1, 0, 'L')
    pdf.cell(35, 8, f"{kpis_old['roas']:.2f}x", 1, 0, 'R')
    pdf.cell(35, 8, f"{kpis_kily['roas']:.2f}x", 1, 0, 'R')
    pdf.set_font("Arial", 'B', 10);
    pdf.set_text_color(0, 128, 0)
    pdf.cell(35, 8, f"+{uplift:.1f}%", 1, 1, 'R');
    pdf.set_text_color(0, 0, 0)
    conv_gain = kpis_kily['conv'] - kpis_old['conv']
    pdf.set_font("Arial", '', 10)
    pdf.cell(80, 8, "Total Conversions", 1, 0, 'L')
    pdf.cell(35, 8, f"{kpis_old['conv']:,}", 1, 0, 'R')
    pdf.cell(35, 8, f"{kpis_kily['conv']:,}", 1, 0, 'R')
    pdf.set_font("Arial", 'B', 10);
    pdf.set_text_color(0, 128, 0)
    pdf.cell(35, 8, f"+{conv_gain:,}", 1, 1, 'R');
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. Key Impact Drivers & Conclusion", 0, 1, 'L')
    pdf.set_font("Arial", '', 11)
    drivers_text = """The Kily Engine's outperformance is not marginal; it's structural. The primary drivers include:\n\n  * Operational Efficiency: Eradication of wasted ad spend on Out-of-Stock SKUs.\n  * Predictive Allocation: Superior, algorithm-driven budget distribution over human heuristics.\n  * Bidding Superiority: Real-time, reinforcement learning-based bidding that minimizes acquisition cost."""
    pdf.multi_cell(0, 6, drivers_text)
    pdf.ln(2)
    conclusion_text = "Conclusion: The data confirms that an agentic AI approach is a prerequisite for achieving market-leading profitability and scale in the hyper-competitive Quick Commerce landscape."
    pdf.set_font("Arial", 'B', 11)
    pdf.multi_cell(0, 6, conclusion_text)
    return bytes(pdf.output(dest='S'))


# ==============================================================================
# --- 5. THE APP LOGIC STARTS HERE ---
# ==============================================================================

st.sidebar.title("Kily Agentic AI Engine")
st.sidebar.header("ITC Foods")
st.sidebar.markdown("---")
is_kily_activated = st.sidebar.toggle("**Activate Kily AI Engine**", value=True,
                                      help="Toggle to see the direct impact of the Kily Engine vs. the manual baseline.")
df_kily = generate_synthetic_data(is_kily_activated=True)
df_old = generate_synthetic_data(is_kily_activated=False)
df_display = df_kily if is_kily_activated else df_old
page = st.sidebar.radio("Navigation",
                        ("Agentic Orchestrator", "Insights & Action Center", "Strategic Campaign Planner",
                         "Competitive Intelligence", "SKU Deep-Dive"))
st.sidebar.markdown("---")
st.sidebar.info("This is a functional POC for ITC's 'Interrobang' competition. All data is synthetically generated.")

if page == "Agentic Orchestrator":
    st.title("Agentic Orchestrator")

    # --- KILY EFFICIENCY SCORE ---
    st.markdown("### The Ultimate KPI: One Score to Rule Them All")
    score_col1, score_col2 = st.columns(2)
    with score_col1:
        if is_kily_activated:
            score = 92
            delta_score = score - 55
            st.metric("Kily Efficiency Score", f"{score}/100", f"{delta_score} vs Baseline")
        else:
            score = 55
            st.metric("Kily Efficiency Score", f"{score}/100", "Activate Kily for Uplift", delta_color="off")
    with score_col2:
        st.write("""
        This score is a composite metric reflecting the overall health and efficiency of your marketing operations. 
        It synthesizes **ROAS**, **OOS prevention**, **Content Quality**, and **CPA** into a single, undeniable number.
        """)
    st.markdown("---")

    st.markdown(
        "A strategic cockpit for oversight and insight into ITC's performance marketing for the **Last 30 Days**.")

    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        city_filter = st.selectbox("Filter by City", ["All Cities"] + list(df_display['City'].unique()))
    with fcol2:
        platform_filter = st.selectbox("Filter by Platform", ["All Platforms"] + list(df_display['Platform'].unique()))
    with fcol3:
        brand_filter = st.selectbox("Filter by Brand", ["All Brands"] + list(df_display['Brand'].unique()))

    df_filtered = df_display.copy()
    df_kily_filtered = df_kily.copy()
    df_old_filtered = df_old.copy()
    if city_filter != "All Cities":
        df_filtered = df_filtered[df_filtered['City'] == city_filter]
        df_kily_filtered = df_kily_filtered[df_kily_filtered['City'] == city_filter]
        df_old_filtered = df_old_filtered[df_old_filtered['City'] == city_filter]
    if platform_filter != "All Platforms":
        df_filtered = df_filtered[df_filtered['Platform'] == platform_filter]
        df_kily_filtered = df_kily_filtered[df_kily_filtered['Platform'] == platform_filter]
        df_old_filtered = df_old_filtered[df_old_filtered['Platform'] == platform_filter]
    if brand_filter != "All Brands":
        df_filtered = df_filtered[df_filtered['Brand'] == brand_filter]
        df_kily_filtered = df_kily_filtered[df_kily_filtered['Brand'] == brand_filter]
        df_old_filtered = df_old_filtered[df_old_filtered['Brand'] == brand_filter]

    sales_kily = df_kily_filtered['Direct Sales'].sum()
    spend_kily = df_kily_filtered['Spend'].sum()
    conv_kily = df_kily_filtered['Conversions'].sum()
    roas_kily = sales_kily / spend_kily if spend_kily > 0 else 0
    cpa_kily = spend_kily / conv_kily if conv_kily > 0 else 0
    sales_old = df_old_filtered['Direct Sales'].sum()
    spend_old = df_old_filtered['Spend'].sum()
    conv_old = df_old_filtered['Conversions'].sum()
    roas_old = sales_old / spend_old if spend_old > 0 else 0
    cpa_old = spend_old / conv_old if conv_old > 0 else 0

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    if is_kily_activated:
        kpi1.metric("Total Direct Sales", f"₹{sales_kily:,.0f}", delta=f"₹{(sales_kily - sales_old):,.0f} vs Baseline")
        kpi2.metric("Blended ROAS", f"{roas_kily:.2f}x", delta=f"{roas_kily - roas_old:.2f}x vs Baseline")
        kpi3.metric("Total Conversions", f"{conv_kily:,}", delta=f"{(conv_kily - conv_old):,} vs Baseline",
                    help="A 'conversion' is a successful purchase.")
        kpi4.metric("Cost Per Acquisition (CPA)", f"₹{cpa_kily:,.2f}", delta=f"₹{cpa_kily - cpa_old:,.2f} vs Baseline",
                    delta_color="inverse")
        kpi5.metric("Total Spend", f"₹{spend_kily:,.0f}", delta=f"₹{spend_kily - spend_old:,.0f} vs Baseline")
    else:
        kpi1.metric("Total Direct Sales", f"₹{sales_old:,.0f}")
        kpi2.metric("Blended ROAS", f"{roas_old:.2f}x")
        kpi3.metric("Total Conversions", f"{conv_old:,}", help="A 'conversion' is a successful purchase.")
        kpi4.metric("Cost Per Acquisition (CPA)", f"₹{cpa_old:,.2f}")
        kpi5.metric("Total Spend", f"₹{spend_old:,.0f}")

    st.write("")
    pdf_data = create_pdf_summary({"sales": sales_kily, "roas": roas_kily, "conv": conv_kily},
                                  {"sales": sales_old, "roas": roas_old, "conv": conv_old})
    st.download_button("Download Performance Brief (PDF)", data=pdf_data, file_name="ITC_Kily_Performance_Brief.pdf",
                       use_container_width=True)
    st.markdown("---")

    kily_time_perf = df_kily_filtered.groupby(df_kily_filtered['Date'].dt.date)['Direct Sales'].sum().rename(
        'Kily Performance')
    old_time_perf = df_old_filtered.groupby(df_old_filtered['Date'].dt.date)['Direct Sales'].sum().rename(
        'Baseline Performance')
    time_perf_df = pd.concat([kily_time_perf, old_time_perf], axis=1).reset_index()
    sales_uplift_percentage = ((sales_kily / sales_old) - 1) * 100 if sales_old > 0 else 100
    time_title_new = f"Daily Sales: Kily Driving a +{sales_uplift_percentage:.1f}% Uplift" if is_kily_activated else "Daily Sales: Baseline vs. Kily Potential"

    fig_time_new = go.Figure()
    fig_time_new.add_trace(
        go.Scatter(x=time_perf_df['Date'], y=time_perf_df['Baseline Performance'], mode='lines', name='Baseline',
                   line=dict(color='#FF4B4B', dash='dash')))
    fig_time_new.add_trace(
        go.Scatter(x=time_perf_df['Date'], y=time_perf_df['Kily Performance'], mode='lines', name='Kily Performance',
                   line=dict(color='#00A86B', width=3), fill='tonexty', fillcolor='rgba(0, 168, 107, 0.3)'))
    fig_time_new.update_layout(title=time_title_new, template="plotly_dark", height=450,
                               legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig_time_new, use_container_width=True)

    st.markdown("---")
    st.subheader("Proactive Agent Feed: Threats & Opportunities")
    intel_col1, intel_col2 = st.columns(2)
    with intel_col1:
        st.info(
            "`[OPPORTUNITY]` Social sentiment for 'late-night snacks' is up 30% in Bangalore. Suggesting a 5% budget shift to Sunfeast Dark Fantasy ads between 10 PM - 1 AM.")
        st.warning(
            "`[MARKET SHIFT]` Weather forecast predicts a heatwave in Delhi next week. Predictive model shows a 60% increase in demand for 'B Natural' juices. Pre-emptively increasing bid aggression.")
    with intel_col2:
        st.error(
            "`[THREAT]` Competitor 'Britannia' has launched a new ad campaign on YouTube targeting 'healthy biscuits'. Our model predicts a 10% overlap with our 'Farmlite' audience. Recommending a counter-campaign.")
        st.info(
            "`[OPPORTUNITY]` High search volume detected for 'party packs' related to 'Bingo!'. Recommending launch of new ad group targeting these keywords.")
    st.markdown("---")

    gcol1, gcol2 = st.columns(2)
    with gcol1:
        platform_title = "Platform Performance"
        platform_perf = df_filtered.groupby('Platform').agg({'Direct Sales': 'sum', 'ROAS': 'mean'}).reset_index()
        fig_platform = px.bar(platform_perf.sort_values('Direct Sales', ascending=False), x='Platform',
                              y='Direct Sales', color='ROAS', color_continuous_scale='greens', title=platform_title)
        fig_platform.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_platform, use_container_width=True)
        geo_title = "Geographical Performance"
        city_perf = df_filtered.groupby('City').agg(
            {'Direct Sales': 'sum', 'ROAS': 'mean', 'Spend': 'sum'}).reset_index()
        fig_tree = px.treemap(city_perf, path=[px.Constant("All India"), 'City'], values='Direct Sales', color='ROAS',
                              hover_data={'Spend': ':,.0f'}, color_continuous_scale='RdYlGn', title=geo_title)
        fig_tree.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_tree, use_container_width=True)
    with gcol2:
        brand_title = "Brand Contribution"
        brand_perf = df_filtered.groupby('Brand')['Direct Sales'].sum().reset_index()
        fig_pie = px.pie(brand_perf, names='Brand', values='Direct Sales', title=brand_title, hole=0.4)
        fig_pie.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
        heatmap_title = "ROAS Heatmap: Brand vs. Daypart"
        heatmap_brands = ['Aashirvaad', 'Bingo!', 'Sunfeast', 'YiPPee!']
        heatmap_df = df_filtered[df_filtered['Brand'].isin(heatmap_brands)]
        if not heatmap_df.empty:
            pivot_data = heatmap_df.pivot_table(index='Daypart', columns='Brand', values='ROAS', aggfunc='mean').fillna(
                0)
            if not pivot_data.empty:
                pivot_data = pivot_data.reindex(['Breakfast', 'Dinner', 'Lunch', 'Snacks']).dropna(how='all')
            fig_heatmap = px.imshow(pivot_data, text_auto=".2f", aspect="auto", color_continuous_scale='RdYlGn',
                                    title=heatmap_title)
            fig_heatmap.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_heatmap, use_container_width=True)

elif page == "Insights & Action Center":
    st.title("Insights & Action Center")
    st.markdown("The AI's logbook: real-time alerts and strategic recommendations.")
    tab1, tab2, tab3, tab4 = st.tabs(["OOS Alerts", "Content Audit", "AI Logbook", "Raw Audit Trail"])
    with tab1:
        oos_df = df_display[df_display['Is OOS'] == True]
        if is_kily_activated:
            st.success(
                f"Kily Engine is active. Only {len(oos_df)} OOS instances detected. Ad spend automatically paused.")
        else:
            st.error(f"Kily Engine is INACTIVE. {len(oos_df)} OOS instances detected, wasting ad spend.")
        st.dataframe(oos_df[['Brand', 'SKU', 'Platform', 'City', 'Spend']].sort_values('Spend', ascending=False),
                     use_container_width=True, hide_index=True)
    with tab2:
        content_df = df_display[df_display['Content Score'] < 8]
        if is_kily_activated:
            st.success("Kily Engine has optimized content across most SKUs.")
            if not content_df.empty:
                st.dataframe(content_df[['Brand', 'SKU', 'Platform', 'City', 'Content Score']],
                             use_container_width=True, hide_index=True)
            else:
                st.write("No SKUs with poor content scores found.")
        else:
            st.warning(f"Found {len(content_df)} SKUs with poor content scores, hurting conversion rates.")
            st.dataframe(content_df[['Brand', 'SKU', 'Platform', 'City', 'Content Score']].sort_values('Content Score'),
                         use_container_width=True, hide_index=True)
    with tab3:
        if is_kily_activated:
            st.markdown("##### Agentic AI's Live Log (Illustrative)")
            with st.container():
                st.markdown(
                    """<div class="log-container-blue"><b>11:39 AM:</b> BUDGET SHIFT - High ROAS (3.8x) detected for 'Aashirvaad Atta' in Hyderabad. Agent reallocated +10% of daily budget.</div>""",
                    unsafe_allow_html=True)
                with st.expander("Show Rationale"):
                    st.write(
                        "Correlation analysis detected a 45% increase in searches for 'healthy meals' in Hyderabad, which has a 0.87 predictive coefficient with 'Aashirvaad Atta' sales. The agent acted to capture this emergent demand.")
                    st.line_chart(pd.DataFrame(np.random.randn(20, 2),
                                               columns=['"healthy meals" search volume', '"Aashirvaad Atta" sales']),
                                  height=150)
            with st.container():
                st.markdown(
                    """<div class="log-container-red"><b>02:00 PM:</b> OOS ALERT - 'Bingo! Tedhe Medhe' 50g OOS in Bangalore (Blinkit). Agent paused 3 associated campaigns. Prevented ~₹15,000 in wasted spend.</div>""",
                    unsafe_allow_html=True)
                with st.expander("Show Rationale"):
                    st.write(
                        "Real-time inventory API reported 0 stock for the specified SKU. Pausing campaigns prevents budget waste on unfulfillable conversions, protecting ROAS.")
            with st.container():
                st.markdown(
                    """<div class="log-container-yellow"><b>04:15 PM:</b> CONTENT AUDIT - 4 'Candyman' SKUs on Flipkart are missing video assets. Score is 6/10. Recommendation issued.</div>""",
                    unsafe_allow_html=True)
                with st.expander("Show Rationale"):
                    st.write(
                        "Our models indicate that SKUs with video assets have an average 22% higher conversion rate. An automated ticket has been issued to the content team to address this opportunity.")
            with st.container():
                st.markdown(
                    """<div class="log-container-green"><b>05:00 PM:</b> CREATIVE OPTIMIZATION - New ad copy for 'Dark Fantasy' (Dinner slot) achieved a 18% higher CTR. Scaling winning variation.</div>""",
                    unsafe_allow_html=True)
                with st.expander("Show Rationale"):
                    st.write(
                        "The winning creative (variation B) is being automatically promoted to 100% of traffic for this ad set. The losing variation has been paused to maximize click-through rate and quality score.")
                    st.bar_chart({"Variation A": 0.042, "Variation B (Winner)": 0.057}, height=200)
        else:
            st.info("Activate the Kily Engine to see the live AI log and autonomous actions.")
    with tab4:
        st.subheader("Raw Event Log: Full Audit Trail")
        st.write(
            "This provides a clear, immutable record of a single agentic action, from event trigger to execution, ensuring full transparency and accountability for critical operations.")
        log_data = {
            "Timestamp": ["2025-08-16 15:42:31"],
            "SKU_ID": ["SunDarkF-101"],
            "Event": ["OOS detected (Blinkit)"],
            "Action": ["Paused Campaign ID=BK-334"],
            "Actor": ["BudgetAgent v1.3"],
            "Evidence": ["API Response: Inventory=0"],
            "Impact Forecast": ["Loss prevention ~₹42,000/hr"],
            "Override Status": ["None"]
        }
        log_df = pd.DataFrame(log_data)
        st.dataframe(log_df, use_container_width=True, hide_index=True)
        st.code("""
# Sample Raw Event Data (JSON)
{
    "eventId": "e9c2b8e3-ff4d-4d7a-8b17-f2a1b9e0f3d5",
    "timestamp": "2025-08-16T15:42:31.054Z",
    "source": "BlinkitInventoryAPI",
    "actor": "BudgetAgent/v1.3",
    "trigger": {
        "type": "inventory.level.zero",
        "sku": "SunDarkF-101",
        "city": "Bangalore"
    },
    "action": {
        "type": "campaign.pause",
        "targetId": "BK-334",
        "reason": "OOS_DETECTED"
    },
    "metadata": {
        "forecastedLossPerHour": 42000,
        "humanOverride": false,
        "confidenceScore": 0.998
    }
}
        """, language="json")

elif page == "Strategic Campaign Planner":
    st.title("Strategic Campaign Planner")
    st.markdown(
        "Define high-level goals. The Kily Engine will architect and autonomously deploy a data-backed campaign strategy.")
    st.subheader("1. State Your Strategic Objective")
    objective_text = st.text_area("Example: 'I need to increase market share for Bingo! in Delhi by 5% before Diwali.'",
                                  height=100)
    if st.button("Synthesize Strategy from Objective", use_container_width=True):
        with st.spinner(
                "Parsing natural language objective... Cross-referencing market data... Formulating preliminary parameters..."):
            time.sleep(2)
            if 'bingo' in objective_text.lower(): st.session_state.brand_select = "Bingo!"
            if 'delhi' in objective_text.lower(): st.session_state.geo_select = ["Delhi"]
            if 'market share' in objective_text.lower(): st.session_state.objective_select = "Dominate a Category"
            if 'diwali' in objective_text.lower(): st.session_state.budget_select = 5000000
        st.success("Strategy parameters synthesized. Please review and adjust below.")
    st.markdown("---")
    st.subheader("2. Simulate Outcomes with Key Levers")
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        sim_budget = st.slider("Campaign Budget (₹)", min_value=500000, max_value=10000000,
                               value=st.session_state.get('budget_select', 2500000), step=100000)
    with sim_col2:
        sim_risk = st.select_slider("Risk vs. Reward Tolerance", options=["Conservative", "Balanced", "Aggressive"],
                                    value="Balanced")
    risk_multiplier = {"Conservative": 0.9, "Balanced": 1.0, "Aggressive": 1.15}
    base_roas = 2.85
    noise = np.random.uniform(-0.15, 0.15)
    sim_roas = (base_roas + noise) * risk_multiplier[sim_risk]
    sim_revenue = sim_budget * sim_roas
    st.markdown("##### Live Performance Forecast")
    f_col1, f_col2 = st.columns(2)
    f_col1.metric("Projected Revenue", f"₹{sim_revenue:,.0f}")
    f_col2.metric("Projected ROAS", f"{sim_roas:.2f}x")
    st.markdown("---")
    if 'plan_architected' not in st.session_state: st.session_state.plan_architected = False
    if 'plan_deployed' not in st.session_state: st.session_state.plan_deployed = False
    st.subheader("3. Finalize & Deploy Campaign")
    with st.form("campaign_form"):
        brand_options = list(df_display['Brand'].unique())
        brand_default_index = brand_options.index(st.session_state.get('brand_select', brand_options[0]))
        obj_options = ["Maximize ROAS", "Brand Awareness (Reach)", "New Product Launch", "Dominate a Category"]
        obj_default_index = obj_options.index(st.session_state.get('objective_select', obj_options[0]))
        col1, col2, col3 = st.columns(3)
        with col1:
            objective = st.selectbox("Campaign Objective", obj_options, index=obj_default_index)
            brand = st.selectbox("Select Brand", brand_options, index=brand_default_index)
            start_date = st.date_input("Campaign Start Date", date.today())
        with col2:
            budget = st.number_input("Enter Total Budget (₹)", min_value=100000, value=sim_budget, step=100000)
            platforms = st.multiselect("Platform Focus", df_display['Platform'].unique(), default=["Blinkit", "Zepto"])
            end_date = st.date_input("Campaign End Date", date.today() + timedelta(days=30))
        with col3:
            geo_focus = st.multiselect("Geographical Focus", df_display['City'].unique(),
                                       default=st.session_state.get('geo_select', ["Mumbai", "Delhi"]))
            sku = st.selectbox("Select Target SKU", df_display[df_display['Brand'] == brand]['SKU'].unique())
        submitted = st.form_submit_button("ARCHITECT STRATEGY", use_container_width=True)
        if submitted:
            with st.spinner(
                    "Analyzing historical data... Running multi-objective genetic algorithm... Simulating market response..."):
                time.sleep(2.5)
            st.session_state.plan_architected = True
            st.session_state.plan_deployed = False
            st.session_state.params = {"objective": objective, "brand": brand, "budget": budget, "geo_focus": geo_focus,
                                       "platforms": platforms, "sku": sku, "start_date": start_date,
                                       "end_date": end_date}
            st.rerun()
    if st.session_state.plan_architected and not st.session_state.plan_deployed:
        st.subheader("4. AI-Generated Strategic Brief & Deployment Plan")
        st.info(f"Mission Architecture Complete & Ready for Deployment for '{st.session_state.params['sku']}'.")
        plan_col1, plan_col2 = st.columns([2, 3])
        with plan_col1:
            st.markdown("##### AI-Recommended Platform Allocation")
            df_split = pd.DataFrame({'Platform': st.session_state.params['platforms'],
                                     'Allocation': np.random.dirichlet(
                                         np.ones(len(st.session_state.params['platforms']))) * 100})
            fig = px.pie(df_split, names='Platform', values='Allocation', hole=0.5)
            fig.update_layout(height=300, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20),
                              legend_title_text='')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("##### Recommended Spend Pacing")
            days = (st.session_state.params['end_date'] - st.session_state.params['start_date']).days
            if days > 0:
                pacing_dates = pd.to_datetime(
                    pd.date_range(start=st.session_state.params['start_date'], end=st.session_state.params['end_date']))
                x = np.linspace(-2, 2, len(pacing_dates))
                y = np.exp(-x ** 2)
                pacing_spend = (y / y.sum()) * st.session_state.params['budget']
                pacing_df = pd.DataFrame({'Date': pacing_dates, 'Daily Spend': pacing_spend})
                fig_pacing = px.area(pacing_df, x='Date', y='Daily Spend')
                fig_pacing.update_layout(height=300, template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20),
                                         yaxis_title=None, xaxis_title=None)
                st.plotly_chart(fig_pacing, use_container_width=True)
        with plan_col2:
            st.markdown("##### Kily's Agentic Rationale & Actions")
            with st.expander("Final Performance Forecast", expanded=True):
                projected_roas = sim_roas
                projected_revenue = st.session_state.params['budget'] * projected_roas
                st.metric("Projected Revenue", f"₹{projected_revenue:,.0f}")
                st.metric("Projected ROAS", f"{projected_roas:.2f}x")
            with st.expander("Kily's 3-Phase Action Plan", expanded=True):
                st.markdown("###### Phase 1: Awareness & Reach (Days 1-7)")
                st.write("- **Focus:** Maximize impressions and clicks on high-reach platforms.")
                st.markdown("###### Phase 2: High-Intent Conversion (Days 8-21)")
                st.write("- **Focus:** Drive conversions and improve ROAS.")
                st.markdown("###### Phase 3: Optimization & ROAS Maximization (Days 22-30)")
                st.write("- **Focus:** Squeeze maximum efficiency from the remaining budget.")
            with st.expander("AI Rationale & Risk Mitigation"):
                st.write(
                    "**Rationale:** This strategy balances initial awareness with a strong mid-campaign push to maximize conversions and ROAS, tapering off as the campaign concludes to optimize remaining budget.")
                st.write("**Risk:** Potential for competitor price wars to suppress ROAS mid-campaign.")
                st.write(
                    "**Mitigation:** Kily's Price War Monitor will detect competitor promotions in real-time and autonomously deploy counter-measures.")
        st.markdown("---")
        _, d_col1, d_col2, _ = st.columns([1, 2, 2, 1])
        if d_col1.button("DEPLOY AUTONOMOUSLY", use_container_width=True):
            with st.spinner(
                    "Instantiating sub-agents... Propagating parameters to RL Bidding Engine... Verifying live deployment..."):
                time.sleep(2.5)
            st.session_state.plan_deployed = True
            st.rerun()
        if d_col2.button("MODIFY PARAMETERS", use_container_width=True, type="secondary"):
            st.session_state.plan_architected = False
            st.rerun()
    if st.session_state.plan_deployed:
        st.success(f"Strategy Deployed! Monitoring live performance for '{st.session_state.params['sku']}'.")
        ts = pd.Timestamp.now()
        log_html = f"""<div class="agent-log"><div class="log-line"><span class="log-time">[{ts.strftime('%H:%M:%S')}]</span> <span class="agent-name agent-orchestrator">AGENT_ORCHESTRATOR:</span> Goal received. Deploying sub-agents.</div><div class="log-line"><span class="log-time">[{ts.strftime('%H:%M:%S')}]</span> <span class="agent-name agent-budget">BUDGET_AGENT:</span> Allocating ₹ {st.session_state.params['budget']:,} according to spend pacing curve.</div><div class="log-line"><span class="log-time">[{ts.strftime('%H:%M:%S')}]</span> <span class="agent-name agent-creative">CREATIVE_AGENT:</span> Generating {random.randint(45, 60)} ad variations.</div><div class="log-line"><span class="log-time">[{ts.strftime('%H:%M:%S')}]</span> <span class="agent-name agent-bidding">BIDDING_AGENT:</span> Initiating real time bidding on high-intent keywords.</div><div class="log-line"><span class="log-time">[{ts.strftime('%H:%M:%S')}]</span> <span class="agent-name agent-status">DEPLOYMENT_STATUS:</span> SUCCESSFUL. CAMPAIGN IS LIVE.</div></div>"""
        st.markdown(log_html, unsafe_allow_html=True)
        if st.button("Plan New Campaign"):
            st.session_state.plan_architected = False
            st.session_state.plan_deployed = False
            st.rerun()

elif page == "Competitive Intelligence":
    st.title("Competitive Intelligence")
    st.markdown("Monitor the market, track competitors, and **win the digital shelf.**")
    st.subheader("The Keyword Battleground")
    st.markdown("Measuring rank for: **Sunfeast Dark Fantasy**")
    keyword = st.text_input("Enter a generic keyword to check ranking", "cream biscuits")
    if keyword:
        battle_col1, battle_col2 = st.columns(2)
        with battle_col1:
            st.markdown("##### Your Ranking (Kily Engine OFF)")
            st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>#3</h1>", unsafe_allow_html=True)
            st.warning("Risk of losing high-intent customers to competitors.")
        with battle_col2:
            st.markdown("##### Your Ranking (Kily Engine ON)")
            st.markdown("<h1 style='text-align: center; color: #00A86B;'>#1</h1>", unsafe_allow_html=True)
            st.success("Dominating the first screen for high-volume searches.")
        st.markdown("---")
        sov_title = "Share of Voice: **Kily Engine Dominating Search**" if is_kily_activated else "Share of Voice: **Losing the Keyword War**"
        st.subheader(sov_title)
        competitors = ["Britannia", "Parle", "Cadbury"]
        sov_data_old = {"Brand": ["Sunfeast (Kily OFF)"] + competitors, "SoV": [15, 35, 30, 20]}
        sov_data_kily = {"Brand": ["Sunfeast (Kily ON)"] + competitors, "SoV": [45, 25, 20, 10]}
        df_sov = pd.DataFrame(sov_data_kily if is_kily_activated else sov_data_old)
        fig = px.bar(df_sov.sort_values('SoV', ascending=False), x="Brand", y="SoV", color="Brand",
                     color_discrete_map={"Sunfeast (Kily ON)": "#00A86B", "Sunfeast (Kily OFF)": "#FF4B4B"}, text='SoV')
        fig.update_layout(template="plotly_dark", yaxis_title="Share of Voice (%)", xaxis_title="")
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.subheader("Live Competitor Product & Pricing Analysis")
    platforms_ci = ["Blinkit", "Zepto", "Instamart"]
    competitors_ci = ['Competitor A', 'Competitor B', 'Competitor C']
    ci_col1, ci_col2 = st.columns([2, 3])
    with ci_col1:
        st.markdown("##### Prices For Cream Biscuits")
        st.dataframe(pd.DataFrame(
            [{'Competitor': c, **{p: f"₹{np.random.uniform(25, 45):.1f}" for p in platforms_ci}} for c in
             competitors_ci]), use_container_width=True, hide_index=True)
        st.markdown("##### Prices For Instant Noodles")
        st.dataframe(pd.DataFrame(
            [{'Competitor': c, **{p: f"₹{np.random.uniform(10, 15):.1f}" for p in platforms_ci}} for c in
             competitors_ci]), use_container_width=True, hide_index=True)
    with ci_col2:
        st.markdown("##### Product Traffic (Last 24h)")
        st.bar_chart(pd.DataFrame(
            {"Blinkit": np.random.randint(2000, 10000, 5), "Zepto": np.random.randint(2000, 10000, 5),
             "Instamart": np.random.randint(2000, 10000, 5)}, index=['Biscuits', 'Noodles', 'Chips', 'Juice', 'Atta']),
                     height=250)
        st.markdown("##### Average Discount by Brand")
        st.bar_chart(pd.DataFrame({"Avg Discount (%)": np.random.uniform(2, 18, 7)},
                                  index=['Aashirvaad', 'Sunfeast', 'Bingo!', 'YiPPee!', 'Competitor A', 'Competitor B',
                                         'Competitor C']), height=250)
    st.markdown("---")
    st.subheader("Price War Monitor (Real-Time Simulated Alerts)")
    st.warning("`ALERT:` Britannia running a 2-hour 15% off promotion on 'Bourbon' on Zepto in **Mumbai**.")
    st.info("`KILY ACTION:` A targeted 10% off counter-promotion on 'Dark Fantasy' has been **autonomously deployed**.")
    st.warning("`ALERT:` Cadbury running a 'Buy 2 Get 1 Free' on 'Oreo' on Blinkit in **Delhi**.")
    st.info(
        "`KILY ACTION:` Kily advises against matching. Instead, it has **reallocated ₹50,000** to outbid them on high-intent keywords.")

elif page == "SKU Deep-Dive":
    st.title("SKU Deep-Dive & Digital Shelf Audit")
    st.markdown("Analyze individual product performance and make the problem of poor content **painfully visible.**")
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        brand_select = st.selectbox("Select a Brand to Analyze", df_display['Brand'].unique())
    with dcol2:
        sku_select = st.selectbox("Select a Specific SKU",
                                  df_display[df_display['Brand'] == brand_select]['SKU'].unique())
    st.markdown("---")
    if sku_select:
        sku_df = df_display[df_display['SKU'] == sku_select]
        st.subheader("The Tale of Two Shelves: Your SKU vs. The Enemy")
        competitor = COMPETITOR_MAPPING.get(brand_select, {"name": "Competitor", "sku": "Generic SKU"})
        shelf1, shelf2 = st.columns(2)
        with shelf1:
            st.markdown(f"**Your Shelf (Kily Engine {'ON' if is_kily_activated else 'OFF'})**")
            st.markdown(f"**SKU:** *{sku_select}*")
            avg_score = sku_df['Content Score'].mean()
            st.metric("Content Score", f"{avg_score:.1f}/10",
                      delta="Optimized by AI" if avg_score > 8 else "Needs Improvement",
                      delta_color="normal" if avg_score > 8 else "inverse")
            if avg_score < 8:
                st.error("**AI Recommendations:** Missing Video Asset. Short Description. Only 3 images.")
            else:
                st.success(
                    "**Analysis:** Content is fully optimized with rich media, A+ descriptions, and sufficient imagery.")
        with shelf2:
            st.markdown(f"**Competitor Shelf ({competitor['name']})**")
            st.markdown(f"**SKU:** *{competitor['sku']}*")
            st.metric("Content Score", "9.2/10", delta="Market Leader", delta_color="off")
            st.success(
                "**Analysis:** Rich video content. Detailed A+ description. 7 high-res images. They are winning.")
        st.markdown("---")
        st.subheader("AI-Generated Strategic SWOT Analysis")
        swot_data = {
            "Dark Fantasy Choco Fills": {
                "S": ["High brand recall", "Strong ROAS in 'Snacks' daypart", "Excellent content score (9.5/10)"],
                "W": ["Underperforming in Hyderabad", "Higher CPA than competitor 'Bourbon'"],
                "O": ["High search volume for 'choco-filled cookies' not fully captured",
                      "Opportunity for combo-pack promotions"],
                "T": ["'Britannia Bourbon' running aggressive discounts", "Emergence of D2C premium cookie brands"]
            },
            "Magic Masala Noodles": {
                "S": ["Market leader in taste preference surveys", "Strong performance on Quick-Commerce platforms"],
                "W": ["Lower share-of-voice compared to 'Maggi'", "Content score needs video assets"],
                "O": ["Growing demand for 'spicy noodles' keyword", "Collaborate with influencers for recipe videos"],
                "T": ["'Maggi' has a dominant market position", "New instant noodle brands entering the market"]
            },
            "Bingo! Mad Angles": {
                "S": ["Unique product shape and texture", "High engagement on social media campaigns"],
                "W": ["Inconsistent stock levels in Bangalore", "Lower repeat purchase rate than 'Lays'"],
                "O": ["Target 'party snack' and 'combo offer' keywords", "Potential for new flavor launches"],
                "T": ["'Lays' has a massive distribution advantage", "Health-conscious snacking trend"]
            }
        }

        swot = swot_data.get(sku_select)
        if swot:
            swot_c1, swot_c2, swot_c3, swot_c4 = st.columns(4)
            with swot_c1:
                st.success("##### Strengths")
                for item in swot["S"]: st.markdown(f"- {item}")
            with swot_c2:
                st.error("##### Weaknesses")
                for item in swot["W"]: st.markdown(f"- {item}")
            with swot_c3:
                st.info("##### Opportunities")
                for item in swot["O"]: st.markdown(f"- {item}")
            with swot_c4:
                st.warning("##### Threats")
                for item in swot["T"]: st.markdown(f"- {item}")
        else:
            st.info("Detailed SWOT analysis for this specific SKU is being computed. Check back later.")
        st.markdown("---")

        hcol1, hcol2 = st.columns([2, 3])
        with hcol1:
            st.subheader("ROAS Heatmap")
            heatmap_data = sku_df.pivot_table(index='Daypart', columns='Brand', values='ROAS', aggfunc='mean').fillna(0)
            title_heatmap = f"ROAS Hotspots: Kily Engine Active" if is_kily_activated else f"ROAS Hotspots (Baseline)"
            fig = px.imshow(heatmap_data, text_auto=".2f", aspect="auto", color_continuous_scale='Greens',
                            title=title_heatmap)
            fig.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig, use_container_width=True)
        with hcol2:
            st.subheader(f"ROAS Trend")
            title_trend = f"Kily Drives Consistent ROAS" if is_kily_activated else f"Volatile Daily ROAS (Baseline)"
            roas_trend_df = sku_df.groupby(sku_df['Date'].dt.date)['ROAS'].mean().reset_index()
            fig = px.line(roas_trend_df, x='Date', y='ROAS', title=title_trend, markers=True)
            fig.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig, use_container_width=True)