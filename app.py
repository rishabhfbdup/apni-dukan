import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Apni Dukaan Register", layout="centered")

st.title("🏪 Apni Dukaan Ka Digital Register")
st.write("🚀 Premium Version: Dashboard + Analytics + Charts + Passbook + Backup!")

# Session state for data storage
if "dukaan_ledger" not in st.session_state:
    st.session_state.dukaan_ledger = pd.DataFrame(columns=["ID", "Tarikh", "Grahak Ka Naam", "Mobile Number", "Details", "Amount (₹)"])

df = st.session_state.dukaan_ledger

# --- 1. DASHBOARD ANALYTICS & CHARTS ---
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

# --- 2. NAYI ENTRY ---
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
        
    submit_button = st.form_submit_button(label="Register me Save Karein")

if submit_button:
    if name == "":
        st.error("Kripya Grahak ka naam zaroor dalein!")
    elif amount <= 0:
        st.error("Kripya valid amount dalein!")
    else:
        now = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        next_id = int(df["ID"].max() + 1) if not df.empty else 1
        
        final_amount = amount if "Udhaar Diya" in entry_type else -amount
        entry_detail = details if details else ("Udhaar" if final_amount > 0 else "Jama Kiya")
        
        if not mobile and not df.empty:
            prev_mob = df[df["Grahak Ka Naam"].str.lower() == name.lower()]["Mobile Number"].values
            mobile = prev_mob[0] if len(prev_mob) > 0 else "N/A"
        elif not mobile:
            mobile = "N/A"

        new_row = pd.DataFrame([{
            "ID": next_id,
            "Tarikh": now,
            "Grahak Ka Naam": name,
            "Mobile Number": mobile,
            "Details": entry_detail,
            "Amount (₹)": final_amount
        }])
        
        st.session_state.dukaan_ledger = pd.concat([df, new_row], ignore_index=True)
        st.success(f"🎉 {name} ka hisab kamyabi se save ho gaya!")
        st.rerun()

# --- 3. SEARCH, REMINDERS & LIVE LEDGER ---
st.subheader("🔎 Grahak Dhoondhein aur Reminders")
search_query = st.text_input("Naam likh kar search karein...", "").strip().lower()

if not df.empty:
    summary_df = df.groupby(["Grahak Ka Naam", "Mobile Number"])["Amount (₹)"].sum().reset_index()
    summary_df.columns = ["Grahak Ka Naam", "Mobile Number", "Total Balance (₹)"]
    
    if search_query:
        summary_df = summary_df[summary_df["Grahak Ka Naam"].str.lower().str.contains(search_query)]
        
    for index, row in summary_df.iterrows():
        with st.container():
            c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
            with c1:
                st.write(f"👤 **{row['Grahak Ka Naam']}** ({row['Mobile Number']})")
            with c2:
                if row['Total Balance (₹)'] > 0:
                    st.write(f"🔴 Udhaar: **₹{row['Total Balance (₹)']}**")
                else:
                    st.write(f"🟢 Clear: **₹{abs(row['Total Balance (₹)'])}**")
            
            if row['Total Balance (₹)'] > 0:
                msg = f"Namaste {row['Grahak Ka Naam']}, aapka ₹{row['Total Balance (₹)']} ka udhaar baaki hai. Kripya samay par jama karein. 🙏 - Apni Dukaan"
            else:
                msg = f"Namaste {row['Grahak Ka Naam']}, aapka hisab poora clear hai. Dhanyawad! 🙏 - Apni Dukaan"
                
            with c3:
                if row['Mobile Number'] != "N/A" and len(str(row['Mobile Number'])) == 10:
                    whatsapp_url = f"https://wa.me/91{row['Mobile Number']}?text={urllib.parse.quote(msg)}"
                    st.markdown(f"[💬 WhatsApp]({whatsapp_url})", unsafe_allow_html=True)
                else:
                    st.write("No WhatsApp")
                    
            with c4:
                st.text_input("Copy Msg", value=msg, key=f"copy_{index}", label_visibility="collapsed")
                st.caption("Text select karke copy karein")
        st.markdown("---")

    # --- 4. GRAHAK PASSBOOK ---
    st.subheader("📉 Grahak Passbook (Statement History)")
    all_custs = sorted(df["Grahak Ka Naam"].unique())
    selected_cust = st.selectbox("Kisi Grahak ki poori history dekhne ke liye chunein:", ["-- Select Customer --"] + all_custs)
    
    if selected_cust != "-- Select Customer --":
        cust_history = df[df["Grahak Ka Naam"] == selected_cust][["Tarikh", "Details", "Amount (₹)"]].copy()
