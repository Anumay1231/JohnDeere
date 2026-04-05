"""
data_loader.py
Robust data cleaning for Mahindra/JD Dealership Dashboard.
Handles messy Excel: blank rows, multi-headers, mixed date formats, slash-prices.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# SHARED CONSTANTS
# ─────────────────────────────────────────────────────────────

MAKE_MAP = {
    "JD": "John Deere", "J D": "John Deere", "J.D.": "John Deere",
    "M&M": "Mahindra", "MM": "Mahindra", "M & M": "Mahindra", "MAHINDRA": "Mahindra",
    "HMT": "HMT",
    "ESCORT": "Escorts", "ESCORTS": "Escorts",
    "EICHER": "Eicher",
    "SWARAJ": "Swaraj",
    "SONALICA": "Sonalika", "SONALIKA": "Sonalika",
    "POWERTRAC": "Powertrac",
    "NEW HOLLAND": "New Holland",
    "ERTIGA": "Maruti (Ertiga)",
}

DISTRICT_MAP = {
    "BSP": "Bilaspur", "BILASPUR": "Bilaspur", "TAKHATPUR": "Bilaspur",
    "RAHOD": "Bilaspur", "MASTURI": "Bilaspur", "PENDRAROAD": "Bilaspur",
    "PENDRA": "Bilaspur",
    "JANJGIR": "Janjgir", "JANJGEER": "Janjgir", "AKALTARA": "Janjgir",
    "PAMGARH": "Janjgir", "PAMGRAH": "Janjgir", "SAKTI": "Janjgir",
    "NAVAGARH": "Janjgir", "NAVAGRAH": "Janjgir",
    "MUNGELI": "Mungeli", "RISDA": "Mungeli", "LORMI": "Mungeli",
    "BELHA": "Mungeli",
    "GPM": "GPM", "GAURELA": "GPM",
    "KOTA": "Kota",
    "KORBA": "Korba",
    "YARD": "Yard (Internal)",
    "CUSTOMER": "Customer Site",
    "OFFICE": "Office",
    "RAJENDRA": "Office",
}


def parse_date(val):
    """Parse wildly inconsistent date formats."""
    if val is None:
        return pd.NaT
    if isinstance(val, (datetime, pd.Timestamp)):
        return pd.Timestamp(val)
    if hasattr(val, 'date'):
        return pd.Timestamp(val)
    s = str(val).strip()
    if not s or s.lower() in ('nan', 'nat', 'stock', 'none', '', '-'):
        return pd.NaT
    for fmt in (
        '%d/%m/%Y', '%d/%m/%y', '%m/%d/%Y', '%d-%m-%Y',
        '%d-%m-%y', '%d-%b-%Y', '%d-%b-%y', '%Y-%m-%d',
    ):
        try:
            return pd.Timestamp(datetime.strptime(s, fmt))
        except (ValueError, TypeError):
            pass
    try:
        return pd.Timestamp(pd.to_datetime(s, dayfirst=True, errors='raise'))
    except Exception:
        return pd.NaT


def parse_price(val):
    """Handle prices like '155000/105000' → take first value."""
    if val is None:
        return np.nan
    if isinstance(val, (int, float)):
        return float(val) if not (isinstance(val, float) and np.isnan(val)) else np.nan
    s = str(val).strip().replace(',', '').replace(' ', '')
    if not s or s.lower() in ('nan', '-', ''):
        return np.nan
    s = s.split('/')[0]
    try:
        return float(s)
    except ValueError:
        return np.nan


def clean_make(val):
    key = str(val).strip().upper()
    return MAKE_MAP.get(key, str(val).strip().title())


def map_district(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "Unknown"
    key = str(val).strip().upper()
    return DISTRICT_MAP.get(key, str(val).strip().title())


# ─────────────────────────────────────────────────────────────
# PHASE 1: OLD TRACTOR STOCK
# ─────────────────────────────────────────────────────────────

def load_old_tractor_stock(filepath):
    """
    Returns df_all, df_stock, df_sold as clean DataFrames.
    
    Column layout (confirmed):
      0=sl_no, 1=owner_name, 2=reg_no, 3=serial_no, 4=make,
      5=model, 6=variant, 7=year_mfg, 8=exchange_date,
      12=status, 13=sold_date, 14=sold_via, 19=exchange_price,
      20=sold_price, 21=location/comments, 22=dse_name
    """
    raw = pd.read_excel(filepath, sheet_name="Not Eligible", header=None)

    # Skip 2 blank rows + 1 header row → data starts at row index 3
    data = raw.iloc[3:].copy().reset_index(drop=True)

    # Filter rows with valid serial numbers
    data = data[pd.to_numeric(data[0], errors='coerce').notna()].copy()

    # Rename
    data = data.rename(columns={
        0: 'sl_no', 1: 'owner_name', 2: 'reg_no', 3: 'serial_no',
        4: 'make_raw', 5: 'model', 6: 'variant', 7: 'year_mfg',
        8: 'exchange_date_raw', 12: 'status', 13: 'sold_date_raw',
        14: 'sold_via', 19: 'exchange_price_raw', 20: 'sold_price_raw',
        21: 'location_raw', 22: 'dse_name',
    })

    keep = ['sl_no','owner_name','reg_no','make_raw','model','variant','year_mfg',
            'exchange_date_raw','status','sold_date_raw','sold_via',
            'exchange_price_raw','sold_price_raw','location_raw','dse_name']
    data = data[keep].copy()

    # Clean status
    data['status'] = data['status'].astype(str).str.strip().str.upper()
    data = data[data['status'].isin(['SOLD', 'STOCK'])].copy()

    # Parse
    data['exchange_date']  = data['exchange_date_raw'].apply(parse_date)
    data['sold_date']      = data['sold_date_raw'].apply(parse_date)
    data['exchange_price'] = data['exchange_price_raw'].apply(parse_price)
    data['sold_price']     = data['sold_price_raw'].apply(parse_price)
    data['make']           = data['make_raw'].apply(clean_make)
    data['district']       = data['location_raw'].apply(map_district)
    data['model']          = data['model'].astype(str).str.strip().str.upper()
    data['dse_name']       = data['dse_name'].astype(str).str.strip().str.title()
    data['dse_name']       = data['dse_name'].replace({'Nan': 'Unknown', 'Office': 'Office/Direct'})

    # Derived
    today = pd.Timestamp.today().normalize()
    data['age_days']        = (today - data['exchange_date']).dt.days
    data['holding_period']  = (data['sold_date'] - data['exchange_date']).dt.days
    data['realized_margin'] = data['sold_price'] - data['exchange_price']
    data['margin_pct']      = (data['realized_margin'] / data['exchange_price'].replace(0, np.nan)) * 100

    # Age buckets
    def age_bucket(d):
        if pd.isna(d):   return "Unknown"
        if d > 730:      return "> 2 Years"
        if d > 365:      return "1–2 Years"
        if d > 180:      return "6–12 Months"
        if d > 90:       return "3–6 Months"
        return "< 3 Months"

    data['age_bucket']      = data['age_days'].apply(age_bucket)
    data['year_exchanged']  = data['exchange_date'].dt.year

    df_stock = data[data['status'] == 'STOCK'].copy()
    df_sold  = data[data['status'] == 'SOLD'].copy()
    return data, df_stock, df_sold


# ─────────────────────────────────────────────────────────────
# PHASE 2: DSE PERFORMANCE (MASTER FILE)
# ─────────────────────────────────────────────────────────────

def load_dse_master(filepath):
    """
    Returns cleaned DSE master DataFrame with implement flags and derived KPIs.
    
    Key columns confirmed:
      0=sl, 1=customer_name, 2=village, 3=tehsil, 4=district, 5=rc_book,
      6=mobile, 8=model, 11=delivery_date, 12=unit_value, 13=deposit,
      14=finance_amount, 15=balance, 16=retail_date, 17=finance_type,
      20=dse_name,
      21=cultivator, 22=cage_wheel, 23=trolley, 24=koper_datari,
      25=leveller, 26=rotavator, 27=plough, 28=others
    """
    raw = pd.read_excel(filepath, sheet_name='MASTER FILE', header=None)

    # Row 0 = headers, data starts row 1
    data = raw.iloc[1:].copy().reset_index(drop=True)

    # Filter valid records (numeric sl_no in col 0)
    data = data[pd.to_numeric(data[0], errors='coerce').notna()].copy()

    data = data.rename(columns={
        0:  'sl_no',
        1:  'customer_name',
        2:  'village',
        3:  'tehsil',
        4:  'district_raw',
        6:  'mobile',
        8:  'model',
        11: 'delivery_date_raw',
        12: 'unit_value_raw',
        13: 'deposit_raw',
        14: 'finance_amount_raw',
        15: 'balance_raw',
        17: 'finance_type',
        20: 'dse_name',
        21: 'cultivator',
        22: 'cage_wheel',
        23: 'trolley',
        24: 'koper_datari',
        25: 'leveller',
        26: 'rotavator',
        27: 'plough',
        28: 'others_impl',
    })

    keep = [
        'sl_no','customer_name','village','tehsil','district_raw','mobile',
        'model','delivery_date_raw','unit_value_raw','deposit_raw',
        'finance_amount_raw','balance_raw','finance_type','dse_name',
        'cultivator','cage_wheel','trolley','koper_datari',
        'leveller','rotavator','plough','others_impl',
    ]
    data = data[keep].copy()

    # Clean strings
    for col in ['dse_name','district_raw','tehsil','model','finance_type']:
        data[col] = data[col].astype(str).str.strip().str.upper()
        data[col] = data[col].replace('NAN', np.nan)

    data['dse_name']    = data['dse_name'].str.title().replace('Nan', 'Unknown')
    data['district']    = data['district_raw'].apply(map_district)

    # Parse numerics
    data['delivery_date']   = data['delivery_date_raw'].apply(parse_date)
    data['unit_value']      = pd.to_numeric(data['unit_value_raw'], errors='coerce')
    data['deposit']         = pd.to_numeric(data['deposit_raw'], errors='coerce')
    data['finance_amount']  = pd.to_numeric(data['finance_amount_raw'], errors='coerce')
    data['balance']         = pd.to_numeric(data['balance_raw'], errors='coerce')

    # Cap absurd unit values (data entry errors: values > 5Cr are clearly wrong)
    data.loc[data['unit_value'] > 5_000_000, 'unit_value'] = np.nan

    # Implement flags → binary
    impl_cols = ['cultivator','cage_wheel','trolley','koper_datari','leveller','rotavator','plough','others_impl']
    for col in impl_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce').gt(0).astype(int)

    data['implement_count']    = data[impl_cols].sum(axis=1)
    data['has_any_implement']  = (data['implement_count'] > 0).astype(int)
    data['has_rotavator']      = data['rotavator']
    data['has_trolley']        = data['trolley']

    # High-margin implement flag (rotavator + trolley = high-margin)
    data['high_margin_impl']   = ((data['rotavator'] == 1) | (data['trolley'] == 1)).astype(int)

    # Time fields
    data['year']  = data['delivery_date'].dt.year
    data['month'] = data['delivery_date'].dt.month
    data['month_name'] = data['delivery_date'].dt.strftime('%b')

    # Filter realistic years only
    data = data[data['year'].between(2013, 2026, inclusive='both') | data['year'].isna()].copy()

    return data


# ─────────────────────────────────────────────────────────────
# PHASE 3: BILLING / SEASONALITY
# ─────────────────────────────────────────────────────────────

MONTH_ORDER = ['NOV','DEC','JAN','FEB','MAR','APR','MAY','JUN','JUNE','JUL','AUG','SEP','OCT']
MONTH_CLEAN = {'JUNE': 'JUN'}

def load_billing_summary(billing_path, billing_2015_path):
    """
    Returns:
      df_annual  - year-by-year totals (billing + delivery)
      df_monthly - monthly billing pivot (years as columns, months as rows)
      df_delivery_monthly - same for delivery
      df_recent  - cleaned DEL 2025-26 detail records
    """
    # ── BILLING DELIVERY summary (main billing file) ──────────────────────
    raw = pd.read_excel(billing_path, sheet_name='BILLING DELIVERY', header=None)

    # Confirmed column layout from exploration:
    # BILLING (cols 1-14): 2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026
    # DELIVERY (cols 16-33, skipping INDUSTRY cols): 2013,2014,...2026
    BILLING_YEAR_COLS  = {2013:1, 2014:2, 2015:3, 2016:4, 2017:5, 2018:6, 2019:7,
                          2020:8, 2021:9, 2022:10, 2023:11, 2024:12, 2025:13, 2026:14}
    DELIVERY_YEAR_COLS = {2013:16, 2014:17, 2015:18, 2016:19, 2017:20, 2018:21, 2019:22,
                          2020:23, 2021:24, 2022:25, 2023:27, 2024:29, 2025:31, 2026:33}

    # Month rows (rows 2-13 = NOV through OCT), row 14 = TOTAL
    month_rows = raw.iloc[2:14].copy()

    def build_pivot(col_map, rows):
        records = []
        for _, r in rows.iterrows():
            month = str(r[0]).strip().upper()
            month = MONTH_CLEAN.get(month, month)
            if month not in MONTH_ORDER:
                continue
            rec = {'month': month}
            for yr, col in col_map.items():
                val = pd.to_numeric(r.iloc[col], errors='coerce')
                rec[yr] = val
            records.append(rec)
        return pd.DataFrame(records)

    df_billing_pivot  = build_pivot(BILLING_YEAR_COLS, month_rows)
    df_delivery_pivot = build_pivot(DELIVERY_YEAR_COLS, month_rows)

    # Annual totals from TOTAL row
    total_row = raw.iloc[14]
    annual_records = []
    for yr, col in BILLING_YEAR_COLS.items():
        billing_val  = pd.to_numeric(total_row.iloc[col], errors='coerce')
        del_col      = DELIVERY_YEAR_COLS.get(yr)
        delivery_val = pd.to_numeric(total_row.iloc[del_col], errors='coerce') if del_col else np.nan
        annual_records.append({'year': yr, 'billing': billing_val, 'delivery': delivery_val})

    df_annual = pd.DataFrame(annual_records).dropna(subset=['billing'])
    df_annual = df_annual[df_annual['billing'] > 0].sort_values('year')

    # ── Recent DEL 2025-26 detail ─────────────────────────────────────────
    raw2 = pd.read_excel(billing_2015_path, sheet_name='DEL 2025-26', header=None)
    detail = raw2.iloc[2:].copy()  # skip title + header
    detail.columns = range(len(detail.columns))
    detail = detail[pd.to_numeric(detail[0], errors='coerce').notna()].copy()
    detail = detail.rename(columns={
        0: 'sl_no', 1: 'customer_name', 2: 'village',
        3: 'tehsil', 4: 'model', 5: 'dse_name', 6: 'delivery_date_raw'
    })
    detail['delivery_date'] = detail['delivery_date_raw'].apply(parse_date)
    detail['month']         = detail['delivery_date'].dt.month
    detail['month_name']    = detail['delivery_date'].dt.strftime('%b')
    detail['dse_name']      = detail['dse_name'].astype(str).str.strip().str.title()
    detail['district']      = detail['tehsil'].apply(map_district)

    return df_annual, df_billing_pivot, df_delivery_pivot, detail


# ─────────────────────────────────────────────────────────────
# PHASE 4: FINANCIAL RECONCILIATION
# ─────────────────────────────────────────────────────────────

def load_financial_recon(billing_path):
    """
    Scans through 40+ vendor/dealer ledger sheets in BILLING.xlsx
    Returns a DataFrame with net positions (Receivable / Payable).
    """
    xl = pd.ExcelFile(billing_path)
    exclude_sheets = ['Sheet1', 'Sheet2', 'Sheet3', 'BILLING DELIVERY', 'BOOKING']
    
    records = []
    
    for s in xl.sheet_names:
        if s in exclude_sheets:
            continue
            
        try:
            # Most ledgers have their header on the second row
            df = pd.read_excel(xl, sheet_name=s, header=1)
            
            # Find a column containing "BALANCE"
            bal_cols = [c for c in df.columns if isinstance(c, str) and 'BALANCE' in c.upper()]
            
            if bal_cols:
                bal_col = bal_cols[0]
                # Drop rows where balance is NaN, take the last one
                valid_bals = df[bal_col].dropna()
                
                if not valid_bals.empty:
                    last_bal = valid_bals.iloc[-1]
                    
                    try:
                        last_bal = float(last_bal)
                    except (ValueError, TypeError):
                        continue
                        
                    # Skip 0 balances to declutter
                    if pd.notna(last_bal) and last_bal != 0:
                        records.append({
                            'Vendor': str(s).strip().title(),
                            'Balance': last_bal,
                            # Assumption: Positive balance in vendor ledger = Payable. Negative = Receivable.
                            'Category': 'Payable' if last_bal > 0 else 'Receivable'
                        })
        except Exception:
            pass
            
    df_recon = pd.DataFrame(records)
    if not df_recon.empty:
        # Absolute balance for magnitude sorting
        df_recon['Abs_Balance'] = df_recon['Balance'].abs()
        df_recon = df_recon.sort_values(by=['Category', 'Abs_Balance'], ascending=[True, False])
        
    return df_recon
