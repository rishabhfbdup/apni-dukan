import streamlit as st
import pandas as pd
import urllib.parse
import requests
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Apni Dukaan Register", layout="centered")

# FIREBASE REALTIME DATABASE URL
FIREBASE_URL = "https://apni-dukaan-db-default-rtdb.firebaseio.com/"

# --- FEATURE 1: APP THEME CHANGER ---
st.sidebar.title("⚙️ App Settings")
theme = st.sidebar.selectbox("App Mode Chunein:", ["☀️ Light Mode", "🌑 Dark Mode"])

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

# --- DUKAANDAR PROFILE SESSION STATE ---
if "dukaan_profile" not in st.session_state:
    st.session_state.dukaan_profile = {
        "registered": False, "owner_name": "", "shop_name": "", "mobile": "", "alt_mobile": "", "pan": ""
    }

if "dukaan_ledger" not in st.session_state:
    st.session_state.dukaan_ledger = pd.DataFrame(columns=["ID", "Tarikh", "Grahak Ka Naam", "Mobile Number", "Details", "Amount (₹)"])

df = st.session_state.dukaan_ledger

# --- LOCK GATE: LOGIN / REGISTRATION SYSTEM ---
if not st.session_state.dukaan_profile["registered"]:
    st.title("🔐 Apni Dukaan Digital Register Login")
    
    choice = st.radio("Kya aap naye user hain ya purane?", ["Existing User (Login)", "New User (Register)"], horizontal=True)
    
    if choice == "Existing User (Login)":
        st.subheader("🔑 Apna Account Login Karein")
        with st.form(key="login_form"):
            l_mobile = st.text_input("Registered Mobile Number", max_chars=10)
            l_pin = st.text_input("Enter 4-Digit Secret PIN", type="password", max_chars=4)
            login_btn = st.form_submit_button("🔓 Log In")
            
        if login_btn:
            if len(l_mobile.strip()) != 10 or len(l_pin.strip()) != 4:
                st.error("❌ Kripya sahi Mobile Number aur 4-digit PIN dalein!")
            else:
                try:
                    # Fetching user from Firebase using mobile number
                    response = requests.get(f"{FIREBASE_URL}users/{l_mobile.strip()}.json")
                    user_data = response.json()
                    
                    if user_data and user_data.get("pin") == l_pin.strip():
                        st.session_state.dukaan_profile = {
                            "registered": True,
                            "owner_name": user_data["owner_name"],
                            "shop_name": user_data["shop_name"],
                            "mobile": user_data["mobile"],
                            "alt_mobile": user_data["alt_mobile"],
                            "pan": user_data["pan"]
                        }
                        st.success(f"🎉 Welcome Back {user_data['owner_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Galat Mobile Number ya PIN! Kripya dobara check karein.")
                except:
                    st.error("⚠️ Database connection fail! Internet check karein.")
                    
    else:
        st.subheader("📋 Nayi Dukaan Ka Registration")
        with st.form(key="main_reg_form"):
            d_shop_name = st.text_input("Dukaan Ka Naam *")
            d_owner_name = st.text_input("Dukaandar Ka Naam *")
            d_mobile = st.text_input("Mobile Number *", max_chars=10)
            d_pin = st.text_input("Set 4-Digit Secret PIN * (For Login)", type="password", max_chars=4)
            d_alt_mobile = st.text_input("Alternative Number (Optional)", max_chars=10)
            d_pan = st.text_input("PAN Card Number (Optional)", max_chars=10).upper()
            
            submit_reg = st.form_submit_button("🚀 Registration Complete Karein")
            
        if submit_reg:
            if d_shop_name.strip() == "" or d_owner_name.strip() == "" or d_mobile.strip() == "" or d_pin.strip() == "":
                st.error("❌ Kripya saari zaroori (*) details bharein!")
            elif len(d_mobile.strip()) != 10:
                st.error("❌ Kripya valid 10-digit mobile number dalein!")
            elif len(d_pin.strip()) != 4 or not d_pin.isdigit():
                st.error("❌ PIN sirf 4 अंकों ka number hona chahiye!")
            else:
                # Check if user already exists
                try:
                    check_exist = requests.get(f"{FIREBASE_URL}users/{d_mobile.strip()}.json").json()
                    if check_exist:
                        st.error("🚨 Yeh mobile number pehle se registered hai! Login karein.")
                    else:
                        # Save new user into Firebase
                        user_data = {
                            "shop_name": d_shop_name.strip(),
                            "owner_name": d_owner_name.strip(),
                            "mobile": d_mobile.strip(),
                            "pin": d_pin.strip(),
                            "alt_mobile": d_alt_mobile.strip() if d_alt_mobile else "N/A",
                            "pan": d_pan.strip() if d_pan else "N/A",
                            "registered_at": datetime.now().strftime("%d-%m-%Y %I:%M %p")
                        }
                        requests.put(f"{FIREBASE_URL}users/{user_data['mobile']}.json", json=user_data)
                        
                        st.session_state.dukaan_profile = {
                            "registered": True,
                            "owner_name": user_data["owner_name"],
                            "shop_name": user_data["shop_name"],
                            "mobile": user_data["mobile"],
                            "alt_mobile": user_data["alt_mobile"],
                            "pan": user_data["pan"]
                        }
                        st.success("🎉 Registration Successful! Aapka register khul raha hai...")
                        st.rerun()
                except:
                    st.error("⚠️ Cloud connectivity issue. Kripya thodi der baad try karein.")

# --- MAIN APP LOGIC: REGISTRATION/LOGIN KE BAAD KA SCREEN ---
else:
    current_shop = st.session_state.dukaan_profile["shop_name"]
    current_owner = st.session_state.dukaan_profile["owner_name"]
    
    # Sidebar Profile View
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏪 Active Profile")
    st.sidebar.write(f"**Dukaan:** {current_shop}")
    st.sidebar.write(f"**Owner:** {current_owner}")
    st.sidebar.write(f"**Mobile:** {st.session_state.dukaan_profile['mobile']}")
    if st.sidebar.button("Logout 🚪"):
        st.session_state.dukaan_profile["registered"] = False
        st.session_state.dukaan_ledger = pd.DataFrame(columns=["ID", "Tarikh", "Grahak Ka Naam", "Mobile Number", "Details", "Amount (₹)"])
        st.rerun()

    st.title(f"🏪 {current_shop} Ka Digital Register")
    st.write(f"Welcome back, **{current_owner}**! Cloud storage secure hai. ☁️")

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
                "ID": next_id, "Tarikh": now, "Grahak Ka Naam": name, 
                "Mobile Number": mobile, "Details": entry_detail, "Amount (₹)": final_amount
            }])
            st.session_state.dukaan_ledger = pd.concat([df, new_row], ignore_index=True)
            st.success(f"🎉 {name} ka hisab save ho gaya!")
            st.rerun()

    # --- SIDEBAR CALCULATOR ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧮 Quick Calculator")
    num1 = st.sidebar.number_input("Pehla Number", value=0, step=1, key="calc1")
    num2 = st.sidebar.number_input("Doosra Number", value=0, step=1, key="calc2")
    op = st.sidebar.selectbox("Operation:", ["➕ Jodein (+)", "➖ Ghatayein (-)"])
    if op == "➕ Jodein (+)":
        st.sidebar.info(f"Total Jod: **{num1 + num2}**")
    else:
        st.sidebar.info(f"Total bacha: **{num1 - num2}**")

    # --- ALWAYS VISIBLE DELETE OPTION ---
    st.markdown("---")
    st.subheader("🗑️ Entry Hataiyein (Delete)")
    delete_id = st.number_input("Mitane ke liye Entry ID daalye", min_value=1, step=1)
    if st.button("Register se Saaf Karein"):
        if not df.empty and delete_id in df["ID"].values:
            st.session_state.dukaan_ledger = df[df["ID"] != delete_id]
            st.success(f"ID {delete_id} ko mita diya gaya!")
            st.rerun()
        else:
            st.error("Is ID ki koi entry nahi mili ya register khali hai!")
    st.markdown("---")

    # --- SEARCH, REMINDERS & LIVE LEDGER ---
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
                    if row['Total Balance (₹)'] >= 5000:
                        st.error("🚨 WARNING: Limit Paar (>= 5000)!")
                with c2:
                    if row['Total Balance (₹)'] > 0:
                        st.write(f"🔴 Udhaar: **₹{row['Total Balance (₹)']}**")
                    else:
                        st.write(f"🟢 Clear: **₹{abs(row['Total Balance (₹)'])}**")
                
                if row['Total Balance (₹)'] > 0:
                    msg = f"Namaste {row['Grahak Ka Naam']}, aapka ₹{row['Total Balance (₹)']} ka udhaar baaki hai. Kripya samay par jama karein. 🙏 - {current_shop}"
                else:
                    msg = f"Namaste {row['Grahak Ka Naam']}, aapka hisab poora clear hai. Dhanyawad! 🙏 - {current_shop}"
                    
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

        # --- GRAHAK PASSBOOK ---
        st.subheader("📉 Grahak Passbook (Statement History)")
        all_custs = sorted(df["Grahak Ka Naam"].unique())
        selected_cust = st.selectbox("Kisi Grahak ki poori history dekhne ke liye chunein:", ["-- Select Customer --"] + all_custs)
        if selected_cust != "-- Select Customer --":
            cust_history = df[df["Grahak Ka Naam"] == selected_cust][["Tarikh", "Details", "Amount (₹)"]].copy()
            cust_history["Amount (₹)"] = cust_history["Amount (₹)"].apply(lambda x: f"🔴 Udhaar: ₹{x}" if x > 0 else f"🟢 Jama: ₹{abs(x)}")
            st.table(cust_history)

        # BACKUP DOWNLOAD
        st.markdown("---")
        st.subheader("📥 Register Ka Backup Download Karein")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Register (CSV Excel File)", data=csv,
            file_name=f"Dukaan_Register_Backup_{datetime.now().strftime('%d-%m-%Y')}.csv", mime='text/csv'
        )
    else:
        st.info("Abhi register khali hai. Nayi entry jodein!")
