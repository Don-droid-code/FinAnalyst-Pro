"""
charts.py - Plotly Chart Generation Module
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Optional, Dict

# Color palettes
COLORS = {
    'primary': '#6366f1',
    'secondary': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#3b82f6',
    'neutral': '#94a3b8',
}

CHART_COLORS = [
    '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6', '#06b6d4'
]


def get_layout(title: str, dark_mode: bool = False) -> dict:
    bg = '#0f172a' if dark_mode else '#ffffff'
    paper_bg = '#1e293b' if dark_mode else '#f8fafc'
    font_color = '#e2e8f0' if dark_mode else '#1e293b'
    grid_color = '#334155' if dark_mode else '#e2e8f0'
    
    return dict(
        title=dict(text=title, font=dict(size=16, color=font_color, family='Sora, sans-serif')),
        plot_bgcolor=bg,
        paper_bgcolor=paper_bg,
        font=dict(color=font_color, family='Sora, sans-serif'),
        xaxis=dict(gridcolor=grid_color, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=grid_color, showgrid=True, zeroline=False),
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    )


def revenue_chart(df: pd.DataFrame, col_map: Dict, labels: List[str], dark_mode: bool = False) -> Optional[go.Figure]:
    rev_col = col_map.get('revenue')
    if not rev_col or rev_col not in df.columns:
        return None
    
    revenue = pd.to_numeric(df[rev_col], errors='coerce')
    gross_col = col_map.get('gross_profit')
    ni_col = col_map.get('net_income')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=labels, y=revenue, name='Revenue',
        marker_color=COLORS['primary'], opacity=0.9,
        hovertemplate='$%{y:,.0f}<extra>Revenue</extra>'
    ))
    
    if gross_col and gross_col in df.columns:
        gp = pd.to_numeric(df[gross_col], errors='coerce')
        fig.add_trace(go.Bar(
            x=labels, y=gp, name='Gross Profit',
            marker_color=COLORS['success'], opacity=0.9,
            hovertemplate='$%{y:,.0f}<extra>Gross Profit</extra>'
        ))
    
    if ni_col and ni_col in df.columns:
        ni = pd.to_numeric(df[ni_col], errors='coerce')
        fig.add_trace(go.Scatter(
            x=labels, y=ni, name='Net Income',
            mode='lines+markers', line=dict(color=COLORS['warning'], width=3),
            marker=dict(size=8),
            hovertemplate='$%{y:,.0f}<extra>Net Income</extra>'
        ))
    
    layout = get_layout('Revenue, Gross Profit & Net Income', dark_mode)
    layout['barmode'] = 'group'
    fig.update_layout(**layout)
    return fig


def margin_chart(kpi_df: pd.DataFrame, labels: List[str], dark_mode: bool = False) -> Optional[go.Figure]:
    margin_fields = [
        ('gross_margin', 'Gross Margin', COLORS['success']),
        ('operating_margin', 'Operating Margin', COLORS['primary']),
        ('net_margin', 'Net Margin', COLORS['warning']),
        ('ebitda_margin', 'EBITDA Margin', COLORS['info']),
    ]
    
    fig = go.Figure()
    has_data = False
    
    for field, name, color in margin_fields:
        if field in kpi_df.columns:
            values = kpi_df[field] * 100
            if values.notna().any():
                has_data = True
                fig.add_trace(go.Scatter(
                    x=labels, y=values, name=name,
                    mode='lines+markers',
                    line=dict(color=color, width=2.5),
                    marker=dict(size=7),
                    hovertemplate=f'%{{y:.1f}}%<extra>{name}</extra>'
                ))
    
    if not has_data:
        return None
    
    fig.update_layout(**get_layout('Profitability Margins (%)', dark_mode))
    fig.update_yaxes(ticksuffix='%')
    return fig


def kpi_gauge(value: float, title: str, benchmark: float = None, 
              max_val: float = None, is_percentage: bool = True, dark_mode: bool = False) -> go.Figure:
    if max_val is None:
        max_val = max(value * 1.5, (benchmark or value) * 1.5) if value > 0 else 1
    
    font_color = '#e2e8f0' if dark_mode else '#1e293b'
    paper_bg = '#1e293b' if dark_mode else '#f8fafc'
    
    display_val = value * 100 if is_percentage else value
    display_max = max_val * 100 if is_percentage else max_val
    
    steps = [
        {'range': [0, display_max * 0.4], 'color': '#fecaca'},
        {'range': [display_max * 0.4, display_max * 0.7], 'color': '#fde68a'},
        {'range': [display_max * 0.7, display_max], 'color': '#bbf7d0'},
    ]
    
    threshold = None
    if benchmark:
        b_val = benchmark * 100 if is_percentage else benchmark
        threshold = {'line': {'color': COLORS['primary'], 'width': 3}, 'thickness': 0.75, 'value': b_val}
    
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=display_val,
        title={'text': title, 'font': {'size': 13, 'color': font_color}},
        number={'suffix': '%' if is_percentage else 'x', 'font': {'size': 20, 'color': font_color}},
        gauge={
            'axis': {'range': [0, display_max], 'tickcolor': font_color},
            'bar': {'color': COLORS['primary']},
            'steps': steps,
            'threshold': threshold,
        }
    ))
    
    fig.update_layout(
        paper_bgcolor=paper_bg,
        font={'color': font_color, 'family': 'Sora, sans-serif'},
        margin=dict(l=20, r=20, t=40, b=20),
        height=200,
    )
    return fig


def waterfall_chart(df: pd.DataFrame, col_map: Dict, labels: List[str], period_idx: int = -1, dark_mode: bool = False) -> Optional[go.Figure]:
    """P&L waterfall for a single period."""
    fields = ['revenue', 'cogs', 'gross_profit', 'operating_profit', 'net_income']
    field_labels = ['Revenue', 'COGS', 'Gross Profit', 'Op. Profit', 'Net Income']
    
    values = []
    valid_labels = []
    measures = []
    
    prev = 0
    for field, label in zip(fields, field_labels):
        col = col_map.get(field)
        if col and col in df.columns:
            val = pd.to_numeric(df[col], errors='coerce').iloc[period_idx]
            if not pd.isna(val):
                values.append(val)
                valid_labels.append(label)
                if label in ['Revenue', 'Gross Profit', 'Net Income', 'Op. Profit']:
                    measures.append('absolute')
                else:
                    measures.append('relative')
    
    if len(values) < 2:
        return None
    
    font_color = '#e2e8f0' if dark_mode else '#1e293b'
    paper_bg = '#1e293b' if dark_mode else '#f8fafc'
    
    fig = go.Figure(go.Waterfall(
        name='P&L', orientation='v',
        measure=measures,
        x=valid_labels,
        y=values,
        texttemplate='$%{y:,.0f}',
        textposition='outside',
        connector={'line': {'color': COLORS['neutral']}},
        increasing={'marker': {'color': COLORS['success']}},
        decreasing={'marker': {'color': COLORS['danger']}},
        totals={'marker': {'color': COLORS['primary']}},
    ))
    
    label = labels[period_idx] if period_idx < len(labels) else 'Latest Period'
    fig.update_layout(
        title=dict(text=f'P&L Waterfall — {label}', font=dict(size=16, color=font_color)),
        paper_bgcolor=paper_bg,
        plot_bgcolor='#0f172a' if dark_mode else '#ffffff',
        font=dict(color=font_color, family='Sora, sans-serif'),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig


def balance_sheet_chart(kpi_df: pd.DataFrame, labels: List[str], dark_mode: bool = False) -> Optional[go.Figure]:
    if 'total_assets' not in kpi_df.columns:
        return None
    
    fig = go.Figure()
    
    if 'equity' in kpi_df.columns:
        fig.add_trace(go.Bar(
            x=labels, y=kpi_df['equity'], name='Equity',
            marker_color=COLORS['success'], hovertemplate='$%{y:,.0f}<extra>Equity</extra>'
        ))
    
    if 'total_liabilities' in kpi_df.columns:
        fig.add_trace(go.Bar(
            x=labels, y=kpi_df['total_liabilities'], name='Total Liabilities',
            marker_color=COLORS['danger'], hovertemplate='$%{y:,.0f}<extra>Liabilities</extra>'
        ))
    
    if 'total_assets' in kpi_df.columns:
        fig.add_trace(go.Scatter(
            x=labels, y=kpi_df['total_assets'], name='Total Assets',
            mode='lines+markers', line=dict(color=COLORS['primary'], width=3),
            hovertemplate='$%{y:,.0f}<extra>Total Assets</extra>'
        ))
    
    layout = get_layout('Balance Sheet Overview', dark_mode)
    layout['barmode'] = 'stack'
    fig.update_layout(**layout)
    return fig


def ratio_radar(latest_kpis: Dict, dark_mode: bool = False) -> go.Figure:
    """Radar chart comparing KPIs to benchmarks."""
    from config import INDUSTRY_BENCHMARKS
    
    fields = ['gross_margin', 'operating_margin', 'current_ratio', 'roe', 'roa']
    field_labels = ['Gross Margin', 'Op. Margin', 'Current Ratio', 'RoE', 'RoA']
    
    actual_normalized = []
    bench_normalized = []
    valid_labels = []
    
    for f, lbl in zip(fields, field_labels):
        val = latest_kpis.get(f, np.nan)
        bench = INDUSTRY_BENCHMARKS.get(f)
        if not pd.isna(val) and bench and bench != 0:
            # Normalize to benchmark = 1.0
            normalized = min(val / bench, 2.0)
            actual_normalized.append(normalized)
            bench_normalized.append(1.0)
            valid_labels.append(lbl)
    
    if len(valid_labels) < 3:
        return None
    
    font_color = '#e2e8f0' if dark_mode else '#1e293b'
    paper_bg = '#1e293b' if dark_mode else '#f8fafc'
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=actual_normalized + [actual_normalized[0]],
        theta=valid_labels + [valid_labels[0]],
        fill='toself', name='Company',
        line_color=COLORS['primary'], fillcolor=COLORS['primary'],
        opacity=0.5,
    ))
    fig.add_trace(go.Scatterpolar(
        r=bench_normalized + [bench_normalized[0]],
        theta=valid_labels + [valid_labels[0]],
        fill='toself', name='Industry Benchmark',
        line_color=COLORS['neutral'], fillcolor=COLORS['neutral'],
        opacity=0.3,
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 2], color=font_color),
            angularaxis=dict(color=font_color),
            bgcolor='#0f172a' if dark_mode else '#ffffff',
        ),
        paper_bgcolor=paper_bg,
        font=dict(color=font_color, family='Sora, sans-serif'),
        title=dict(text='KPI vs Industry Benchmark (1.0 = Benchmark)', font=dict(size=14, color=font_color)),
        legend=dict(orientation='h', y=-0.1),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def ev_visualization(kpi_df: pd.DataFrame, labels: List[str], dark_mode: bool = False) -> Optional[go.Figure]:
    if 'enterprise_value' not in kpi_df.columns:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=labels, y=kpi_df['enterprise_value'],
        name='Enterprise Value',
        marker_color=COLORS['secondary'],
        hovertemplate='$%{y:,.0f}<extra>Enterprise Value</extra>'
    ))
    
    if 'equity_value' in kpi_df.columns:
        fig.add_trace(go.Bar(
            x=labels, y=kpi_df['equity_value'],
            name='Equity Value',
            marker_color=COLORS['primary'],
            hovertemplate='$%{y:,.0f}<extra>Equity Value</extra>'
        ))
    
    layout = get_layout('Enterprise Value & Equity Value Over Time', dark_mode)
    layout['barmode'] = 'group'
    fig.update_layout(**layout)
    return fig
