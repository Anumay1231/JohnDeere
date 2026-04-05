"""
app.py — JD Dealership Drag-and-Drop Executive Analytics
"""

import os
import sys
from datetime import datetime, timezone, timedelta
import warnings

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
# plotly.express reserved for future phases

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import (
    load_old_tractor_stock,
    load_dse_master,
)

st.set_page_config(
    page_title="JD Dealership · Inference Dashboard",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root{
  --green:  #367C2B;
  --yellow: #FFDE00;
  --red:    #C8102E;
  --bg0:    #090C11;
  --bg1:    #0F1420;
  --bg2:    #141A28;
  --bg3:    #1A2236;
  --line:   #1F2B3E;
  --text:   #D6E4F7;
  --muted:  #5A7099;
  --dim:    #2E3D55;
  --danger: #FF3D51;
  --warn:   #F5A623;
  --ok:     #23C882;
  --info:   #3B8EF5;
}

html,body,[data-testid="stAppViewContainer"]{
  background:var(--bg0)!important;
  color:var(--text)!important;
  font-family:'DM Sans','Segoe UI',system-ui,sans-serif;
}
[data-testid="stHeader"],[data-testid="stToolbar"]{background:transparent!important;}
.block-container{padding:1.2rem 1.8rem!important;max-width:1700px;}
div[data-testid="stVerticalBlock"]>div{gap:6px;}

.topbar{
  display:flex;align-items:center;justify-content:space-between;
  background:linear-gradient(90deg,#090C11 0%,#0e1620 60%,#061208 100%);
  border:1px solid var(--line);border-bottom:2px solid var(--green);
  border-radius:10px;padding:18px 28px;margin-bottom:20px;
}
.topbar-left h1{
  font-family:'Barlow Condensed','Arial Narrow',Arial,sans-serif;
  font-size:1.9rem;font-weight:800;letter-spacing:.06em;
  color:var(--text);margin:0 0 4px;
}
.topbar-left .sub{
  font-family:'DM Mono','Courier New',monospace;font-size:.62rem;
  color:var(--muted);letter-spacing:.14em;text-transform:uppercase;
}
.topbar-right{text-align:right;}
.topbar-right .ts{
  font-family:'DM Mono','Courier New',monospace;font-size:.6rem;color:var(--muted);
}

.kpi-row{display:flex;gap:14px;margin:16px 0;}
.kpi{
  flex:1;background:var(--bg1);border:1px solid var(--line);
  border-radius:10px;padding:18px 20px;position:relative;overflow:hidden;
}
.kpi::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;}
.kpi.danger::after{background:var(--danger);}
.kpi.warn::after{background:var(--warn);}
.kpi.ok::after{background:var(--ok);}
.kpi.info::after{background:var(--info);}
.kpi.neutral::after{background:var(--muted);}
.kpi .label{
  font-family:'DM Mono','Courier New',monospace;font-size:.6rem;
  color:var(--muted);text-transform:uppercase;letter-spacing:.14em;margin-bottom:8px;
}
.kpi .value{
  font-family:'Barlow Condensed','Arial Narrow',Arial,sans-serif;
  font-size:2rem;font-weight:700;line-height:1;
}
.kpi.danger .value{color:var(--danger);}
.kpi.warn   .value{color:var(--warn);}
.kpi.ok     .value{color:var(--ok);}
.kpi.info   .value{color:var(--info);}
.kpi.neutral .value{color:var(--text);}
.kpi .sub2{font-size:.72rem;color:var(--muted);margin-top:5px;line-height:1.4;}
.kpi .icon{position:absolute;top:14px;right:16px;font-size:1.5rem;opacity:.12;}

.sec{
  font-family:'Barlow Condensed','Arial Narrow',Arial,sans-serif;
  font-size:1.05rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  color:var(--text);border-bottom:1px solid var(--line);
  padding-bottom:9px;margin:26px 0 14px;display:flex;align-items:center;gap:10px;
}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex-shrink:0;}
.dot-r{background:var(--danger);}
.dot-y{background:var(--warn);}
.dot-g{background:var(--ok);}
.dot-b{background:var(--info);}

.ccard{
  background:var(--bg1);border:1px solid var(--line);
  border-radius:10px;padding:18px 18px 10px;margin-bottom:14px;
}
.ccard-t{
  font-family:'DM Mono','Courier New',monospace;font-size:.65rem;
  color:var(--muted);text-transform:uppercase;letter-spacing:.12em;margin-bottom:12px;
}

.stDataFrame{border:1px solid var(--line)!important;border-radius:8px;}

/* ── ALERT BARS ── */
.alert-danger{
  background:rgba(255,61,81,.07);border:1px solid rgba(255,61,81,.25);
  border-left:4px solid var(--danger);border-radius:8px;
  padding:12px 18px;margin:10px 0;font-size:.83rem;
}
.alert-danger b{color:var(--danger);}
.alert-warn{
  background:rgba(245,166,35,.07);border:1px solid rgba(245,166,35,.25);
  border-left:4px solid var(--warn);border-radius:8px;
  padding:12px 18px;margin:10px 0;font-size:.83rem;
}
.alert-warn b{color:var(--warn);}
</style>
""", unsafe_allow_html=True)


def inr(v, short=True):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    v = float(v)
    if short:
        if abs(v) >= 1e7: return f"₹{v/1e7:.2f} Cr"
        if abs(v) >= 1e5: return f"₹{v/1e5:.1f} L"
    return f"₹{v:,.0f}"

CBASE = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, Segoe UI, system-ui, sans-serif", color="#5A7099", size=11),
    margin=dict(l=8, r=8, t=28, b=8),
)
XSTYLE = dict(gridcolor="#1F2B3E", linecolor="#1F2B3E", zerolinecolor="#1F2B3E")
YSTYLE = dict(gridcolor="#1F2B3E", linecolor="#1F2B3E", zerolinecolor="#1F2B3E")

C = dict(
    green="#367C2B", yellow="#FFDE00", red="#C8102E",
    danger="#FF3D51", warn="#F5A623", ok="#23C882", info="#3B8EF5",
    muted="#5A7099", dim="#2E3D55", text="#D6E4F7", bg1="#0F1420",
)

PALETTE = ["#3B8EF5","#F5A623","#23C882","#FF3D51","#FFDE00",
           "#367C2B","#C8102E","#9B59B6","#1ABC9C","#E67E22"]

def kpi(label, value, sub, kind="neutral", icon=""):
    return f'''<div class="kpi {kind}">
  <div class="icon">{icon}</div>
  <div class="label">{label}</div>
  <div class="value">{value}</div>
  <div class="sub2">{sub}</div>
</div>'''

# ──────────────────────────────────────────────────────────────
# DRAG AND DROP UPLOADER
# ──────────────────────────────────────────────────────────────
IST = timezone(timedelta(hours=5, minutes=30))
ts = datetime.now(IST).strftime("%d %b %Y  ·  %H:%M")

st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <h1>🚜 JD Dealership · GM Command Center</h1>
    <div class="sub">Executive Inference Dashboard · Drag & Drop Active</div>
  </div>
  <div class="topbar-right">
    <div class="ts">LAST REFRESHED</div>
    <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;color:#D6E4F7;letter-spacing:.06em;">{ts}</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="sec"><span class="dot dot-b"></span>DATA UPLOAD</div>', unsafe_allow_html=True)

st.info("Drop **OLD_TRACTOR_STOCK.xlsx** and **SALERY_SHEET_FINAL.xlsx** below to generate the inference dashboard.")
uploaded_files = st.file_uploader("Upload Excel Files", accept_multiple_files=True, type=['xlsx'])

if not uploaded_files:
    st.stop()

stock_file = None
salary_file = None
for f in uploaded_files:
    nm = f.name.upper()
    is_stock = ("OLD" in nm or "STOCK" in nm)
    is_salary = ("SALERY" in nm or "SALARY" in nm or "MASTER" in nm)
    
    # Deep inspect via sheet names if filename is ambiguous
    try:
        xl = pd.ExcelFile(f)
        sheets = [s.upper() for s in xl.sheet_names]
        if "NOT ELIGIBLE" in sheets:
            is_stock = True
            is_salary = False
        elif "MASTER" in sheets or any("SALARY" in s for s in sheets):
            is_salary = True
            is_stock = False
        f.seek(0)  # Reset stream after peeking
    except Exception:
        pass
    
    if is_stock:
        stock_file = f
    elif is_salary:
        salary_file = f

if not stock_file or not salary_file:
    st.error("❌ Please upload BOTH the Old Tractor Stock file and the DSE Salary/Master file.")
    st.stop()

def load_uploaded_data(stock_bytes, salary_bytes):
    df_all, df_stock, df_sold = load_old_tractor_stock(stock_bytes)
    dse = load_dse_master(salary_bytes)
    return df_all, df_stock, df_sold, dse

with st.spinner("Analyzing Data..."):
    try:
        df_all, df_stock, df_sold, dse = load_uploaded_data(stock_file, salary_file)
    except Exception as e:
        st.error(f"Error parsing files: {e}")
        st.stop()

# ──────────────────────────────────────────────────────────────
# OVERALL INFERENCE SECTION
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="sec"><span class="dot dot-r"></span>OVERALL INFERENCE — AT A GLANCE</div>', unsafe_allow_html=True)

trapped_capital = df_stock["exchange_price"].sum()
critical_stock = df_stock[df_stock["age_days"] > 365]
cap_critical = critical_stock["exchange_price"].sum()

# Guard against empty sold data
if len(df_sold) > 0:
    avg_buy = df_sold["exchange_price"].mean()
    avg_sold = df_sold["sold_price"].mean()
    avg_loss = df_sold["realized_margin"].dropna().mean() if df_sold["realized_margin"].notna().any() else 0
    pct_loss = (df_sold["realized_margin"].dropna() < 0).mean() * 100 if df_sold["realized_margin"].notna().any() else 0
else:
    avg_buy = avg_sold = avg_loss = 0
    pct_loss = 0

st.markdown(f"""<div class="kpi-row">
  {kpi("Total Trapped Capital", inr(trapped_capital), f"{len(df_stock)} unsold tractors on lot", "warn", "🔒")}
  {kpi("Critical Capital (>1 yr)", inr(cap_critical), f"{len(critical_stock)} tractors rotting on lot", "danger", "⏰")}
  {kpi("Used Sales Economics", f"{pct_loss:.0f}% Loss Rate", f"Avg Loss: {inr(abs(avg_loss))}/tractor", "danger" if avg_loss<0 else "ok", "📉")}
</div>""", unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown('<div class="ccard"><div class="ccard-t">Overall Trapped Capital vs Who is Most Responsible</div>', unsafe_allow_html=True)
    
    dse_vol = dse.groupby("dse_name").size().reset_index(name="Lifetime_Sales")
    dse_stock = df_stock.groupby("dse_name").agg(
        Unsold_Tractors=("sl_no", "count"),
        Trapped_Cap=("exchange_price", "sum"),
        Max_Single_Cap=("exchange_price", "max"),
        Oldest_Tractor=("age_days", "max"),
    ).reset_index()
    dse_critical = critical_stock.groupby("dse_name").agg(
        Critical_Cap=("exchange_price", "sum")
    ).reset_index()
    
    dse_resp = pd.merge(dse_stock, dse_critical, on="dse_name", how="left").fillna(0)
    dse_resp = pd.merge(dse_resp, dse_vol, on="dse_name", how="left").fillna(0)
    # Cast lifetime sales to int (comes as float after fillna)
    dse_resp["Lifetime_Sales"] = dse_resp["Lifetime_Sales"].astype(int)
    dse_resp["Unsold_Tractors"] = dse_resp["Unsold_Tractors"].astype(int)
    dse_resp = dse_resp.sort_values(by="Trapped_Cap", ascending=False)
    
    disp = dse_resp[["dse_name", "Lifetime_Sales", "Unsold_Tractors", "Trapped_Cap", "Critical_Cap", "Max_Single_Cap", "Oldest_Tractor"]].copy()
    disp.columns = ["DSE Name", "Lifetime Sales volume", "Unsold Tractors on lot", "Total Trapped (₹)", "Very Old >1 Yr (₹)", "Largest Single Tractor (₹)", "Oldest Tractor (Days)"]
    
    disp["Total Trapped (₹)"] = disp["Total Trapped (₹)"].apply(lambda x: inr(x, short=False))
    disp["Very Old >1 Yr (₹)"] = disp["Very Old >1 Yr (₹)"].apply(lambda x: inr(x, short=False))
    disp["Largest Single Tractor (₹)"] = disp["Largest Single Tractor (₹)"].apply(lambda x: inr(x, short=False))
    disp["Oldest Tractor (Days)"] = disp["Oldest Tractor (Days)"].apply(lambda x: f"{int(x):,.0f} days" if pd.notna(x) else "—")
    
    st.dataframe(disp, use_container_width=True, hide_index=True)
    st.caption("Context: Expected scaling. Bigger volume sellers naturally hold more stock. Use 'Very Old >1 Yr (₹)' for immediate negligence priority.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="ccard"><div class="ccard-t">Old Tractor Economics — Sold Units</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <ul style="color:#D6E4F7;font-size:0.95rem;line-height:1.8;padding-left:14px;margin-bottom:12px;">
        <li><b>Total Used Tractors Sold:</b> {len(df_sold)}</li>
        <li><b>Average Purchase Price:</b> {inr(avg_buy, short=False)}</li>
        <li><b>Average Sale Price:</b> {inr(avg_sold, short=False)}</li>
        <li style="color:#FF3D51;"><b>Average Net Loss:</b> {inr(abs(avg_loss), short=False)} per unit</li>
    </ul>
    """, unsafe_allow_html=True)
    
    if len(df_sold) > 0 and df_sold["realized_margin"].notna().any():
        worst_sales = df_sold.dropna(subset=["realized_margin"]).sort_values("realized_margin", ascending=True).head(3)
        st.markdown("**Worst Historic Exchanges**")
        for _, row in worst_sales.iterrows():
            st.markdown(f"<div style='font-size:0.82rem;color:#5A7099;border-left:2px solid #FF3D51;padding-left:10px;margin-bottom:8px;'>"
                        f"<b>{row['make']} {row['model']}</b> (Acquired by {row['dse_name']})<br>"
                        f"Bought: {inr(row['exchange_price'])} · Sold: {inr(row['sold_price'])} <br>"
                        f"<strong style='color:#FF3D51'>Loss: {inr(abs(row['realized_margin']))}</strong>"
                        f"</div>", unsafe_allow_html=True)
    else:
        st.caption("No sold tractor data available.")
    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# COLLAPSABLE DATA DROPS
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="sec"><span class="dot dot-y"></span>IN-DEPTH COLLAPSABLE DATA MODE</div>', unsafe_allow_html=True)

with st.expander("📦 Show In-Depth: Trapped Capital Data (Phase 1)"):
    plot_s = df_stock[df_stock["exchange_price"].notna() & df_stock["age_days"].notna()].copy()
    makes = sorted(plot_s["make"].unique())
    make_clr = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(makes)}
    fig = go.Figure()
    for make in makes:
        sub = plot_s[plot_s["make"] == make]
        fig.add_trace(go.Scatter(
            x=sub["age_days"], y=sub["exchange_price"], mode="markers", name=make,
            marker=dict(color=make_clr[make], size=11, opacity=0.85, line=dict(color="#090C11", width=1)),
            hovertemplate="<b>%{customdata[0]}</b><br>Model: %{customdata[1]}<br>Exchange Price: ₹%{y:,.0f}<br>Age: %{x:.0f} days<br>District: %{customdata[2]}<extra></extra>",
            customdata=sub[["owner_name","model","district"]].values,
        ))
    fig.add_vline(x=90,  line=dict(color=C["warn"], width=1.5, dash="dot"), annotation_text="90d", annotation_font_color=C["warn"])
    fig.add_vline(x=365, line=dict(color=C["danger"], width=1.5, dash="dot"), annotation_text="1 Yr", annotation_font_color=C["danger"])
    if len(plot_s):
        fig.add_vrect(x0=365, x1=float(plot_s["age_days"].max())+30, fillcolor="rgba(255,61,81,0.05)", layer="below", line_width=0)
    
    fig.update_layout(**CBASE, xaxis=dict(**XSTYLE, title="Days Since Exchange"), yaxis=dict(**YSTYLE, title="Exchange Price (₹)"), height=380)
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("Expand Table for full list of aging stock...")
    st.dataframe(df_stock[["owner_name","make","model","year_mfg","exchange_date","exchange_price","age_days","dse_name"]], hide_index=True)


with st.expander("👤 Show In-Depth: DSE Composite Scorecard (Phase 2)"):
    meaningful = dse.groupby("dse_name").agg(
        units_sold=("sl_no","count"),
        impl_count=("has_any_implement","sum")
    ).reset_index()
    meaningful["impl_rate"] = meaningful["impl_count"] / meaningful["units_sold"] * 100
    meaningful = meaningful[meaningful["units_sold"] >= 5].sort_values("impl_rate", ascending=False)
    
    col3, col4 = st.columns([1.5, 1])
    with col3:
        fig6 = go.Figure()
        top_n = meaningful.head(15).sort_values("units_sold")
        fig6.add_trace(go.Bar(name="Units Delivered", x=top_n["units_sold"], y=top_n["dse_name"], orientation="h", marker_color=C["info"]))
        fig6.add_trace(go.Bar(name="Implements Upsold", x=top_n["impl_count"], y=top_n["dse_name"], orientation="h", marker_color=C["warn"]))
        fig6.update_layout(**CBASE, barmode="overlay", title="Highest Volume Dealers with Implements Overlay", height=400)
        st.plotly_chart(fig6, use_container_width=True)
    with col4:
        disp2 = meaningful.copy()
        disp2.columns = ["DSE Name", "Units Delivered", "Upsold Implements", "Upsell Rate (%)"]
        disp2["Upsell Rate (%)"] = disp2["Upsell Rate (%)"].round(1)
        st.dataframe(disp2, use_container_width=True, hide_index=True, height=400)


# ══════════════════════════════════════════════════════════════
#  PHASE 3 (SEASONALITY) & PHASE 4 (FINANCIAL RECONCILIATION) 
#  HAVE BEEN DEFERRED / COMMENTED OUT PER INSTRUCTIONS.
#  Will be added when Phase 1 and 2 are 100% satisfactory.
# ══════════════════════════════════════════════════════════════

st.markdown(f"""
<div style="font-family:'DM Mono','Courier New',monospace;font-size:.58rem;color:#2E3D55;
  text-align:right;border-top:1px solid #1F2B3E;padding-top:12px;margin-top:32px;">
  JD DEALERSHIP · CHHATTISGARH · INFERENCE DASHBOARD v2.0 &nbsp;·&nbsp;
  DRAG AND DROP MODE &nbsp;·&nbsp; {ts}
</div>""", unsafe_allow_html=True)
