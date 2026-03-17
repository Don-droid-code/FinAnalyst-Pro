"""
Configuration settings for FinAnalyst Pro
"""

APP_NAME = "FinAnalyst Pro"
APP_VERSION = "2.0.0"

# Industry benchmark defaults
INDUSTRY_BENCHMARKS = {
    "gross_margin": 0.35,
    "operating_margin": 0.15,
    "net_margin": 0.10,
    "ebitda_margin": 0.18,
    "current_ratio": 1.5,
    "quick_ratio": 1.0,
    "debt_to_equity": 1.0,
    "interest_coverage": 3.0,
    "inventory_turnover": 6.0,
    "ar_turnover": 8.0,
    "roe": 0.15,
    "roa": 0.08,
}

# ─── EXTENDED COLUMN PATTERNS (English + French + German + Spanish + abbreviations) ───
COLUMN_PATTERNS = {
    "revenue": [
        # English
        "revenue", "revenues", "sales", "net sales", "total revenue", "total revenues",
        "turnover", "net revenue", "total sales", "gross sales", "net turnover",
        "total turnover", "sales revenue", "operating revenue",
        # Abbreviations
        "rev", "ca", "tot rev",
        # French
        "chiffre d'affaires", "chiffre daffaires", "ventes", "produits des ventes",
        "recettes", "produits", "ca net", "ventes nettes",
        # German
        "umsatz", "umsatzerlöse", "erlöse", "gesamtumsatz",
        # Spanish
        "ingresos", "ventas", "facturación", "ingresos netos", "importe neto de la cifra de negocios",
        # Italian
        "ricavi", "fatturato", "ricavi delle vendite",
    ],
    "cogs": [
        "cogs", "cost of goods sold", "cost of sales", "cost of revenue",
        "cost of products", "cost of products sold", "cost of merchandise",
        "direct costs", "production costs", "manufacturing costs",
        # Abbreviations
        "cgs", "cos",
        # French
        "coût des ventes", "cout des ventes", "coût des marchandises vendues",
        "coût de production", "achats consommés",
        # German
        "herstellungskosten", "wareneinsatz", "materialaufwand",
        # Spanish
        "coste de ventas", "costo de ventas", "coste de los bienes vendidos",
    ],
    "gross_profit": [
        "gross profit", "gross income", "gross margin value",
        "marge brute", "résultat brut", "bénéfice brut",
        "bruttogewinn", "bruttomarge",
        "beneficio bruto", "margen bruto",
    ],
    "operating_profit": [
        "operating profit", "operating income", "ebit", "income from operations",
        "operating earnings", "operating result", "profit from operations",
        "trading profit", "operating surplus",
        # French
        "résultat d'exploitation", "resultat exploitation", "bénéfice d'exploitation",
        "résultat opérationnel",
        # German
        "betriebsergebnis", "betriebsgewinn", "ebit",
        # Spanish
        "resultado de explotación", "beneficio operativo", "resultado operativo",
    ],
    "ebitda": [
        "ebitda", "earnings before interest tax depreciation amortization",
        "earnings before interest taxes depreciation and amortization",
        "ebita",
        # French
        "excédent brut d'exploitation", "ebe",
        # German
        "ebitda",
        # Spanish
        "ebitda", "resultado antes de intereses impuestos depreciación y amortización",
    ],
    "net_income": [
        "net income", "net profit", "net earnings", "profit after tax", "pat",
        "net income attributable", "bottom line", "profit for the year",
        "profit for the period", "net result", "net loss",
        # Abbreviations
        "ni", "np",
        # French
        "résultat net", "bénéfice net", "résultat de l'exercice",
        "résultat net part du groupe",
        # German
        "jahresüberschuss", "nettoeinkommen", "reingewinn",
        # Spanish
        "resultado neto", "beneficio neto", "utilidad neta",
    ],
    "interest_expense": [
        "interest expense", "interest paid", "finance costs", "interest charges",
        "interest cost", "net interest expense", "borrowing costs",
        # French
        "charges financières", "intérêts payés", "frais financiers",
        # German
        "zinsaufwand", "finanzierungskosten",
        # Spanish
        "gastos financieros", "intereses pagados",
    ],
    "tax": [
        "tax", "income tax", "tax expense", "provision for income taxes",
        "income tax expense", "taxes", "taxation",
        # French
        "impôts sur les bénéfices", "charge fiscale",
        # German
        "ertragsteuern", "steueraufwand",
        # Spanish
        "impuesto sobre beneficios", "gasto por impuesto",
    ],
    "depreciation": [
        "depreciation", "d&a", "depreciation and amortization",
        "depreciation & amortization", "amortization", "d and a",
        "depreciation amortization", "da",
        # French
        "dotations aux amortissements", "amortissements",
        # German
        "abschreibungen",
        # Spanish
        "depreciación y amortización", "amortizaciones",
    ],
    "current_assets": [
        "current assets", "total current assets", "short-term assets",
        "actifs courants", "actifs circulants",
        "umlaufvermögen",
        "activos corrientes", "activos circulantes",
    ],
    "current_liabilities": [
        "current liabilities", "total current liabilities", "short-term liabilities",
        "current obligations",
        "passifs courants", "dettes à court terme",
        "kurzfristige verbindlichkeiten",
        "pasivos corrientes", "pasivos circulantes",
    ],
    "inventory": [
        "inventory", "inventories", "stock", "stocks", "merchandise", "raw materials",
        # French
        "stocks", "inventaires",
        # German
        "vorräte", "bestände",
        # Spanish
        "inventarios", "existencias",
    ],
    "accounts_receivable": [
        "accounts receivable", "ar", "trade receivables", "debtors", "receivables",
        "trade debtors", "net receivables", "customer receivables",
        # French
        "créances clients", "créances commerciales",
        # German
        "forderungen aus lieferungen", "forderungen",
        # Spanish
        "deudores comerciales", "cuentas por cobrar",
    ],
    "total_assets": [
        "total assets", "assets total", "total asset",
        "total actif", "total des actifs",
        "bilanzsumme", "gesamtvermögen",
        "total activos", "activo total",
    ],
    "total_liabilities": [
        "total liabilities", "total debt and liabilities", "liabilities total",
        "total obligations",
        "total passif", "total des passifs", "total dettes",
        "gesamtverbindlichkeiten",
        "total pasivos", "pasivo total",
    ],
    "equity": [
        "equity", "shareholders equity", "total equity", "stockholders equity",
        "net worth", "shareholders funds", "book value", "owners equity",
        "total shareholders equity",
        # French
        "capitaux propres", "fonds propres",
        # German
        "eigenkapital",
        # Spanish
        "patrimonio neto", "fondos propios", "capital propio",
    ],
    "long_term_debt": [
        "long term debt", "long-term debt", "non-current liabilities",
        "noncurrent liabilities", "long term liabilities",
        "dettes à long terme", "dettes financières",
        "langfristige verbindlichkeiten",
        "deuda a largo plazo", "pasivos no corrientes",
    ],
    "capital_employed": ["capital employed", "capitaux engagés"],
    "operating_cashflow": [
        "operating cash flow", "cash from operations", "net cash from operating activities",
        "cash flow from operations", "cfo",
        "flux de trésorerie opérationnel",
        "operativer cashflow",
        "flujos de efectivo de actividades de operación",
    ],
    "capex": [
        "capex", "capital expenditure", "capital expenditures", "purchase of ppe",
        "purchases of property plant and equipment", "property plant equipment",
        "investissements", "dépenses d'investissement",
        "investitionen",
        "gastos de capital", "inversiones en activos fijos",
    ],
    "free_cashflow": [
        "free cash flow", "fcf", "free cashflow",
        "flux de trésorerie disponible",
        "freier cashflow",
        "flujo de caja libre",
    ],
    "date": [
        "date", "period", "year", "month", "quarter", "fiscal year", "fy",
        "année", "période", "exercice",
        "jahr", "quartal",
        "año", "período",
    ],
}

# ─── STATEMENT TYPE DETECTION ───────────────────────────────────────────────────
STATEMENT_TYPE_SIGNALS = {
    "income_statement": ["revenue", "cogs", "gross_profit", "operating_profit", "net_income", "ebitda"],
    "balance_sheet": ["total_assets", "total_liabilities", "equity", "current_assets", "current_liabilities"],
    "cash_flow": ["operating_cashflow", "capex", "free_cashflow"],
}

# ─── SAMPLE DATA PRESETS ────────────────────────────────────────────────────────
SAMPLE_PRESETS = {
    "🛒 Retail Company": {
        "description": "High-volume, low-margin retail with strong inventory turnover.",
        "years": [2020, 2021, 2022, 2023, 2024],
        "data": {
            "Year":               [2020,       2021,       2022,       2023,       2024],
            "Revenue":            [12_000_000, 13_800_000, 15_100_000, 14_600_000, 16_200_000],
            "COGS":               [9_360_000,  10_626_000, 11_475_000, 11_388_000, 12_312_000],
            "Gross Profit":       [2_640_000,  3_174_000,  3_625_000,  3_212_000,  3_888_000],
            "Operating Profit":   [720_000,    897_000,    1_056_500,  730_000,    1_134_000],
            "EBITDA":             [960_000,    1_173_000,  1_358_500,  1_022_000,  1_458_000],
            "Interest Expense":   [180_000,    207_000,    226_500,    219_000,    243_000],
            "Net Income":         [432_000,    552_600,    621_700,    365_000,    729_000],
            "Total Assets":       [6_000_000,  6_900_000,  7_550_000,  7_300_000,  8_100_000],
            "Current Assets":     [3_000_000,  3_450_000,  3_775_000,  3_650_000,  4_050_000],
            "Current Liabilities":[2_400_000,  2_760_000,  3_020_000,  2_920_000,  3_240_000],
            "Inventory":          [1_800_000,  2_070_000,  2_265_000,  2_190_000,  2_430_000],
            "Accounts Receivable":[300_000,    345_000,    377_500,    365_000,    405_000],
            "Total Liabilities":  [3_600_000,  4_140_000,  4_530_000,  4_380_000,  4_860_000],
            "Total Equity":       [2_400_000,  2_760_000,  3_020_000,  2_920_000,  3_240_000],
            "Long Term Debt":     [1_200_000,  1_380_000,  1_510_000,  1_460_000,  1_620_000],
        }
    },
    "🏭 Manufacturing Company": {
        "description": "Asset-heavy manufacturer with capital-intensive operations.",
        "years": [2020, 2021, 2022, 2023, 2024],
        "data": {
            "Year":               [2020,       2021,       2022,       2023,       2024],
            "Revenue":            [8_500_000,  9_200_000,  10_800_000, 11_500_000, 12_400_000],
            "COGS":               [5_950_000,  6_348_000,  7_344_000,  7_705_000,  8_184_000],
            "Gross Profit":       [2_550_000,  2_852_000,  3_456_000,  3_795_000,  4_216_000],
            "Operating Profit":   [1_020_000,  1_196_000,  1_512_000,  1_725_000,  1_984_000],
            "EBITDA":             [1_530_000,  1_748_000,  2_160_000,  2_415_000,  2_728_000],
            "Interest Expense":   [255_000,    276_000,    324_000,    345_000,    372_000],
            "Net Income":         [587_500,    713_200,    921_600,    1_104_000,  1_271_400],
            "Total Assets":       [17_000_000, 18_400_000, 21_600_000, 23_000_000, 24_800_000],
            "Current Assets":     [3_400_000,  3_680_000,  4_320_000,  4_600_000,  4_960_000],
            "Current Liabilities":[2_550_000,  2_760_000,  3_240_000,  3_450_000,  3_720_000],
            "Inventory":          [1_700_000,  1_840_000,  2_160_000,  2_300_000,  2_480_000],
            "Accounts Receivable":[850_000,    920_000,    1_080_000,  1_150_000,  1_240_000],
            "Total Liabilities":  [10_200_000, 11_040_000, 12_960_000, 13_800_000, 14_880_000],
            "Total Equity":       [6_800_000,  7_360_000,  8_640_000,  9_200_000,  9_920_000],
            "Long Term Debt":     [7_650_000,  8_280_000,  9_720_000,  10_350_000, 11_160_000],
        }
    },
    "🚀 SaaS Startup": {
        "description": "High-growth software company investing heavily in R&D and sales.",
        "years": [2020, 2021, 2022, 2023, 2024],
        "data": {
            "Year":               [2020,      2021,      2022,      2023,      2024],
            "Revenue":            [500_000,   1_200_000, 2_800_000, 5_100_000, 8_500_000],
            "COGS":               [150_000,   336_000,   700_000,   1_122_000, 1_700_000],
            "Gross Profit":       [350_000,   864_000,   2_100_000, 3_978_000, 6_800_000],
            "Operating Profit":   [-800_000,  -1_200_000,-900_000,  510_000,   1_700_000],
            "EBITDA":             [-650_000,  -980_000,  -600_000,  850_000,   2_125_000],
            "Interest Expense":   [20_000,    48_000,    84_000,    102_000,   85_000],
            "Net Income":         [-850_000,  -1_320_000,-1_050_000, 306_000,   1_360_000],
            "Total Assets":       [2_000_000, 4_500_000, 7_500_000, 9_000_000, 12_000_000],
            "Current Assets":     [1_200_000, 3_000_000, 5_000_000, 5_400_000, 6_000_000],
            "Current Liabilities":[400_000,   900_000,   1_500_000, 1_530_000, 1_800_000],
            "Inventory":          [0,         0,         0,         0,         0],
            "Accounts Receivable":[100_000,   240_000,   560_000,   1_020_000, 1_700_000],
            "Total Liabilities":  [600_000,   1_350_000, 2_250_000, 2_700_000, 3_600_000],
            "Total Equity":       [1_400_000, 3_150_000, 5_250_000, 6_300_000, 8_400_000],
            "Long Term Debt":     [200_000,   450_000,   750_000,   1_170_000, 1_800_000],
        }
    },
    "🏥 Healthcare Company": {
        "description": "Stable healthcare provider with recurring revenues and moderate leverage.",
        "years": [2020, 2021, 2022, 2023, 2024],
        "data": {
            "Year":               [2020,       2021,       2022,       2023,       2024],
            "Revenue":            [7_000_000,  7_350_000,  7_900_000,  8_400_000,  9_100_000],
            "COGS":               [3_150_000,  3_307_500,  3_555_000,  3_780_000,  4_095_000],
            "Gross Profit":       [3_850_000,  4_042_500,  4_345_000,  4_620_000,  5_005_000],
            "Operating Profit":   [1_400_000,  1_470_000,  1_659_000,  1_764_000,  1_911_000],
            "EBITDA":             [1_750_000,  1_837_500,  1_975_000,  2_100_000,  2_275_000],
            "Interest Expense":   [210_000,    220_500,    237_000,    252_000,    273_000],
            "Net Income":         [945_000,    992_250,    1_091_700,  1_176_000,  1_274_000],
            "Total Assets":       [14_000_000, 14_700_000, 15_800_000, 16_800_000, 18_200_000],
            "Current Assets":     [2_800_000,  2_940_000,  3_160_000,  3_360_000,  3_640_000],
            "Current Liabilities":[1_400_000,  1_470_000,  1_580_000,  1_680_000,  1_820_000],
            "Inventory":          [350_000,    367_500,    395_000,    420_000,    455_000],
            "Accounts Receivable":[1_050_000,  1_102_500,  1_185_000,  1_260_000,  1_365_000],
            "Total Liabilities":  [7_000_000,  7_350_000,  7_900_000,  8_400_000,  9_100_000],
            "Total Equity":       [7_000_000,  7_350_000,  7_900_000,  8_400_000,  9_100_000],
            "Long Term Debt":     [5_600_000,  5_880_000,  6_320_000,  6_720_000,  7_280_000],
        }
    },
}

# Fields that appear in each statement type (for multi-file tagging)
INCOME_STATEMENT_FIELDS = [
    "revenue", "cogs", "gross_profit", "operating_profit", "ebitda",
    "net_income", "interest_expense", "tax", "depreciation",
]
BALANCE_SHEET_FIELDS = [
    "total_assets", "current_assets", "inventory", "accounts_receivable",
    "total_liabilities", "current_liabilities", "equity", "long_term_debt",
    "capital_employed",
]
CASH_FLOW_FIELDS = ["operating_cashflow", "capex", "free_cashflow"]

# Capitalization rate for Enterprise Value calculation
DEFAULT_CAP_RATE = 0.12  # 12%

# SQL placeholder (future use)
DATABASE_CONFIG = {
    "type": None,
    "host": None,
    "port": None,
    "database": None,
    "username": None,
    "password": None,
}

# Mapping profile storage key (for session-state persistence)
MAPPING_PROFILE_KEY = "finanalyst_mapping_profiles"

