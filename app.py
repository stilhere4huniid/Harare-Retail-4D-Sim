import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import folium
from streamlit_folium import st_folium
from model import HarareMarketModel
from report_generator import create_pdf

st.set_page_config(page_title="Harare Retail War Room", layout="wide", page_icon="🏗️")

# --- GLOBAL SETTINGS ---
COLOR_DICT = {
    "Sam Levy's Village": "#1f77b4", "Arundel Village": "#ff7f0e",
    "Groombridge": "#9467bd", "Highland Park": "#d62728",
    "Mall of Zimbabwe": "#2ca02c"
}

def grid_to_gps(x, y):
    lat_start, lat_end = -17.82, -17.74
    lon_start, lon_end = 31.02, 31.12
    real_lat = lat_start + (y / 12) * (lat_end - lat_start)
    real_lon = lon_start + (x / 12) * (lon_end - lon_start)
    return real_lat, real_lon

# --- SESSION STATE ---
if 'simulation_results' not in st.session_state: st.session_state.simulation_results = None
if 'pdf_fig' not in st.session_state: st.session_state.pdf_fig = None
if 'simulation_inputs' not in st.session_state: st.session_state.simulation_inputs = {}
if 'folium_map' not in st.session_state: st.session_state.folium_map = None

# --- HEADER ---
st.title("🏗️ Harare Retail War Room: Project Timeline Simulator")
st.markdown("""
**4D Agent-Based Simulation:** Modeling the lifecycle of the Mall of Zimbabwe from **Groundbreaking (2026)** to **Stabilization (2029)**.
Includes Financial Forecasting based on Simbisa & Market Spend Data.
""")

# --- SIDEBAR ---
st.sidebar.header("⏳ Project Phase")
current_year = st.sidebar.select_slider("Simulation Year", options=[2026, 2027, 2028, 2029], value=2028)

if current_year < 2028:
    st.sidebar.warning(f"🚧 PHASE: Construction (Mall Closed)")
elif current_year == 2028:
    st.sidebar.success(f"🚀 PHASE: Grand Opening (Hype Bonus)")
else:
    st.sidebar.info(f"🏢 PHASE: Market Stabilization")

st.sidebar.divider()

# STRATEGY CONTROLS
st.sidebar.subheader("🏗️ Mall Strategy")
zim_base_q = st.sidebar.slider("Base Infrastructure Quality", 0, 100, 80)
moz_tenants = st.sidebar.multiselect(
    "Select Destination Pillars:",
    ["Luxury Fashion (Shop)", "Fine Dining (Eat)", "Co-working Hub (Work)", "Family Entertainment (Play)"],
    default=["Luxury Fashion (Shop)", "Fine Dining (Eat)"]
)

st.sidebar.subheader("🚦 External Factors")
traffic_on = st.sidebar.checkbox("Peak Hour Traffic (School Run)", value=False)

st.sidebar.divider()
st.sidebar.caption("Competitor Benchmarks")
sam_q = st.sidebar.slider("Sam Levy's Village", 0, 100, 85)
highland_q = st.sidebar.slider("Highland Park", 0, 100, 75)
arundel_q = st.sidebar.slider("Arundel Village", 0, 100, 60)
groombridge_q = st.sidebar.slider("Groombridge", 0, 100, 50)
n_shoppers = st.sidebar.slider("Simulation Agents", 500, 3000, 1000)

if st.sidebar.button("🔄 Reset Simulator"):
    st.session_state.clear()
    st.rerun()

# --- RUN SIMULATION ---
if st.sidebar.button("▶️ RUN SIMULATION", type="primary"):
    
    # TIME TRAVEL LOGIC
    if current_year < 2028:
        effective_zim_q = 0
        effective_tenants = [] 
    elif current_year == 2028:
        effective_zim_q = zim_base_q + 15
        effective_tenants = moz_tenants
    else:
        effective_zim_q = zim_base_q
        effective_tenants = moz_tenants

    # Run Logic
    model = HarareMarketModel(n_shoppers, sam_q, arundel_q, groombridge_q, highland_q, effective_zim_q, traffic_on, effective_tenants)
    model.step()
    results = model.get_results()
    
    # STATIC FIGURE (For PDF)
    agent_x = [a.pos[0] for a in model.agents]
    agent_y = [a.pos[1] for a in model.agents]
    choices = [a.chosen_mall for a in model.agents]
    point_colors = [COLOR_DICT.get(c, "gray") for c in choices]
    
    fig_static = plt.figure(figsize=(10, 8))
    ax = fig_static.add_subplot(111)
    ax.scatter(agent_x, agent_y, c=point_colors, s=15, alpha=0.6)
    for mall in model.malls:
        ax.scatter(mall["pos"][0], mall["pos"][1], c=COLOR_DICT[mall["name"]], s=400, marker="*", edgecolors="black", zorder=10)
        ax.text(mall["pos"][0], mall["pos"][1]+0.4, mall["name"], ha="center", fontsize=10, fontweight="bold", 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 12); ax.axis("off")
    ax.set_title(f"Year: {current_year} | Status: {'OPEN' if current_year >= 2028 else 'UNDER CONSTRUCTION'}")
    
    # INTERACTIVE MAP (Folium)
    m = folium.Map(location=[-17.76, 31.08], zoom_start=13, tiles="CartoDB positron")
    for mall in model.malls:
        lat, lon = grid_to_gps(mall["pos"][0], mall["pos"][1])
        if mall["name"] == "Mall of Zimbabwe" and current_year < 2028:
            icon_color = "red"; tooltip = "Mall of Zimbabwe (Under Construction)"
        else:
            icon_color = "green" if "Zimbabwe" in mall["name"] else "blue"; tooltip = f"{mall['name']}"
        folium.Marker([lat, lon], tooltip=tooltip, icon=folium.Icon(color=icon_color)).add_to(m)

    display_agents = model.agents[:500] 
    for agent in display_agents:
        lat, lon = grid_to_gps(agent.pos[0], agent.pos[1])
        color = COLOR_DICT.get(agent.chosen_mall, "gray")
        folium.CircleMarker([lat, lon], radius=2, color=color, fill=True, fill_opacity=0.7).add_to(m)

    # Save State
    st.session_state.simulation_results = results
    st.session_state.pdf_fig = fig_static 
    st.session_state.folium_map = m       
    st.session_state.simulation_inputs = {
        "n_shoppers": n_shoppers, "Mall of Zimbabwe": zim_base_q, "Sam Levy's Village": sam_q,
        "traffic": traffic_on, "tenants": moz_tenants, "year": current_year
    }

# --- DISPLAY RESULTS ---
if st.session_state.simulation_results is not None:
    data = st.session_state.simulation_results
    counts = data["counts"]
    revenue = data["revenue"]
    year_display = st.session_state.simulation_inputs['year']
    
    st.subheader(f"📊 Financial & Traffic Forecast: {year_display}")
    
    # METRICS ROW
    cols = st.columns(5)
    malls = ["Mall of Zimbabwe", "Sam Levy's Village", "Highland Park", "Arundel Village", "Groombridge"]
    
    for i, mall in enumerate(malls):
        rev = revenue[mall]
        count = counts[mall]
        share = (count / n_shoppers) * 100
        
        # Format Revenue (Big Number)
        rev_str = f"${rev/1000:.1f}k" if rev > 1000 else f"${rev}"
        
        # Format Share (Small Number)
        share_str = f"{share:.1f}% Share"

        # Display Both
        if mall == "Mall of Zimbabwe":
            # Green arrow for our mall
            cols[i].metric(label=mall, value=rev_str, delta=share_str, delta_color="normal")
        else:
            # Grey arrow for competitors
            cols[i].metric(label=mall, value=rev_str, delta=share_str, delta_color="off")

    st.divider()
    col_map, col_chart = st.columns([2, 1])
    
    with col_map:
        st.subheader(f"📍 Geospatial View ({year_display})")
        st_folium(st.session_state.folium_map, width=700, height=500, returned_objects=[])

    with col_chart:
        tab1, tab2 = st.tabs(["🏆 Visitor Volume", "💰 Estimated Revenue"])
        
        with tab1:
            df_counts = pd.DataFrame(list(counts.items()), columns=["Mall", "Shoppers"]).sort_values("Shoppers", ascending=True)
            fig_bar = plt.figure(figsize=(5, 4))
            ax_bar = fig_bar.add_subplot(111)
            ax_bar.barh(df_counts["Mall"], df_counts["Shoppers"], color=[COLOR_DICT[m] for m in df_counts["Mall"]])
            ax_bar.set_xlabel("Visitor Headcount")
            st.pyplot(fig_bar); plt.close(fig_bar)
            
        with tab2:
            df_rev = pd.DataFrame(list(revenue.items()), columns=["Mall", "Revenue"]).sort_values("Revenue", ascending=True)
            fig_rev = plt.figure(figsize=(5, 4))
            ax_rev = fig_rev.add_subplot(111)
            ax_rev.barh(df_rev["Mall"], df_rev["Revenue"], color=[COLOR_DICT[m] for m in df_rev["Mall"]])
            ax_rev.set_xlabel("Est. Spend ($)")
            st.pyplot(fig_rev); plt.close(fig_rev)
            
    st.divider()
    st.subheader("📑 Export Strategy Report")
    pdf_bytes = create_pdf(
        st.session_state.simulation_results,
        st.session_state.simulation_inputs['n_shoppers'],
        st.session_state.simulation_inputs,
        st.session_state.pdf_fig 
    )
    st.download_button(label="📥 Download Forecast PDF", data=pdf_bytes, file_name=f"Mall_of_Zimbabwe_{year_display}_Report.pdf", mime="application/pdf")