from pathlib import Path


import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# PAGE CONFIG

st.set_page_config(
    page_title="FORESIGHT Dashboard",
    page_icon="📦",
    layout="wide",
)

st.title("📦 FORESIGHT")
st.caption("Demand & Inventory Intelligence")

# PROJECT PATHS
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
PROCESSED_DIR = BASE_DIR / "processed"


def find_csv(filename: str) -> Path:
    """Find a project CSV in the app or processed folder."""
    for folder in (APP_DIR, PROCESSED_DIR):
        path = folder / filename
        if path.exists():
            return path
    raise FileNotFoundError(
        f"Could not find {filename}. Expected it in {APP_DIR} or {PROCESSED_DIR}."
    )


DECISION_PATH = find_csv("decision_table.csv")
FORECAST_PATH = find_csv("model_forecast_results.csv")
ANALYSIS_PATH = find_csv("analysis_ready.csv")

# LOAD + PREPARE DATA

@st.cache_data

def load_data():
    decision = pd.read_csv("D:/foresight-demand-inventory-intelligence/app/decision_table.csv")
    forecast = pd.read_csv("D:/foresight-demand-inventory-intelligence/app/model_forecast_results.csv")
    analysis = pd.read_csv("D:/foresight-demand-inventory-intelligence/app/analysis_ready.csv")

    # Standardize SKU values.
    for frame in (decision, forecast, analysis):
        if "SKU" in frame.columns:
            frame["SKU"] = frame["SKU"].astype(str).str.strip()

    # Forecast dataset.
    if "Model_Forecast" in forecast.columns and "Forecast" not in forecast.columns:
        forecast["Forecast"] = forecast["Model_Forecast"]

    if "Forecast" in forecast.columns:
        forecast["Forecast"] = pd.to_numeric(forecast["Forecast"], errors="coerce")
    if "Units_Sold" in forecast.columns:
        forecast["Actual"] = pd.to_numeric(forecast["Units_Sold"], errors="coerce")
    if "Week_Start" in forecast.columns:
        forecast["Week"] = pd.to_datetime(forecast["Week_Start"], errors="coerce")

    if "SKU" in forecast.columns and "Week" in forecast.columns:
        forecast = forecast.dropna(subset=["SKU", "Week"])

    # Decision numeric fields.
    numeric_columns = [
        "Forecast",
        "Current_Stock",
        "On_Order",
        "Lead_Time_Days",
        "Reorder_Point",
        "Stockout_Risk",
        "Overstock_Risk",
    ]
    for column in numeric_columns:
        if column in decision.columns:
            decision[column] = pd.to_numeric(decision[column], errors="coerce")

    # Use the latest inventory snapshot from analysis_ready.csv.
    if "Snapshot_Date" in analysis.columns:
        analysis["Snapshot_Date"] = pd.to_datetime(
            analysis["Snapshot_Date"], errors="coerce"
        )
        inventory = (
            analysis.sort_values("Snapshot_Date")
            .groupby("SKU", as_index=False)
            .tail(1)
        )
    else:
        inventory = analysis.drop_duplicates("SKU", keep="last")

    inventory_columns = [
        "SKU",
        "Category",
        "Current_Stock",
        "On_Order",
        "Lead_Time_Days",
        "Reorder_Point",
    ]
    inventory_columns = [c for c in inventory_columns if c in inventory.columns]
    inventory = inventory[inventory_columns].copy()

    # Prevent duplicate Category/stock columns after merging the snapshot.
    decision = decision.drop(columns=["Category"], errors="ignore")
    decision = decision.merge(
        inventory,
        on="SKU",
        how="left",
        suffixes=("", "_snapshot"),
    )

    for column in [
        "Current_Stock",
        "On_Order",
        "Lead_Time_Days",
        "Reorder_Point",
    ]:
        snapshot_column = f"{column}_snapshot"
        if snapshot_column in decision.columns:
            if column not in decision.columns:
                decision[column] = decision[snapshot_column]
            else:
                decision[column] = decision[column].fillna(decision[snapshot_column])
            decision.drop(columns=[snapshot_column], inplace=True)

    # Fill decision forecast from the latest model forecast by SKU if needed.
    if "Forecast" not in decision.columns:
        decision["Forecast"] = pd.NA
    if "SKU" in forecast.columns and "Forecast" in forecast.columns:
        latest_forecast = forecast.sort_values("Week").groupby("SKU")["Forecast"].last()
        decision["Forecast"] = decision["Forecast"].fillna(
            decision["SKU"].map(latest_forecast)
        )

    # Clean action/priority values.
    if "Action" not in decision.columns:
        decision["Action"] = "MONITOR"
    decision["Action"] = (
        decision["Action"].fillna("MONITOR").astype(str).str.strip().str.upper()
    )

    if "Priority" not in decision.columns:
        decision["Priority"] = "Normal"
    decision["Priority"] = decision["Priority"].fillna("Normal").astype(str).str.strip()

    # Fallback action calculation if exported action values are blank.
    has_stock = decision["Current_Stock"].notna() & decision["Forecast"].notna()
    derived_reorder = has_stock & (decision["Current_Stock"] < decision["Forecast"])
    blank_actions = decision["Action"].isin(["", "NAN", "NONE"])
    decision.loc[blank_actions & derived_reorder, "Action"] = "REORDER"
    decision.loc[blank_actions & ~derived_reorder, "Action"] = "MONITOR"
    decision.loc[decision["Action"] == "REORDER", "Priority"] = "High"

    # Keep useful risk labels available even when source risk columns are missing.
    if "Stockout_Risk" not in decision.columns:
        decision["Stockout_Risk"] = pd.NA
    if "Overstock_Risk" not in decision.columns:
        decision["Overstock_Risk"] = pd.NA

    return decision, forecast


try:
    decision, forecast = load_data()
except (FileNotFoundError, pd.errors.EmptyDataError, KeyError) as error:
    st.error(f"Dashboard data could not be loaded: {error}")
    st.info(
        "Make sure decision_table.csv, model_forecast_results.csv, and "
        "analysis_ready.csv are inside the project's app or processed folder."
    )
    st.stop()


# SIDEBAR FILTERS

st.sidebar.header("🎛️ Dashboard Filters")

categories = sorted(
    decision.get("Category", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()
)
skus = sorted(decision["SKU"].dropna().astype(str).unique().tolist())

available_actions = [
    action
    for action in ["REORDER", "OVERSTOCK", "MONITOR"]
    if action in decision["Action"].unique()
]
# Include any additional action values from the project data.
additional_actions = sorted(
    set(decision["Action"].dropna().astype(str).unique()) - set(available_actions)
)
actions = available_actions + additional_actions

# Every widget has an explicit unique key. This prevents the duplicate-ID error.
selected_sku = st.sidebar.selectbox(
    "SKU",
    ["All"] + skus,
    key="sidebar_sku_filter",
)

selected_actions = st.sidebar.multiselect(
    "Action / Risk",
    actions,
    default=actions,
    key="sidebar_action_filter",
)

selected_category = st.sidebar.selectbox(
    "Category",
    ["All"] + categories,
    key="sidebar_category_filter",
)

# ============================================================
# APPLY FILTERS
# ============================================================
filtered = decision.copy()

if selected_sku != "All":
    filtered = filtered[filtered["SKU"] == selected_sku]

if selected_category != "All" and "Category" in filtered.columns:
    filtered = filtered[filtered["Category"] == selected_category]

filtered = filtered[filtered["Action"].isin(selected_actions)]


# KPI CARDS — EXACTLY 4

st.subheader("📊 Inventory Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

reorder_count = int((filtered["Action"] == "REORDER").sum())
overstock_count = int((filtered["Action"] == "OVERSTOCK").sum())
monitor_count = int((filtered["Action"] == "MONITOR").sum())

with kpi1:
    st.metric("Total SKUs", f"{len(filtered):,}")
with kpi2:
    st.metric("🔴 Reorder", f"{reorder_count:,}")
with kpi3:
    st.metric("🟠 Overstock", f"{overstock_count:,}")
with kpi4:
    st.metric("🟢 Monitor", f"{monitor_count:,}")


# RISK DISTRIBUTION

st.subheader("⚠️ Risk Distribution")

risk = (
    filtered["Action"]
    .value_counts()
    .reindex(actions, fill_value=0)
    .rename_axis("Action")
    .reset_index(name="SKUs")
)

if risk["SKUs"].sum() == 0:
    st.info("No risk data matches the selected filters.")
else:
    fig_risk = px.pie(
        risk,
        names="Action",
        values="SKUs",
        hole=0.48,
        title="Inventory Risk / Action Distribution",
        color="Action",
        color_discrete_map={
            "REORDER": "#E45756",
            "OVERSTOCK": "#F2A541",
            "MONITOR": "#2A9D8F",
        },
    )
    fig_risk.update_traces(textinfo="percent+label", hovertemplate="%{label}: %{value} SKUs<extra></extra>")
    fig_risk.update_layout(height=430, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig_risk, use_container_width=True, key="risk_distribution_chart")

# FORECAST VS ACTUAL
st.subheader("📈 Forecast vs Actual")

forecast_data = forecast.copy()

if selected_sku != "All" and "SKU" in forecast_data.columns:
    forecast_data = forecast_data[forecast_data["SKU"] == selected_sku]
else:
    # Apply category and action filters to the forecast chart through the
    # currently visible SKU population.
    visible_skus = set(filtered["SKU"].astype(str))
    if visible_skus:
        forecast_data = forecast_data[forecast_data["SKU"].isin(visible_skus)]

if selected_category != "All" and "Category" in decision.columns and selected_sku == "All":
    category_skus = set(
        decision.loc[decision["Category"] == selected_category, "SKU"].astype(str)
    )
    forecast_data = forecast_data[forecast_data["SKU"].isin(category_skus)]

if "Week" in forecast_data.columns and "Actual" in forecast_data.columns and "Forecast" in forecast_data.columns:
    forecast_data = forecast_data.dropna(subset=["Week"])
    weekly = (
        forecast_data.groupby("Week", as_index=False)[["Actual", "Forecast"]]
        .sum()
        .sort_values("Week")
    )

    if not weekly.empty:
        chart_data = weekly.melt(
            id_vars="Week",
            value_vars=["Actual", "Forecast"],
            var_name="Series",
            value_name="Units",
        )
        fig_forecast = px.line(
            chart_data,
            x="Week",
            y="Units",
            color="Series",
            markers=True,
            title="Actual Units Sold vs Forecast",
            labels={"Units": "Units", "Week": "Week"},
            color_discrete_map={"Actual": "#457B9D", "Forecast": "#E45756"},
        )
        fig_forecast.update_layout(height=450, hovermode="x unified")
        st.plotly_chart(fig_forecast, use_container_width=True, key="forecast_actual_chart")
    else:
        st.info("No forecast/actual data matches the selected filters.")
else:
    st.warning("Forecast data is missing Week_Start, Units_Sold, or Forecast columns.")


# STOCK VS FORECAST

st.subheader("📦 Stock vs Forecast")

stock_columns = [c for c in ["SKU", "Current_Stock", "Forecast"] if c in filtered.columns]
if len(stock_columns) == 3:
    stock = filtered[stock_columns].dropna(subset=["Forecast"]).copy()
    stock = stock.sort_values("Forecast", ascending=False).head(15)

    if not stock.empty:
        stock_long = stock.melt(
            id_vars="SKU",
            value_vars=["Current_Stock", "Forecast"],
            var_name="Measure",
            value_name="Units",
        )
        fig_stock = px.bar(
            stock_long,
            x="SKU",
            y="Units",
            color="Measure",
            barmode="group",
            title="Current Stock Compared With Forecast Demand",
            labels={"Units": "Units", "SKU": "SKU"},
            color_discrete_map={"Current_Stock": "#2A9D8F", "Forecast": "#E45756"},
        )
        fig_stock.update_layout(height=450, hovermode="x unified")
        st.plotly_chart(fig_stock, use_container_width=True, key="stock_forecast_chart")
    else:
        st.info("No stock/forecast data matches the selected filters.")
else:
    st.warning("Current_Stock and Forecast columns are required for this chart.")


# REORDER PRIORITY VISUALIZATION

st.subheader("🚨 Reorder Priority")

priority = filtered[filtered["Action"] == "REORDER"].copy()

if priority.empty:
    st.info("No REORDER SKUs match the selected filters.")
else:
    priority = priority.dropna(subset=["Forecast"]).copy()
    priority["Priority"] = priority["Priority"].replace({"Normal": "Watch"})
    priority = priority.sort_values(
        ["Forecast", "SKU"], ascending=[False, True]
    ).head(10)

    if not priority.empty:
        fig_priority = px.bar(
            priority.sort_values("Forecast"),
            x="Forecast",
            y="SKU",
            orientation="h",
            color="Priority",
            text="Forecast",
            title="Top SKUs Requiring Reorder",
            labels={"Forecast": "Forecast Demand", "SKU": "SKU"},
            color_discrete_map={
                "High": "#E45756",
                "Watch": "#F2A541",
                "Normal": "#457B9D",
            },
            hover_data=[
                c
                for c in ["Action", "Current_Stock", "On_Order", "Priority"]
                if c in priority.columns
            ],
        )
        fig_priority.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_priority.update_layout(height=450)
        st.plotly_chart(fig_priority, use_container_width=True, key="reorder_priority_chart")
    else:
        st.info("No reorder products with forecast values are available.")

# DECISION TABLE

st.subheader("📋 Decision Table")

display_columns = [
    "SKU",
    "Category",
    "Forecast",
    "Current_Stock",
    "On_Order",
    "Lead_Time_Days",
    "Stockout_Risk",
    "Overstock_Risk",
    "Action",
    "Priority",
]
display_columns = [c for c in display_columns if c in filtered.columns]

display_table = filtered[display_columns].copy()

# Make the table easier to inspect without changing the underlying data.
for column in ["Forecast", "Current_Stock", "On_Order", "Lead_Time_Days"]:
    if column in display_table.columns:
        display_table[column] = pd.to_numeric(display_table[column], errors="coerce").round(2)

st.dataframe(
    display_table,
    use_container_width=True,
    hide_index=True,
)

# DOWNLOAD
st.subheader("⬇️ Download")

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Filtered Decisions",
    data=csv_bytes,
    file_name="foresight_inventory_decisions.csv",
    mime="text/csv",
    key="download_filtered_decisions",
)

st.caption(
    f"Showing {len(filtered):,} SKU records after applying the selected filters. "
    "Charts are interactive: hover, zoom, pan, and use the Plotly toolbar."
)

# Command for local run
# python -m streamlit run app/streamlit_app.py

df find_csv("D:/foresight-demand-inventory-intelligence/app/decision_table.csv")