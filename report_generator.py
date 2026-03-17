"""
report_generator.py - PDF Report Export Module
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
import io


def generate_html_report(
    kpi_df: pd.DataFrame,
    insights: Dict,
    labels: List[str],
    company_name: str = "Company Analysis"
) -> str:
    """Generate a professional HTML report (for PDF export via browser)."""
    
    latest = kpi_df.iloc[-1].to_dict() if not kpi_df.empty else {}
    health_score = insights.get('health_score', 0)
    
    def fmt_pct(val, decimals=1):
        if pd.isna(val):
            return "N/A"
        return f"{val*100:.{decimals}f}%"
    
    def fmt_money(val):
        if pd.isna(val):
            return "N/A"
        if abs(val) >= 1_000_000:
            return f"${val/1_000_000:.2f}M"
        elif abs(val) >= 1_000:
            return f"${val/1_000:.1f}K"
        return f"${val:.0f}"
    
    def fmt_ratio(val, decimals=2):
        if pd.isna(val):
            return "N/A"
        return f"{val:.{decimals}f}x"
    
    # Build summary rows
    kpi_table_rows = ""
    kpi_rows = [
        ("Gross Margin", fmt_pct(latest.get('gross_margin'))),
        ("Operating Margin", fmt_pct(latest.get('operating_margin'))),
        ("Net Margin", fmt_pct(latest.get('net_margin'))),
        ("EBITDA Margin", fmt_pct(latest.get('ebitda_margin'))),
        ("Return on Equity", fmt_pct(latest.get('roe'))),
        ("Return on Assets", fmt_pct(latest.get('roa'))),
        ("Current Ratio", fmt_ratio(latest.get('current_ratio'))),
        ("Quick Ratio", fmt_ratio(latest.get('quick_ratio'))),
        ("Debt/Equity", fmt_ratio(latest.get('debt_to_equity'))),
        ("Interest Coverage", fmt_ratio(latest.get('interest_coverage'))),
        ("Inventory Turnover", fmt_ratio(latest.get('inventory_turnover'))),
        ("AR Turnover", fmt_ratio(latest.get('ar_turnover'))),
        ("Revenue CAGR (3Y)", fmt_pct(latest.get('revenue_cagr_3y'))),
        ("Enterprise Value", fmt_money(latest.get('enterprise_value'))),
    ]
    
    for i, (name, val) in enumerate(kpi_rows):
        bg = "#f8fafc" if i % 2 == 0 else "#ffffff"
        kpi_table_rows += f'<tr style="background:{bg}"><td style="padding:8px 12px;font-weight:500">{name}</td><td style="padding:8px 12px;text-align:right;font-weight:700;color:#6366f1">{val}</td></tr>'
    
    # Executive summary
    exec_summary_html = ""
    for bullet in insights.get('executive_summary', []):
        exec_summary_html += f'<li style="margin-bottom:8px">{bullet}</li>'
    
    # Recommendations
    recs_html = ""
    for rec in insights.get('recommendations', []):
        color = '#dc2626' if rec.get('priority') == 'High' else '#d97706' if rec.get('priority') == 'Medium' else '#059669'
        recs_html += f'''
        <div style="border-left:4px solid {color};padding:12px 16px;margin-bottom:12px;background:#fafafa;border-radius:0 8px 8px 0">
            <div style="font-weight:700;margin-bottom:4px">{rec.get("icon","")} {rec.get("title","")} <span style="font-size:11px;color:{color};font-weight:600;margin-left:8px">{rec.get("priority","")} Priority</span></div>
            <div style="color:#475569;font-size:13px">{rec.get("action","")}</div>
        </div>'''
    
    score_color = '#059669' if health_score >= 75 else '#d97706' if health_score >= 50 else '#dc2626'
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Financial Analysis Report — {company_name}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');
  body {{ font-family: 'Sora', sans-serif; margin: 0; padding: 0; color: #1e293b; background: #fff; }}
  .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 40px 50px; }}
  .header h1 {{ margin: 0 0 8px; font-size: 28px; font-weight: 700; }}
  .header p {{ margin: 0; opacity: 0.85; font-size: 14px; }}
  .section {{ padding: 30px 50px; border-bottom: 1px solid #e2e8f0; }}
  .section h2 {{ color: #6366f1; font-size: 18px; margin-bottom: 16px; }}
  .health-badge {{ display: inline-block; background: {score_color}; color: white; padding: 6px 16px; border-radius: 20px; font-weight: 700; font-size: 14px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ background: #6366f1; color: white; padding: 10px 12px; text-align: left; font-size: 13px; }}
  .footer {{ text-align: center; padding: 20px; color: #94a3b8; font-size: 11px; }}
</style>
</head>
<body>

<div class="header">
  <h1>📊 {company_name}</h1>
  <p>Financial Analysis Report &nbsp;|&nbsp; Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
  <p style="margin-top:12px">Analysis Period: {labels[0] if labels else 'N/A'} – {labels[-1] if labels else 'N/A'} &nbsp;|&nbsp; 
     Financial Health Score: <span class="health-badge">{health_score}/100</span></p>
</div>

<div class="section">
  <h2>Executive Summary</h2>
  <ul style="line-height:1.8;color:#475569">
    {exec_summary_html}
  </ul>
</div>

<div class="section">
  <h2>Key Performance Indicators (Latest Period)</h2>
  <table>
    <tr><th>KPI</th><th style="text-align:right">Value</th></tr>
    {kpi_table_rows}
  </table>
</div>

<div class="section">
  <h2>Strategic Recommendations</h2>
  {recs_html}
</div>

<div class="section">
  <h2>Valuation Analysis</h2>
  <div style="background:#faf5ff;border:1px solid #d8b4fe;border-radius:8px;padding:16px;font-size:13px;line-height:1.7;color:#4c1d95">
    {insights.get('valuation_insight','').replace('**', '').replace('\n', '<br>')}
  </div>
</div>

<div class="footer">
  <p>FinAnalyst Pro | Confidential Financial Analysis | {datetime.now().year}</p>
  <p>This report is for internal analytical purposes only. All projections are estimates based on historical data.</p>
</div>

</body>
</html>"""
    
    return html


def kpi_to_csv(kpi_df: pd.DataFrame, labels: List[str]) -> str:
    """Export KPI data to CSV string."""
    export_df = kpi_df.copy()
    if labels:
        export_df.insert(0, 'Period', labels[:len(kpi_df)])
    
    # Format percentage columns
    pct_cols = ['gross_margin', 'operating_margin', 'net_margin', 'ebitda_margin', 
                'roe', 'roa', 'roce', 'revenue_growth', 'revenue_cagr_3y', 'ebitda_cagr_3y']
    for col in pct_cols:
        if col in export_df.columns:
            export_df[col] = export_df[col].apply(
                lambda x: f"{x*100:.2f}%" if not pd.isna(x) else "N/A"
            )
    
    return export_df.to_csv(index=False)
