"""
🌱 Food Sustainability Dashboard
────────────────────────────────────────────────────────────
Visualises the environmental footprint of 40 food products
using data from Poore & Nemecek (2018), Science 360:987–992
— the largest meta-analysis of food systems ever conducted,
covering 38,700 farms across 119 countries.

Metrics covered per kg of food at retail:
  • Greenhouse gas emissions  (kg CO₂-eq)
  • Land use                  (m²)
  • Freshwater withdrawals    (litres)
  • Eutrophication potential  (g PO₄-eq)

Author : [Your Name]
GitHub : https://github.com/[your-username]/food-sustainability-dashboard
Dataset: https://science.sciencemag.org/content/360/6392/987
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌱 Food Sustainability Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/[your-username]/food-sustainability-dashboard",
        "Report a bug": "https://github.com/[your-username]/food-sustainability-dashboard/issues",
        "About": (
            "**Food Sustainability Dashboard** — built with Streamlit & Plotly.\n\n"
            "Data: Poore & Nemecek (2018), *Science* 360(6392):987–992."
        ),
    },
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    padding: 5px;
    background: #e8f5e9;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 6px 18px;
    font-weight: 500;
    color: #2d6a4f;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #1a3d2b !important;
    font-weight: 700 !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: white;
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

/* ── Custom card components ── */
.insight-card {
    background: white;
    border-radius: 10px;
    border-left: 5px solid #40916c;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 0.6rem;
    line-height: 1.5;
}
.insight-card.red   { border-left-color: #dc2626; }
.insight-card.amber { border-left-color: #f59e0b; }
.insight-card.blue  { border-left-color: #3b82f6; }

/* ── Typography helpers ── */
.big-num   { font-size: 1.9rem; font-weight: 800; color: #2d6a4f; }
.big-red   { font-size: 1.9rem; font-weight: 800; color: #dc2626; }
.label-sm  { font-size: 0.78rem; color: #64748b; text-transform: uppercase;
             letter-spacing: 0.06em; }

/* ── Footer ── */
.footer { font-size: 0.78rem; color: #94a3b8; text-align: center; padding: 1.2rem 0; }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
METRIC_CONFIG: dict = {
    "🌡️ GHG Emissions": {
        "col": "ghg_per_kg",
        "unit": "kg CO₂-eq / kg food",
        "unit_short": "kg CO₂-eq",
        "description": "Greenhouse-gas emissions across the full supply chain",
        "axis_color": "#dc2626",
    },
    "🌍 Land Use": {
        "col": "land_per_kg",
        "unit": "m² / kg food",
        "unit_short": "m²",
        "description": "Land occupied for production, including feed crops",
        "axis_color": "#b45309",
    },
    "💧 Water Use": {
        "col": "water_per_kg",
        "unit": "L / kg food",
        "unit_short": "L",
        "description": "Freshwater withdrawals throughout the supply chain",
        "axis_color": "#2563eb",
    },
    "🔬 Eutrophication": {
        "col": "eutro_per_kg",
        "unit": "g PO₄-eq / kg food",
        "unit_short": "g PO₄-eq",
        "description": "Nutrient runoff causing algal blooms & aquatic dead zones",
        "axis_color": "#7c3aed",
    },
}

SUBCAT_COLORS: dict = {
    "Meat": "#dc2626",
    "Dairy & Eggs": "#f97316",
    "Seafood": "#0ea5e9",
    "Grains": "#ca8a04",
    "Vegetables": "#16a34a",
    "Legumes": "#059669",
    "Fruit": "#d97706",
    "Nuts & Seeds": "#92400e",
    "Beverages": "#7c3aed",
    "Oils": "#db2777",
    "Other": "#64748b",
}

# Context equivalents for 1 kg CO₂-eq
KM_PER_KG_CO2 = 1 / 0.21        # avg petrol car emits 0.21 kg CO₂/km
PHONE_PER_KG_CO2 = 1 / 0.0083   # smartphone charge ≈ 0.0083 kg CO₂
NETFLIX_PER_KG_CO2 = 1 / 0.036  # streaming 1 h ≈ 0.036 kg CO₂

# Pre-built sample meals  {name: [(food_name, grams), ...]}
SAMPLE_MEALS: dict = {
    "🥗 Vegan Bowl": [
        ("Rice", 150),
        ("Lentils", 100),
        ("Tomatoes", 100),
        ("Olive Oil", 20),
    ],
    "🍗 Chicken Dinner": [
        ("Chicken", 200),
        ("Potatoes", 200),
        ("Peas", 80),
        ("Butter", 15),
    ],
    "🥩 Beef Dinner": [
        ("Beef (beef herd)", 250),
        ("Potatoes", 200),
        ("Butter", 20),
    ],
}

# Curated swap pairs  (from, to, display_label, emoji_label)
SWAP_PAIRS: list = [
    ("Beef (beef herd)", "Chicken",     "Beef → Chicken",        "🥩→🍗"),
    ("Beef (beef herd)", "Tofu",         "Beef → Tofu",           "🥩→🫘"),
    ("Beef (beef herd)", "Lentils",      "Beef → Lentils",        "🥩→🫘"),
    ("Lamb & Mutton",    "Chicken",      "Lamb → Chicken",        "🍖→🍗"),
    ("Cheese",           "Tofu",         "Cheese → Tofu",         "🧀→🫘"),
    ("Milk",             "Oat Milk",     "Dairy Milk → Oat Milk", "🥛→🥛"),
    ("Farmed Shrimp",    "Lentils",      "Shrimp → Lentils",      "🦐→🫘"),
    ("Butter",           "Olive Oil",    "Butter → Olive Oil",    "🧈→🫒"),
]

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("data/food_emissions.csv")
    df["color"] = df["subcategory"].map(SUBCAT_COLORS)
    return df


df = load_data()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🌱 Food Sustainability Dashboard")
    st.markdown("---")

    st.markdown("### 📊 Global controls")

    metric_choice = st.selectbox(
        "Primary metric",
        list(METRIC_CONFIG.keys()),
        help="Applies to the Overview bar chart and ranking.",
    )

    category_filter = st.multiselect(
        "Food categories",
        options=sorted(df["subcategory"].unique()),
        default=sorted(df["subcategory"].unique()),
        help="Filter which food groups to show across all charts.",
    )

    st.markdown("---")
    st.markdown("### 📚 About the data")
    st.markdown(
        """
**Poore & Nemecek (2018)**  
*Science* 360(6392):987–992

The largest meta-analysis of food systems ever conducted:

- 📍 **38,700 farms**
- 🌐 **119 countries**
- 🍽️ **40 food products**

All metrics are **per kg of food at retail weight**, expressed as median values across the full supply chain (farm → processing → transport → retail).
"""
    )

    st.markdown("---")
    st.markdown("### 🔗 Links")
    st.markdown(
        "📄 [Source paper](https://science.sciencemag.org/content/360/6392/987)  \n"
        "💻 [GitHub repo](https://github.com/[your-username]/food-sustainability-dashboard)"
    )

# ─────────────────────────────────────────────────────────────────────────────
# FILTERED DATA  (respects sidebar category selection)
# ─────────────────────────────────────────────────────────────────────────────
fdf = df[df["subcategory"].isin(category_filter)] if category_filter else df.copy()

mcfg   = METRIC_CONFIG[metric_choice]
mcol   = mcfg["col"]

# ─────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("# 🌱 Food Sustainability Dashboard")
st.markdown(
    "Explore the environmental footprint of what we eat — "
    "greenhouse gases, land, water, and eutrophication — "
    "from the landmark **Poore & Nemecek (2018)** meta-analysis of 38,700 farms in 119 countries."
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    top_food = df.loc[df["ghg_per_kg"].idxmax()]
    st.metric(
        "Highest GHG emitter",
        top_food["food"],
        f"{top_food['ghg_per_kg']:.0f} kg CO₂-eq / kg",
    )
with c2:
    animal_avg = df[df["category"] == "Animal"]["ghg_per_kg"].mean()
    plant_avg  = df[df["category"] == "Plant"]["ghg_per_kg"].mean()
    st.metric(
        "Avg animal GHG",
        f"{animal_avg:.1f} kg CO₂-eq",
        f"{animal_avg / plant_avg:.1f}× higher than plant avg",
    )
with c3:
    lowest = df.loc[df["ghg_per_kg"].idxmin()]
    st.metric(
        "Lowest GHG emitter",
        lowest["food"],
        f"{lowest['ghg_per_kg']:.2f} kg CO₂-eq / kg",
        delta_color="off",
    )
with c4:
    st.metric(
        "Foods analysed",
        str(len(df)),
        "Poore & Nemecek, 2018",
        delta_color="off",
    )

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["🌍 Overview", "🔬 Deep Dive", "🍽️ Meal Calculator", "💡 Make a Change"]
)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader(f"Environmental impact by food — {metric_choice}")
    st.caption(f"{mcfg['description']}  •  unit: {mcfg['unit']}")

    col_chart, col_insight = st.columns([3, 1])

    # ── Sorted horizontal bar chart ──────────────────────────────────────────
    with col_chart:
        sorted_df = fdf.sort_values(mcol, ascending=True)

        fig_bar = go.Figure()
        for subcat in sorted_df["subcategory"].unique():
            sdf = sorted_df[sorted_df["subcategory"] == subcat]
            fig_bar.add_trace(
                go.Bar(
                    x=sdf[mcol],
                    y=sdf["food"],
                    orientation="h",
                    name=subcat,
                    marker_color=SUBCAT_COLORS.get(subcat, "#94a3b8"),
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        f"{metric_choice}: %{{x:.2f}} {mcfg['unit_short']}"
                        "<extra></extra>"
                    ),
                )
            )

        fig_bar.update_layout(
            height=max(520, len(sorted_df) * 22),
            barmode="stack",
            xaxis_title=mcfg["unit"],
            yaxis_title=None,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#e2e8f0", zeroline=False),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,
                xanchor="right",
                x=1,
                font=dict(size=11),
            ),
            margin=dict(l=0, r=10, t=10, b=30),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Insight panel ────────────────────────────────────────────────────────
    with col_insight:
        st.markdown("#### 🔑 Key insights")

        top3    = fdf.nlargest(3, mcol)
        bottom3 = fdf.nsmallest(3, mcol)

        st.markdown("**Highest impact:**")
        for _, r in top3.iterrows():
            st.markdown(
                f'<div class="insight-card red">'
                f'<b>{r["emoji"]} {r["food"]}</b><br>'
                f'<span class="big-red" style="font-size:1.3rem;">{r[mcol]:.1f}</span> '
                f'<span class="label-sm">{mcfg["unit_short"]}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("**Lowest impact:**")
        for _, r in bottom3.iterrows():
            st.markdown(
                f'<div class="insight-card">'
                f'<b>{r["emoji"]} {r["food"]}</b><br>'
                f'<span class="big-num" style="font-size:1.3rem;">{r[mcol]:.2f}</span> '
                f'<span class="label-sm">{mcfg["unit_short"]}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

        # Animal vs plant ratio
        a_avg = fdf[fdf["category"] == "Animal"][mcol].mean()
        p_avg = fdf[fdf["category"] == "Plant"][mcol].mean()
        if p_avg > 0:
            ratio = a_avg / p_avg
            st.markdown(
                f'<div class="insight-card amber" style="margin-top:1rem;">'
                f"On average, animal foods produce<br>"
                f'<span class="big-red">{ratio:.1f}×</span><br>'
                f"more {metric_choice.split()[-1].lower()} than plant foods."
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── Animal vs Plant — all metrics normalised ─────────────────────────────
    st.markdown("---")
    st.subheader("🐄 Animal vs 🌿 Plant — all four metrics")

    comp_rows = []
    for m_label, m_cfg in METRIC_CONFIG.items():
        for cat in ["Animal", "Plant"]:
            avg = fdf[fdf["category"] == cat][m_cfg["col"]].mean()
            comp_rows.append({"Metric": m_label, "Category": cat, "Average": avg})

    comp_df = pd.DataFrame(comp_rows)
    # Normalise each metric so Animal bar = 1.0 (Plant is its fraction)
    for m in comp_df["Metric"].unique():
        mx = comp_df[comp_df["Metric"] == m]["Average"].max()
        if mx > 0:
            comp_df.loc[comp_df["Metric"] == m, "Normalised"] = (
                comp_df.loc[comp_df["Metric"] == m, "Average"] / mx
            )

    fig_comp = px.bar(
        comp_df,
        x="Metric",
        y="Normalised",
        color="Category",
        barmode="group",
        color_discrete_map={"Animal": "#dc2626", "Plant": "#16a34a"},
        labels={"Normalised": "Relative impact (0 = lowest, 1 = highest)"},
        title="Relative environmental impact — normalised to the highest value in each metric",
        height=340,
    )
    fig_comp.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#e2e8f0", tickformat=".0%"),
        xaxis=dict(title=None),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=40, b=10),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    st.caption(
        "Bars show each category's average as a fraction of whichever is higher in that metric. "
        "This lets you compare the *relative* animal–plant gap across very different units."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DEEP DIVE
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🔬 Multi-dimensional impact explorer")
    st.markdown(
        "Map any two metrics against each other. "
        "Bubble size encodes a third metric. Hover for details."
    )

    ctrl_col, chart_col = st.columns([1, 3])

    with ctrl_col:
        x_key  = st.selectbox("X axis",      list(METRIC_CONFIG.keys()), index=0, key="x")
        y_key  = st.selectbox("Y axis",      list(METRIC_CONFIG.keys()), index=1, key="y")
        sz_key = st.selectbox("Bubble size", list(METRIC_CONFIG.keys()), index=2, key="sz")
        log_x  = st.toggle("Log scale X", value=False)
        log_y  = st.toggle("Log scale Y", value=False)
        st.markdown("---")
        st.markdown(
            "**Tip:** try GHG (X) vs Land (Y) to see how animal products "
            "dominate both axes, then add Water as bubble size."
        )

    with chart_col:
        xcol  = METRIC_CONFIG[x_key]["col"]
        ycol  = METRIC_CONFIG[y_key]["col"]
        szcol = METRIC_CONFIG[sz_key]["col"]

        bdf = fdf.copy()
        sz_min, sz_max = bdf[szcol].min(), bdf[szcol].max()
        bdf["bubble_size"] = (
            12 + 50 * (bdf[szcol] - sz_min) / (sz_max - sz_min)
            if sz_max > sz_min
            else 30
        )

        fig_bubble = go.Figure()
        for subcat in bdf["subcategory"].unique():
            s = bdf[bdf["subcategory"] == subcat]
            fig_bubble.add_trace(
                go.Scatter(
                    x=s[xcol],
                    y=s[ycol],
                    mode="markers+text",
                    name=subcat,
                    text=s["food"],
                    textposition="top center",
                    textfont=dict(size=9, color="#334155"),
                    marker=dict(
                        size=s["bubble_size"],
                        color=SUBCAT_COLORS.get(subcat, "#94a3b8"),
                        opacity=0.78,
                        line=dict(width=1.5, color="white"),
                    ),
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        f"{x_key}: %{{x:.2f}} {METRIC_CONFIG[x_key]['unit_short']}<br>"
                        f"{y_key}: %{{y:.2f}} {METRIC_CONFIG[y_key]['unit_short']}<br>"
                        f"Bubble = {sz_key}<br>"
                        "<extra></extra>"
                    ),
                )
            )

        fig_bubble.update_layout(
            xaxis_title=f"{x_key}  ({METRIC_CONFIG[x_key]['unit']})",
            yaxis_title=f"{y_key}  ({METRIC_CONFIG[y_key]['unit']})",
            xaxis_type="log" if log_x else "linear",
            yaxis_type="log" if log_y else "linear",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#e2e8f0"),
            yaxis=dict(gridcolor="#e2e8f0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, font=dict(size=11)),
            height=540,
            margin=dict(t=20, b=20),
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    # ── Sortable data table ──────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Full data table")

    col_opts = {
        "🌡️ GHG (kg CO₂-eq/kg)": "ghg_per_kg",
        "🌍 Land (m²/kg)":        "land_per_kg",
        "💧 Water (L/kg)":        "water_per_kg",
        "🔬 Eutro (g PO₄-eq/kg)": "eutro_per_kg",
    }
    sort_by = st.selectbox("Sort by", list(col_opts.keys()), key="sort_table")

    tdf = fdf[
        ["emoji", "food", "category", "subcategory",
         "ghg_per_kg", "land_per_kg", "water_per_kg", "eutro_per_kg"]
    ].copy()
    tdf = tdf.sort_values(col_opts[sort_by], ascending=False)
    tdf.columns = [
        "", "Food", "Category", "Subcategory",
        "🌡️ GHG (kg CO₂-eq/kg)", "🌍 Land (m²/kg)",
        "💧 Water (L/kg)", "🔬 Eutro (g PO₄-eq/kg)",
    ]

    st.dataframe(
        tdf,
        use_container_width=True,
        hide_index=True,
        column_config={
            "🌡️ GHG (kg CO₂-eq/kg)": st.column_config.ProgressColumn(
                format="%.2f",
                min_value=0,
                max_value=float(tdf["🌡️ GHG (kg CO₂-eq/kg)"].max()),
            ),
        },
    )
    st.caption(
        "Source: Poore J & Nemecek T (2018). *Science* 360(6392):987–992. "
        "Values are median estimates across supply chain stages."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MEAL CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🍽️ Meal Carbon Calculator")
    st.markdown(
        "Build a meal item-by-item and see its total environmental footprint — "
        "then compare it against typical meal benchmarks."
    )

    # Initialise session state
    if "meal_items" not in st.session_state:
        st.session_state.meal_items = []

    # ── Sample meal quick-start ──────────────────────────────────────────────
    if not st.session_state.meal_items:
        st.markdown("#### ⚡ Quick start — try a sample meal")
        q1, q2, q3 = st.columns(3)
        for btn_col, (meal_name, items) in zip([q1, q2, q3], SAMPLE_MEALS.items()):
            with btn_col:
                if st.button(meal_name, use_container_width=True):
                    for food_name, grams in items:
                        row = df[df["food"] == food_name]
                        if not row.empty:
                            r = row.iloc[0]
                            w = grams / 1000
                            st.session_state.meal_items.append(
                                {
                                    "food": food_name,
                                    "emoji": r["emoji"],
                                    "weight_g": grams,
                                    "category": r["category"],
                                    "subcategory": r["subcategory"],
                                    "ghg":   round(r["ghg_per_kg"]   * w, 4),
                                    "land":  round(r["land_per_kg"]  * w, 4),
                                    "water": round(r["water_per_kg"] * w, 2),
                                    "eutro": round(r["eutro_per_kg"] * w, 5),
                                }
                            )
                    st.rerun()
        st.markdown("---")

    # ── Add food controls ────────────────────────────────────────────────────
    col_sel, col_wt, col_add = st.columns([3, 1, 1])

    with col_sel:
        food_choice = st.selectbox(
            "Add food",
            df["food"].tolist(),
            format_func=lambda x: (
                f"{df.loc[df['food'] == x, 'emoji'].values[0]}  {x}"
            ),
        )
    with col_wt:
        weight_g = st.number_input("Grams", min_value=1, max_value=2000, value=150, step=10)
    with col_add:
        st.markdown("<div style='padding-top:1.75rem;'></div>", unsafe_allow_html=True)
        if st.button("➕ Add to meal", use_container_width=True, type="primary"):
            r = df[df["food"] == food_choice].iloc[0]
            w = weight_g / 1000
            st.session_state.meal_items.append(
                {
                    "food": food_choice,
                    "emoji": r["emoji"],
                    "weight_g": weight_g,
                    "category": r["category"],
                    "subcategory": r["subcategory"],
                    "ghg":   round(r["ghg_per_kg"]   * w, 4),
                    "land":  round(r["land_per_kg"]  * w, 4),
                    "water": round(r["water_per_kg"] * w, 2),
                    "eutro": round(r["eutro_per_kg"] * w, 5),
                }
            )
            st.rerun()

    # ── Meal contents ────────────────────────────────────────────────────────
    if st.session_state.meal_items:
        st.markdown("---")
        items_col, pie_col = st.columns([1, 1])

        with items_col:
            st.markdown("**Items in your meal:**")
            for i, item in enumerate(st.session_state.meal_items):
                r1, r2, r3 = st.columns([5, 3, 1])
                with r1:
                    st.markdown(
                        f"{item['emoji']} **{item['food']}** &nbsp;—&nbsp; {item['weight_g']} g"
                    )
                with r2:
                    st.markdown(
                        f"🌡️ `{item['ghg']:.3f}` kg CO₂-eq"
                    )
                with r3:
                    if st.button("🗑️", key=f"del_{i}", help="Remove this item"):
                        st.session_state.meal_items.pop(i)
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Clear meal", use_container_width=True):
                st.session_state.meal_items = []
                st.rerun()

        with pie_col:
            meal_df = pd.DataFrame(st.session_state.meal_items)
            if meal_df["ghg"].sum() > 0:
                fig_pie = px.pie(
                    meal_df,
                    values="ghg",
                    names="food",
                    title="GHG breakdown by ingredient",
                    hole=0.42,
                    color_discrete_sequence=px.colors.qualitative.Safe,
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=300,
                    margin=dict(t=36, b=0, l=0, r=0),
                    legend=dict(font=dict(size=10)),
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        # ── Totals ──────────────────────────────────────────────────────────
        st.markdown("---")
        total_ghg   = sum(i["ghg"]   for i in st.session_state.meal_items)
        total_land  = sum(i["land"]  for i in st.session_state.meal_items)
        total_water = sum(i["water"] for i in st.session_state.meal_items)
        total_eutro = sum(i["eutro"] for i in st.session_state.meal_items)

        st.markdown("#### 📊 Total meal impact")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("🌡️ GHG emissions",   f"{total_ghg:.3f} kg CO₂-eq")
        with m2:
            st.metric("🌍 Land use",         f"{total_land:.3f} m²")
        with m3:
            st.metric("💧 Water use",        f"{total_water:.1f} L")
        with m4:
            st.metric("🔬 Eutrophication",   f"{total_eutro:.5f} kg PO₄-eq")

        # ── Context equivalents ──────────────────────────────────────────────
        st.markdown("#### 🚗 Putting it in context")
        cx1, cx2, cx3 = st.columns(3)
        km     = total_ghg * KM_PER_KG_CO2
        phones = total_ghg * PHONE_PER_KG_CO2
        ntflx  = total_ghg * NETFLIX_PER_KG_CO2

        with cx1:
            st.markdown(
                f'<div class="insight-card">'
                f'🚗 Driving a petrol car<br>'
                f'<span class="big-num">{km:.1f} km</span>'
                f"</div>",
                unsafe_allow_html=True,
            )
        with cx2:
            st.markdown(
                f'<div class="insight-card blue">'
                f'📱 Smartphone charges<br>'
                f'<span class="big-num">{phones:.0f}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )
        with cx3:
            st.markdown(
                f'<div class="insight-card amber">'
                f'📺 Hours of Netflix streaming<br>'
                f'<span class="big-num">{ntflx:.1f} h</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

        # ── Benchmark comparison ─────────────────────────────────────────────
        st.markdown("---")
        st.markdown("#### 📏 How does your meal compare?")

        benchmarks = {
            "Vegan salad (typ.)":      0.25,
            "Veggie meal (typ.)":      0.80,
            "Chicken dinner (typ.)":   1.50,
            "Beef burger (typ.)":      3.50,
            "Beef steak dinner (typ.)":6.00,
        }
        bench_df = pd.DataFrame(
            list(benchmarks.items()), columns=["Meal", "GHG (kg CO₂-eq)"]
        )
        your_row = pd.DataFrame(
            [{"Meal": "🍽️ Your meal", "GHG (kg CO₂-eq)": round(total_ghg, 3)}]
        )
        bench_df = pd.concat([bench_df, your_row]).sort_values("GHG (kg CO₂-eq)")

        bench_df["Highlight"] = bench_df["Meal"].apply(
            lambda x: "Your meal" if "Your meal" in x else "Typical"
        )

        fig_bench = px.bar(
            bench_df,
            x="Meal",
            y="GHG (kg CO₂-eq)",
            color="Highlight",
            color_discrete_map={"Your meal": "#2d6a4f", "Typical": "#94a3b8"},
            title="Your meal vs. typical meal GHG footprints",
            text="GHG (kg CO₂-eq)",
            height=340,
        )
        fig_bench.update_traces(texttemplate="%{text:.2f} kg", textposition="outside")
        fig_bench.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#e2e8f0", title="kg CO₂-eq"),
            xaxis=dict(title=None),
            showlegend=False,
            margin=dict(t=40, b=10),
        )
        st.plotly_chart(fig_bench, use_container_width=True)

    else:
        st.info(
            "👆 Select a food above and press **Add to meal** — "
            "or try one of the quick-start sample meals."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — MAKE A CHANGE
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("💡 Make a Change — Food Swap Calculator")
    st.markdown(
        "Even small, consistent swaps can deliver significant savings. "
        "See the GHG reduction from common substitutions, then model your own."
    )

    # ── Pre-built swap cards ─────────────────────────────────────────────────
    st.markdown("#### 🔄 Common food swaps (per kg of food)")

    cols = st.columns(4)
    for idx, (frm, to, label, emj) in enumerate(SWAP_PAIRS):
        fr_row = df[df["food"] == frm].iloc[0]
        to_row = df[df["food"] == to].iloc[0]
        ghg_save  = fr_row["ghg_per_kg"]  - to_row["ghg_per_kg"]
        land_save = fr_row["land_per_kg"] - to_row["land_per_kg"]
        pct       = (ghg_save / fr_row["ghg_per_kg"]) * 100 if fr_row["ghg_per_kg"] > 0 else 0

        bg  = "#f0fdf4" if ghg_save > 0 else "#fef2f2"
        brd = "#22c55e" if ghg_save > 0 else "#dc2626"
        sign = "-" if ghg_save > 0 else "+"

        with cols[idx % 4]:
            st.markdown(
                f'<div style="background:{bg};border-left:4px solid {brd};'
                f'border-radius:0 10px 10px 0;padding:0.85rem;margin-bottom:0.8rem;">'
                f"<div style='font-size:1.2rem;'>{emj}</div>"
                f"<b style='font-size:0.88rem;'>{label}</b><br>"
                f"<span style='color:{brd};font-size:1.4rem;font-weight:800;'>"
                f"{sign}{abs(pct):.0f}%</span> GHG<br>"
                f"<span style='color:#64748b;font-size:0.8rem;'>"
                f"saves {abs(ghg_save):.1f} kg CO₂-eq/kg</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── Custom swap builder ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🛠️ Build your own swap")

    food_list = df["food"].tolist()

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        swap_from = st.selectbox(
            "I currently eat…",
            food_list,
            index=food_list.index("Beef (beef herd)"),
            format_func=lambda x: (
                f"{df.loc[df['food'] == x, 'emoji'].values[0]}  {x}"
            ),
            key="sf",
        )
    with sc2:
        swap_to = st.selectbox(
            "I want to switch to…",
            food_list,
            index=food_list.index("Lentils"),
            format_func=lambda x: (
                f"{df.loc[df['food'] == x, 'emoji'].values[0]}  {x}"
            ),
            key="st_",
        )
    with sc3:
        ppw  = st.slider("Meals per week", 1, 14, 3)
        gpp  = st.slider("Grams per meal", 50, 500, 200, step=50)

    fr_data = df[df["food"] == swap_from].iloc[0]
    to_data = df[df["food"] == swap_to].iloc[0]

    weekly_kg       = (ppw * gpp) / 1000
    from_ghg_wk     = fr_data["ghg_per_kg"]  * weekly_kg
    to_ghg_wk       = to_data["ghg_per_kg"]   * weekly_kg
    annual_ghg_save = (from_ghg_wk - to_ghg_wk) * 52

    from_land_wk     = fr_data["land_per_kg"] * weekly_kg
    to_land_wk       = to_data["land_per_kg"]  * weekly_kg
    annual_land_save = (from_land_wk - to_land_wk) * 52

    from_water_wk     = fr_data["water_per_kg"] * weekly_kg
    to_water_wk       = to_data["water_per_kg"]  * weekly_kg
    annual_water_save = (from_water_wk - to_water_wk) * 52

    sa1, sa2, sa3, sa4 = st.columns(4)
    with sa1:
        pct_change = (annual_ghg_save / (from_ghg_wk * 52) * 100) if from_ghg_wk > 0 else 0
        st.metric(
            "Annual GHG saving",
            f"{annual_ghg_save:+.1f} kg CO₂-eq",
            f"{pct_change:+.0f}% vs current",
            delta_color="normal" if annual_ghg_save > 0 else "inverse",
        )
    with sa2:
        st.metric(
            "Annual land saving",
            f"{annual_land_save:+.1f} m²",
            delta_color="normal" if annual_land_save > 0 else "inverse",
        )
    with sa3:
        st.metric(
            "Annual water saving",
            f"{annual_water_save:+,.0f} L",
            delta_color="normal" if annual_water_save > 0 else "inverse",
        )
    with sa4:
        km_saved = annual_ghg_save * KM_PER_KG_CO2
        st.metric(
            "Driving equivalent avoided",
            f"{km_saved:,.0f} km / yr",
            delta_color="normal" if km_saved > 0 else "inverse",
        )

    # Before / after bar chart
    before_after = pd.DataFrame(
        [
            {
                "Scenario": f"🔴 {swap_from}",
                "Weekly GHG (kg CO₂-eq)": round(from_ghg_wk, 3),
                "Type": "Before",
            },
            {
                "Scenario": f"🟢 {swap_to}",
                "Weekly GHG (kg CO₂-eq)": round(to_ghg_wk, 3),
                "Type": "After",
            },
        ]
    )

    fig_ba = px.bar(
        before_after,
        x="Scenario",
        y="Weekly GHG (kg CO₂-eq)",
        color="Type",
        color_discrete_map={"Before": "#dc2626", "After": "#16a34a"},
        text="Weekly GHG (kg CO₂-eq)",
        title=f"Weekly GHG: {ppw}× {gpp}g portion",
        height=350,
    )
    fig_ba.update_traces(texttemplate="%{text:.3f} kg CO₂-eq", textposition="outside")
    fig_ba.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#e2e8f0", title="kg CO₂-eq / week"),
        xaxis=dict(title=None),
        showlegend=False,
        margin=dict(t=40, b=10),
    )
    st.plotly_chart(fig_ba, use_container_width=True)

    # Per-metric breakdown of all four savings
    st.markdown("#### 📊 All metrics — current vs. swapped (weekly)")

    metrics_comp = []
    for m_label, m_cfg in METRIC_CONFIG.items():
        from_val = fr_data[m_cfg["col"]] * weekly_kg
        to_val   = to_data[m_cfg["col"]] * weekly_kg
        for scenario, val in [(f"🔴 {swap_from}", from_val), (f"🟢 {swap_to}", to_val)]:
            metrics_comp.append(
                {"Metric": m_label, "Scenario": scenario, "Value": round(val, 4)}
            )

    mc_df = pd.DataFrame(metrics_comp)

    fig_mc = px.bar(
        mc_df,
        x="Metric",
        y="Value",
        color="Scenario",
        barmode="group",
        color_discrete_map={
            f"🔴 {swap_from}": "#dc2626",
            f"🟢 {swap_to}":   "#16a34a",
        },
        labels={"Value": "Weekly amount (unit depends on metric)", "Metric": ""},
        title="Weekly environmental cost across all four metrics",
        height=350,
    )
    fig_mc.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#e2e8f0"),
        legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=40, b=10),
    )
    st.plotly_chart(fig_mc, use_container_width=True)
    st.caption(
        "Units differ per metric (kg CO₂-eq / m² / L / g PO₄-eq), "
        "so bars for different metrics are not directly comparable in height — "
        "focus on the red-vs-green contrast within each metric."
    )


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p class="footer">'
    "Data: Poore J & Nemecek T (2018). "
    "Reducing food's environmental impacts through producers and consumers. "
    "<i>Science</i> 360(6392):987–992.&nbsp;·&nbsp;"
    "Built with Streamlit &amp; Plotly.&nbsp;·&nbsp;"
    "Portfolio project — not affiliated with or endorsed by Poore &amp; Nemecek."
    "</p>",
    unsafe_allow_html=True,
)
