import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import io
import altair as alt

# ---------------- CONFIG ----------------
USE_XERO_API = False
# ----------------------------------------

# ---------- Data Loader ----------
def load_sample_data():
    np.random.seed(42)

    accounts = pd.DataFrame([
        {"AccountCode": "200", "Name": "Sales - Retail", "Type": "REVENUE"},
        {"AccountCode": "210", "Name": "Sales - Wholesale", "Type": "REVENUE"},
        {"AccountCode": "500", "Name": "Cost of Goods Sold", "Type": "EXPENSE"},
        {"AccountCode": "610", "Name": "Salaries & Wages", "Type": "EXPENSE"},
        {"AccountCode": "620", "Name": "Rent", "Type": "EXPENSE"},
        {"AccountCode": "630", "Name": "Utilities", "Type": "EXPENSE"},
        {"AccountCode": "640", "Name": "Marketing", "Type": "EXPENSE"},
        {"AccountCode": "650", "Name": "Office Supplies", "Type": "EXPENSE"},
    ])

    today = datetime.today()
    start = datetime(today.year, 1, 1)
    months = [(start + relativedelta(months=i)).strftime("%Y-%m") for i in range(8)]

    def make_budget_for_account(code, base, variance=0.1):
        return [
            {"Month": mon, "AccountCode": code,
             "BudgetAmount": round(base * (1 + np.random.uniform(-variance, variance)), 2)}
            for mon in months
        ]

    budgets = pd.DataFrame(
        make_budget_for_account("200", 120000)
        + make_budget_for_account("210", 80000)
        + make_budget_for_account("500", 95000)
        + make_budget_for_account("610", 45000)
        + make_budget_for_account("620", 20000)
        + make_budget_for_account("630", 8000)
        + make_budget_for_account("640", 15000)
        + make_budget_for_account("650", 3000)
    )

    def random_dates_in_month(month_str, n):
        base = datetime.strptime(month_str + "-01", "%Y-%m-%d")
        days_in_month = (base + relativedelta(months=1) - relativedelta(days=1)).day
        return [base.replace(day=int(d)).date() for d in np.random.randint(1, days_in_month + 1, size=n)]

    trans_rows = []
    for _, b in budgets.iterrows():
        n = np.random.randint(8, 21)
        dates = random_dates_in_month(b["Month"], n)
        base_amount = b["BudgetAmount"] / n
        noise = np.random.uniform(-0.35, 0.35, size=n)
        drift = np.random.uniform(-0.15, 0.15)
        amounts = base_amount * (1 + noise) * (1 + drift)
        for d, amt in zip(dates, amounts):
            trans_rows.append({
                "Date": pd.to_datetime(d),
                "AccountCode": b["AccountCode"],
                "Description": f"Auto TXN for {b['AccountCode']}",
                "Amount": round(float(amt), 2),
            })

    transactions = pd.DataFrame(trans_rows).merge(accounts, on="AccountCode", how="left")
    transactions["Month"] = transactions["Date"].dt.strftime("%Y-%m")

    return accounts, budgets, transactions

# ---------- Load Data ----------
accounts, budgets, transactions = load_sample_data()

# ---------- Actuals vs Budget ----------
actuals = transactions.groupby(["Month", "AccountCode"], as_index=False).agg(ActualAmount=("Amount", "sum"))
actuals = actuals.merge(accounts, on="AccountCode", how="left")

actuals_vs_budget = budgets.merge(actuals, on=["Month", "AccountCode"], how="left")
actuals_vs_budget["ActualAmount"] = actuals_vs_budget["ActualAmount"].fillna(0.0)
actuals_vs_budget = actuals_vs_budget.merge(accounts, on="AccountCode", how="left", suffixes=("", "_acc"))
actuals_vs_budget["Variance"] = actuals_vs_budget["ActualAmount"] - actuals_vs_budget["BudgetAmount"]
actuals_vs_budget["VariancePct"] = np.where(
    actuals_vs_budget["BudgetAmount"] != 0,
    actuals_vs_budget["Variance"] / actuals_vs_budget["BudgetAmount"],
    np.nan
)

detail_cols = ["Month", "AccountCode", "Name", "Type", "BudgetAmount", "ActualAmount", "Variance", "VariancePct"]
detail = actuals_vs_budget[detail_cols].sort_values(["Month", "AccountCode"])

# Monthly P&L summary
monthly_type = detail.groupby(["Month", "Type"], as_index=False)[["BudgetAmount", "ActualAmount", "Variance"]].sum()
monthly_pivot = monthly_type.pivot(index="Month", columns="Type", values=["BudgetAmount", "ActualAmount", "Variance"]).reset_index()

# KPI latest month
latest_month = sorted(detail["Month"].unique())[-1]
kpi_latest = monthly_pivot[monthly_pivot["Month"] == latest_month].copy()

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Automated Budget Tracker", layout="wide")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", [
    "Dashboard", "Accounts", "Budgets", "Transactions",
    "Actuals vs Budget", "Charts", "Monthly Summary", "KPIs", "Download Report"
])

# --------- Dashboard ---------
if page == "Dashboard":
    st.title("📊 Automated Budget Tracker - Dashboard")

    # KPIs
    st.subheader(f"Key Metrics - {latest_month}")
    col1, col2, col3 = st.columns(3)

    revenue = kpi_latest[("ActualAmount", "REVENUE")].values[0]
    expenses = kpi_latest[("ActualAmount", "EXPENSE")].values[0]
    profit = revenue - expenses

    col1.metric("Revenue (Actual)", f"${revenue:,.0f}")
    col2.metric("Expenses (Actual)", f"${expenses:,.0f}")
    col3.metric("Profit/Loss", f"${profit:,.0f}")

    # P&L Table
    st.subheader("Latest Month P&L")
    st.dataframe(kpi_latest, use_container_width=True)

    # Trend Chart
    st.subheader("Budget vs Actual Trend")
    trend_df = detail.groupby(["Month", "Type"], as_index=False)[["BudgetAmount", "ActualAmount"]].sum()
    chart = alt.Chart(trend_df).transform_fold(
        ["BudgetAmount", "ActualAmount"],
        as_=["Metric", "Value"]
    ).mark_line(point=True).encode(
        x="Month:T",
        y="Value:Q",
        color="Metric:N",
        strokeDash="Type:N"
    ).properties(width=800)
    st.altair_chart(chart, use_container_width=True)

elif page == "Accounts":
    st.title("🏦 Accounts Overview")

    col1, col2 = st.columns(2)
    col1.metric("Total Accounts", accounts.shape[0])
    col2.metric("Revenue Accounts", accounts[accounts['Type']=="REVENUE"].shape[0])

    st.subheader("Accounts by Type")
    chart = alt.Chart(accounts).mark_bar().encode(
        x="Type:N", y="count():Q", color="Type:N"
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("📋 Full Accounts List"):
        st.dataframe(accounts, use_container_width=True)

elif page == "Budgets":
    st.title("📑 Budgets")

    st.subheader("Budget Allocation by Account")
    budget_summary = budgets.groupby("AccountCode", as_index=False)["BudgetAmount"].sum().merge(accounts, on="AccountCode")
    chart = alt.Chart(budget_summary).mark_bar().encode(
        x="Name:N", y="BudgetAmount:Q", color="Type:N"
    ).properties(width=800)
    st.altair_chart(chart, use_container_width=True)

    with st.expander("📋 Full Budget Table"):
        st.dataframe(budgets, use_container_width=True)

elif page == "Transactions":
    st.title("💳 Transactions")

    st.subheader("Transaction Volume by Month")
    txn_summary = transactions.groupby("Month", as_index=False)["Amount"].sum()
    chart = alt.Chart(txn_summary).mark_area(opacity=0.5).encode(
        x="Month:T", y="Amount:Q"
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("📋 All Transactions"):
        st.dataframe(transactions, use_container_width=True)

elif page == "Actuals vs Budget":
    st.title("📊 Actuals vs Budget")

    st.subheader("Variance by Account")
    var_summary = detail.groupby("Name", as_index=False)[["Variance"]].sum()
    chart = alt.Chart(var_summary).mark_bar().encode(
        x="Variance:Q",
        y=alt.Y("Name:N", sort='-x'),
        color=alt.condition("datum.Variance > 0", alt.value("green"), alt.value("red"))
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("📋 Variance Details"):
        st.dataframe(detail.style.background_gradient(
            subset=["Variance"], cmap="RdYlGn"), use_container_width=True)

elif page == "Charts":
    st.title("📈 Budget vs Actual Charts")

    st.subheader("By Account")
    account_summary = detail.groupby("Name", as_index=False)[["BudgetAmount", "ActualAmount"]].sum()
    chart1 = alt.Chart(account_summary).transform_fold(
        ["BudgetAmount", "ActualAmount"], as_=["Type", "Value"]
    ).mark_bar().encode(x="Name:N", y="Value:Q", color="Type:N")
    st.altair_chart(chart1, use_container_width=True)

    st.subheader("By Month")
    monthly_summary = detail.groupby("Month", as_index=False)[["BudgetAmount", "ActualAmount"]].sum()
    chart2 = alt.Chart(monthly_summary).transform_fold(
        ["BudgetAmount", "ActualAmount"], as_=["Type", "Value"]
    ).mark_line(point=True).encode(
        x="Month:T", y="Value:Q", color="Type:N"
    )
    st.altair_chart(chart2, use_container_width=True)

elif page == "Monthly Summary":
    st.title("📅 Monthly P&L Summary")

    melted = monthly_type.melt(
        id_vars=["Month", "Type"],
        value_vars=["BudgetAmount", "ActualAmount"],
        var_name="Metric", value_name="Value"
    )
    chart = alt.Chart(melted).mark_bar().encode(
        x="Month:T", y="Value:Q", color="Type:N", column="Metric:N"
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("📋 Monthly Table"):
        st.dataframe(monthly_pivot, use_container_width=True)

elif page == "KPIs":
    st.title(f"📌 KPIs - {latest_month}")

    col1, col2, col3 = st.columns(3)
    revenue = kpi_latest[("ActualAmount", "REVENUE")].values[0]
    expenses = kpi_latest[("ActualAmount", "EXPENSE")].values[0]
    profit = revenue - expenses

    col1.metric("Revenue", f"${revenue:,.0f}")
    col2.metric("Expenses", f"${expenses:,.0f}")
    col3.metric("Profit", f"${profit:,.0f}")

    st.subheader("KPI Table")
    st.dataframe(kpi_latest, use_container_width=True)

elif page == "Download Report":
    st.subheader("Download Excel Report")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        if isinstance(monthly_pivot.columns, pd.MultiIndex):
            monthly_pivot.columns = ["_".join([str(c) for c in col if c]).strip("_")
                                     for col in monthly_pivot.columns]
        monthly_pivot.reset_index(drop=True, inplace=True)
        monthly_pivot.to_excel(writer, sheet_name="Monthly_Summary", index=False)

        raw_data = detail.copy()
        if isinstance(raw_data.columns, pd.MultiIndex):
            raw_data.columns = ["_".join([str(c) for c in col if c]).strip("_")
                                for col in raw_data.columns]
        raw_data.reset_index(drop=True, inplace=True)
        raw_data.to_excel(writer, sheet_name="Raw_Data", index=False)

    st.download_button(
        label="📥 Download Excel Report",
        data=buffer.getvalue(),
        file_name="budget_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
