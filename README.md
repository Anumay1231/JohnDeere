# 🚜 JD Dealership — GM Executive Dashboard

**Management by Exception · Chhattisgarh Operations · 2013–2026**

---

## Quickstart (3 steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Put your Excel files in the data/ folder
mkdir data
cp /path/to/your/files/*.xlsx data/

# 3. Run
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## Required Files (place in `data/`)

| File | What it contains |
|------|-----------------|
| `OLD_TRACTOR_STOCK.xlsx` | Exchange tractors — 756 rows, sold/stock status, prices |
| `SALERY_SHEET_FINAL.xlsx` | All sales 2013–2026 — 2,512 rows, DSE names, implements |
| `BILLING.xlsx` | Annual billing/delivery pivot + vendor ledgers |
| `BILLING_OF_2015.xlsx` | Historical billing + 2025-26 delivery detail |

The app **auto-discovers** files — it checks `./data/`, then the script directory, then the current directory.

---

## Dashboard Tabs

| Tab | Purpose | Key Output |
|-----|---------|-----------|
| 📦 Phase 1 | Trapped Capital | ₹2.85 Cr locked, 71% sold at a loss |
| 👤 Phase 2 | DSE Performance | Composite score: volume + implement upsell |
| 📈 Phase 3 | Seasonality | June = 2× avg month, run-rate vs last year |

---

## Git Setup (for version control)

```bash
git init
git add app.py data_loader.py requirements.txt README.md .gitignore .streamlit/
git commit -m "Initial dashboard — v1.1"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/jd-dashboard.git
git push -u origin main
```

> ⚠️ The `data/` folder is in `.gitignore` — Excel files are **never committed**.
> Each person who clones the repo drops their own Excel files into `data/`.

---

## Deploying on Streamlit Cloud (free)

1. Push this repo to GitHub (without the `data/` folder)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → select `app.py`
4. Under **Advanced → Secrets**, add nothing — just deploy
5. Upload Excel files via the Streamlit file uploader (add Phase 4 for this if needed)

---

## File Structure

```
jd-dashboard/
├── app.py              ← Streamlit UI (all 3 phases)
├── data_loader.py      ← Data cleaning (edit this to change parsing logic)
├── requirements.txt    ← pip dependencies
├── README.md           ← This file
├── .gitignore          ← Excludes data/ and Excel files
├── .streamlit/
│   └── config.toml     ← Dark theme + server config
└── data/               ← YOUR EXCEL FILES GO HERE (not committed to git)
    ├── OLD_TRACTOR_STOCK.xlsx
    ├── SALERY_SHEET_FINAL.xlsx
    ├── BILLING.xlsx
    └── BILLING_OF_2015.xlsx
```

---

## Key Metrics (from actual data)

| Metric | Value |
|--------|-------|
| Trapped capital | ₹2.85 Crore (93 tractors) |
| Sold at a loss | 71.3% of exchange sales |
| Avg loss per sale | ₹77,164 |
| Top DSE | Lalit Diwan (670 units, 62% impl rate) |
| Best upseller | Arun Koushik (71% implement rate) |
| Peak month | June (index: 199 — almost 2× average) |
| Dead month | August (index: 38) |
| 2025-26 YTD | 126 deliveries (Nov–Feb) |

---

## Data Quality Notes

- 84 of 93 stock tractors have **no exchange date** — age shows as Unknown. Fix this in the register.
- Sold prices like `155000/105000` — app takes the first value (down-payment structure).
- Unit values >₹5 Crore are treated as data entry errors and nulled.
- Fiscal year: **November → October** (not January → December).

---

*Built for 15-minute daily management calls. Exceptions first, details on demand.*
