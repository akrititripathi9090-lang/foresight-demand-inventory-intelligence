# Project FORESIGHT — Demand & Inventory Intelligence

A demand forecasting and inventory risk analysis project designed to help identify expected SKU-level demand, potential stockout and overstock risks, and inventory actions that require attention.

## 📌 Project Overview

**Project FORESIGHT** is a Data Science and Analytics project focused on demand forecasting and inventory intelligence for a fictional direct-to-consumer home and lifestyle brand, **NorthBay Living**.

The project combines historical sales, SKU information, calendar information, and inventory snapshots to build an analysis workflow that answers practical inventory planning questions:

* What demand can be expected for each SKU?
* Which SKUs may face stockout risk?
* Which SKUs may have excessive inventory?
* Which products should receive attention first?
* What is the estimated inventory exposure associated with these risks?

The project progresses from raw data preparation and exploratory analysis through demand forecasting, risk scoring, decision prioritization, dashboarding, and business impact analysis.


## 🎯 Project Objectives

The main objectives of Project FORESIGHT are:

1. Prepare and validate multiple business data sources.
2. Create an analysis-ready dataset.
3. Understand historical sales and demand patterns.
4. Establish a seasonal-naive forecasting baseline.
5. Develop a machine-learning demand forecasting model.
6. Evaluate forecast performance using appropriate metrics.
7. Identify potential stockout and overstock risks.
8. Prioritize inventory actions using a decision table.
9. Build an interactive Streamlit dashboard.
10. Estimate the financial exposure associated with inventory risks.
11. Present the results through an executive readout.

## 🔄 Project Workflow

```text
Raw Data
   ↓
Data Validation & Cleaning
   ↓
Analysis-Ready Dataset
   ↓
Exploratory Data Analysis
   ↓
Seasonal-Naive Baseline
   ↓
Demand Forecasting Model
   ↓
Model Evaluation
   ↓
Inventory Risk Scoring
   ↓
Decision Table
   ↓
Interactive Streamlit Dashboard
   ↓
Rupee Impact Analysis
   ↓
Executive Readout
```
# 📂 Data Sources

The project uses four main CSV datasets.

### 1. `sales_daily.csv`

Contains daily SKU-level sales information.

Key fields include:

* Date
* SKU
* Units Sold
* Revenue
* Price
* Promotion

### 2. `sku_master.csv`

Contains product-level information.

Key fields include:

* SKU
* Product Name
* Category
* Subcategory
* Launch Date
* Cost Price
* Selling Price
* Gross Margin Per Unit

### 3. `calendar.csv`

Contains calendar and seasonal information.

Key fields include:

* Date
* Year
* Month
* Quarter
* Week
* Day of Week
* Weekend indicator
* Season
* Holiday information
* Promotion events

### 4. `inventory_snapshots.csv`

Contains inventory position information.

Key fields include:

* Snapshot Date
* SKU
* Current Stock
* On Order
* Lead Time Days
* Safety Stock
* Reorder Point
* Inventory Value

# 🧹 Data Preparation

The data preparation workflow included:

* Loading all four source datasets.
* Inspecting dataset shapes and columns.
* Checking data types.
* Converting date fields to appropriate datetime formats.
* Checking missing values.
* Checking duplicate records.
* Checking duplicate SKU/date combinations.
* Checking SKU consistency across datasets.
* Checking negative sales, revenue, and price values.
* Validating calendar dates.
* Combining sales, SKU, and calendar information.
* Incorporating inventory information where required.
* Creating an analysis-ready dataset.

The processed analysis-ready data is stored in:

```text
processed/analysis_ready.csv
```

# 📊 Exploratory Data Analysis

The exploratory analysis examined several dimensions of the business data, including:

* Overall sales performance
* Daily demand
* Revenue trends
* Monthly demand
* Category performance
* Top-performing SKUs
* Promotional activity
* Seasonal patterns
* Weekend effects
* Holiday indicators
* Inventory indicators
* Price versus units sold
* Correlations between numerical variables

The EDA was used to understand the underlying demand patterns before developing the forecasting model.

# 📈 Demand Forecasting

## Seasonal-Naive Baseline

A seasonal-naive baseline was developed as a benchmark for the machine-learning model.

The baseline uses historical demand from the corresponding seasonal period as the forecast reference.

Weekly SKU-level demand was created and evaluated using a final test period.

Baseline outputs are stored in:

```text
processed/weekly_demand_baseline.csv
processed/sku_baseline_performance.csv
```

---

## Machine-Learning Forecast Model

A **Random Forest Regressor** was developed for SKU-level weekly demand forecasting.

The model incorporated features such as:

* SKU
* Historical demand lags
* Lag 1
* Lag 2
* Lag 4
* Lag 8
* Lag 12
* Lag 52
* Rolling demand averages
* Calendar information
* Price
* Promotion information

The model was evaluated on a final holdout period.

Forecast results are stored in:

```text
processed/model_forecast_results.csv
```

Feature importance results are stored in:

```text
processed/model_feature_importance.csv
```

# 📏 Model Evaluation

The final model evaluation produced the following results:

| Metric | Result |
| ------ | -----: |
| MAE    |  13.48 |
| RMSE   |  23.17 |
| WAPE   | 16.85% |
| Bias   |  -6.89 |

### Metric interpretation

**MAE — Mean Absolute Error**

Measures the average absolute difference between actual and predicted demand.

**RMSE — Root Mean Squared Error**

Penalizes larger forecasting errors more heavily than MAE.

**WAPE — Weighted Absolute Percentage Error**

Used as the primary forecasting accuracy metric for this project.

**Bias**

Indicates the overall direction of forecast error. The negative value indicates that the model's forecasts were lower than actual demand on average during the evaluated period.

The evaluation results are stored in:

```text
processed/model_evaluation_metrics.csv
```

# ⚠️ Inventory Risk Scoring

The project uses forecast demand and inventory information to identify potential inventory risks.

Two main risk categories were considered:

### Stockout Risk

Stockout risk compares expected demand during the inventory lead-time period against available stock.

The calculation considers:

```text
Lead-Time Demand
=
Forecast × Lead Time Days / 7
```

Available inventory is calculated using:

```text
Available Stock
=
Current Stock + On Order
```

A SKU is flagged for potential stockout risk when available stock is below estimated lead-time demand.

### Overstock Risk

Potential overstock is identified using a forward demand comparison.

The current project uses:

```text
Overstock Risk
=
Current Stock > Forecast × 4
```

These thresholds are rule-based project assumptions and should be reviewed before being used in a real production inventory system.

Risk results are stored in:

```text
processed/risk_scoring.csv
```
# 📋 Decision Table

The risk results are converted into an inventory decision table.

Each SKU receives an action such as:

* **REORDER**
* **OVERSTOCK**
* **MONITOR**

Priority is also assigned:

* **High**
* **Medium**
* **Normal**

The resulting decision table is stored in:

```text
processed/decision_table.csv
```

This table is designed to make the model output easier for an inventory planner or business user to interpret.

# 💰 Rupee Impact Analysis

The project also estimates the financial exposure associated with inventory risks.

Current analysis produced:

| Measure                             |         Result |
| ----------------------------------- | -------------: |
| REORDER SKUs                        |              5 |
| OVERSTOCK SKUs                      |             21 |
| MONITOR SKUs                        |             24 |
| Estimated Excess Units              |          4,909 |
| Estimated Excess Inventory Value    | ₹15,093,567.07 |
| Estimated Stockout Exposure         |     ₹67,557.84 |
| Combined Modeled Inventory Exposure | ₹15,161,124.91 |

These figures represent **modeled inventory exposure based on the project's forecasting and risk rules**.

They should not be interpreted as realized financial losses or guaranteed savings.

The detailed analysis is available in:

```text
Reports/rupee_impact_analysis.csv
```

# 📊 Interactive Dashboard

The project includes a Streamlit dashboard designed to make the analysis easier to explore.

### Dashboard features

* Category filter
* SKU filter
* Action/Risk filter
* KPI cards
* Risk distribution visualization
* Forecast vs Actual visualization
* Stock vs Forecast visualization
* Reorder priority visualization
* Decision table
* Download functionality
* Interactive Plotly charts

Dashboard application:

```bash
app/streamlit_app.py
```

### Live Dashboard

The Streamlit dashboard is deployed and available online.

**Live Dashboard:**
https://foresight-demand-inventory-intelligence-pkcu93wnjwyoxuutcmzueh.streamlit.app/


# 📑 Executive Readout

The project includes an executive-level PDF summarizing:

* Project overview
* Forecast performance
* Inventory risk distribution
* Business impact
* Recommended areas for operational review
* Model limitations and assumptions

Reports are stored under:

```text
Reports/
```

Current report files include:

```text
Reports/
├── FORESIGHT_Executive_Readout.pdf
├── FORESIGHT_Executive_Readout_Visual.pdf
└── rupee_impact_analysis.csv

# 🗂️ Repository Structure

```text
foresight-demand-inventory-intelligence/
│
├── .devcontainer/
│
├── Raw Datsets/
│   ├── calendar.csv
│   ├── inventory_snapshots.csv
│   ├── sales_daily.csv
│   └── sku_master.csv
│
├── Reports/
│   ├── FORESIGHT_Executive_Readout.pdf
│   ├── FORESIGHT_Executive_Readout_Visual.pdf
│   └── rupee_impact_analysis.csv
│
├── app/
│   ├── streamlit_app.py
│   ├── analysis_ready.csv
│   ├── model_forecast.csv
│   └── decision_table copy.csv
│
├── notebooks/
│   └── 01_data_quality_EDA.ipynb
│
├── processed/
│   ├── analysis_ready.csv
│   ├── decision_table.csv
│   ├── model_evaluation_metrics.csv
│   ├── model_feature_importance.csv
│   ├── model_forecast_results.csv
│   ├── risk_scoring.csv
│   ├── sku_baseline_performance.csv
│   └── weekly_demand_baseline.csv
│
├── service/
│   └── api.py
│
├── .gitignore
├── README.md
└── requirements.txt

# 🛠️ Technology Stack

### Programming & Analysis

* Python
* Pandas
* NumPy
* Scikit-learn
* Jupyter Notebook

### Visualization

* Plotly
* Matplotlib

### Machine Learning

* Random Forest Regressor
* Seasonal-naive forecasting baseline

### Dashboard

* Streamlit

### Version Control

* Git
* GitHub

---

# ▶️ Running the Dashboard Locally

Clone the repository:

```bash
git clone https://github.com/umairr-95/foresight-demand-inventory-intelligence.git
```

Move into the project directory:

```bash
cd foresight-demand-inventory-intelligence
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

Install the currently listed dashboard dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit dashboard:
```bash
python -m streamlit run app/streamlit_app.py
```
The dashboard will then be available through the local Streamlit URL shown in the terminal.

# 📦 Current Requirements

The repository currently lists:
streamlit
pandas
plotly

The forecasting and notebook workflow additionally uses machine-learning and analysis libraries such as scikit-learn and NumPy.

For complete reproducibility of the entire modelling workflow, the dependency file should be expanded to include all libraries required by the notebooks and model code.

# 🌐 Deployment

The Streamlit dashboard has been deployed using Streamlit Community Cloud.

The forecasting/risk API code is present in:

service/api.py

However, a publicly deployed API endpoint is **not currently part of the live project**.

Therefore, the repository does not claim that the FastAPI scoring service is currently deployed.

# ⚙️ Key Business Logic

The project uses the following main decision logic.

### Lead-Time Demand

Forecast × Lead Time Days / 7

### Available Stock

Current Stock + On Order

### Stockout Risk

Available Stock < Lead-Time Demand

### Overstock Risk

Current Stock > Forecast × 4

### Action Priority

Stockout Risk → High
Overstock Risk → Medium
Otherwise → Normal

These rules are project-level assumptions and should be recalibrated using actual service levels, lead-time distributions, safety-stock policies, and business constraints before production use.

# ⚠️ Limitations

Several limitations should be considered when interpreting the results.

### 1. Forecast evaluation period

The model was evaluated using a final holdout period rather than a full production-scale forecasting history.

### 2. Forecast bias

The final model produced a negative bias of approximately **-6.89**, indicating an overall tendency toward under-forecasting during the evaluated period.

### 3. Rule-based inventory thresholds

The stockout and overstock rules use simplified thresholds.

For example:
Overstock = Current Stock > Forecast × 4

A production implementation should consider:

* Service-level targets
* Lead-time variability
* Safety stock
* Demand uncertainty
* Supplier constraints
* Order quantities
* Seasonality
* Promotions

### 4. Financial estimates

The rupee values represent **modeled exposure**, not confirmed financial losses or savings.

### 5. API deployment

The FastAPI service exists in the repository but has not been deployed as a public scoring service.

### 6. Data governance

The repository currently contains the project datasets. In a real client engagement, data-sharing permissions and confidentiality requirements would need to be reviewed before making raw business data publicly accessible.

# 🚀 Future Improvements

Potential next steps include:

* Rolling-origin cross-validation
* More advanced forecasting models
* Hyperparameter tuning
* Improved feature engineering
* Probabilistic forecasting
* Prediction intervals
* Better lead-time demand estimation
* Dynamic safety-stock calculations
* Service-level optimization
* More sophisticated reorder recommendations
* Automated model retraining
* Production API deployment
* Automated data-quality checks
* Improved dashboard monitoring
* Model monitoring and drift detection

# 📌 Project Status

| Component                | Status                              
| ------------------------ | ------------------
| Raw data ingestion       | ✅ Completed                         
| Data validation          | ✅ Completed                         
| Analysis-ready dataset   | ✅ Completed                         
| Exploratory analysis     | ✅ Completed                         
| Seasonal-naive baseline  | ✅ Completed                         
| Demand forecasting model | ✅ Completed                         
| Model evaluation         | ✅ Completed                         
| Risk scoring             | ✅ Completed                         
| Decision table           | ✅ Completed                         
| Rupee impact analysis    | ✅ Completed                         
| Streamlit dashboard      | ✅ Deployed                          
| Executive readout        | ✅ Completed                         


---

# 👤 Author

**Umair Akbar Mohammed**

Data Science & Analytics Project

Project: **FORESIGHT — Demand & Inventory Intelligence**

---

## Repository

Project repository:

https://github.com/umairr-95/foresight-demand-inventory-intelligence.git

## Live Dashboard

https://foresight-demand-inventory-intelligence-eeg5qmcckjscbtvg55ku6d.streamlit.app/

# 📄 Disclaimer

This project is an analytical and portfolio/internship project using simulated project data and assumptions.

Forecasts, risk classifications, inventory exposure estimates, and recommended actions should be treated as analytical outputs rather than direct operational or financial decisions.

Before production use, the methodology should be validated against real business requirements, historical backtesting, inventory policies, and operational constraints.
