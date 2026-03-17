"""
mapping_ui.py - Enhanced Column Mapping Interface
Provides a rich, interactive column mapping experience with:
- Confidence indicators (exact / fuzzy / missing)
- Multilingual synonym suggestions
- Save/load mapping profiles
- Disabled KPI explanations for unmapped fields
"""

import streamlit as st
import pandas as pd
import json
from typing import Dict, Optional, List, Tuple
from config import COLUMN_PATTERNS, MAPPING_PROFILE_KEY, INCOME_STATEMENT_FIELDS, BALANCE_SHEET_FIELDS, CASH_FLOW_FIELDS
from data_loader import auto_detect_columns, get_mapping_confidence


# ─── KPI DEPENDENCY MAP ───────────────────────────────────────────────────────
# Which fields are required for each KPI group
KPI_DEPENDENCIES = {
    "Gross Margin":           ["revenue", "cogs"],
    "Operating Margin":       ["revenue", "operating_profit"],
    "Net Margin":             ["revenue", "net_income"],
    "EBITDA Margin":          ["revenue", "ebitda"],
    "Return on Equity":       ["net_income", "equity"],
    "Return on Assets":       ["net_income", "total_assets"],
    "ROCE":                   ["operating_profit", "total_assets", "current_liabilities"],
    "Current Ratio":          ["current_assets", "current_liabilities"],
    "Quick Ratio":            ["current_assets", "current_liabilities", "inventory"],
    "Debt / Equity":          ["total_liabilities", "equity"],
    "Interest Coverage":      ["operating_profit", "interest_expense"],
    "Inventory Turnover":     ["cogs", "inventory"],
    "AR Turnover":            ["revenue", "accounts_receivable"],
    "Revenue Growth":         ["revenue"],
    "Enterprise Value":       ["ebitda"],
}

# Grouped field display for the UI
FIELD_GROUPS = {
    "📊 Income Statement": [
        ("revenue",          "Revenue / Sales",        True),
        ("cogs",             "Cost of Goods Sold",      True),
        ("gross_profit",     "Gross Profit",            False),
        ("operating_profit", "Operating Profit / EBIT", True),
        ("ebitda",           "EBITDA",                  False),
        ("net_income",       "Net Income / PAT",        True),
        ("interest_expense", "Interest Expense",        False),
        ("depreciation",     "Depreciation & Amort.",   False),
        ("tax",              "Income Tax",              False),
    ],
    "🏦 Balance Sheet": [
        ("total_assets",       "Total Assets",           True),
        ("current_assets",     "Current Assets",         False),
        ("inventory",          "Inventory",              False),
        ("accounts_receivable","Accounts Receivable",    False),
        ("total_liabilities",  "Total Liabilities",      False),
        ("current_liabilities","Current Liabilities",    False),
        ("equity",             "Total Equity",           True),
        ("long_term_debt",     "Long-Term Debt",         False),
        ("capital_employed",   "Capital Employed",       False),
    ],
    "💰 Cash Flow": [
        ("operating_cashflow", "Operating Cash Flow",   False),
        ("capex",              "Capital Expenditure",   False),
        ("free_cashflow",      "Free Cash Flow",        False),
    ],
    "📅 Period": [
        ("date",               "Date / Period / Year",  False),
    ],
}


# ─── CONFIDENCE BADGE HTML ────────────────────────────────────────────────────

def confidence_badge(level: str) -> str:
    styles = {
        'exact':   ('✅', '#bbf7d0', '#065f46', 'Exact match'),
        'fuzzy':   ('🔶', '#fde68a', '#92400e', 'Fuzzy match'),
        'missing': ('❌', '#fecaca', '#991b1b', 'Not detected'),
        'manual':  ('✏️', '#dbeafe', '#1e40af', 'Manually set'),
    }
    icon, bg, color, label = styles.get(level, ('❓', '#f1f5f9', '#475569', 'Unknown'))
    return (
        f'<span style="background:{bg};color:{color};padding:2px 8px;border-radius:10px;'
        f'font-size:10px;font-weight:700;white-space:nowrap">{icon} {label}</span>'
    )


def kpi_impact_html(field: str) -> str:
    """Return a compact list of KPIs affected by this field."""
    affected = [kpi for kpi, deps in KPI_DEPENDENCIES.items() if field in deps]
    if not affected:
        return ""
    tags = "".join(
        f'<span style="background:#f0f9ff;color:#0369a1;padding:1px 6px;border-radius:8px;'
        f'font-size:9px;margin:1px;display:inline-block">{k}</span>'
        for k in affected
    )
    return f'<div style="margin-top:4px">{tags}</div>'


# ─── PROFILE PERSISTENCE ─────────────────────────────────────────────────────

def save_mapping_profile(name: str, col_map: Dict) -> None:
    """Save a column mapping profile to session state."""
    if MAPPING_PROFILE_KEY not in st.session_state:
        st.session_state[MAPPING_PROFILE_KEY] = {}
    st.session_state[MAPPING_PROFILE_KEY][name] = {
        k: v for k, v in col_map.items() if v is not None
    }


def load_mapping_profile(name: str) -> Optional[Dict]:
    """Load a saved mapping profile from session state."""
    profiles = st.session_state.get(MAPPING_PROFILE_KEY, {})
    return profiles.get(name)


def list_mapping_profiles() -> List[str]:
    return list(st.session_state.get(MAPPING_PROFILE_KEY, {}).keys())


def export_mapping_json(col_map: Dict) -> str:
    """Export current mapping as JSON string."""
    return json.dumps({k: v for k, v in col_map.items() if v}, indent=2)


def import_mapping_json(json_str: str) -> Tuple[Optional[Dict], Optional[str]]:
    """Import a mapping from JSON string. Returns (col_map, error)."""
    try:
        data = json.loads(json_str)
        if not isinstance(data, dict):
            return None, "JSON must be an object/dict."
        # Validate keys
        valid_keys = set(COLUMN_PATTERNS.keys())
        col_map = {}
        for k, v in data.items():
            if k in valid_keys:
                col_map[k] = v if v else None
        return col_map, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"


# ─── MAIN MAPPING UI ─────────────────────────────────────────────────────────

def render_mapping_interface(df: pd.DataFrame, key_prefix: str = "map") -> Dict:
    """
    Render the full enhanced column mapping interface.
    Returns the final col_map dict after user interaction.
    """
    # Auto-detect baseline
    auto_map = auto_detect_columns(df)
    confidence = get_mapping_confidence(auto_map, df)

    # Session state key for this mapping instance
    state_key = f"{key_prefix}_colmap"
    if state_key not in st.session_state:
        st.session_state[state_key] = dict(auto_map)

    col_map = st.session_state[state_key]

    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;
                padding:18px 24px;margin-bottom:16px;color:white">
        <div style="font-weight:700;font-size:16px;margin-bottom:4px">
            🔗 Column Mapping
        </div>
        <div style="font-size:12px;opacity:0.9">
            Auto-detected from your data. Adjust any incorrect matches below.
            ✅ Exact · 🔶 Fuzzy · ❌ Missing
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats row ────────────────────────────────────────────────────────────
    all_fields = [f for grp in FIELD_GROUPS.values() for f, _, _ in grp]
    n_exact = sum(1 for f in all_fields if confidence.get(f) == 'exact')
    n_fuzzy = sum(1 for f in all_fields if confidence.get(f) == 'fuzzy')
    n_miss  = sum(1 for f in all_fields if confidence.get(f) == 'missing')
    n_required_missing = sum(
        1 for f, _, req in [item for grp in FIELD_GROUPS.values() for item in grp]
        if req and col_map.get(f) is None
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("✅ Exact Matches", n_exact)
    c2.metric("🔶 Fuzzy Matches", n_fuzzy)
    c3.metric("❌ Not Detected",  n_miss)
    c4.metric("⚠️ Required Missing", n_required_missing,
              delta=f"-{n_required_missing} KPIs affected" if n_required_missing else None,
              delta_color="inverse")

    # ── Profile management ────────────────────────────────────────────────────
    with st.expander("💾 Mapping Profiles — Save / Load / Import / Export", expanded=False):
        pcol1, pcol2 = st.columns([3, 1])
        with pcol1:
            profile_name = st.text_input("Profile name", key=f"{key_prefix}_profile_name",
                                          placeholder="e.g. Retail Company Template")
        with pcol2:
            st.write("")
            st.write("")
            if st.button("💾 Save", key=f"{key_prefix}_save_profile"):
                if profile_name:
                    save_mapping_profile(profile_name, col_map)
                    st.success(f"Saved profile: '{profile_name}'")
                else:
                    st.warning("Enter a profile name first.")

        profiles = list_mapping_profiles()
        if profiles:
            selected_profile = st.selectbox("Load saved profile", [""] + profiles,
                                             key=f"{key_prefix}_load_profile")
            if selected_profile and st.button("📂 Apply Profile", key=f"{key_prefix}_apply_profile"):
                loaded = load_mapping_profile(selected_profile)
                if loaded:
                    for k, v in loaded.items():
                        col_map[k] = v
                    st.session_state[state_key] = col_map
                    st.success(f"Loaded: '{selected_profile}'")
                    st.rerun()

        st.divider()
        imp_json = st.text_area("Import mapping JSON", height=100,
                                 key=f"{key_prefix}_import_json",
                                 placeholder='{"revenue": "Sales Column", "cogs": "Cost Column"}')
        imp_col1, imp_col2 = st.columns(2)
        with imp_col1:
            if st.button("📥 Apply JSON", key=f"{key_prefix}_apply_json"):
                if imp_json:
                    imported, err = import_mapping_json(imp_json)
                    if err:
                        st.error(err)
                    else:
                        for k, v in imported.items():
                            col_map[k] = v
                        st.session_state[state_key] = col_map
                        st.success("Mapping imported.")
                        st.rerun()
        with imp_col2:
            st.download_button(
                "📤 Export JSON", export_mapping_json(col_map),
                file_name="finanalyst_mapping.json", mime="application/json",
                key=f"{key_prefix}_export_json"
            )

    # ── Reset button ──────────────────────────────────────────────────────────
    if st.button("🔄 Reset to Auto-Detected", key=f"{key_prefix}_reset"):
        st.session_state[state_key] = dict(auto_detect_columns(df))
        st.rerun()

    # ── Field-by-field mapping ─────────────────────────────────────────────────
    all_cols = ['(Not Mapped)'] + list(df.columns)

    for group_label, fields in FIELD_GROUPS.items():
        st.markdown(f"**{group_label}**")

        for field, display_name, is_required in fields:
            current_val = col_map.get(field)
            conf = confidence.get(field, 'missing')

            # Recalculate confidence if user changed the mapping
            if current_val != auto_map.get(field):
                conf = 'manual' if current_val else 'missing'

            default_idx = all_cols.index(current_val) if current_val in all_cols else 0

            label_html = (
                f'{"🔴 " if is_required else ""}'
                f'<strong>{display_name}</strong>'
                f'{" <sup style=\'color:#ef4444\'>required</sup>" if is_required else ""}'
            )

            row_cols = st.columns([3, 4, 2])
            with row_cols[0]:
                st.markdown(
                    f'<div style="padding-top:8px;font-size:13px">'
                    f'{label_html}</div>'
                    f'{kpi_impact_html(field)}',
                    unsafe_allow_html=True
                )
            with row_cols[1]:
                selected = st.selectbox(
                    f"###{field}",
                    all_cols,
                    index=default_idx,
                    key=f"{key_prefix}_{field}",
                    label_visibility="collapsed"
                )
                new_val = None if selected == '(Not Mapped)' else selected
                if new_val != col_map.get(field):
                    col_map[field] = new_val
                    st.session_state[state_key] = col_map
            with row_cols[2]:
                st.markdown(
                    f'<div style="padding-top:8px">{confidence_badge(conf)}</div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")

    # ── KPI availability summary ───────────────────────────────────────────────
    with st.expander("📊 KPI Availability Preview", expanded=False):
        for kpi_name, deps in KPI_DEPENDENCIES.items():
            mapped_deps = [col_map.get(d) for d in deps]
            all_mapped = all(v is not None for v in mapped_deps)
            icon = "✅" if all_mapped else "❌"
            missing_fields = [d for d in deps if not col_map.get(d)]
            note = "" if all_mapped else f" ← needs: {', '.join(missing_fields)}"
            st.markdown(
                f"{icon} **{kpi_name}**{note}",
                help=f"Requires: {', '.join(deps)}"
            )

    return col_map
