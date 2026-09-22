
import streamlit as st
import pandas as pd

# Page settings
st.set_page_config(
    page_title="FORESIGHT Dashboard",
    layout="wide"
)

st.title("FORESIGHT — Demand & Inventory Dashboard")

# Load decision table
data = pd.read_csv(
    "D:/foresight-demand-inventory-intelligence/app/decision_table.csv"
)

# Sidebar filters
st.sidebar.header("Filters")

sku_list = ["All"] + sorted(data["SKU"].unique().tolist())

selected_sku = st.sidebar.selectbox(
    "Select SKU",
    sku_list
)

# Apply filter
if selected_sku != "All":
    filtered = data[data["SKU"] == selected_sku]
else:
    filtered = data

# Summary
st.subheader("Inventory Risk Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Products",
    len(filtered)
)

col2.metric(
    "Reorder",
    (filtered["Action"] == "REORDER").sum()
)

col3.metric(
    "Overstock",
    (filtered["Action"] == "OVERSTOCK").sum()
)

# Decision table
st.subheader("Inventory Decisions")

st.dataframe(
    filtered,
    use_container_width=True
)


# (using terminal put this syntax to view the dashboard in local host)
# python -m streamlit run app/streamlit_app.py