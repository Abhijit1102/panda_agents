# src/emi_calculator.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from math import pow

def emi_calculator_app():
    st.title("💰 EMI Calculator")

    st.sidebar.header("Loan Details")
    principal = st.sidebar.number_input("Loan Amount (₹)", value=500000, step=10000, min_value=1000)
    annual_rate = st.sidebar.slider("Annual Interest Rate (%)", 0.0, 25.0, 7.5, 0.1)
    years = st.sidebar.slider("Tenure (Years)", 1, 30, 5)

    n = years * 12
    r = annual_rate / 100 / 12

    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

    total_payment = emi * n
    total_interest = total_payment - principal

    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly EMI", f"₹{emi:,.2f}")
    col2.metric("Total Payment", f"₹{total_payment:,.2f}")
    col3.metric("Total Interest", f"₹{total_interest:,.2f}")

    def amortization_schedule(principal, emi, r, n):
        balance = principal
        schedule = []
        for m in range(1, n + 1):
            interest = 0 if r == 0 else balance * r
            principal_paid = emi - interest
            balance = max(balance - principal_paid, 0)
            schedule.append([m, emi, principal_paid, interest, balance])
        return pd.DataFrame(schedule, columns=["Month", "Payment", "Principal Paid", "Interest Paid", "Balance"])

    schedule_df = amortization_schedule(principal, emi, r, n)
    st.subheader("📅 Amortization Schedule")
    st.dataframe(schedule_df.head(60), width="stretch") 

    st.subheader("📈 Principal vs Interest Over Time")
    fig, ax = plt.subplots()
    ax.plot(schedule_df["Month"], schedule_df["Principal Paid"].cumsum(), label="Principal Paid")
    ax.plot(schedule_df["Month"], schedule_df["Interest Paid"].cumsum(), label="Interest Paid")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (₹)")
    ax.legend()
    st.pyplot(fig)

    csv = schedule_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Amortization Schedule (CSV)",
        data=csv,
        file_name="amortization_schedule.csv",
        mime="text/csv"
    )
