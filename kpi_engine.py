"""
kpi_engine.py - KPI Calculation Engine
Computes all financial KPIs from mapped column data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from config import DEFAULT_CAP_RATE, INDUSTRY_BENCHMARKS
from data_loader import get_numeric_series


def safe_divide(numerator, denominator, default=np.nan):
    """Safe division avoiding zero/null errors."""
    try:
        if pd.isna(denominator) or denominator == 0:
            return default
        return numerator / denominator
    except Exception:
        return default


def calculate_all_kpis(df: pd.DataFrame, col_map: Dict) -> Dict:
    """
    Master KPI calculation function.
    Returns nested dict of all computed KPIs per row/period.
    """
    results = []
    n = len(df)
    
    # Extract series
    revenue = get_numeric_series(df, col_map.get('revenue'))
    cogs = get_numeric_series(df, col_map.get('cogs'))
    gross_profit = get_numeric_series(df, col_map.get('gross_profit'))
    operating_profit = get_numeric_series(df, col_map.get('operating_profit'))
    ebitda = get_numeric_series(df, col_map.get('ebitda'))
    net_income = get_numeric_series(df, col_map.get('net_income'))
    interest_expense = get_numeric_series(df, col_map.get('interest_expense'))
    depreciation = get_numeric_series(df, col_map.get('depreciation'))
    current_assets = get_numeric_series(df, col_map.get('current_assets'))
    current_liabilities = get_numeric_series(df, col_map.get('current_liabilities'))
    inventory = get_numeric_series(df, col_map.get('inventory'))
    ar = get_numeric_series(df, col_map.get('accounts_receivable'))
    total_assets = get_numeric_series(df, col_map.get('total_assets'))
    total_liabilities = get_numeric_series(df, col_map.get('total_liabilities'))
    equity = get_numeric_series(df, col_map.get('equity'))
    long_term_debt = get_numeric_series(df, col_map.get('long_term_debt'))
    
    # Derived series
    if gross_profit is None and revenue is not None and cogs is not None:
        gross_profit = revenue - cogs
    
    if ebitda is None and operating_profit is not None and depreciation is not None:
        ebitda = operating_profit + depreciation
    elif ebitda is None and operating_profit is not None:
        ebitda = operating_profit  # approximation
    
    if operating_profit is None and net_income is not None and interest_expense is not None:
        operating_profit = net_income + interest_expense  # rough EBIT
    
    # Per-row KPIs
    for i in range(n):
        kpi = {}
        
        rev = revenue.iloc[i] if revenue is not None else np.nan
        cgs = cogs.iloc[i] if cogs is not None else np.nan
        gp = gross_profit.iloc[i] if gross_profit is not None else np.nan
        op = operating_profit.iloc[i] if operating_profit is not None else np.nan
        ebit = op  # EBIT approximated by operating profit
        ebt = ebitda.iloc[i] if ebitda is not None else np.nan
        ni = net_income.iloc[i] if net_income is not None else np.nan
        ie = interest_expense.iloc[i] if interest_expense is not None else np.nan
        ca = current_assets.iloc[i] if current_assets is not None else np.nan
        cl = current_liabilities.iloc[i] if current_liabilities is not None else np.nan
        inv = inventory.iloc[i] if inventory is not None else np.nan
        acc_rec = ar.iloc[i] if ar is not None else np.nan
        ta = total_assets.iloc[i] if total_assets is not None else np.nan
        tl = total_liabilities.iloc[i] if total_liabilities is not None else np.nan
        eq = equity.iloc[i] if equity is not None else np.nan
        ltd = long_term_debt.iloc[i] if long_term_debt is not None else np.nan
        
        # --- PROFITABILITY ---
        kpi['gross_margin'] = safe_divide(gp, rev)
        kpi['operating_margin'] = safe_divide(op, rev)
        kpi['net_margin'] = safe_divide(ni, rev)
        kpi['ebitda_margin'] = safe_divide(ebt, rev)
        
        kpi['roe'] = safe_divide(ni, eq)
        kpi['roa'] = safe_divide(ni, ta)
        
        # ROCE = EBIT / Capital Employed (Total Assets - Current Liabilities)
        capital_employed = ta - cl if not (np.isnan(ta) or np.isnan(cl)) else np.nan
        kpi['roce'] = safe_divide(ebit, capital_employed)
        
        # --- LIQUIDITY ---
        kpi['current_ratio'] = safe_divide(ca, cl)
        kpi['quick_ratio'] = safe_divide(ca - inv if not np.isnan(inv) else ca, cl)
        
        # --- LEVERAGE ---
        kpi['debt_to_equity'] = safe_divide(tl, eq)
        kpi['interest_coverage'] = safe_divide(ebit, ie)
        
        # --- EFFICIENCY (need prior period for turnover) ---
        prev_inv = inventory.iloc[i-1] if (inventory is not None and i > 0) else inv
        avg_inv = (inv + prev_inv) / 2 if not (np.isnan(inv) or np.isnan(prev_inv)) else inv
        kpi['inventory_turnover'] = safe_divide(cgs, avg_inv)
        
        prev_ar = ar.iloc[i-1] if (ar is not None and i > 0) else acc_rec
        avg_ar = (acc_rec + prev_ar) / 2 if not (np.isnan(acc_rec) or np.isnan(prev_ar)) else acc_rec
        kpi['ar_turnover'] = safe_divide(rev, avg_ar)
        
        # Days metrics
        kpi['days_inventory'] = safe_divide(365, kpi['inventory_turnover'])
        kpi['days_ar'] = safe_divide(365, kpi['ar_turnover'])
        
        # --- GROWTH (computed at series level below) ---
        kpi['revenue_growth'] = np.nan
        kpi['ni_growth'] = np.nan
        
        # --- RAW VALUES (for charts) ---
        kpi['revenue'] = rev
        kpi['gross_profit'] = gp
        kpi['operating_profit'] = op
        kpi['ebitda'] = ebt
        kpi['net_income'] = ni
        kpi['total_assets'] = ta
        kpi['equity'] = eq
        kpi['total_liabilities'] = tl
        
        results.append(kpi)
    
    kpi_df = pd.DataFrame(results)
    
    # Growth rates
    if revenue is not None:
        kpi_df['revenue_growth'] = revenue.pct_change().values
    if net_income is not None:
        kpi_df['ni_growth'] = net_income.pct_change().values
    if ebitda is not None:
        kpi_df['ebitda_growth'] = pd.Series(
            [v for v in ebitda], name='ebitda'
        ).pct_change().values
    
    # CAGR calculations (3-year)
    kpi_df['revenue_cagr_3y'] = np.nan
    kpi_df['ebitda_cagr_3y'] = np.nan
    
    if revenue is not None and len(revenue) >= 4:
        for i in range(3, len(revenue)):
            if revenue.iloc[i-3] > 0 and revenue.iloc[i] > 0:
                cagr = (revenue.iloc[i] / revenue.iloc[i-3]) ** (1/3) - 1
                kpi_df.at[i, 'revenue_cagr_3y'] = cagr
    
    if ebitda is not None and len(ebitda) >= 4:
        for i in range(3, len(ebitda)):
            if ebitda.iloc[i-3] > 0 and ebitda.iloc[i] > 0:
                cagr = (ebitda.iloc[i] / ebitda.iloc[i-3]) ** (1/3) - 1
                kpi_df.at[i, 'ebitda_cagr_3y'] = cagr
    
    # Enterprise Value (True Value)
    kpi_df['enterprise_value'] = np.nan
    if ebitda is not None:
        # EV = Normalized EBITDA / Capitalization Rate
        # Using trailing EBITDA as normalized earnings proxy
        kpi_df['enterprise_value'] = kpi_df['ebitda'] / DEFAULT_CAP_RATE
        
        # Adjust for debt (Enterprise Value = Equity Value + Net Debt)
        if long_term_debt is not None and equity is not None:
            kpi_df['equity_value'] = kpi_df['enterprise_value'] - long_term_debt.values
        
        kpi_df['ev_ebitda_multiple'] = np.nan
        if ebitda is not None:
            for i in range(n):
                kpi_df.at[i, 'ev_ebitda_multiple'] = safe_divide(
                    kpi_df.at[i, 'enterprise_value'],
                    kpi_df.at[i, 'ebitda']
                )
    
    return kpi_df


def get_latest_kpis(kpi_df: pd.DataFrame) -> Dict:
    """Get the most recent period's KPIs as a flat dict."""
    if kpi_df.empty:
        return {}
    return kpi_df.iloc[-1].to_dict()


def calculate_summary_stats(kpi_df: pd.DataFrame) -> Dict:
    """Calculate summary statistics for trend analysis."""
    stats = {}
    
    numeric_cols = kpi_df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        series = kpi_df[col].dropna()
        if len(series) > 0:
            stats[col] = {
                'mean': series.mean(),
                'min': series.min(),
                'max': series.max(),
                'latest': series.iloc[-1],
                'trend': 'up' if len(series) > 1 and series.iloc[-1] > series.iloc[0] else 'down'
            }
    
    return stats
