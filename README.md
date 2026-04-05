# 🚜 JD Dealership — GM Inference Dashboard

**Drag-and-Drop Executive Analytics · Chhattisgarh Operations · Free Forever**

---

## 🔗 Launch the Dashboard

### Live App (works on any phone, laptop, or tablet):

> **https://anumay1231-johndeere.streamlit.app**

Just open the link → drag your Excel files → get instant inferences.

No installation. No setup. Works everywhere.

---

## How It Works

1. **Open the link** above on any device (phone, laptop, iPad — anything with a browser).
2. **Drag and drop** your two Excel files:
   - `OLD_TRACTOR_STOCK.xlsx` — Exchange tractor register
   - `SALERY_SHEET_FINAL.xlsx` — DSE master sales file
3. **Instant inference** — the dashboard automatically:
   - Calculates total **trapped capital** sitting unsold on lot
   - Identifies **who is most responsible** (adjusted for volume — bigger sellers naturally hold more)
   - Flags **critical >1 year aging** where money is rotting
   - Shows **used tractor economics** — what you bought vs what you sold for
   - Highlights the **worst historic losses** with exact DSE accountability
4. **Expand for detail** — collapsible sections show deeper scatter plots and DSE scorecard tables only when you want them.

> 📱 **Your data never leaves your browser.** Files are processed in-memory and discarded after the session.

---

## Running Locally (optional)

If you prefer to run it on your own machine:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## Project Structure

```
JohnDeere/
├── app.py              ← Dashboard UI (drag-and-drop + inference engine)
├── data_loader.py      ← Data cleaning and parsing logic
├── requirements.txt    ← Dependencies
├── .streamlit/
│   └── config.toml     ← Dark theme configuration
└── README.md           ← This file
```

> ⚠️ Excel files are **never committed to git**. Each user uploads their own files via the dashboard.

---

*Built for 15-minute daily management calls. Exceptions first, details on demand.*
