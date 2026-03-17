"""
app.py — FinAnalyst Pro v2.0
Professional Financial Analysis Platform
Supports: Single file, Multi-file merge, Google Sheets, Sample presets.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import APP_VERSION, INDUSTRY_BENCHMARKS, SAMPLE_PRESETS, DEFAULT_CAP_RATE
from data_loader import (
    load_file, clean_dataframe, auto_detect_columns, detect_period_column,
    validate_data_quality, generate_sample_data, generate_split_sample_files,
    load_excel_sheet, detect_statement_type, merge_multiple_files,
    load_google_sheet,
)
from mapping_ui import render_mapping_interface, export_mapping_json
from kpi_engine import calculate_all_kpis, get_latest_kpis
from intelligence import analyze_all
from charts import (
    revenue_chart, margin_chart, kpi_gauge, waterfall_chart,
    balance_sheet_chart, ratio_radar, ev_visualization,
)
from report_generator import generate_html_report, kpi_to_csv
from database import DatabaseConnector

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinAnalyst Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── CSS ────────────────────────────────────────────────────────────────────────
def inject_css(dark: bool):
    bg      = "#0f172a" if dark else "#f8fafc"
    card_bg = "#1e293b" if dark else "#ffffff"
    text    = "#e2e8f0" if dark else "#1e293b"
    border  = "#334155" if dark else "#e2e8f0"
    muted   = "#94a3b8" if dark else "#64748b"
    danger_bg = "#2d1515" if dark else "#fff5f5"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Sora', sans-serif !important;
        background: {bg} !important;
        color: {text} !important;
    }}
    .stApp {{ background: {bg}; }}
    [data-testid="stSidebar"] {{
        background: {card_bg} !important;
        border-right: 1px solid {border};
    }}
    .kpi-card {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
        transition: transform .2s, box-shadow .2s;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99,102,241,.18);
    }}
    .kpi-label {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .1em;
        text-transform: uppercase;
        color: {muted};
        margin-bottom: 4px;
    }}
    .kpi-value {{
        font-size: 26px;
        font-weight: 800;
        color: #6366f1;
        line-height: 1.1;
    }}
    .kpi-sub {{ font-size: 11px; color: {muted}; margin-top: 4px; }}
    .insight-card {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }}
    .insight-positive {{ border-left: 4px solid #10b981; }}
    .insight-negative {{ border-left: 4px solid #ef4444; }}
    .insight-warning  {{ border-left: 4px solid #f59e0b; }}
    .insight-danger   {{ border-left: 4px solid #dc2626; background: {danger_bg}; }}
    .insight-info     {{ border-left: 4px solid #3b82f6; }}
    .insight-neutral  {{ border-left: 4px solid #94a3b8; }}
    .insight-title   {{ font-weight: 700; font-size: 13px; margin-bottom: 4px; color: {text}; }}
    .insight-message {{ font-size: 12px; color: {muted}; line-height: 1.5; }}
    .section-header {{
        font-size: 17px;
        font-weight: 700;
        color: {text};
        margin: 24px 0 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #6366f1;
    }}
    .hero-banner {{
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        border-radius: 16px;
        padding: 32px 40px;
        color: white;
        margin-bottom: 28px;
    }}
    .hero-title {{ font-size: 30px; font-weight: 800; margin: 0 0 6px; }}
    .hero-sub   {{ font-size: 13px; opacity: .85; margin: 0; }}
    .health-ring {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255,255,255,.15);
        padding: 6px 16px;
        border-radius: 24px;
        margin-top: 12px;
        font-weight: 700;
        font-size: 13px;
    }}
    .rec-card {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }}
    .rec-High   {{ border-left: 5px solid #dc2626; }}
    .rec-Medium {{ border-left: 5px solid #d97706; }}
    .rec-Low    {{ border-left: 5px solid #059669; }}
    .badge {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .05em;
        text-transform: uppercase;
    }}
    .badge-High   {{ background: #fecaca; color: #991b1b; }}
    .badge-Medium {{ background: #fde68a; color: #92400e; }}
    .badge-Low    {{ background: #bbf7d0; color: #065f46; }}
    .merge-card {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }}
    div[data-testid="stMetric"] {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 10px;
        padding: 14px;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: {card_bg};
        padding: 6px;
        border-radius: 10px;
        border: 1px solid {border};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        font-size: 13px;
    }}
    .stTabs [aria-selected="true"] {{
        background: #6366f1 !important;
        color: white !important;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 20px;
        transition: opacity .2s;
    }}
    .stButton > button:hover {{ opacity: .9; }}
    .stDownloadButton > button {{
        background: {card_bg};
        color: #6366f1;
        border: 1px solid #6366f1;
        border-radius: 8px;
        font-weight: 600;
    }}
    footer {{ visibility: hidden; }}
    #MainMenu {{ visibility: hidden; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────────
def kpi_card(label, value, subtitle="", delta=None):
    delta_html = ""
    if delta is not None:
        color = "#10b981" if delta >= 0 else "#ef4444"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<div style="font-size:11px;color:{color};margin-top:2px">{arrow} {abs(delta)*100:.1f}pp</div>'
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{subtitle}</div>'
        f'{delta_html}'
        f'</div>'
    )


def insight_card(ins):
    t = ins.get("type", "neutral")
    icon = ins.get("icon", "📌")
    title = ins.get("title", "")
    message = ins.get("message", "")
    return (
        f'<div class="insight-card insight-{t}">'
        f'<div class="insight-title">{icon} {title}</div>'
        f'<div class="insight-message">{message}</div>'
        f'</div>'
    )


def fmt_pct(v, d=1):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    return f"{v * 100:.{d}f}%"


def fmt_money(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    if abs(v) >= 1e9:
        return f"${v / 1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"${v / 1e6:.2f}M"
    if abs(v) >= 1e3:
        return f"${v / 1e3:.1f}K"
    return f"${v:.0f}"


def fmt_ratio(v, d=2):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    return f"{v:.{d}f}x"


def section(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


# ─── DATA SOURCE PANEL ───────────────────────────────────────────────────────────
def render_data_source_panel():
    """Returns (df_raw, labels, source_label)."""
    st.markdown("### 📂 Data Source")

    mode = st.radio(
        "Source mode",
        ["📁 Single File", "📂 Multi-File Merge", "🌐 Google Sheets", "🧪 Sample Preset"],
        label_visibility="collapsed",
    )

    df_raw = None
    labels = []
    source_label = "—"

    # ── SINGLE FILE ─────────────────────────────────────────────────────────
    if mode == "📁 Single File":
        uploaded = st.file_uploader("Drop Excel or CSV here", type=["xlsx", "xls", "csv"])
        if uploaded:
            df_raw, err, sheet_names = load_file(uploaded)
            if err:
                st.error(err)
                df_raw = None
            elif df_raw is not None:
                if len(sheet_names) > 1:
                    sel = st.selectbox("Sheet tab", sheet_names)
                    if sel != sheet_names[0]:
                        uploaded.seek(0)
                        df_raw = load_excel_sheet(uploaded, sel)
                if df_raw is not None:
                    df_raw = clean_dataframe(df_raw)
                    period_col = detect_period_column(df_raw)
                    if period_col:
                        labels = [str(v) for v in df_raw[period_col].tolist()]
                    else:
                        labels = [f"Period {i+1}" for i in range(len(df_raw))]
                    source_label = f"📁 {uploaded.name}"
                    st.success(f"✅ Loaded {len(df_raw)} rows, {len(df_raw.columns)} columns")

    # ── MULTI-FILE MERGE ─────────────────────────────────────────────────────
    elif mode == "📂 Multi-File Merge":
        info_html = (
            '<div style="background:#faf5ff;border:1px solid #d8b4fe;border-radius:8px;'
            'padding:10px 14px;font-size:12px;margin-bottom:12px">'
            '<strong>💡 Multi-File Merge</strong><br>'
            'Upload separate P&amp;L, Balance Sheet, and/or Cash Flow files. '
            'The app detects statement types and merges by fiscal period automatically.'
            '</div>'
        )
        st.markdown(info_html, unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Upload 2–5 files",
            type=["xlsx", "xls", "csv"],
            accept_multiple_files=True,
        )

        if st.button("📋 Load sample split files (P&L + Balance Sheet + Cash Flow)"):
            pl, bs, cf = generate_split_sample_files()
            st.session_state["_split_samples"] = [
                {"df": pl, "label": "Income Statement (sample)", "period_col": "Fiscal Year", "stmt_type": "income_statement"},
                {"df": bs, "label": "Balance Sheet (sample)",    "period_col": "FY",           "stmt_type": "balance_sheet"},
                {"df": cf, "label": "Cash Flow (sample)",        "period_col": "Period",        "stmt_type": "cash_flow"},
            ]
            st.success("✅ Sample files loaded — click 'Merge Files' below")

        file_infos = []
        if uploaded_files:
            for uf in uploaded_files:
                d, err, _ = load_file(uf)
                if err or d is None:
                    st.error(f"❌ {uf.name}: {err}")
                    continue
                d = clean_dataframe(d)
                file_infos.append({
                    "df": d,
                    "label": uf.name,
                    "stmt_type": detect_statement_type(d),
                    "period_col": detect_period_column(d),
                })
        elif "_split_samples" in st.session_state:
            file_infos = st.session_state["_split_samples"]

        if file_infos:
            st.markdown("**Confirm detected statement types:**")
            stmt_options = ["income_statement", "balance_sheet", "cash_flow", "unknown"]
            for i, fi in enumerate(file_infos):
                col_a, col_b, col_c = st.columns([3, 2, 2])
                with col_a:
                    st.markdown(f"**{fi['label']}** — {len(fi['df'])} rows · {len(fi['df'].columns)} cols")
                with col_b:
                    fi["stmt_type"] = st.selectbox(
                        "Type",
                        stmt_options,
                        index=stmt_options.index(fi.get("stmt_type", "unknown")),
                        key=f"stmt_type_{i}",
                        label_visibility="collapsed",
                    )
                with col_c:
                    pc_opts = ["(auto)"] + list(fi["df"].columns)
                    sel_pc = st.selectbox(
                        "Period col",
                        pc_opts,
                        index=0,
                        key=f"period_col_{i}",
                        label_visibility="collapsed",
                    )
                    fi["period_col"] = None if sel_pc == "(auto)" else sel_pc

            if st.button("🔀 Merge Files", type="primary"):
                with st.spinner("Merging..."):
                    merged, err, periods = merge_multiple_files(file_infos)
                if err:
                    st.error(f"Merge failed: {err}")
                else:
                    st.session_state["_merged_df"] = merged
                    st.session_state["_merged_periods"] = periods
                    st.success(f"✅ Merged {len(file_infos)} files → {len(merged)} rows, {len(merged.columns)} columns")

        if "_merged_df" in st.session_state:
            df_raw = st.session_state["_merged_df"]
            labels = st.session_state.get("_merged_periods", [f"Period {i+1}" for i in range(len(df_raw))])
            source_label = f"📂 {len(file_infos)} files merged"
            with st.expander("👁️ Merged Dataset Preview"):
                st.dataframe(df_raw.head(10), use_container_width=True)

    # ── GOOGLE SHEETS ────────────────────────────────────────────────────────
    elif mode == "🌐 Google Sheets":
        info_html = (
            '<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;'
            'padding:10px 14px;font-size:12px;margin-bottom:12px">'
            '<strong>✅ Public sheets only.</strong> In Google Sheets:<br>'
            '<strong>Option A:</strong> File → Share → Publish to the web → CSV → Publish<br>'
            '<strong>Option B:</strong> Share → Anyone with the link → Viewer'
            '</div>'
        )
        st.markdown(info_html, unsafe_allow_html=True)

        gs_url = st.text_input(
            "Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/YOUR_ID/edit#gid=0",
            key="gs_url",
        )

        col1, col2 = st.columns(2)
        with col1:
            fetch_btn = st.button("🔗 Fetch Sheet", type="primary", disabled=not gs_url)
        with col2:
            if st.button("🧪 Load test public sheet"):
                st.session_state["gs_url_to_load"] = (
                    "https://docs.google.com/spreadsheets/d/"
                    "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/export?format=csv"
                )

        url_to_use = st.session_state.pop("gs_url_to_load", gs_url if fetch_btn else None)

        if url_to_use:
            with st.spinner("Fetching from Google Sheets..."):
                d, err, _ = load_google_sheet(url_to_use)
            if err:
                st.error(err)
            elif d is not None:
                df_raw = clean_dataframe(d)
                period_col = detect_period_column(df_raw)
                if period_col:
                    labels = [str(v) for v in df_raw[period_col].tolist()]
                else:
                    labels = [f"Row {i+1}" for i in range(len(df_raw))]
                source_label = "🌐 Google Sheets"
                st.session_state["_gs_df"] = df_raw
                st.session_state["_gs_labels"] = labels
                st.success(f"✅ Fetched {len(df_raw)} rows from Google Sheets")

        if "_gs_df" in st.session_state and df_raw is None:
            df_raw = st.session_state["_gs_df"]
            labels = st.session_state.get("_gs_labels", [])
            source_label = "🌐 Google Sheets"

    # ── SAMPLE PRESETS ───────────────────────────────────────────────────────
    elif mode == "🧪 Sample Preset":
        preset_options = list(SAMPLE_PRESETS.keys())
        selected_preset = st.selectbox("Choose a company type", preset_options)

        preset_info = SAMPLE_PRESETS[selected_preset]
        desc_html = (
            f'<div style="background:#faf5ff;border:1px solid #d8b4fe;border-radius:8px;'
            f'padding:10px 14px;font-size:12px;margin-bottom:8px">'
            f'{preset_info["description"]}'
            f'</div>'
        )
        st.markdown(desc_html, unsafe_allow_html=True)

        df_raw = generate_sample_data(selected_preset)
        df_raw = clean_dataframe(df_raw)
        period_col = detect_period_column(df_raw)
        if period_col:
            labels = [str(v) for v in df_raw[period_col].tolist()]
        else:
            labels = [f"Period {i+1}" for i in range(len(df_raw))]
        source_label = f"🧪 {selected_preset}"
        st.success(f"✅ Loaded {selected_preset} — {len(df_raw)} periods")

        with st.expander("Preview raw data"):
            st.dataframe(df_raw, use_container_width=True, hide_index=True)

    return df_raw, labels, source_label


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        logo_html = (
            '<div style="text-align:center;padding:16px 0">'
            '<div style="font-size:32px">📊</div>'
            f'<div style="font-size:18px;font-weight:800;color:#6366f1">FinAnalyst Pro</div>'
            f'<div style="font-size:10px;color:#94a3b8;letter-spacing:.1em">v{APP_VERSION}</div>'
            '</div>'
        )
        st.markdown(logo_html, unsafe_allow_html=True)
        st.divider()
        dark_mode = st.toggle("🌙 Dark Mode", value=True)
        st.divider()
        df_raw, labels, source_label = render_data_source_panel()
    return dark_mode, df_raw, labels, source_label


# ─── EMPTY STATE ─────────────────────────────────────────────────────────────────
def render_empty_state(dark_mode):
    card_bg  = "#1e293b" if dark_mode else "white"
    card_bdr = "#334155" if dark_mode else "#e2e8f0"

    features = [
        ("📁", "Single File",    "Excel (.xlsx) or CSV"),
        ("📂", "Multi-File",     "Merge P&L + Balance Sheet + Cash Flow"),
        ("🌐", "Google Sheets",  "Paste a public sheet URL"),
        ("🧪", "Sample Presets", "Retail, Manufacturing, SaaS, Healthcare"),
    ]

    cards_html = ""
    for icon, title, desc in features:
        cards_html += (
            f'<div style="background:{card_bg};border:1px solid {card_bdr};'
            f'border-radius:12px;padding:16px 22px;text-align:left;max-width:200px">'
            f'<div style="font-size:22px">{icon}</div>'
            f'<div style="font-weight:700;margin:6px 0 4px;font-size:13px">{title}</div>'
            f'<div style="font-size:11px;color:#64748b">{desc}</div>'
            f'</div>'
        )

    html = (
        '<div style="text-align:center;padding:80px 20px">'
        '<div style="font-size:64px;margin-bottom:16px">📊</div>'
        '<div style="font-size:28px;font-weight:800;color:#6366f1;margin-bottom:8px">FinAnalyst Pro</div>'
        '<div style="font-size:15px;color:#64748b;margin-bottom:32px">'
        'Import financial data to begin. Supports Excel, CSV, Google Sheets &amp; sample presets.'
        '</div>'
        '<div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap">'
        + cards_html
        + '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ─── MAIN ─────────────────────────────────────────────────────────────────────────
def main():
    dark_mode, df_raw, labels, source_label = render_sidebar()
    inject_css(dark_mode)

    if df_raw is None or len(df_raw) == 0:
        render_empty_state(dark_mode)
        return

    # ── COLUMN MAPPING ───────────────────────────────────────────────────────
    with st.expander("🔗 Column Mapping — Click to review & adjust", expanded=False):
        col_map = render_mapping_interface(df_raw, key_prefix="main")

    if "main_colmap" in st.session_state:
        col_map = st.session_state["main_colmap"]
    else:
        col_map = auto_detect_columns(df_raw)

    # ── COMPUTE KPIs ─────────────────────────────────────────────────────────
    with st.spinner("🔄 Computing KPIs..."):
        kpi_df   = calculate_all_kpis(df_raw, col_map)
        insights = analyze_all(kpi_df, labels)
        latest   = kpi_df.iloc[-1].to_dict()
        health   = insights.get("health_score", 0)

    # ── HERO BANNER ──────────────────────────────────────────────────────────
    h_emoji = "💚" if health >= 75 else "🟡" if health >= 50 else "🔴"
    h_label = "Strong" if health >= 75 else "Moderate" if health >= 50 else "At Risk"
    detected_count = sum(1 for v in col_map.values() if v)

    hero_html = (
        '<div class="hero-banner">'
        '<div class="hero-title">📊 Financial Dashboard</div>'
        f'<div class="hero-sub">'
        f'Source: {source_label}'
        f' &nbsp;·&nbsp; {len(df_raw)} periods'
        f' &nbsp;·&nbsp; {detected_count} fields mapped'
        f'</div>'
        f'<div class="health-ring">{h_emoji} Health Score: {health}/100 — {h_label}</div>'
        '</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    # ── TABS ─────────────────────────────────────────────────────────────────
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📋 Overview", "📈 Charts", "🧠 Insights", "⚖️ Valuation", "🔢 Raw KPIs", "📄 Export"
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — OVERVIEW
    # ════════════════════════════════════════════════════════════════════════
    with t1:
        # Data quality preview
        with st.expander("📂 Raw Data Preview", expanded=False):
            st.dataframe(df_raw.head(10), use_container_width=True)
            qual = validate_data_quality(df_raw, col_map)
            q1, q2, q3, q4 = st.columns(4)
            q1.metric("Data Quality",      f"{qual['quality_score']}/100")
            q2.metric("Rows",              qual["row_count"])
            q3.metric("Fields Detected",   len(qual["detected"]))
            q4.metric("Critical Missing",  len(qual["missing_critical"]))
            for w in qual["warnings"]:
                st.info(f"ℹ️ {w}")
            if qual["missing_critical"]:
                st.warning(f"⚠️ Missing: {', '.join(qual['missing_critical'])}")

        # Helper: get delta vs prior period
        def get_delta(field):
            if len(kpi_df) < 2 or field not in kpi_df.columns:
                return None
            prev = kpi_df[field].iloc[-2]
            curr = latest.get(field, np.nan)
            if pd.isna(prev) or pd.isna(curr):
                return None
            return curr - prev

        # ── Profitability ─────────────────────────────────────────────────
        section("💰 Profitability")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(kpi_card("Gross Margin", fmt_pct(latest.get("gross_margin")),
                                 f"Bench: {INDUSTRY_BENCHMARKS['gross_margin']*100:.0f}%",
                                 get_delta("gross_margin")), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Operating Margin", fmt_pct(latest.get("operating_margin")),
                                 f"Bench: {INDUSTRY_BENCHMARKS['operating_margin']*100:.0f}%",
                                 get_delta("operating_margin")), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("Net Margin", fmt_pct(latest.get("net_margin")),
                                 f"Bench: {INDUSTRY_BENCHMARKS['net_margin']*100:.0f}%"), unsafe_allow_html=True)
        with c4:
            st.markdown(kpi_card("EBITDA Margin", fmt_pct(latest.get("ebitda_margin")),
                                 f"Bench: {INDUSTRY_BENCHMARKS['ebitda_margin']*100:.0f}%"), unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi_card("Return on Equity", fmt_pct(latest.get("roe")),
                                 f"Bench: {INDUSTRY_BENCHMARKS['roe']*100:.0f}%"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Return on Assets", fmt_pct(latest.get("roa")),
                                 f"Bench: {INDUSTRY_BENCHMARKS['roa']*100:.0f}%"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("ROCE", fmt_pct(latest.get("roce")),
                                 "EBIT / Capital Employed"), unsafe_allow_html=True)

        # ── Liquidity ─────────────────────────────────────────────────────
        section("💧 Liquidity")
        c1, c2 = st.columns(2)
        cr = latest.get("current_ratio")
        qr = latest.get("quick_ratio")
        cr_status = "✅ Healthy" if cr and cr >= 1.5 else ("⚠️ Tight" if cr and cr >= 1.0 else "🔴 Critical")
        qr_status = "✅ Healthy" if qr and qr >= 1.0 else "⚠️ Watch"
        with c1:
            st.markdown(kpi_card("Current Ratio", fmt_ratio(cr), cr_status), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Quick Ratio", fmt_ratio(qr), qr_status), unsafe_allow_html=True)

        # ── Leverage ──────────────────────────────────────────────────────
        section("🏦 Leverage")
        c1, c2 = st.columns(2)
        de = latest.get("debt_to_equity")
        ic = latest.get("interest_coverage")
        de_status = "✅ Low" if de and de < 1.0 else ("⚠️ Elevated" if de and de < 2.0 else "🔴 High Risk")
        ic_status = "✅ Safe" if ic and ic >= 3.0 else ("⚠️ Low" if ic and ic >= 1.5 else "🔴 Danger")
        with c1:
            st.markdown(kpi_card("Debt / Equity", fmt_ratio(de), de_status), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Interest Coverage", fmt_ratio(ic), ic_status), unsafe_allow_html=True)

        # ── Efficiency ────────────────────────────────────────────────────
        section("⚡ Efficiency")
        c1, c2, c3, c4 = st.columns(4)
        di = latest.get("days_inventory")
        da = latest.get("days_ar")
        with c1:
            st.markdown(kpi_card("Inventory Turnover", fmt_ratio(latest.get("inventory_turnover")),
                                 f"Bench: {INDUSTRY_BENCHMARKS['inventory_turnover']:.0f}x"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("AR Turnover", fmt_ratio(latest.get("ar_turnover")),
                                 f"Bench: {INDUSTRY_BENCHMARKS['ar_turnover']:.0f}x"), unsafe_allow_html=True)
        with c3:
            di_str = f"{di:.0f} days" if di and not np.isnan(di) else "N/A"
            st.markdown(kpi_card("Days Inventory", di_str, "Lower is better"), unsafe_allow_html=True)
        with c4:
            da_str = f"{da:.0f} days" if da and not np.isnan(da) else "N/A"
            st.markdown(kpi_card("Days AR", da_str, "Lower is better"), unsafe_allow_html=True)

        # ── Growth ────────────────────────────────────────────────────────
        section("🚀 Growth")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi_card("Revenue Growth YoY", fmt_pct(latest.get("revenue_growth")),
                                 "Current vs prior period"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Revenue CAGR 3Y", fmt_pct(latest.get("revenue_cagr_3y")),
                                 "Compound growth rate"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("EBITDA CAGR 3Y", fmt_pct(latest.get("ebitda_cagr_3y")),
                                 "Compound growth rate"), unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — CHARTS
    # ════════════════════════════════════════════════════════════════════════
    with t2:
        fig_rev = revenue_chart(df_raw, col_map, labels, dark_mode)
        if fig_rev:
            st.plotly_chart(fig_rev, use_container_width=True)
        else:
            st.info("Revenue data not detected — check column mapping.")

        c1, c2 = st.columns(2)
        with c1:
            fig_mg = margin_chart(kpi_df, labels, dark_mode)
            if fig_mg:
                st.plotly_chart(fig_mg, use_container_width=True)
        with c2:
            fig_bs = balance_sheet_chart(kpi_df, labels, dark_mode)
            if fig_bs:
                st.plotly_chart(fig_bs, use_container_width=True)

        fig_wf = waterfall_chart(df_raw, col_map, labels, -1, dark_mode)
        if fig_wf:
            st.plotly_chart(fig_wf, use_container_width=True)
        else:
            st.info("Waterfall chart requires Revenue, COGS, and Net Income columns.")

        fig_radar = ratio_radar(get_latest_kpis(kpi_df), dark_mode)
        if fig_radar:
            st.plotly_chart(fig_radar, use_container_width=True)

        section("KPI Gauges")
        g1, g2, g3, g4 = st.columns(4)
        gauge_configs = [
            (g1, latest.get("gross_margin",  np.nan), "Gross Margin",    INDUSTRY_BENCHMARKS["gross_margin"],  1.0, True),
            (g2, latest.get("net_margin",    np.nan), "Net Margin",      INDUSTRY_BENCHMARKS["net_margin"],    0.5, True),
            (g3, latest.get("current_ratio", np.nan), "Current Ratio",   INDUSTRY_BENCHMARKS["current_ratio"], 4.0, False),
            (g4, latest.get("roe",           np.nan), "Return on Equity",INDUSTRY_BENCHMARKS["roe"],           0.5, True),
        ]
        for col, val, title, bench, mx, is_pct in gauge_configs:
            with col:
                if not pd.isna(val):
                    fig = kpi_gauge(val, title, bench, mx, is_pct, dark_mode)
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — INSIGHTS
    # ════════════════════════════════════════════════════════════════════════
    with t3:
        section("📋 Executive Summary")
        for bullet in insights.get("executive_summary", []):
            st.markdown(f"- {bullet}")

        c1, c2 = st.columns(2)
        with c1:
            section("📈 Trend Analysis")
            for item in insights.get("trend_analysis", []):
                st.markdown(insight_card(item), unsafe_allow_html=True)

            section("🔍 Anomaly Detection")
            for item in insights.get("anomalies", []):
                st.markdown(insight_card(item), unsafe_allow_html=True)

        with c2:
            section("🏭 Peer Comparison")
            for item in insights.get("peer_comparison", []):
                st.markdown(insight_card(item), unsafe_allow_html=True)

        section("🚨 Risk Alerts")
        for item in insights.get("risk_alerts", []):
            st.markdown(insight_card(item), unsafe_allow_html=True)

        section("⚡ Efficiency Alerts")
        for item in insights.get("efficiency_alerts", []):
            st.markdown(insight_card(item), unsafe_allow_html=True)

        section("💡 Strategic Recommendations")
        for rec in insights.get("recommendations", []):
            p = rec.get("priority", "Low")
            rec_html = (
                f'<div class="rec-card rec-{p}">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
                f'<span style="font-size:16px">{rec.get("icon","💡")}</span>'
                f'<span style="font-weight:700;font-size:13px">{rec.get("title","")}</span>'
                f'<span class="badge badge-{p}">{p}</span>'
                f'</div>'
                f'<div style="font-size:12px;color:#64748b;line-height:1.6">{rec.get("action","")}</div>'
                f'</div>'
            )
            st.markdown(rec_html, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — VALUATION
    # ════════════════════════════════════════════════════════════════════════
    with t4:
        ev      = latest.get("enterprise_value", np.nan)
        eq_val  = latest.get("equity_value",     np.nan)
        ev_mult = latest.get("ev_ebitda_multiple", np.nan)
        ebitda  = latest.get("ebitda",            np.nan)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Enterprise Value", fmt_money(ev))
        c2.metric("Equity Value",     fmt_money(eq_val))
        c3.metric("EV / EBITDA",      fmt_ratio(ev_mult))
        c4.metric("EBITDA",           fmt_money(ebitda))

        st.markdown("---")
        vi = insights.get("valuation_insight", "")
        if vi:
            st.markdown(vi)

        fig_ev = ev_visualization(kpi_df, labels, dark_mode)
        if fig_ev:
            st.plotly_chart(fig_ev, use_container_width=True)

        section("🎛️ EV Sensitivity (Cap Rate)")
        if not pd.isna(ebitda) and ebitda > 0:
            cap_rates = [0.08, 0.10, 0.12, 0.14, 0.16, 0.20]
            profiles  = ["Very Low Risk", "Low Risk", "Moderate", "Moderate-High", "High Risk", "Distressed"]
            sens_df = pd.DataFrame({
                "Cap Rate":           [f"{r*100:.0f}%" for r in cap_rates],
                "Enterprise Value":   [fmt_money(ebitda / r) for r in cap_rates],
                "EV/EBITDA Multiple": [f"{1/r:.1f}x" for r in cap_rates],
                "Investor Profile":   profiles,
            })
            st.dataframe(sens_df, use_container_width=True, hide_index=True)
        else:
            st.info("EBITDA data needed for sensitivity analysis.")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 5 — RAW KPIs
    # ════════════════════════════════════════════════════════════════════════
    with t5:
        section("📊 All KPIs — Full Table")
        display_df = kpi_df.copy()
        if labels:
            display_df.insert(0, "Period", labels[:len(display_df)])

        pct_cols = [
            "gross_margin", "operating_margin", "net_margin", "ebitda_margin",
            "roe", "roa", "roce", "revenue_growth", "ni_growth", "ebitda_growth",
            "revenue_cagr_3y", "ebitda_cagr_3y",
        ]
        for col in pct_cols:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(
                    lambda x: f"{x*100:.2f}%" if not pd.isna(x) else "N/A"
                )

        money_cols = [
            "revenue", "gross_profit", "operating_profit", "ebitda", "net_income",
            "total_assets", "equity", "total_liabilities", "enterprise_value", "equity_value",
        ]
        for col in money_cols:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(
                    lambda x: fmt_money(x) if not pd.isna(x) else "N/A"
                )

        ratio_cols = [
            "current_ratio", "quick_ratio", "debt_to_equity", "interest_coverage",
            "inventory_turnover", "ar_turnover", "ev_ebitda_multiple",
        ]
        for col in ratio_cols:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(
                    lambda x: f"{x:.2f}x" if not pd.isna(x) else "N/A"
                )

        st.dataframe(display_df, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 6 — EXPORT
    # ════════════════════════════════════════════════════════════════════════
    with t6:
        section("📄 Export Reports")
        company_name = st.text_input("Report / Company Name", value="Financial Analysis Report")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 📊 KPI Data (CSV)")
            csv_data = kpi_to_csv(kpi_df, labels)
            st.download_button(
                "⬇️ Download KPIs CSV",
                csv_data,
                file_name="finanalyst_kpis.csv",
                mime="text/csv",
            )
        with c2:
            st.markdown("#### 🌐 HTML Report")
            html_report = generate_html_report(kpi_df, insights, labels, company_name)
            st.download_button(
                "⬇️ Download HTML Report",
                html_report,
                file_name="finanalyst_report.html",
                mime="text/html",
            )

        st.info("💡 **PDF:** Download the HTML report → open in browser → File → Print → Save as PDF")

        st.markdown("---")
        section("🔌 SQL Integration Status")
        st.json(DatabaseConnector.get_status())

        st.markdown("---")
        section("🗂️ Column Mapping Export")
        st.download_button(
            "⬇️ Download Mapping JSON",
            export_mapping_json(col_map),
            file_name="finanalyst_mapping.json",
            mime="application/json",
        )
        st.caption("Re-import this JSON next session via the Column Mapping panel to skip auto-detection.")


if __name__ == "__main__":
    main()
