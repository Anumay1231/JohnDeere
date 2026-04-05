"""
app.py  —  JD Dealership Executive Analytics Dashboard
Phases 1 (Trapped Capital) + 2 (DSE Performance) + 3 (Seasonality)

Run:  streamlit run app.py
Data: place Excel files in  ./data/  folder beside this file
"""

import os
import sys
from datetime import datetime
import warnings

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_loader import (
    load_old_tractor_stock,
    load_dse_master,
    load_billing_summary,
    MONTH_ORDER,
)

# ──────────────────────────────────────────────────────────────
# FILE DISCOVERY  (checks ./data/ → script dir → cwd)
# ──────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))

def _find(filename):
    candidates = [
        os.path.join(_HERE, "data", filename),
        os.path.join(_HERE, filename),
        os.path.join(os.getcwd(), "data", filename),
        os.path.join(os.getcwd(), filename),
        f"/mnt/user-data/uploads/{filename}",   # Claude.ai sandbox
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

DATA_FILES = {
    "stock":    "OLD_TRACTOR_STOCK.xlsx",
    "salary":   "SALERY_SHEET_FINAL.xlsx",
    "billing":  "BILLING.xlsx",
    "billing2": "BILLING_OF_2015.xlsx",
}

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JD Dealership · GM Dashboard",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────
# DESIGN SYSTEM  (fonts bundled via CSS fallbacks — no internet required)
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Google Fonts — loads if online, graceful system-font fallback if offline */
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

/* ── TOPBAR ── */
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
.pill{
  display:inline-block;padding:3px 11px;border-radius:5px;
  font-family:'DM Mono','Courier New',monospace;
  font-size:.65rem;font-weight:500;letter-spacing:.1em;margin-right:6px;
}
.pill-jd{background:var(--yellow);color:var(--green);}
.pill-mm{background:var(--red);color:#fff;}
.pill-phase{border:1px solid var(--line);color:var(--muted);}
.topbar-right{text-align:right;}
.topbar-right .ts{
  font-family:'DM Mono','Courier New',monospace;font-size:.6rem;color:var(--muted);
}

/* ── KPI CARDS ── */
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

/* ── SECTION HEADS ── */
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

/* ── CHART CARD ── */
.ccard{
  background:var(--bg1);border:1px solid var(--line);
  border-radius:10px;padding:18px 18px 10px;margin-bottom:14px;
}
.ccard-t{
  font-family:'DM Mono','Courier New',monospace;font-size:.65rem;
  color:var(--muted);text-transform:uppercase;letter-spacing:.12em;margin-bottom:12px;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{
  background:var(--bg1);border-radius:8px;padding:4px;
  gap:4px;border:1px solid var(--line);
}
.stTabs [data-baseweb="tab"]{
  font-family:'DM Mono','Courier New',monospace;font-size:.68rem;
  letter-spacing:.1em;text-transform:uppercase;
  color:var(--muted)!important;background:transparent!important;border-radius:6px!important;
}
.stTabs [aria-selected="true"]{
  color:var(--text)!important;background:var(--bg2)!important;
}

/* ── CONTROLS ── */
.stSelectbox label,.stSlider label,.stMultiSelect label{
  font-family:'DM Mono','Courier New',monospace;
  font-size:.62rem!important;text-transform:uppercase;
  letter-spacing:.1em;color:var(--muted)!important;
}

/* ── TABLE ── */
.stDataFrame{border:1px solid var(--line)!important;border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
def inr(v, short=True):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    v = float(v)
    if short:
        if abs(v) >= 1e7: return f"₹{v/1e7:.2f} Cr"
        if abs(v) >= 1e5: return f"₹{v/1e5:.1f} L"
    return f"₹{v:,.0f}"

CBASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
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
    return f"""<div class="kpi {kind}">
  <div class="icon">{icon}</div>
  <div class="label">{label}</div>
  <div class="value">{value}</div>
  <div class="sub2">{sub}</div>
</div>"""

# ──────────────────────────────────────────────────────────────
# FILE VALIDATION & LOAD
# ──────────────────────────────────────────────────────────────
paths = {k: _find(v) for k, v in DATA_FILES.items()}
missing = [DATA_FILES[k] for k, v in paths.items() if v is None]

if missing:
    st.error(f"### ❌ Missing data files\n\nCannot find: **{', '.join(missing)}**\n\n"
             f"Place all 4 Excel files inside a `data/` folder next to `app.py`:\n\n"
             f"```\ndashboard/\n├── app.py\n├── data_loader.py\n└── data/\n"
             f"    ├── OLD_TRACTOR_STOCK.xlsx\n    ├── SALERY_SHEET_FINAL.xlsx\n"
             f"    ├── BILLING.xlsx\n    └── BILLING_OF_2015.xlsx\n```")
    st.stop()

@st.cache_data(show_spinner=False)
def get_all_data(stock_path, salary_path, billing_path, billing2_path):
    df_all, df_stock, df_sold = load_old_tractor_stock(stock_path)
    dse = load_dse_master(salary_path)
    ann, bp, dp, recent = load_billing_summary(billing_path, billing2_path)
    return df_all, df_stock, df_sold, dse, ann, bp, dp, recent

with st.spinner("Loading dealership data…"):
    df_all, df_stock, df_sold, dse, ann, bp, dp, recent = get_all_data(
        paths["stock"], paths["salary"], paths["billing"], paths["billing2"]
    )

# ──────────────────────────────────────────────────────────────
# TOP BAR
# ──────────────────────────────────────────────────────────────
ts = datetime.now().strftime("%d %b %Y  ·  %H:%M")

st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <h1>🚜 JD Dealership · GM Command Center</h1>
    <div class="sub">Chhattisgarh Operations · Bilaspur · Janjgir · Mungeli · GPM · Kota</div>
    <div style="margin-top:10px;">
      <span class="pill pill-jd">JOHN DEERE</span>
      <span class="pill pill-mm">MAHINDRA</span>
      <span class="pill pill-phase">PHASE 1: OLD STOCK</span>
      <span class="pill pill-phase">PHASE 2: DSE PERF.</span>
      <span class="pill pill-phase">PHASE 3: SEASONALITY</span>
    </div>
  </div>
  <div class="topbar-right">
    <div class="ts">LAST REFRESHED</div>
    <div style="font-family:'Barlow Condensed','Arial Narrow',Arial,sans-serif;font-size:1.1rem;color:#D6E4F7;letter-spacing:.06em;">{ts}</div>
    <div class="ts" style="margin-top:4px;">DATA: 2013 – 2026 · {len(df_all)+len(dse):,} RECORDS</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📦  Phase 1 · Trapped Capital",
    "👤  Phase 2 · DSE Performance",
    "📈  Phase 3 · Seasonality",
])


# ══════════════════════════════════════════════════════════════
#  PHASE 1 — TRAPPED CAPITAL
# ══════════════════════════════════════════════════════════════
with tab1:

    trapped_capital  = df_stock["exchange_price"].sum()
    n_stock          = len(df_stock)
    critical_stock   = df_stock[df_stock["age_days"] > 365]
    n_critical       = len(critical_stock)
    cap_critical     = critical_stock["exchange_price"].sum()
    avg_margin_sold  = df_sold["realized_margin"].mean()
    pct_loss         = (df_sold["realized_margin"] < 0).mean() * 100
    avg_hold_days    = df_sold["holding_period"].dropna().mean()
    n_sold_total     = len(df_sold)

    # ── EXCEPTION ALERTS ──────────────────────────────────────
    st.markdown('<div class="sec"><span class="dot dot-r"></span>EXCEPTION FLAGS — ACT ON THESE TODAY</div>',
                unsafe_allow_html=True)

    if n_critical > 0:
        st.markdown(f"""<div class="alert-danger">
          🚨 <b>{n_critical} tractors sitting &gt;1 year</b> —
          locking {inr(cap_critical)} in depreciating capital.
          These are your highest-priority disposals.
        </div>""", unsafe_allow_html=True)

    if avg_margin_sold < 0:
        st.markdown(f"""<div class="alert-danger">
          📉 <b>Average sold margin is NEGATIVE ({inr(avg_margin_sold)})</b> —
          {pct_loss:.0f}% of old tractors are sold below acquisition cost.
        </div>""", unsafe_allow_html=True)

    if trapped_capital > 2_500_000:
        st.markdown(f"""<div class="alert-warn">
          ⚠️ <b>Total trapped capital: {inr(trapped_capital)}</b> across
          {n_stock} unsold tractors. Target liquidating 30% this quarter.
        </div>""", unsafe_allow_html=True)

    # ── KPI ROW ────────────────────────────────────────────────
    hold_str = f"{avg_hold_days:.0f}d" if not np.isnan(avg_hold_days) else "—"
    st.markdown(f"""<div class="kpi-row">
      {kpi("Total Trapped Capital", inr(trapped_capital), f"{n_stock} unsold tractors on lot", "danger", "🔒")}
      {kpi("Critical Aged (>1 yr)", str(n_critical), f"{inr(cap_critical)} locked >365 days", "danger", "⏰")}
      {kpi("Avg Realized Margin", inr(avg_margin_sold), f"{pct_loss:.0f}% of sales at a loss", "warn" if avg_margin_sold < 0 else "ok", "📊")}
      {kpi("Avg Days to Sell", hold_str, f"Across {n_sold_total:,} sold units", "info", "📅")}
    </div>""", unsafe_allow_html=True)

    # ── ROW 1: AGING SCATTER + DISTRICT BAR ───────────────────
    col_a, col_b = st.columns([1.5, 1])

    with col_a:
        st.markdown('<div class="ccard"><div class="ccard-t">Aging Analysis — Every Unsold Tractor (x=days idle, y=capital at risk)</div>', unsafe_allow_html=True)
        plot_s = df_stock[df_stock["exchange_price"].notna() & df_stock["age_days"].notna()].copy()
        makes = sorted(plot_s["make"].unique())
        make_clr = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(makes)}

        fig = go.Figure()
        for make in makes:
            sub = plot_s[plot_s["make"] == make]
            fig.add_trace(go.Scatter(
                x=sub["age_days"], y=sub["exchange_price"],
                mode="markers", name=make,
                marker=dict(color=make_clr[make], size=11, opacity=0.85,
                            line=dict(color="#090C11", width=1)),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>Model: %{customdata[1]}<br>"
                    "Exchange Price: ₹%{y:,.0f}<br>Age: %{x:.0f} days<br>"
                    "District: %{customdata[2]}<extra></extra>"
                ),
                customdata=sub[["owner_name","model","district"]].values,
            ))
        fig.add_vline(x=90,  line=dict(color=C["warn"],   width=1.5, dash="dot"),
                      annotation_text="90d",    annotation_font_color=C["warn"],   annotation_font_size=10)
        fig.add_vline(x=365, line=dict(color=C["danger"], width=1.5, dash="dot"),
                      annotation_text="1 Year", annotation_font_color=C["danger"], annotation_font_size=10)
        if len(plot_s):
            fig.add_vrect(x0=365, x1=float(plot_s["age_days"].max())+30,
                          fillcolor="rgba(255,61,81,0.05)", layer="below", line_width=0)
        fig.update_layout(**CBASE,
            xaxis=dict(**XSTYLE, title="Days Since Exchange"),
            yaxis=dict(**YSTYLE, title="Exchange Price (₹)", tickformat=",.0f"),
            legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                        yanchor="bottom", y=1.02, xanchor="left", x=0),
            height=380)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="ccard"><div class="ccard-t">Trapped Capital by District</div>', unsafe_allow_html=True)
        dist_cap = (df_stock.groupby("district")
                    .agg(capital=("exchange_price","sum"), count=("exchange_price","count"))
                    .reset_index().sort_values("capital", ascending=True))

        fig2 = go.Figure(go.Bar(
            x=dist_cap["capital"], y=dist_cap["district"], orientation="h",
            marker=dict(color=dist_cap["capital"],
                        colorscale=[[0,"#1F2B3E"],[0.5,C["warn"]],[1.0,C["danger"]]],
                        showscale=False),
            text=[f"{inr(v)}  ({c})" for v, c in zip(dist_cap["capital"], dist_cap["count"])],
            textposition="outside", textfont=dict(size=10, color=C["text"]),
            hovertemplate="<b>%{y}</b><br>Capital: ₹%{x:,.0f}<extra></extra>",
        ))
        fig2.update_layout(**CBASE,
            xaxis=dict(**XSTYLE, tickformat=",.0f", showticklabels=False),
            yaxis=dict(**YSTYLE),
            height=380, margin=dict(l=8, r=120, t=28, b=8))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── ROW 2: MARGIN HISTOGRAM + FILTERABLE TABLE ─────────────
    col_c, col_d = st.columns([1, 1.5])

    with col_c:
        st.markdown('<div class="ccard"><div class="ccard-t">Sold Units — Realized Margin Distribution</div>', unsafe_allow_html=True)
        sold_m = df_sold[df_sold["realized_margin"].notna() & df_sold["exchange_price"].notna()].copy()
        fig3 = go.Figure(go.Histogram(
            x=sold_m["realized_margin"] / 1000, nbinsx=40,
            marker=dict(
                color=sold_m["realized_margin"].apply(
                    lambda v: "rgba(255,61,81,0.7)" if v < 0 else "rgba(35,200,130,0.7)"),
                line=dict(color="#090C11", width=0.5)),
            hovertemplate="Margin ₹%{x:.0f}K · %{y} tractors<extra></extra>",
        ))
        fig3.add_vline(x=0, line=dict(color=C["warn"], width=2),
                       annotation_text="Break-Even", annotation_font_color=C["warn"])
        fig3.update_layout(**CBASE,
            xaxis=dict(**XSTYLE, title="Realized Margin (₹ Thousands)"),
            yaxis=dict(**YSTYLE, title="# Tractors"),
            height=300)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="sec" style="margin-top:0;"><span class="dot dot-r"></span>CURRENT STOCK — FULL DETAIL</div>',
                    unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1:
            dist_opts = ["All"] + sorted(df_stock["district"].dropna().unique().tolist())
            f_dist = st.selectbox("District", dist_opts, key="p1_dist")
        with f2:
            make_opts = ["All"] + sorted(df_stock["make"].dropna().unique().tolist())
            f_make = st.selectbox("Make", make_opts, key="p1_make")
        with f3:
            age_opts = ["All", "> 1 Year 🚨", "> 6 Months", "> 90 Days"]
            f_age = st.selectbox("Age Filter", age_opts, key="p1_age")

        tbl = df_stock.copy()
        if f_dist != "All": tbl = tbl[tbl["district"] == f_dist]
        if f_make != "All": tbl = tbl[tbl["make"] == f_make]
        if f_age == "> 1 Year 🚨":  tbl = tbl[tbl["age_days"] > 365]
        elif f_age == "> 6 Months": tbl = tbl[tbl["age_days"] > 180]
        elif f_age == "> 90 Days":  tbl = tbl[tbl["age_days"] > 90]

        disp = tbl[["owner_name","make","model","year_mfg","exchange_price",
                     "sold_price_raw","age_days","district","dse_name"]].copy()
        disp.columns = ["Owner","Make","Model","Yr Mfg","Exch Price","Asking","Age (Days)","District","DSE"]
        disp["Exch Price"] = disp["Exch Price"].apply(lambda v: inr(v, short=False))
        disp["Age (Days)"] = disp["Age (Days)"].apply(
            lambda v: f"🔴 {int(v)}" if v > 365 else (f"🟡 {int(v)}" if v > 90 else f"🟢 {int(v)}")
            if pd.notna(v) else "—")
        st.dataframe(disp, use_container_width=True, height=280, hide_index=True)
        st.caption(f"Showing {len(tbl)} of {n_stock} · Total: {inr(tbl['exchange_price'].sum())}")

    # ── ROW 3: BRAND PERF + VOLUME BY YEAR ────────────────────
    st.markdown('<div class="sec"><span class="dot dot-y"></span>BRAND PERFORMANCE — SOLD UNITS</div>',
                unsafe_allow_html=True)
    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown('<div class="ccard"><div class="ccard-t">Avg Margin by Make (min 3 sales)</div>', unsafe_allow_html=True)
        make_perf = (df_sold[df_sold["realized_margin"].notna()]
                     .groupby("make")
                     .agg(avg_margin=("realized_margin","mean"), count=("realized_margin","count"))
                     .reset_index().query("count >= 3").sort_values("avg_margin"))
        fig4 = go.Figure(go.Bar(
            x=make_perf["avg_margin"], y=make_perf["make"], orientation="h",
            marker_color=make_perf["avg_margin"].apply(
                lambda v: "rgba(255,61,81,0.7)" if v < 0 else "rgba(35,200,130,0.7)"),
            text=[f"₹{v/1000:.0f}K  (n={c})"
                  for v, c in zip(make_perf["avg_margin"], make_perf["count"])],
            textposition="outside", textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>Avg Margin: ₹%{x:,.0f}<extra></extra>",
        ))
        fig4.add_vline(x=0, line=dict(color=C["warn"], width=2))
        fig4.update_layout(**CBASE,
            xaxis=dict(**XSTYLE, tickformat=",.0f"),
            yaxis=dict(**YSTYLE),
            height=300, margin=dict(l=8, r=120, t=28, b=8))
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_f:
        st.markdown('<div class="ccard"><div class="ccard-t">Exchange Volume by Year & Status</div>', unsafe_allow_html=True)
        yr_vol = (df_all.dropna(subset=["year_exchanged"])
                  .groupby(["year_exchanged","status"]).size().reset_index(name="count"))
        fig5 = px.bar(yr_vol, x="year_exchanged", y="count", color="status",
                      color_discrete_map={"SOLD": C["ok"], "STOCK": C["danger"]},
                      barmode="stack",
                      labels={"year_exchanged":"Year","count":"Tractors","status":"Status"})
        fig5.update_layout(**CBASE,
            xaxis=dict(**XSTYLE, type="category"),
            yaxis=dict(**YSTYLE),
            legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                        yanchor="bottom", y=1.02, xanchor="left", x=0),
            height=300)
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  PHASE 2 — DSE PERFORMANCE
# ══════════════════════════════════════════════════════════════
with tab2:

    all_years = sorted(dse["year"].dropna().unique().astype(int).tolist())
    col_yr1, col_yr2, _ = st.columns([1, 1, 4])
    with col_yr1:
        yr_start = st.selectbox("From Year", all_years, index=0, key="dse_yr1")
    with col_yr2:
        yr_end = st.selectbox("To Year", all_years, index=len(all_years)-1, key="dse_yr2")

    d = dse[(dse["year"] >= yr_start) & (dse["year"] <= yr_end)].copy()

    dse_agg = (d.groupby("dse_name").agg(
        units_sold     =("sl_no","count"),
        impl_count     =("has_any_implement","sum"),
        rotavator_cnt  =("rotavator","sum"),
        trolley_cnt    =("trolley","sum"),
        cage_wheel_cnt =("cage_wheel","sum"),
        cultivator_cnt =("cultivator","sum"),
        high_margin_cnt=("high_margin_impl","sum"),
        total_value    =("unit_value","sum"),
    ).reset_index())

    dse_agg["impl_rate"]  = dse_agg["impl_count"] / dse_agg["units_sold"] * 100
    dse_agg["hm_rate"]    = dse_agg["high_margin_cnt"] / dse_agg["units_sold"] * 100
    dse_agg["avg_val"]    = dse_agg["total_value"] / dse_agg["units_sold"]
    dse_agg["score_vol"]  = dse_agg["units_sold"] / dse_agg["units_sold"].max()
    dse_agg["score_impl"] = dse_agg["impl_rate"] / dse_agg["impl_rate"].max()
    dse_agg["composite"]  = (dse_agg["score_vol"] * 60 + dse_agg["score_impl"] * 40).round(1)
    dse_agg = dse_agg.sort_values("composite", ascending=False)
    meaningful = dse_agg[dse_agg["units_sold"] >= 5].copy()

    top_dse         = meaningful.iloc[0]["dse_name"] if len(meaningful) else "—"
    top_units       = int(meaningful.iloc[0]["units_sold"]) if len(meaningful) else 0
    impl_rate_total = d["has_any_implement"].mean() * 100
    rot_rate_total  = d["has_rotavator"].mean() * 100
    troll_rate_total= d["has_trolley"].mean() * 100

    st.markdown(f"""<div class="kpi-row">
      {kpi("Top DSE (Composite)", top_dse, f"{top_units} units · {yr_start}–{yr_end}", "ok", "🏆")}
      {kpi("Total Deliveries", f"{len(d):,}", f"{yr_start} – {yr_end}", "info", "🚜")}
      {kpi("Implement Upsell Rate", f"{impl_rate_total:.1f}%", "% customers with ≥1 implement", "warn", "🔧")}
      {kpi("Rotavator Attach Rate", f"{rot_rate_total:.1f}%", f"Trolley: {troll_rate_total:.1f}%", "neutral", "⚙️")}
    </div>""", unsafe_allow_html=True)

    col_g, col_h = st.columns([1.4, 1])

    with col_g:
        st.markdown('<div class="ccard"><div class="ccard-t">DSE Composite Leaderboard — Volume (blue) + Implements Upsold (orange)</div>', unsafe_allow_html=True)
        top_n = meaningful.head(15).sort_values("composite")
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            name="Units Sold", x=top_n["units_sold"], y=top_n["dse_name"],
            orientation="h",
            marker=dict(color=C["info"], opacity=0.85, line=dict(color="#090C11", width=0.5)),
            hovertemplate="<b>%{y}</b><br>Units: %{x}<extra></extra>",
        ))
        fig6.add_trace(go.Bar(
            name="Implements Upsold", x=top_n["impl_count"], y=top_n["dse_name"],
            orientation="h",
            marker=dict(color=C["warn"], opacity=0.85, line=dict(color="#090C11", width=0.5)),
            hovertemplate="<b>%{y}</b><br>Implements: %{x}<extra></extra>",
        ))
        for _, row in top_n.iterrows():
            fig6.add_annotation(
                x=row["units_sold"]+2, y=row["dse_name"],
                text=f"  Score: {row['composite']:.0f}",
                showarrow=False, font=dict(size=9, color=C["muted"]), xanchor="left")
        fig6.update_layout(**CBASE,
            barmode="overlay",
            xaxis=dict(**XSTYLE, title="Count"),
            yaxis=dict(**YSTYLE),
            legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                        yanchor="bottom", y=1.02, x=0),
            height=430)
        st.plotly_chart(fig6, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_h:
        st.markdown('<div class="ccard"><div class="ccard-t">Volume vs Upsell Rate · Bubble = Revenue Generated</div>', unsafe_allow_html=True)
        bub = meaningful[meaningful["avg_val"].notna() & (meaningful["avg_val"] > 0)].copy()
        fig7 = go.Figure(go.Scatter(
            x=bub["units_sold"], y=bub["impl_rate"],
            mode="markers+text",
            text=bub["dse_name"].str.split().str[0],
            textposition="top center",
            textfont=dict(size=9, color=C["text"]),
            marker=dict(
                size=(bub["total_value"] / bub["total_value"].max() * 45 + 10),
                color=bub["composite"],
                colorscale=[[0,"#1F2B3E"],[0.5,C["warn"]],[1,C["ok"]]],
                showscale=True,
                colorbar=dict(title="Score", thickness=10, len=0.6,
                              tickfont=dict(size=9, color=C["muted"])),
                line=dict(color="#090C11", width=1), opacity=0.85),
            hovertemplate="<b>%{text}</b><br>Units: %{x}<br>Impl Rate: %{y:.1f}%<extra></extra>",
        ))
        med_x = bub["units_sold"].median()
        med_y = bub["impl_rate"].median()
        fig7.add_vline(x=med_x, line=dict(color=C["dim"], width=1, dash="dot"))
        fig7.add_hline(y=med_y, line=dict(color=C["dim"], width=1, dash="dot"))
        fig7.add_annotation(x=bub["units_sold"].max()*0.95, y=bub["impl_rate"].max()*0.95,
                             text="★ Stars", showarrow=False, font=dict(size=9, color=C["ok"]))
        fig7.add_annotation(x=bub["units_sold"].max()*0.95, y=0,
                             text="Volume only", showarrow=False, font=dict(size=9, color=C["warn"]))
        fig7.update_layout(**CBASE,
            xaxis=dict(**XSTYLE, title="Units Sold"),
            yaxis=dict(**YSTYLE, title="Implement Upsell Rate (%)"),
            height=430)
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col_i, col_j = st.columns(2)

    with col_i:
        st.markdown('<div class="ccard"><div class="ccard-t">Implement Mix — What Gets Attached</div>', unsafe_allow_html=True)
        impl_totals = {
            "Rotavator":    int(d["rotavator"].sum()),
            "Cage Wheel":   int(d["cage_wheel"].sum()),
            "Trolley":      int(d["trolley"].sum()),
            "Cultivator":   int(d["cultivator"].sum()),
            "Koper Datari": int(d["koper_datari"].sum()),
            "Leveller":     int(d["leveller"].sum()),
            "Plough":       int(d["plough"].sum()),
            "Others":       int(d["others_impl"].sum()),
        }
        impl_df = (pd.DataFrame(list(impl_totals.items()), columns=["impl","count"])
                   .query("count > 0").sort_values("count", ascending=True))
        fig8 = go.Figure(go.Bar(
            x=impl_df["count"], y=impl_df["impl"], orientation="h",
            marker=dict(color=impl_df["count"],
                        colorscale=[[0,"#1F2B3E"],[1,C["warn"]]], showscale=False),
            text=impl_df["count"], textposition="outside", textfont=dict(size=11),
            hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>",
        ))
        fig8.update_layout(**CBASE,
            xaxis=dict(**XSTYLE, showticklabels=False),
            yaxis=dict(**YSTYLE),
            height=320, margin=dict(r=50))
        st.plotly_chart(fig8, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_j:
        st.markdown('<div class="ccard"><div class="ccard-t">District × Implement Upsell Rate</div>', unsafe_allow_html=True)
        dist_impl = (d.groupby("district").agg(
            units=("sl_no","count"),
            impl_rate=("has_any_implement","mean"),
            rot_rate=("rotavator","mean"),
        ).reset_index())
        dist_impl = dist_impl[dist_impl["units"] >= 10].copy()
        dist_impl["impl_pct"] = (dist_impl["impl_rate"] * 100).round(1)
        dist_impl["rot_pct"]  = (dist_impl["rot_rate"] * 100).round(1)
        dist_impl = dist_impl.sort_values("impl_pct", ascending=False)
        fig9 = go.Figure()
        fig9.add_trace(go.Bar(name="Any Implement",
            x=dist_impl["district"], y=dist_impl["impl_pct"],
            marker_color="rgba(59,142,245,0.7)",
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
        fig9.add_trace(go.Bar(name="Rotavator",
            x=dist_impl["district"], y=dist_impl["rot_pct"],
            marker_color="rgba(245,166,35,0.8)",
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
        fig9.update_layout(**CBASE,
            barmode="group",
            xaxis=dict(**XSTYLE),
            yaxis=dict(**YSTYLE, title="Upsell Rate (%)"),
            legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                        yanchor="bottom", y=1.02, x=0),
            height=320)
        st.plotly_chart(fig9, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sec"><span class="dot dot-b"></span>DSE SCORECARD — FULL BREAKDOWN</div>',
                unsafe_allow_html=True)
    dse_display = meaningful[["dse_name","units_sold","impl_count","impl_rate",
                               "rotavator_cnt","trolley_cnt","cage_wheel_cnt","composite"]].copy()
    dse_display.columns = ["DSE","Units","Implements","Impl Rate %",
                            "Rotavators","Trolleys","Cage Wheels","Score"]
    dse_display["Impl Rate %"] = dse_display["Impl Rate %"].round(1)
    dse_display["Score"]       = dse_display["Score"].round(0).astype(int)
    st.dataframe(dse_display.sort_values("Score", ascending=False),
                 use_container_width=True, height=300, hide_index=True)

    st.markdown('<div class="ccard"><div class="ccard-t">Top 8 DSE — Year-over-Year Unit Sales (2018–2026)</div>', unsafe_allow_html=True)
    top8 = meaningful.head(8)["dse_name"].tolist()
    yoy  = (dse[dse["dse_name"].isin(top8)]
            .groupby(["dse_name","year"]).size().reset_index(name="units"))
    yoy  = yoy[yoy["year"].between(2018, 2026)]
    fig10 = px.line(yoy, x="year", y="units", color="dse_name", markers=True,
                    color_discrete_sequence=PALETTE,
                    labels={"year":"Year","units":"Units Sold","dse_name":"DSE"})
    fig10.update_layout(**CBASE,
        xaxis=dict(**XSTYLE, dtick=1),
        yaxis=dict(**YSTYLE),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                    yanchor="bottom", y=1.02, x=0),
        height=300)
    st.plotly_chart(fig10, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  PHASE 3 — SEASONALITY
# ══════════════════════════════════════════════════════════════
with tab3:

    st.markdown("""<div class="alert-warn">
      ⚠️ <b>Directional Only:</b> Seasonality is based on units billed JD→Dealer (procurement),
      not retail sales. Use for trend direction and seasonal planning — not financial forecasting.
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec"><span class="dot dot-g"></span>ANNUAL BILLING & DELIVERY — 2013 → 2026</div>',
                unsafe_allow_html=True)

    ann_plot = ann.copy()
    ann_plot["partial"] = ann_plot["year"] == 2026

    st.markdown('<div class="ccard"><div class="ccard-t">Units Billed (JD→Dealer) vs Delivered (Dealer→Customer) · 2026 is partial YTD</div>', unsafe_allow_html=True)
    fig11 = go.Figure()
    fig11.add_trace(go.Bar(
        name="Billed (JD→Dealer)", x=ann_plot["year"], y=ann_plot["billing"],
        marker=dict(color=ann_plot["partial"].map({False:"rgba(59,142,245,0.7)",True:"rgba(59,142,245,0.3)"}),
                    line=dict(color="#090C11", width=0.5)),
        hovertemplate="<b>%{x}</b><br>Billed: %{y}<extra></extra>"))
    fig11.add_trace(go.Bar(
        name="Delivered (Dealer→Customer)", x=ann_plot["year"], y=ann_plot["delivery"],
        marker=dict(color=ann_plot["partial"].map({False:"rgba(35,200,130,0.7)",True:"rgba(35,200,130,0.3)"}),
                    line=dict(color="#090C11", width=0.5)),
        hovertemplate="<b>%{x}</b><br>Delivered: %{y}<extra></extra>"))
    fig11.add_trace(go.Scatter(
        name="Billing Trend", x=ann_plot["year"], y=ann_plot["billing"],
        mode="lines", line=dict(color=C["info"], width=2, dash="dot"), showlegend=False))
    ytd_row = ann_plot[ann_plot["year"] == 2026]
    if len(ytd_row):
        fig11.add_annotation(x=2026, y=float(ytd_row["billing"].values[0]) + 10,
                              text="YTD", font=dict(size=9, color=C["warn"]), showarrow=False)
    fig11.update_layout(**CBASE,
        barmode="group",
        xaxis=dict(**XSTYLE, dtick=1, tickangle=-30),
        yaxis=dict(**YSTYLE, title="Units"),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                    yanchor="bottom", y=1.02, x=0),
        height=320)
    st.plotly_chart(fig11, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sec"><span class="dot dot-y"></span>HARVEST SEASON FINGERPRINT</div>',
                unsafe_allow_html=True)
    col_k, col_l = st.columns(2)
    MONTH_DISPLAY = ["NOV","DEC","JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT"]

    with col_k:
        st.markdown('<div class="ccard"><div class="ccard-t">Billing Heatmap — Units per Month per Year</div>', unsafe_allow_html=True)
        bp2      = bp.set_index("month").reindex(MONTH_DISPLAY)
        yr_cols  = [c for c in bp2.columns if isinstance(c, int) and c >= 2017]
        hdata    = bp2[yr_cols].values.astype(float)

        fig12 = go.Figure(go.Heatmap(
            z=hdata, x=[str(y) for y in yr_cols], y=MONTH_DISPLAY,
            colorscale=[[0,"#0F1420"],[0.3,"#1a3a5c"],[0.6,C["warn"]],[1.0,C["danger"]]],
            text=[[f"{v:.0f}" if not np.isnan(v) else "" for v in row] for row in hdata],
            texttemplate="%{text}", textfont=dict(size=10),
            hovertemplate="<b>%{y} %{x}</b><br>Units: %{z}<extra></extra>",
            colorbar=dict(thickness=10, len=0.8, tickfont=dict(size=9, color=C["muted"])),
        ))
        for shape_y0, shape_y1, clr in [(6.5, 9.5, C["ok"]), (-0.5, 1.5, C["warn"])]:
            fig12.add_shape(type="rect", x0=-0.5, x1=len(yr_cols)-0.5,
                            y0=shape_y0, y1=shape_y1,
                            line=dict(color=clr, width=1.5, dash="dot"),
                            fillcolor=f"rgba({','.join(str(int(int(clr[1:3],16))) for _ in range(1)) + '0,0,0'}.04)",
                            layer="above")
        fig12.update_layout(**CBASE, xaxis=dict(side="top"), height=360, margin=dict(t=40, b=8))
        st.plotly_chart(fig12, use_container_width=True)
        st.caption("🟡 Rabi prep (Nov–Dec)  ·  🟢 Kharif prep (Jun–Sep)")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_l:
        st.markdown('<div class="ccard"><div class="ccard-t">Seasonality Index — Avg 2017–2025 (100 = average month)</div>', unsafe_allow_html=True)
        hist_yrs    = [c for c in bp2.columns if isinstance(c, int) and 2017 <= c <= 2025]
        monthly_avg = bp2[hist_yrs].mean(axis=1).reindex(MONTH_DISPLAY)
        season_idx  = (monthly_avg / monthly_avg.mean() * 100).fillna(0)

        s_colors = ["rgba(255,61,81,0.8)" if v >= 130 else
                    "rgba(245,166,35,0.8)" if v >= 110 else
                    "rgba(59,142,245,0.7)" for v in season_idx.values]
        fig13 = go.Figure(go.Bar(
            x=season_idx.index, y=season_idx.values,
            marker=dict(color=s_colors, line=dict(color="#090C11", width=0.5)),
            text=[f"{v:.0f}" for v in season_idx.values],
            textposition="outside", textfont=dict(size=10),
            hovertemplate="<b>%{x}</b><br>Index: %{y:.0f}<extra></extra>",
        ))
        fig13.add_hline(y=100, line=dict(color=C["muted"], width=1.5, dash="dot"),
                        annotation_text="Avg = 100", annotation_font_color=C["muted"])
        fig13.update_layout(**CBASE,
            xaxis=dict(**XSTYLE, categoryorder="array", categoryarray=MONTH_DISPLAY),
            yaxis=dict(**YSTYLE, title="Index"),
            height=360)
        st.plotly_chart(fig13, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── 2025-26 RUN RATE ───────────────────────────────────────
    st.markdown('<div class="sec"><span class="dot dot-b"></span>2025-26 SEASON · RUN-RATE CHECK</div>',
                unsafe_allow_html=True)
    col_m, col_n = st.columns([1, 1.5])

    with col_m:
        b25 = float(ann[ann["year"]==2025]["billing"].values[0]) if len(ann[ann["year"]==2025]) else 0
        b26 = float(ann[ann["year"]==2026]["billing"].values[0]) if len(ann[ann["year"]==2026]) else 0
        b24 = float(ann[ann["year"]==2024]["billing"].values[0]) if len(ann[ann["year"]==2024]) else 0
        ytd_units   = int(b26)
        months_done = 4  # Nov, Dec, Jan, Feb
        projected   = round(ytd_units / months_done * 12)
        vs_2025     = ((projected - b25) / b25 * 100) if b25 else 0
        pace_kind   = "ok" if projected >= b25 else "danger"

        st.markdown(f"""<div class="kpi-row" style="flex-direction:column;gap:10px;">
          {kpi("YTD Units (Nov–Feb)", str(ytd_units), "4 months of fiscal year done", "info", "📦")}
          {kpi("Projected Full Year", f"~{projected}", f"If pace holds · vs 2025: {vs_2025:+.0f}%", pace_kind, "🎯")}
          {kpi("2025 Full Year", str(int(b25)), "Billing units (JD→Dealer)", "neutral", "📋")}
          {kpi("2024 Full Year", str(int(b24)), "Best year on record", "neutral", "📋")}
        </div>""", unsafe_allow_html=True)

        if projected < b25:
            st.markdown(f"""<div class="alert-danger">
              📉 <b>Pace is below 2025.</b> Trajectory ~{projected} units vs {int(b25)} last year
              ({abs(vs_2025):.0f}% behind). Jun–Sep Kharif push is critical.
            </div>""", unsafe_allow_html=True)

    with col_n:
        st.markdown('<div class="ccard"><div class="ccard-t">2025-26 Actual Deliveries by Month</div>', unsafe_allow_html=True)
        mc = (recent.groupby(["month","month_name"]).size().reset_index(name="units")
              .sort_values("month"))
        fig14 = go.Figure(go.Bar(
            x=mc["month_name"], y=mc["units"],
            marker=dict(color=mc["units"],
                        colorscale=[[0,"#1a3a5c"],[1,C["ok"]]], showscale=False,
                        line=dict(color="#090C11", width=0.5)),
            text=mc["units"], textposition="outside",
            textfont=dict(size=13, color=C["text"]),
            hovertemplate="<b>%{x}</b><br>Deliveries: %{y}<extra></extra>",
        ))
        fig14.update_layout(**CBASE,
            xaxis=dict(**XSTYLE),
            yaxis=dict(**YSTYLE, title="Deliveries"),
            height=260)
        st.plotly_chart(fig14, use_container_width=True)

        dse_recent = (recent.groupby("dse_name").size()
                      .reset_index(name="Units").sort_values("Units", ascending=False).head(12))
        dse_recent.columns = ["DSE", "Deliveries (2025-26)"]
        st.dataframe(dse_recent, use_container_width=True, height=180, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""<div class="alert-warn" style="margin-top:16px;">
      🌾 <b>Season Guide:</b>
      <b>Rabi (Oct–Feb)</b> — post-harvest cash in hand, peak retail window.
      <b>Kharif (Jun–Sep)</b> — monsoon sowing, high finance demand, your biggest months.
      <b>Mar–May</b> — lean period; use for exchange promotions to clear old stock before June rush.
    </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="font-family:'DM Mono','Courier New',monospace;font-size:.58rem;color:#2E3D55;
  text-align:right;border-top:1px solid #1F2B3E;padding-top:12px;margin-top:32px;">
  JD DEALERSHIP · CHHATTISGARH · GM DASHBOARD v1.1 &nbsp;·&nbsp;
  DATA THROUGH FEB 2026 &nbsp;·&nbsp; MANAGEMENT BY EXCEPTION &nbsp;·&nbsp; {ts}
</div>""", unsafe_allow_html=True)
