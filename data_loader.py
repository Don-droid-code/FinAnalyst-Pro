"""
data_loader.py - Data Import, Multi-File Merging & Google Sheets Module
Handles: Excel, CSV, multiple files, and Google Sheets (public URLs)
"""

import pandas as pd
import numpy as np
import re
import io
import json
from typing import Optional, Tuple, Dict, List, Any
from config import COLUMN_PATTERNS, STATEMENT_TYPE_SIGNALS


# ─── SINGLE FILE LOADING ───────────────────────────────────────────────────────

def load_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str], List[str]]:
    """Load Excel or CSV. Returns (df, error, sheet_names)."""
    try:
        filename = uploaded_file.name.lower()
        if filename.endswith('.csv'):
            df = _load_csv(uploaded_file)
            return df, None, ["Sheet1"]
        elif filename.endswith(('.xlsx', '.xls')):
            return _load_excel(uploaded_file)
        else:
            return None, "Unsupported format. Upload .xlsx, .xls, or .csv", []
    except Exception as e:
        return None, f"Error loading file: {str(e)}", []


def _load_csv(file) -> pd.DataFrame:
    """Auto-detect separator and encoding."""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    separators = [',', ';', '\t', '|']
    for encoding in encodings:
        for sep in separators:
            try:
                file.seek(0)
                df = pd.read_csv(file, sep=sep, encoding=encoding, thousands=',')
                if len(df.columns) > 1:
                    return df
            except Exception:
                continue
    file.seek(0)
    return pd.read_csv(file)


def _load_excel(file) -> Tuple[Optional[pd.DataFrame], Optional[str], List[str]]:
    try:
        xl = pd.ExcelFile(file)
        sheet_names = xl.sheet_names
        df = xl.parse(sheet_names[0], thousands=',')
        return df, None, sheet_names
    except Exception as e:
        return None, f"Excel load error: {str(e)}", []


def load_excel_sheet(file, sheet_name: str) -> Optional[pd.DataFrame]:
    try:
        return pd.read_excel(file, sheet_name=sheet_name, thousands=',')
    except Exception:
        return None


# ─── GOOGLE SHEETS ─────────────────────────────────────────────────────────────

def parse_google_sheets_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract spreadsheet ID and optional gid from URL."""
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9_-]+)', url)
    if not match:
        return None, None
    spreadsheet_id = match.group(1)
    gid_match = re.search(r'[#&?]gid=(\d+)', url)
    gid = gid_match.group(1) if gid_match else None
    return spreadsheet_id, gid


def build_gsheets_csv_url(spreadsheet_id: str, gid: Optional[str] = None) -> str:
    """Build the public CSV export URL for a Google Sheet."""
    base = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"
    if gid:
        base += f"&gid={gid}"
    return base


def load_google_sheet(url: str) -> Tuple[Optional[pd.DataFrame], Optional[str], List[str]]:
    """
    Fetch a public Google Sheet as a DataFrame.
    Returns (df, error_message, sheet_names).
    Sheet must be published to web or shared as 'Anyone with link can view'.
    """
    try:
        import urllib.request

        spreadsheet_id, gid = parse_google_sheets_url(url)
        if not spreadsheet_id:
            return None, "Invalid Google Sheets URL. Must contain '/spreadsheets/d/'.", []

        csv_url = build_gsheets_csv_url(spreadsheet_id, gid)
        req = urllib.request.Request(csv_url, headers={'User-Agent': 'FinAnalystPro/2.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')

        df = pd.read_csv(io.StringIO(content), thousands=',')
        df = clean_dataframe(df)
        return df, None, ["Sheet1"]

    except Exception as e:
        err = str(e)
        if "403" in err or "Forbidden" in err:
            return None, (
                "Access denied (403). The sheet must be publicly accessible.\n"
                "In Google Sheets: File → Share → Publish to the web → CSV → Publish.\n"
                "Or: Share → Anyone with the link → Viewer."
            ), []
        elif "404" in err:
            return None, "Sheet not found (404). Verify the URL.", []
        elif "timed out" in err.lower() or "timeout" in err.lower():
            return None, "Connection timed out. Check the URL or your internet connection.", []
        else:
            return None, f"Could not fetch Google Sheet: {err}", []


# ─── CLEANING & DETECTION ──────────────────────────────────────────────────────

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize: strip whitespace, parse numbers, drop empty rows/cols."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how='all').dropna(axis=1, how='all')

    for col in df.columns:
        if df[col].dtype == object:
            cleaned = df[col].astype(str).str.strip()
            cleaned = cleaned.str.replace(r'[$€£¥\s]', '', regex=True)
            cleaned = cleaned.str.replace(r',(?=\d{3})', '', regex=True)
            cleaned = cleaned.str.replace(r'\((\d+\.?\d*)\)', r'-\1', regex=True)
            try:
                converted = pd.to_numeric(cleaned, errors='coerce')
                if converted.notna().sum() / max(len(converted), 1) > 0.5:
                    df[col] = converted
            except Exception:
                pass
    return df


def auto_detect_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Auto-detect financial column mappings using 3-pass strategy:
    Pass 1 — Exact match
    Pass 2 — Substring containment
    Pass 3 — Token overlap (word-level fuzzy)
    Supports English, French, German, Spanish and abbreviations.
    """
    col_map = {key: None for key in COLUMN_PATTERNS.keys()}
    columns_lower = {col.lower().strip(): col for col in df.columns}

    for field, patterns in COLUMN_PATTERNS.items():
        # Pass 1: exact
        for pattern in patterns:
            p = pattern.lower()
            if p in columns_lower:
                col_map[field] = columns_lower[p]
                break
        if col_map[field]:
            continue

        # Pass 2: substring
        for pattern in patterns:
            p = pattern.lower()
            for col_lower, col_original in columns_lower.items():
                if p in col_lower or col_lower in p:
                    col_map[field] = col_original
                    break
            if col_map[field]:
                break
        if col_map[field]:
            continue

        # Pass 3: token overlap
        stop = {'', 'of', 'the', 'and', 'des', 'les', 'von', 'la', 'le', 'de', 'du'}
        for pattern in patterns:
            p_tokens = set(re.split(r'\W+', pattern.lower())) - stop
            if not p_tokens:
                continue
            for col_lower, col_original in columns_lower.items():
                c_tokens = set(re.split(r'\W+', col_lower)) - stop
                overlap = p_tokens & c_tokens
                if overlap and len(overlap) >= min(2, len(p_tokens)):
                    col_map[field] = col_original
                    break
            if col_map[field]:
                break

    return col_map


def get_mapping_confidence(col_map: Dict, df: pd.DataFrame) -> Dict[str, str]:
    """Return 'exact', 'fuzzy', or 'missing' confidence per field."""
    confidence = {}
    for field, mapped_col in col_map.items():
        if mapped_col is None:
            confidence[field] = 'missing'
            continue
        exact = any(
            p.lower() == mapped_col.lower().strip()
            for p in COLUMN_PATTERNS.get(field, [])
        )
        confidence[field] = 'exact' if exact else 'fuzzy'
    return confidence


def detect_period_column(df: pd.DataFrame) -> Optional[str]:
    """Identify the column representing fiscal periods."""
    for col in df.columns:
        col_l = col.lower().strip()
        if any(d in col_l for d in ['date', 'period', 'year', 'month', 'quarter', 'fy',
                                     'année', 'exercice', 'jahr', 'año', 'periodo']):
            return col
    # Fallback: integer column in year range
    for col in df.columns:
        try:
            nums = pd.to_numeric(df[col].dropna(), errors='coerce').dropna()
            if len(nums) > 0 and nums.between(2000, 2099).mean() > 0.7:
                return col
        except Exception:
            pass
    return None


def detect_date_column(df: pd.DataFrame) -> Optional[str]:
    return detect_period_column(df)


def get_numeric_series(df: pd.DataFrame, column: Optional[str]) -> Optional[pd.Series]:
    if column is None or column not in df.columns:
        return None
    series = pd.to_numeric(df[column], errors='coerce')
    return series if series.notna().any() else None


def validate_data_quality(df: pd.DataFrame, col_map: Dict) -> Dict:
    warnings_list = []
    detected = []
    missing = []
    critical_fields = ['revenue', 'cogs', 'net_income', 'total_assets', 'equity']

    for field, col in col_map.items():
        if col and col in df.columns:
            detected.append(f"{field} → '{col}'")
            null_pct = df[col].isna().mean() * 100
            if null_pct > 20:
                warnings_list.append(f"'{col}' has {null_pct:.0f}% missing values")
        elif field in critical_fields:
            missing.append(field)

    return {
        "detected": detected,
        "missing_critical": missing,
        "warnings": warnings_list,
        "row_count": len(df),
        "quality_score": max(0, 100 - len(missing) * 15 - len(warnings_list) * 5),
    }


def aggregate_to_periods(df: pd.DataFrame, col_map: Dict, date_col: Optional[str]) -> pd.DataFrame:
    if date_col and date_col in df.columns:
        try:
            df = df.copy()
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce', infer_datetime_format=True)
            df = df.sort_values(date_col)
        except Exception:
            pass
    return df


# ─── STATEMENT TYPE DETECTION ──────────────────────────────────────────────────

def detect_statement_type(df: pd.DataFrame) -> str:
    """Detect which financial statement a DataFrame represents."""
    col_map = auto_detect_columns(df)
    detected = set(k for k, v in col_map.items() if v is not None)

    scores = {}
    for stmt_type, signals in STATEMENT_TYPE_SIGNALS.items():
        scores[stmt_type] = sum(1 for f in signals if f in detected)

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"


# ─── MULTI-FILE MERGING ────────────────────────────────────────────────────────

def normalize_period_value(val) -> Optional[str]:
    """Normalize a single period value to a comparable string."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    try:
        dt = pd.to_datetime(s, infer_datetime_format=True)
        return str(dt.year)
    except Exception:
        s = re.sub(r'FY\s*', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\.0$', '', s)
        return s.strip()


def merge_multiple_files(file_infos: List[Dict]) -> Tuple[Optional[pd.DataFrame], Optional[str], List[str]]:
    """
    Merge multiple financial DataFrames into one unified dataset aligned by period.

    file_infos list items:
      'df'         : pd.DataFrame
      'label'      : str (display name)
      'period_col' : str | None (column holding periods in this file)

    Returns (merged_df, error, period_labels)
    """
    if not file_infos:
        return None, "No files to merge.", []

    try:
        frames_with_period = []

        for info in file_infos:
            df = info['df'].copy()
            period_col = info.get('period_col') or detect_period_column(df)

            if period_col and period_col in df.columns:
                df['_period'] = [normalize_period_value(v) for v in df[period_col]]
                if period_col != '_period':
                    df = df.drop(columns=[period_col])
            else:
                df['_period'] = [f"Period {i+1}" for i in range(len(df))]

            frames_with_period.append(df)

        # Single file — just return it
        if len(frames_with_period) == 1:
            df_out = frames_with_period[0].copy()
            periods = df_out['_period'].tolist()
            df_out = df_out.drop(columns=['_period'])
            return df_out, None, periods

        # Outer-merge all frames on _period
        merged = frames_with_period[0]
        for frame in frames_with_period[1:]:
            existing_cols = set(merged.columns) - {'_period'}
            incoming_cols = set(frame.columns) - {'_period'}
            overlap = existing_cols & incoming_cols
            if overlap:
                frame = frame.rename(columns={c: f"{c}__r" for c in overlap})
            merged = pd.merge(merged, frame, on='_period', how='outer')

        # Sort periods
        merged = merged.sort_values('_period').reset_index(drop=True)
        periods = merged['_period'].tolist()
        merged = merged.drop(columns=['_period'])

        # Consolidate duplicates (prefer first non-null)
        merged = _consolidate_duplicate_columns(merged)

        return merged, None, [str(p) for p in periods]

    except Exception as e:
        import traceback
        return None, f"Merge error: {str(e)}\n{traceback.format_exc()}", []


def _consolidate_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Coalesce columns that represent the same field (e.g., 'Revenue' and 'Revenue__r')."""
    base_map: Dict[str, List[str]] = {}
    for col in df.columns:
        base = re.sub(r'__r\d*$', '', col)
        base_map.setdefault(base, []).append(col)

    result = pd.DataFrame(index=df.index)
    for base, cols in base_map.items():
        if len(cols) == 1:
            result[base] = df[cols[0]]
        else:
            combined = df[cols[0]].copy()
            for extra in cols[1:]:
                combined = combined.combine_first(df[extra])
            result[base] = combined
    return result


# ─── SAMPLE DATA ──────────────────────────────────────────────────────────────

def generate_sample_data(preset_name: str = None) -> pd.DataFrame:
    """Generate sample financial data, optionally from a named preset."""
    from config import SAMPLE_PRESETS

    if preset_name and preset_name in SAMPLE_PRESETS:
        return pd.DataFrame(SAMPLE_PRESETS[preset_name]["data"])

    # Default generic 4-year dataset
    return pd.DataFrame({
        "Year":               [2021,       2022,       2023,       2024],
        "Revenue":            [4_200_000,  5_100_000,  5_800_000,  6_350_000],
        "COGS":               [2_520_000,  2_958_000,  3_248_000,  3_492_500],
        "Gross Profit":       [1_680_000,  2_142_000,  2_552_000,  2_857_500],
        "Operating Profit":   [756_000,    918_000,    986_000,    1_079_500],
        "EBITDA":             [945_000,    1_122_000,  1_218_000,  1_333_500],
        "Interest Expense":   [126_000,    153_000,    174_000,    190_500],
        "Net Income":         [504_000,    637_500,    696_000,    825_500],
        "Total Assets":       [5_250_000,  6_375_000,  7_250_000,  7_937_500],
        "Current Assets":     [1_890_000,  2_295_000,  2_610_000,  2_857_500],
        "Current Liabilities":[1_050_000,  1_275_000,  1_450_000,  1_587_500],
        "Inventory":          [630_000,    765_000,    870_000,    952_500],
        "Accounts Receivable":[840_000,    1_020_000,  1_160_000,  1_270_000],
        "Total Liabilities":  [2_625_000,  3_187_500,  3_625_000,  3_968_750],
        "Total Equity":       [2_625_000,  3_187_500,  3_625_000,  3_968_750],
        "Long Term Debt":     [1_575_000,  1_912_500,  2_175_000,  2_381_250],
    })


def generate_split_sample_files() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate three separate sample statements (P&L, Balance Sheet, Cash Flow)
    to demonstrate multi-file merging. Uses intentionally different column names.
    """
    years = [2021, 2022, 2023, 2024]

    pl = pd.DataFrame({
        "Fiscal Year":      years,
        "Net Revenue":      [4_200_000, 5_100_000, 5_800_000, 6_350_000],
        "Cost of Sales":    [2_520_000, 2_958_000, 3_248_000, 3_492_500],
        "Gross Profit":     [1_680_000, 2_142_000, 2_552_000, 2_857_500],
        "Operating Income": [756_000,   918_000,   986_000,   1_079_500],
        "EBITDA":           [945_000,   1_122_000, 1_218_000, 1_333_500],
        "Finance Costs":    [126_000,   153_000,   174_000,   190_500],
        "Profit After Tax": [504_000,   637_500,   696_000,   825_500],
    })

    bs = pd.DataFrame({
        "FY":                    years,
        "Total Assets":          [5_250_000, 6_375_000, 7_250_000, 7_937_500],
        "Current Assets":        [1_890_000, 2_295_000, 2_610_000, 2_857_500],
        "Current Liabilities":   [1_050_000, 1_275_000, 1_450_000, 1_587_500],
        "Inventories":           [630_000,   765_000,   870_000,   952_500],
        "Trade Receivables":     [840_000,   1_020_000, 1_160_000, 1_270_000],
        "Total Liabilities":     [2_625_000, 3_187_500, 3_625_000, 3_968_750],
        "Shareholders Equity":   [2_625_000, 3_187_500, 3_625_000, 3_968_750],
        "Long-term Debt":        [1_575_000, 1_912_500, 2_175_000, 2_381_250],
    })

    cf = pd.DataFrame({
        "Period":               years,
        "Operating Cash Flow":  [882_000,   1_090_000, 1_218_000, 1_397_000],
        "Capital Expenditure":  [-315_000,  -382_500,  -435_000,  -476_250],
        "Free Cash Flow":       [567_000,   707_500,   783_000,   920_750],
    })

    return pl, bs, cf
