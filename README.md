# 📊 Automated Budget Tracker — Streamlit App

An interactive **Budget Tracking Dashboard** built with **Streamlit, Pandas, NumPy, and Altair**.  
It helps finance teams and business owners **track budgets, monitor expenses, compare actuals vs budgets, and export reports** — all in one place.  

👉 **Live Demo**: [Marketing Dashboard on Streamlit Cloud](https://automatedbudgettracker-7bdu6drwnq9zjqzj3zczvc.streamlit.app/)

---

## 🚀 Features

- **Multi-page Navigation** (Dashboard, Accounts, Budgets, Transactions, Variance, Charts, Monthly Summary, KPIs, Report Export)
- **KPIs at a glance** → Revenue, Expenses, Profit/Loss
- **Charts & Visuals** powered by Altair
- **Variance Analysis** (Actual vs Budget with % difference)
- **Monthly P&L Summaries** with drilldowns
- **Downloadable Excel Reports** for offline analysis

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io) → Interactive UI
- [Pandas](https://pandas.pydata.org/) → Data handling
- [NumPy](https://numpy.org/) → Randomized sample data & calculations
- [Altair](https://altair-viz.github.io/) → Interactive charts
- [Dateutil](https://dateutil.readthedocs.io/) → Month-based calculations
- [XlsxWriter](https://xlsxwriter.readthedocs.io/) → Excel report export

---

## 📂 Project Structure

📂 Automated-Budget-Tracker
├── automated_budget_tracker.py # Main Streamlit app
├── requirements.txt # Dependencies
└── README.md # Documentation

---

## ⚡ Installation & Usage

Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/Automated-Budget-Tracker.git
cd Automated-Budget-Tracker
pip install -r requirements.txt
```
Run the Streamlit app:
```bash
streamlit run automated_budget_tracker.py
```

## 📊 Sample Data

The app generates synthetic financial data automatically:
- Accounts (Revenue & Expense categories)
- Monthly Budgets (per account)
- Transactions (randomized per month)
This makes it ready-to-use without uploading any external dataset.

##🔮 Future Improvements

- ✅ Integration with Xero API (toggle already in code)
- 📈 Advanced forecasting (ARIMA / Prophet)
- 📊 Multi-company consolidation
- 📤 Automated report emailing

## 👨‍💻 Author

Developed by **Vincent James Salvino**   
💼 Web Development • Data & Automation • Creative Media  
📧 salvino222vincent@gmail.com
🌐 
