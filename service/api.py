from fastapi import FastAPI, HTTPException
import pandas as pd
from pathlib import Path

app = FastAPI(
    title="FORESIGHT Scoring Service",
    description="Demand Forecast and Inventory Risk Service"
)

# Project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Correct location of your processed data
DATA_FILE = BASE_DIR / "processed" / "decision_table.csv"

# Load decision data
data = pd.read_csv(DATA_FILE)


@app.get("/")
def home():
    return {
        "message": "FORESIGHT Scoring Service is running"
    }


@app.get("/score/{sku}")
def score_sku(sku: str):

    result = data[
        data["SKU"].astype(str).str.upper()
        == sku.upper()
    ]

    if result.empty:
        raise HTTPException(
            status_code=404,
            detail="SKU not found"
        )

    row = result.iloc[0]

    return {
        "SKU": row["SKU"],
        "Forecast": row["Forecast"],
        "Current_Stock": row["Current_Stock"],
        "On_Order": row["On_Order"],
        "Lead_Time_Days": row["Lead_Time_Days"],
        "Stockout_Risk": bool(row["Stockout_Risk"]),
        "Overstock_Risk": bool(row["Overstock_Risk"]),
        "Action": row["Action"],
        "Priority": row["Priority"]
    }