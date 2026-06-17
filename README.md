# 🌱 Food Sustainability Dashboard

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.15%2B-3F4F75?logo=plotly&logoColor=white)](https://plotly.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg)](LICENSE)

> **🔗 Live app → [food-sustainability-dashboard.streamlit.app](https://your-app-name.streamlit.app)**  
> *(Replace with your actual Streamlit Cloud URL after deployment)*

An interactive data visualisation dashboard exploring the environmental impact of 40 food products, built on the landmark **Poore & Nemecek (2018)** meta-analysis - the largest study of food systems ever conducted, spanning 38,700 farms across 119 countries.

---

## 📸 Features

| Tab | What you can do |
|-----|-----------------|
| **🌍 Overview** | Ranked bar chart of all foods by any metric; animal vs. plant normalised comparison |
| **🔬 Deep Dive** | Interactive bubble chart - map any two metrics against each other, bubble size = third metric; sortable full data table |
| **🍽️ Meal Calculator** | Build a meal item-by-item, see GHG/land/water breakdown, compare against typical meal benchmarks, and get real-world context equivalents (driving km, phone charges, Netflix hours) |
| **💡 Make a Change** | Curated swap cards (e.g. Beef → Lentils = −95% GHG); custom swap builder with weekly frequency and portion-size sliders; annual savings across all four metrics |

---

## 🗂️ Project structure

```
food-sustainability-dashboard/
├── app.py                    # Main Streamlit application (~400 lines)
├── data/
│   └── food_emissions.csv    # Poore & Nemecek 2018 dataset (40 foods, 4 metrics)
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml           # Green theme configuration
├── .gitignore
└── README.md
```

---

## 📊 Dataset

**Source:** Poore, J. & Nemecek, T. (2018). *Reducing food's environmental impacts through producers and consumers.* Science, 360(6392), 987–992. DOI: [10.1126/science.aaq0216](https://doi.org/10.1126/science.aaq0216)

| Metric | Unit | Description |
|--------|------|-------------|
| GHG Emissions | kg CO₂-eq / kg food | Full supply-chain greenhouse gas emissions |
| Land Use | m² / kg food | Land area occupied, including feed-crop land |
| Water Use | L / kg food | Freshwater withdrawals |
| Eutrophication | g PO₄-eq / kg food | Nutrient runoff causing algal blooms |

All values are **median estimates per kg of food at retail weight** across all farm systems and geographies in the dataset.

---

## 🚀 Run locally

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/[your-username]/food-sustainability-dashboard.git
cd food-sustainability-dashboard

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**.

---

## ☁️ Deploy to Streamlit Cloud (free, 5 minutes)

This is the fastest way to get a live URL on your CV.

1. **Push this repo to GitHub** (public repository)

2. **Go to [share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub

3. Click **"New app"** and fill in:
   - Repository: `[your-username]/food-sustainability-dashboard`
   - Branch: `main`
   - Main file path: `app.py`

4. Click **"Deploy!"** — Streamlit Cloud reads `requirements.txt` automatically

5. Your app gets a permanent URL:  
   `https://[your-username]-food-sustainability-dashboard-app-[hash].streamlit.app`

6. **Customise the URL** in app settings → share this link on your CV and LinkedIn

> **Tip:** Streamlit Cloud is free for public repos. The app stays live as long as the GitHub repo is public.

---

## 🛠️ Tech stack

| Tool | Role |
|------|------|
| [Streamlit](https://streamlit.io) | Web app framework (no JavaScript needed) |
| [Plotly](https://plotly.com/python/) | Interactive charts (bar, bubble, pie, grouped) |
| [pandas](https://pandas.pydata.org) | Data loading and manipulation |
| [NumPy](https://numpy.org) | Numerical helpers |

---

## 💡 Skills demonstrated

- **Streamlit** — multi-tab layout, sidebar controls, session state (meal calculator), custom CSS, `st.cache_data`
- **Plotly** — `go.Figure` with multiple traces, `px.scatter`, `px.bar`, `px.pie`; custom hover templates; log-scale toggles
- **pandas** — CSV ingestion, filtering, sorting, groupby aggregation
- **Data storytelling** — contextual benchmarks, normalised comparisons, real-world equivalents (driving km, phone charges)
- **Deployment** — Streamlit Cloud CI/CD from a GitHub push

---

## 🔭 Possible extensions

- Add a "per 100g protein" and "per 1000 kcal" metric view (protein and calorie data already in the CSV)
- Integrate the full Poore & Nemecek supplementary dataset for farm-level variance
- Add a carbon-label generator (export a food's footprint as a shareable image)
- Build a weekly diet planner with running annual totals
- Compare with Our World in Data's food emissions data for cross-validation

---

## 📜 Citation & attribution

```
Poore, J., & Nemecek, T. (2018).
Reducing food's environmental impacts through producers and consumers.
Science, 360(6392), 987–992.
https://doi.org/10.1126/science.aaq0216
```

This project is an independent portfolio piece and is not affiliated with, endorsed by, or representative of the views of Poore & Nemecek or the journal *Science*.

---

## 📄 License

[MIT](LICENSE) — free to use, adapt, and share with attribution.
