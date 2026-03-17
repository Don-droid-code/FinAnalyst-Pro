# 📊 FinAnalyst Pro v2.0

**Professional financial analysis for real-world messy data.**

## 🚀 Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## ✨ What's New in v2.0

### 1. Multi-File Upload & Merge
- Upload P&L, Balance Sheet, and Cash Flow as separate files
- Auto-detects which file is which (income statement / balance sheet / cash flow)
- Aligns datasets by fiscal period using outer-join merging
- Handles different time ranges across files
- Preview merged dataset before analysis

### 2. Google Sheets Integration
- Paste any public Google Sheets URL
- Auto-fetches and processes the data
- Same auto-detection and KPI logic applies
- Works with: File → Share → Publish to web → CSV

### 3. Enhanced Column Mapping
- 3-pass detection: Exact → Substring → Token overlap
- **Multilingual**: English, French, German, Spanish, Italian
- **Abbreviations**: CA → Revenue, EBE → EBITDA, PAT → Net Income, etc.
- Confidence badges: ✅ Exact · 🔶 Fuzzy · ❌ Missing
- Save/load named mapping profiles
- Export/import mappings as JSON
- KPI availability preview (shows which KPIs are disabled by missing fields)

### 4. Sample Data Presets
- 🛒 Retail Company (high-volume, low-margin, inventory-intensive)
- 🏭 Manufacturing Company (asset-heavy, capital-intensive)
- 🚀 SaaS Startup (high-growth, early losses, then profitability)
- 🏥 Healthcare Company (stable, recurring, regulated)

## 📁 Project Structure
```
finanalyst/
├── app.py                # Main Streamlit application (v2)
├── config.py             # Settings, benchmarks, presets, multilingual patterns
├── data_loader.py        # Single/multi-file loading, Google Sheets, merge engine
├── mapping_ui.py         # Enhanced column mapping interface
├── kpi_engine.py         # 30+ KPI calculations
├── intelligence.py       # Trends, anomalies, recommendations
├── charts.py             # Plotly visualizations
├── report_generator.py   # HTML/CSV export
├── database.py           # SQL integration placeholder
└── requirements.txt
```

## 🌐 Google Sheets Setup
For a private sheet:
1. File → Share → Publish to the web → Entire Document → CSV → Publish
2. Copy the published URL and paste into FinAnalyst Pro

For a "anyone with link" sheet:
1. Share → Get link → Anyone with the link → Viewer
2. Paste the share URL directly

## 🔗 Column Mapping Profiles
Save time on recurring reports:
1. Map columns for your company once
2. Click "Save Profile" and give it a name
3. Next upload: Load the profile → all mappings applied instantly
4. Export as JSON to share with colleagues

## 🗺️ Supported Languages (Column Names)
| Field       | English             | French                    | German              | Spanish              |
|-------------|---------------------|---------------------------|---------------------|----------------------|
| Revenue     | Revenue, Sales, Net Sales | Chiffre d'affaires, Ventes | Umsatz, Erlöse     | Ingresos, Ventas     |
| Net Income  | Net Income, PAT     | Résultat net              | Jahresüberschuss    | Resultado neto       |
| COGS        | COGS, Cost of Sales | Coût des ventes           | Wareneinsatz        | Coste de ventas      |
| Equity      | Equity, Shareholders' Equity | Capitaux propres | Eigenkapital       | Patrimonio neto      |
| EBITDA      | EBITDA              | EBE                       | EBITDA              | EBITDA               |

## 📊 KPIs Calculated (30+)
Profitability: Gross/Operating/Net/EBITDA Margins, RoE, RoA, RoCE  
Liquidity: Current Ratio, Quick Ratio  
Leverage: Debt/Equity, Interest Coverage  
Efficiency: Inventory Turnover, AR Turnover, Days metrics  
Growth: YoY, 3-Year CAGR (Revenue & EBITDA)  
Valuation: Enterprise Value, Equity Value, EV/EBITDA, Sensitivity Table  
