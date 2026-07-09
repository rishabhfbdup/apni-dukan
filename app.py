import streamlit as st
import pandas as pd
import urllib.parse

# Page configuration
st.set_page_config(page_title="Apni Dukaan Register", layout="centered")

st.title("🏪 Apni Dukaan Ka Digital Register")
st.write("Ab diary chhodo, digital hisab rakho aur WhatsApp par reminder bhejo!")

# Session state use karenge data save rakhne ke liye
if "dukaan_data" not in st.session_state:
    st.session_state.dukaan_data = pd.DataFrame(columns=["ID", "Grahak Ka Naam", "Mobile Number", "Total Balance (₹)"])

df = st.session_state.dukaan_data

# --- FEATURE 1: DASHBOARD ANALYTICS ---
st.markdown("### 📊 Aaj Ka Hisab-Kitab")
total_customers = len(df)
total_udhaar = df[df["Total Balance (₹)"] > 0]["Total Balance (₹)"].sum()

col_cust, col_bal = st.columns(2)
with col_cust:
    st.metric(label="Total Active Customers", value=total_customers)
with col_bal:
    st.metric(label="Total Market Udhaar (₹)", value=f"₹ {total_udhaar}")
st.markdown("---")

# --- FEATURE 2: TYPE OF ENTRY (UDHAAR vs JAMA) ---
st.subheader("📝 Nayi Entry Jodein")
with st.form(key="entry_form", clear_on_submit=True):
    name = st.text_input("Grahak Ka Naam (Required)")
    mobile = st.text_input("Mobile Number (Optional)", max_chars=10)
    
    col_type, col_amt = st.columns(2)
    with col_type:
        entry_type = st.selectbox("Entry Type", ["🔴 Udhaar Diya (Given)", "🟢 Jama Kiya (Received)"])
    with col_amt:
        amount = st.number_input("Amount (₹)", min_value=0, step=1)
        
    submit_button = st.form_submit_button(label="Register me Save Karein")

if submit_button:
    if name.strip() == "":
        st.error("Kripya Grahak ka naam zaroor dalein!")
    else:
        # Check if customer already exists
        existing_idx = df[df["Grahak Ka Naam"].str.lower() == name.strip().lower()].index
        
        # Calculate final amount based on type
        final_amount = amount if "Udhaar Diya" in entry_type else -amount
        
        if not existing_idx.empty:
            # Update existing customer
            st.session_state.dukaan_data.at[existing_idx[0], "Total Balance (₹)"] += final_amount
            # If mobile was provided, update it too
            if mobile:
                st.session_state.dukaan_data.at[existing_idx[0], "Mobile Number"] = mobile
            st.success(f"🎉 {name} ka account update ho gaya!")
        else:
            # Create new customer
            next_id = int(df["ID"].max() + 1)
