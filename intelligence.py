"""
intelligence.py - Intelligent Analysis Engine
Generates business insights, anomaly detection, and recommendations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from config import INDUSTRY_BENCHMARKS, DEFAULT_CAP_RATE


def analyze_all(kpi_df: pd.DataFrame, labels: List[str] = None) -> Dict:
    """
    Run complete intelligent analysis and return structured insights.
    """
    if labels is None:
        labels = [str(i+1) for i in range(len(kpi_df))]
    
    insights = {
        'executive_summary': [],
        'trend_analysis': [],
        'anomalies': [],
        'peer_comparison': [],
        'risk_alerts': [],
        'efficiency_alerts': [],
        'valuation_insight': '',
        'recommendations': [],
        'health_score': 0,
    }
    
    latest = kpi_df.iloc[-1].to_dict() if not kpi_df.empty else {}
    
    # === TREND ANALYSIS ===
    insights['trend_analysis'] = _trend_analysis(kpi_df, labels)
    
    # === ANOMALY DETECTION ===
    insights['anomalies'] = _detect_anomalies(kpi_df, labels)
    
    # === PEER COMPARISON ===
    insights['peer_comparison'] = _peer_comparison(latest)
    
    # === RISK ALERTS ===
    insights['risk_alerts'] = _risk_alerts(latest)
    
    # === EFFICIENCY ALERTS ===
    insights['efficiency_alerts'] = _efficiency_alerts(latest)
    
    # === VALUATION INSIGHT ===
    insights['valuation_insight'] = _valuation_insight(latest)
    
    # === RECOMMENDATIONS ===
    insights['recommendations'] = _generate_recommendations(kpi_df, latest)
    
    # === EXECUTIVE SUMMARY ===
    insights['executive_summary'] = _executive_summary(kpi_df, latest, insights)
    
    # === HEALTH SCORE ===
    insights['health_score'] = _calculate_health_score(latest)
    
    return insights


def _trend_analysis(kpi_df: pd.DataFrame, labels: List[str]) -> List[Dict]:
    trends = []
    
    if len(kpi_df) < 2:
        return [{"type": "info", "message": "Need at least 2 periods for trend analysis."}]
    
    # Revenue trend
    if 'revenue' in kpi_df.columns:
        rev = kpi_df['revenue'].dropna()
        if len(rev) >= 2:
            growth = (rev.iloc[-1] - rev.iloc[-2]) / rev.iloc[-2] * 100
            direction = "📈 increased" if growth > 0 else "📉 decreased"
            label = labels[-1] if labels else "latest period"
            prev_label = labels[-2] if len(labels) >= 2 else "prior period"
            trends.append({
                "type": "positive" if growth > 0 else "negative",
                "icon": "📈" if growth > 0 else "📉",
                "title": "Revenue Trend",
                "message": f"Revenue {direction} by {abs(growth):.1f}% in {label} vs {prev_label}, reaching ${rev.iloc[-1]:,.0f}."
            })
            
            # Multi-year trend
            if len(rev) >= 3:
                overall_growth = (rev.iloc[-1] - rev.iloc[0]) / rev.iloc[0] * 100
                trends.append({
                    "type": "positive" if overall_growth > 0 else "negative",
                    "icon": "📊",
                    "title": "Multi-Period Revenue Trend",
                    "message": f"Revenue has grown {overall_growth:.1f}% overall from {labels[0]} to {labels[-1]}."
                })
    
    # Margin trends
    for field, label in [('gross_margin', 'Gross Margin'), ('operating_margin', 'Operating Margin'), ('net_margin', 'Net Margin')]:
        if field in kpi_df.columns:
            series = kpi_df[field].dropna()
            if len(series) >= 2:
                change = (series.iloc[-1] - series.iloc[-2]) * 100
                pct = series.iloc[-1] * 100
                icon = "📈" if change > 0 else "📉"
                t = "positive" if change > 0 else "negative"
                trends.append({
                    "type": t,
                    "icon": icon,
                    "title": f"{label} Trend",
                    "message": f"{label} is {pct:.1f}%, {'+' if change > 0 else ''}{change:.1f}pp vs prior period."
                })
    
    # EBITDA trend
    if 'ebitda' in kpi_df.columns:
        ebitda = kpi_df['ebitda'].dropna()
        if len(ebitda) >= 2:
            growth = (ebitda.iloc[-1] - ebitda.iloc[-2]) / ebitda.iloc[-2] * 100
            trends.append({
                "type": "positive" if growth > 0 else "negative",
                "icon": "💰",
                "title": "EBITDA Trend",
                "message": f"EBITDA {('grew' if growth > 0 else 'fell')} {abs(growth):.1f}% to ${ebitda.iloc[-1]:,.0f}."
            })
    
    # Net income trend
    if 'net_income' in kpi_df.columns:
        ni = kpi_df['net_income'].dropna()
        if len(ni) >= 2:
            growth = (ni.iloc[-1] - ni.iloc[-2]) / abs(ni.iloc[-2]) * 100 if ni.iloc[-2] != 0 else 0
            trends.append({
                "type": "positive" if growth > 0 else "negative",
                "icon": "💵",
                "title": "Net Income Trend",
                "message": f"Net income {('increased' if growth > 0 else 'decreased')} {abs(growth):.1f}% to ${ni.iloc[-1]:,.0f}."
            })
    
    # CAGR
    if 'revenue_cagr_3y' in kpi_df.columns:
        cagr_val = kpi_df['revenue_cagr_3y'].dropna()
        if len(cagr_val) > 0:
            cagr = cagr_val.iloc[-1] * 100
            trends.append({
                "type": "positive" if cagr > 10 else ("neutral" if cagr > 0 else "negative"),
                "icon": "🚀",
                "title": "3-Year Revenue CAGR",
                "message": f"3-year Revenue CAGR is {cagr:.1f}%. {'Strong compounding growth.' if cagr > 15 else 'Moderate growth trajectory.' if cagr > 5 else 'Growth is below expectations.'}"
            })
    
    return trends


def _detect_anomalies(kpi_df: pd.DataFrame, labels: List[str]) -> List[Dict]:
    anomalies = []
    
    if len(kpi_df) < 3:
        return []
    
    # Check for sudden drops in gross margin
    if 'gross_margin' in kpi_df.columns:
        gm = kpi_df['gross_margin'].dropna()
        for i in range(1, len(gm)):
            change = gm.iloc[i] - gm.iloc[i-1]
            if change < -0.05:  # >5pp drop
                label = labels[i] if i < len(labels) else f"Period {i+1}"
                anomalies.append({
                    "type": "warning",
                    "icon": "⚠️",
                    "title": "Gross Margin Drop",
                    "message": f"Gross margin fell sharply by {abs(change)*100:.1f}pp in {label}. Investigate: pricing pressure, input cost spike, or product mix shift?"
                })
    
    # Revenue decline after growth
    if 'revenue' in kpi_df.columns:
        rev = kpi_df['revenue'].dropna()
        for i in range(1, len(rev)):
            growth = (rev.iloc[i] - rev.iloc[i-1]) / rev.iloc[i-1]
            if growth < -0.10:
                label = labels[i] if i < len(labels) else f"Period {i+1}"
                anomalies.append({
                    "type": "warning",
                    "icon": "🚨",
                    "title": "Revenue Contraction",
                    "message": f"Revenue dropped {abs(growth)*100:.1f}% in {label}. This is a significant decline requiring investigation."
                })
    
    # Net income diverging from revenue
    if 'revenue_growth' in kpi_df.columns and 'ni_growth' in kpi_df.columns:
        for i in range(len(kpi_df)):
            rev_g = kpi_df.at[i, 'revenue_growth'] if not pd.isna(kpi_df.at[i, 'revenue_growth']) else 0
            ni_g = kpi_df.at[i, 'ni_growth'] if not pd.isna(kpi_df.at[i, 'ni_growth']) else 0
            label = labels[i] if i < len(labels) else f"Period {i+1}"
            if rev_g > 0.05 and ni_g < -0.05:
                anomalies.append({
                    "type": "warning",
                    "icon": "🔍",
                    "title": "Profit-Revenue Divergence",
                    "message": f"In {label}, revenue grew {rev_g*100:.1f}% but net income fell {abs(ni_g)*100:.1f}%. Check for hidden cost increases."
                })
    
    # Debt/Equity spike
    if 'debt_to_equity' in kpi_df.columns:
        de = kpi_df['debt_to_equity'].dropna()
        for i in range(1, len(de)):
            change = de.iloc[i] - de.iloc[i-1]
            if change > 0.5:
                label = labels[i] if i < len(labels) else f"Period {i+1}"
                anomalies.append({
                    "type": "warning",
                    "icon": "📊",
                    "title": "Leverage Spike",
                    "message": f"Debt-to-Equity jumped +{change:.2f}x in {label}. Significant new debt taken on — review financing strategy."
                })
    
    if not anomalies:
        anomalies.append({
            "type": "positive",
            "icon": "✅",
            "title": "No Major Anomalies",
            "message": "No significant anomalies detected across the analyzed periods. Data shows consistent patterns."
        })
    
    return anomalies


def _peer_comparison(latest: Dict) -> List[Dict]:
    comparisons = []
    benchmarks = INDUSTRY_BENCHMARKS
    
    comparisons_config = [
        ('gross_margin', 'gross_margin', 'Gross Margin', True),
        ('operating_margin', 'operating_margin', 'Operating Margin', True),
        ('net_margin', 'net_margin', 'Net Margin', True),
        ('ebitda_margin', 'ebitda_margin', 'EBITDA Margin', True),
        ('current_ratio', 'current_ratio', 'Current Ratio', True),
        ('debt_to_equity', 'debt_to_equity', 'Debt-to-Equity', False),  # lower is better
        ('inventory_turnover', 'inventory_turnover', 'Inventory Turnover', True),
        ('roe', 'roe', 'Return on Equity', True),
        ('roa', 'roa', 'Return on Assets', True),
    ]
    
    for field, bench_key, label, higher_better in comparisons_config:
        val = latest.get(field, np.nan)
        bench = benchmarks.get(bench_key)
        
        if pd.isna(val) or bench is None:
            continue
        
        is_better = (val > bench) if higher_better else (val < bench)
        diff = val - bench
        
        if field in ['gross_margin', 'operating_margin', 'net_margin', 'ebitda_margin', 'roe', 'roa']:
            val_str = f"{val*100:.1f}%"
            bench_str = f"{bench*100:.1f}%"
            diff_str = f"{diff*100:+.1f}pp"
        else:
            val_str = f"{val:.2f}x"
            bench_str = f"{bench:.2f}x"
            diff_str = f"{diff:+.2f}x"
        
        comparisons.append({
            "type": "positive" if is_better else "negative",
            "icon": "✅" if is_better else "❌",
            "title": label,
            "message": f"Your {label} is {val_str} vs industry benchmark of {bench_str} ({diff_str} {'above' if diff > 0 else 'below'} benchmark).",
            "value": val,
            "benchmark": bench,
            "field": field
        })
    
    return comparisons


def _risk_alerts(latest: Dict) -> List[Dict]:
    alerts = []
    
    de = latest.get('debt_to_equity', np.nan)
    if not pd.isna(de):
        if de > 3.0:
            alerts.append({"type": "danger", "icon": "🔴", "title": "Critical Leverage Risk",
                "message": f"Debt/Equity ratio of {de:.2f}x is dangerously high. Risk of financial distress if revenue declines."})
        elif de > 2.0:
            alerts.append({"type": "warning", "icon": "🟡", "title": "High Leverage",
                "message": f"Debt/Equity ratio of {de:.2f}x exceeds 2.0x threshold, indicating significant leverage. Monitor covenants."})
        elif de < 0.3:
            alerts.append({"type": "info", "icon": "🟢", "title": "Low Leverage",
                "message": f"Debt/Equity ratio of {de:.2f}x is very conservative. Consider leveraged growth opportunities."})
    
    cr = latest.get('current_ratio', np.nan)
    if not pd.isna(cr):
        if cr < 1.0:
            alerts.append({"type": "danger", "icon": "🔴", "title": "Liquidity Crisis Risk",
                "message": f"Current ratio of {cr:.2f}x means current liabilities exceed current assets. Immediate liquidity risk."})
        elif cr < 1.5:
            alerts.append({"type": "warning", "icon": "🟡", "title": "Tight Liquidity",
                "message": f"Current ratio of {cr:.2f}x is below the 1.5x safety threshold. Build cash reserves."})
    
    ic = latest.get('interest_coverage', np.nan)
    if not pd.isna(ic):
        if ic < 1.5:
            alerts.append({"type": "danger", "icon": "🔴", "title": "Debt Service Risk",
                "message": f"Interest coverage of {ic:.1f}x is critically low. Earnings may not cover interest obligations."})
        elif ic < 3.0:
            alerts.append({"type": "warning", "icon": "🟡", "title": "Low Interest Coverage",
                "message": f"Interest coverage of {ic:.1f}x is below the 3.0x safety standard. Reduce debt or improve EBIT."})
    
    nm = latest.get('net_margin', np.nan)
    if not pd.isna(nm) and nm < 0:
        alerts.append({"type": "danger", "icon": "🔴", "title": "Negative Net Income",
            "message": f"Net margin is {nm*100:.1f}%. The business is currently unprofitable. Immediate corrective action required."})
    
    if not alerts:
        alerts.append({"type": "positive", "icon": "✅", "title": "No Critical Risk Alerts",
            "message": "Key financial risk indicators are within acceptable ranges."})
    
    return alerts


def _efficiency_alerts(latest: Dict) -> List[Dict]:
    alerts = []
    
    it = latest.get('inventory_turnover', np.nan)
    if not pd.isna(it):
        bench = INDUSTRY_BENCHMARKS['inventory_turnover']
        if it < bench * 0.6:
            alerts.append({"type": "warning", "icon": "📦",
                "title": "Low Inventory Turnover",
                "message": f"Inventory turnover of {it:.1f}x is well below the industry standard of {bench:.1f}x. Excess inventory ties up capital and risks obsolescence."})
        elif it > bench * 1.5:
            alerts.append({"type": "info", "icon": "⚡",
                "title": "High Inventory Turnover",
                "message": f"Inventory turnover of {it:.1f}x exceeds benchmarks. Excellent efficiency, but ensure supply chain can keep pace."})
    
    art = latest.get('ar_turnover', np.nan)
    if not pd.isna(art):
        bench = INDUSTRY_BENCHMARKS['ar_turnover']
        dar = latest.get('days_ar', np.nan)
        if art < bench * 0.7:
            alerts.append({"type": "warning", "icon": "💳",
                "title": "Slow Collections",
                "message": f"AR turnover of {art:.1f}x ({dar:.0f} days outstanding) indicates slow collections. Tighten credit terms or collections."})
    
    di = latest.get('days_inventory', np.nan)
    if not pd.isna(di) and di > 90:
        alerts.append({"type": "warning", "icon": "🏭",
            "title": "High Days Inventory",
            "message": f"Inventory is sitting for an average of {di:.0f} days. Review product mix and demand forecasting."})
    
    if not alerts:
        alerts.append({"type": "positive", "icon": "✅",
            "title": "Efficiency Metrics Healthy",
            "message": "Inventory and collections efficiency are within acceptable ranges."})
    
    return alerts


def _valuation_insight(latest: Dict) -> str:
    ev = latest.get('enterprise_value', np.nan)
    eq_val = latest.get('equity_value', np.nan)
    ebitda = latest.get('ebitda', np.nan)
    ev_mult = latest.get('ev_ebitda_multiple', np.nan)
    
    if pd.isna(ev):
        return "Enterprise Value could not be calculated. Ensure EBITDA data is available."
    
    insight = f"""
**Enterprise Value (True Value) = ${ev:,.0f}**

**What is this?** Enterprise Value (EV) represents the *theoretical takeover price* of the business — what an acquirer would pay for the entire operation, regardless of its capital structure. It is calculated by dividing Normalized EBITDA by a capitalization rate of {DEFAULT_CAP_RATE*100:.0f}%, which converts sustainable, recurring earnings into intrinsic business value.

**How to interpret this:**
- An investor or buyer using this methodology would price the business at **${ev:,.0f}**
- This represents **{ev_mult:.1f}x EV/EBITDA**, a common acquisition multiple
- {'The Equity Value (after subtracting net debt) is approximately **$' + f"{eq_val:,.0f}**" if not pd.isna(eq_val) else "Equity Value calculation requires debt data"}

**Key Insight:** The capitalization rate (cap rate) is the investor's required return. A 12% cap rate implies a buyer wants to earn at least 12% annually on this investment. Higher-quality businesses (stable, growing, capital-light) command lower cap rates (8-10%), resulting in higher valuations. Distressed or cyclical businesses face higher cap rates (15-20%), reducing their value.

*Note: This valuation assumes current EBITDA represents sustainable, normalized earnings. One-time items, cyclicality, or recent disruptions should be normalized before relying on this figure.*
"""
    return insight


def _generate_recommendations(kpi_df: pd.DataFrame, latest: Dict) -> List[Dict]:
    recs = []
    
    # Operating expense efficiency
    om = latest.get('operating_margin', np.nan)
    gm = latest.get('gross_margin', np.nan)
    if not (pd.isna(om) or pd.isna(gm)) and gm - om > 0.15:
        recs.append({
            "priority": "High",
            "icon": "💡",
            "title": "Reduce Operating Expenses",
            "action": f"Your gross margin ({gm*100:.1f}%) significantly exceeds your operating margin ({om*100:.1f}%), implying high overhead. Conduct a detailed SG&A review and identify non-essential costs."
        })
    
    # Liquidity improvement
    cr = latest.get('current_ratio', np.nan)
    if not pd.isna(cr) and cr < 1.5:
        recs.append({
            "priority": "High",
            "icon": "💧",
            "title": "Improve Working Capital",
            "action": f"Current ratio of {cr:.2f}x is below optimal. Accelerate accounts receivable collections, negotiate extended supplier payment terms, and review inventory levels."
        })
    
    # Inventory optimization
    it = latest.get('inventory_turnover', np.nan)
    if not pd.isna(it) and it < INDUSTRY_BENCHMARKS['inventory_turnover'] * 0.75:
        recs.append({
            "priority": "Medium",
            "icon": "📦",
            "title": "Optimize Inventory Management",
            "action": f"Inventory turnover of {it:.1f}x is below benchmark. Implement demand-driven inventory planning (JIT/VMI), rationalize SKUs, and consider markdown strategy for slow movers."
        })
    
    # Revenue growth
    if 'revenue_growth' in kpi_df.columns:
        rg = kpi_df['revenue_growth'].dropna()
        if len(rg) > 0 and rg.iloc[-1] < 0.05:
            recs.append({
                "priority": "High",
                "icon": "📈",
                "title": "Accelerate Revenue Growth",
                "action": f"Revenue growth is below 5%. Explore new customer segments, product line extensions, geographic expansion, or pricing optimization to drive top-line growth."
            })
    
    # Debt management
    de = latest.get('debt_to_equity', np.nan)
    if not pd.isna(de) and de > 1.5:
        recs.append({
            "priority": "Medium",
            "icon": "🏦",
            "title": "Deleveraging Strategy",
            "action": f"Debt/Equity of {de:.2f}x is elevated. Prioritize free cash flow towards debt repayment, explore asset monetization, or consider equity raise to strengthen the balance sheet."
        })
    
    # Return on equity
    roe = latest.get('roe', np.nan)
    if not pd.isna(roe) and roe < INDUSTRY_BENCHMARKS['roe']:
        recs.append({
            "priority": "Medium",
            "icon": "💰",
            "title": "Improve Return on Equity",
            "action": f"RoE of {roe*100:.1f}% is below the benchmark of {INDUSTRY_BENCHMARKS['roe']*100:.0f}%. Focus on margin improvement, asset efficiency, or consider share buybacks to enhance returns."
        })
    
    if not recs:
        recs.append({
            "priority": "Low",
            "icon": "🌟",
            "title": "Strong Financial Position",
            "action": "Key metrics are performing well. Focus on sustaining growth momentum, exploring M&A opportunities, or returning capital to shareholders."
        })
    
    return recs


def _executive_summary(kpi_df: pd.DataFrame, latest: Dict, insights: Dict) -> List[str]:
    summary = []
    
    # Revenue position
    rev = latest.get('revenue', np.nan)
    rev_g = kpi_df['revenue_growth'].dropna().iloc[-1] if 'revenue_growth' in kpi_df.columns and len(kpi_df['revenue_growth'].dropna()) > 0 else np.nan
    if not pd.isna(rev):
        growth_str = f", up {rev_g*100:.1f}% YoY" if not pd.isna(rev_g) else ""
        summary.append(f"**Revenue of ${rev:,.0f}{growth_str}**, demonstrating {'strong' if not pd.isna(rev_g) and rev_g > 0.1 else 'moderate' if not pd.isna(rev_g) and rev_g > 0 else 'declining'} top-line momentum.")
    
    # Profitability snapshot
    nm = latest.get('net_margin', np.nan)
    ni = latest.get('net_income', np.nan)
    if not pd.isna(nm) and not pd.isna(ni):
        summary.append(f"**Net income of ${ni:,.0f} ({nm*100:.1f}% margin)** — {'above' if nm > INDUSTRY_BENCHMARKS['net_margin'] else 'below'} industry benchmark of {INDUSTRY_BENCHMARKS['net_margin']*100:.0f}%.")
    
    # Balance sheet health
    de = latest.get('debt_to_equity', np.nan)
    cr = latest.get('current_ratio', np.nan)
    if not pd.isna(de) and not pd.isna(cr):
        bs_health = "strong" if de < 1.0 and cr > 1.5 else "moderate" if de < 2.0 else "stretched"
        summary.append(f"**Balance sheet is {bs_health}** with Debt/Equity of {de:.2f}x and Current Ratio of {cr:.2f}x.")
    
    # EV
    ev = latest.get('enterprise_value', np.nan)
    if not pd.isna(ev):
        summary.append(f"**Enterprise Value estimated at ${ev:,.0f}** based on {DEFAULT_CAP_RATE*100:.0f}% capitalization rate applied to normalized EBITDA.")
    
    # Key risk or positive
    risk_alerts = [r for r in insights.get('risk_alerts', []) if r.get('type') in ('danger', 'warning')]
    if risk_alerts:
        summary.append(f"**⚠️ Key Risk:** {risk_alerts[0]['message']}")
    elif insights.get('health_score', 0) > 75:
        summary.append(f"**Overall financial health is strong** with a composite health score of {insights.get('health_score', 0)}/100. No critical risk flags identified.")
    
    return summary[:5]


def _calculate_health_score(latest: Dict) -> int:
    score = 100
    
    # Profitability (max -30)
    nm = latest.get('net_margin', np.nan)
    if not pd.isna(nm):
        if nm < 0: score -= 30
        elif nm < INDUSTRY_BENCHMARKS['net_margin'] * 0.5: score -= 15
        elif nm < INDUSTRY_BENCHMARKS['net_margin']: score -= 5
    
    # Liquidity (max -20)
    cr = latest.get('current_ratio', np.nan)
    if not pd.isna(cr):
        if cr < 1.0: score -= 20
        elif cr < 1.5: score -= 10
    
    # Leverage (max -20)
    de = latest.get('debt_to_equity', np.nan)
    if not pd.isna(de):
        if de > 3.0: score -= 20
        elif de > 2.0: score -= 10
        elif de > 1.5: score -= 5
    
    # Interest coverage (max -15)
    ic = latest.get('interest_coverage', np.nan)
    if not pd.isna(ic):
        if ic < 1.5: score -= 15
        elif ic < 3.0: score -= 7
    
    # Efficiency (max -10)
    it = latest.get('inventory_turnover', np.nan)
    if not pd.isna(it) and it < INDUSTRY_BENCHMARKS['inventory_turnover'] * 0.5:
        score -= 10
    
    # Growth bonus (max +5)
    if 'revenue_growth' in latest and not pd.isna(latest.get('revenue_growth')):
        if latest['revenue_growth'] > 0.15:
            score = min(100, score + 5)
    
    return max(0, score)
