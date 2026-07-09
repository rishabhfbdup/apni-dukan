import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Apni Dukaan Register", layout="centered")

# --- FEATURE 1: APP THEME CHANGER ---
st.sidebar.title("⚙️ App Settings")
theme = st.sidebar.selectbox("App Mode Chunein:", ["☀️ Light Mode", "🌑 Dark Mode"])

# Custom CSS for Dark Mode styling dynamically
if "Dark Mode" in theme:
    st.markdown(
        """
        <style>
        .stApp { background-color: #121212; color: #FFFFFF; }
        div[data-testid="stForm"] { background-color: #1E1E1E !important; border: 1px solid #333 !important; }
        div[data-testid="stMetricWidget"] { background-color: #1E1E1E !important; border: 1px solid #333 !important; padding: 10px; border-radius: 5px; }
        </style>
        """,
        unsafe_allow_html=True
    )

st.title("🏪 Apni Dukaan Ka Digital Register")
st.write("🚀 VIP Version: Analytics + Charts + Passbook + Calculator + Credit Alert!")

# Session state for data storage
if "dukaan_ledger" not in st.session_state:
    st.session_state.dukaan_ledger = pd.DataFrame(columns=["ID", "Tarikh", "Grahak Ka Naam", "Mobile Number", "Details", "Amount (₹)"])

df = st.session_state.dukaan_ledger

# --- DASHBOARD ANALYTICS & CHARTS ---
st.markdown("### 📊 Aaj Ka Hisab-Kitab")
if not df.empty:
    unique_cust = df["Grahak Ka Naam"].nunique()
    net_balances = df.groupby("Grahak Ka Naam")["Amount (₹)"].sum().reset_index()
    net_balances.columns = ["Grahak Ka Naam", "Net Balance (₹)"]
    total_udhaar = net_balances[net_balances["Net Balance (₹)"] > 0]["Net Balance (₹)"].sum()
else:
    unique_cust = 0
    total_udhaar = 0
    net_balances = pd.DataFrame(columns=["Grahak Ka Naam", "Net Balance (₹)"])

col_cust, col_bal = st.columns(2)
with col_cust:
    st.metric(label="Total Active Customers", value=unique_cust)
with col_bal:
    st.metric(label="Total Market Udhaar (₹)", value=f"₹ {total_udhaar}")

# CHART
if not net_balances.empty and total_udhaar > 0:
    st.markdown("#### 📈 Udhaar Ka Graph (Top Grahak)")
    chart_data = net_balances[net_balances["Net Balance (₹)"] > 0].set_index("Grahak Ka Naam")
    st.bar_chart(chart_data)

st.markdown("---")

# --- NAYI ENTRY FORM ---
st.subheader("📝 Nayi Entry Jodein")
with st.form(key="entry_form", clear_on_submit=True):
    name = st.text_input("Grahak Ka Naam (Required)").strip()
    mobile = st.text_input("Mobile Number (Optional)", max_chars=10)
    details = st.text_input("Samaan ki Details (e.g., Cheeni, Sabun, Cash)")
    
    col_type, col_amt = st.columns(2)
    with col_type:
        entry_type = st.selectbox("Entry Type", ["🔴 Udhaar Diya (Given)", "🟢 Jama Kiya (Received)"])
    with col_amt:
        amount = st.number_input("Amount (₹)", min_value=0, step=1)
        
    submit_button = st.form_submit_button(label="Register me Save
