
# COFCO INTL • Inventory Dashboard (Streamlit)

Power BI–style Streamlit dashboard for your Excel-based inventory. 

## Features
- KPIs: total items, in-use, in-stock, reserved
- Charts: bar (items by category), line (items by month)
- Filter sidebar: status, brand, model, location + free-text search
- Interactive table + Excel download
- COFCO International logo (online)

## Quick Start (local)
```bash
pip install -r requirements.txt
streamlit run app.py
```
Then open the local URL shown by Streamlit.

## Deploy to Streamlit Community Cloud
1. Create a new GitHub repo and upload these files.
2. Go to https://share.streamlit.io/ and choose your repo, branch and `app.py`.
3. (Optional) Add your Excel into the repo or upload it via the app sidebar at runtime.

## Notes
- The app auto-detects header rows and common columns (Status, Brand, Model, Date, etc.).
- If your sheet names include `TEC`, it will be the default.
