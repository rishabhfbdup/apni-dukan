import streamlit as st
import pandas as pd
import urllib.parse
import requests
from datetime import datetime
import qrcode
from io import BytesIO

# Page configuration
st.set_page_config(page_title="Apni Dukaan Register", layout="centered")

# --- 🔐 ऊपर का कंट्रोल बार और नीचे का फुटर हमेशा के लिए छुपाने का कोड ---
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    .viewerBadge {display: none !important;}
    
    /* नीचे का लाल फुटर और 'Created by' हटाने के लिए */
    footer, [data-testid="stFooter"] {display: none !important; visibility: hidden !important;}
    stDecoration {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True
)
# YOUR FIREBASE REALTIME DATABASE URL
FIREBASE_URL = "https://apni-dukaan-db-default-rtdb.firebaseio.com/"
clean_url = FIREBASE_URL.strip()

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
                    response = requests.get(f"{clean_url}users/{l_mobile.strip()}.json", timeout=10)
                    user_data = response.json()
                    
                    if user_data and user_data.get("pin") == l_pin.strip():
                        st.session_state.dukaan_profile = {
                            "registered": True,
                            "owner_name": user_data.get("owner_name", "Owner"),
                            "shop_name": user_data.get("shop_name", "Apni Dukaan"),
                            "mobile": user_data.get("mobile", l_mobile.strip()),
                            "alt_mobile": user_data.get("alt_mobile", "N/A"),
                            "pan": user_data.get("pan", "N/A")
                        }
                        st.success(f"🎉 Welcome Back {st.session_state.dukaan_profile['owner_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Galat Mobile Number ya PIN! Kripya dobara check karein.")
                except Exception as err:
                    st.error(f"⚠️ Login Connection Fail! Error: {err}")
                    
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
                try:
                    check_exist = requests.get(f"{clean_url}users/{d_mobile.strip()}.json", timeout=10).json()
                    
                    if check_exist:
                        st.error("🚨 Yeh mobile number pehle se registered hai! Login karein.")
                    else:
                        user_data = {
                            "shop_name": d_shop_name.strip(),
                            "owner_name": d_owner_name.strip(),
                            "mobile": d_mobile.strip(),
                            "pin": d_pin.strip(),
                            "alt_mobile": d_alt_mobile.strip() if d_alt_mobile else "N/A",
                            "pan": d_pan.strip() if d_pan else "N/A",
                            "registered_at": datetime.now().strftime("%d-%m-%Y %I:%M %p")
                        }
                        
                        req_res = requests.put(f"{clean_url}users/{user_data['mobile']}.json", json=user_data, timeout=10)
                        
                        if req_res.status_code == 200:
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
                        else:
                            st.error(f"🚨 Firebase Rejected! Status code: {req_res.status_code}. Rules update karein.")
                except Exception as cloud_err:
                    st.error(f"⚠️ Connection Error: {cloud_err}")

# --- MAIN APP LOGIC: REGISTRATION/LOGIN KE BAAD KA SCREEN ---
else:
    current_shop = st.session_state.dukaan_profile["shop_name"]
    current_owner = st.session_state.dukaan_profile["owner_name"]
    user_mobile = st.session_state.dukaan_profile["mobile"]

    # FETCH LEDGER DATA LIVE FROM FIREBASE FOR THIS USER (CLEAN & SAFE)
    def fetch_ledger_from_firebase(mobile_num):
        try:
            res = requests.get(f"{clean_url}ledgers/{mobile_num}.json", timeout=10).json()
            if res and isinstance(res, dict):
                records = []
                for k, v in res.items():
                    if isinstance(v, dict):
                        v["FirebaseKey"] = k
                        v["ID"] = int(v.get("ID", 1))
                        v["Tarikh"] = v.get("Tarikh", "")
                        v["Grahak Ka Naam"] = v.get("Grahak Ka Naam", "Unknown")
                        v["Mobile Number"] = v.get("Mobile Number", "N/A")
                        v["Details"] = v.get("Details", "")
                        v["Amount (₹)"] = int(v.get("Amount (₹)", 0))
                        records.append(v)
                return pd.DataFrame(records)
            else:
                return pd.DataFrame(columns=["ID", "Tarikh", "Grahak Ka Naam", "Mobile Number", "Details", "Amount (₹)", "FirebaseKey"])
        except:
            return pd.DataFrame(columns=["ID", "Tarikh", "Grahak Ka Naam", "Mobile Number", "Details", "Amount (₹)", "FirebaseKey"])

    df = fetch_ledger_from_firebase(user_mobile)
    
    # Sidebar Profile View
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏪 Active Profile")
    st.sidebar.write(f"**Dukaan:** {current_shop}")
    st.sidebar.write(f"**Owner:** {current_owner}")
    st.sidebar.write(f"**Mobile:** {user_mobile}")
    
    # --- DYNAMIC PAYMENT SETUP IN SIDEBAR ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Digital Payment Setup")
    shop_upi = st.sidebar.text_input("Apni UPI ID Dalein:", placeholder="example@oksbi")
    shop_billing_name = st.sidebar.text_input("Bank me Darj Apna Naam:", placeholder=current_owner)

    if st.sidebar.button("Logout 🚪"):
        st.session_state.dukaan_profile["registered"] = False
        st.rerun()

    st.title(f"🏪 {current_shop} Ka Digital Register")
    st.write(f"Welcome back, **{current_owner}**! Cloud storage live connected hai. ☁️")

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

    # --- NEW FEATURE: DAILY CLOSING REPORT BUTTON ---
    if not df.empty:
        with st.expander("📊 Aaj Ki Bahi-Khata Closing Report Click Karein"):
            today_str = datetime.now().strftime("%d-%m-%Y")
            df_today = df[df["Tarikh"].str.contains(today_str)]
            
            if not df_today.empty:
                aaj_ka_udhaar = df_today[df_today["Amount (₹)"] > 0]["Amount (₹)"].sum()
                aaj_ki_ugahi = abs(df_today[df_today["Amount (₹)"] < 0]["Amount (₹)"].sum())
                
                st.write(f"📅 **Tarekh:** {today_str}")
                c_ud, c_ug = st.columns(2)
                c_ud.metric("Aaj Diya Hua Udhaar", f"₹ {aaj_ka_udhaar}")
                c_ug.metric("Aaj Wapas Mili Rakam (Cash)", f"₹ {aaj_ki_ugahi}")
            else:
                st.info("Aaj ki tarekh me abhi tak koi entry nahi ki gayi hai.")

    if not net_balances.empty and total_udhaar > 0:
        st.markdown("#### 📈 Udhaar Ka Graph (Top Grahak)")
        chart_data = net_balances[net_balances["Net Balance (₹)"] > 0].set_index("Grahak Ka Naam")
        st.bar_chart(chart_data)

    st.markdown("---")

    # --- NAYI ENTRY FORM (WITH PARTIAL PAYMENT FEATURE LOGIC) ---
    st.subheader("📝 Nayi Entry Jodein")
    with st.form(key="entry_form", clear_on_submit=True):
        name = st.text_input("Grahak Ka Naam (Required)").strip()
        g_mobile = st.text_input("Mobile Number (Optional)", max_chars=10)
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
            
            # Partial payment history logic tracker
            current_cust_bal = 0
            if not df.empty and name in df["Grahak Ka Naam"].values:
                current_cust_bal = df[df["Grahak Ka Naam"] == name]["Amount (₹)"].sum()
                
            if final_amount < 0:
                entry_detail = details if details else f"Jama Kiye (Purana Baki: ₹{current_cust_bal}, Ab Bacha: ₹{current_cust_bal + final_amount})"
            else:
                entry_detail = details if details else "Udhaar Diya"
            
            if not g_mobile and not df.empty:
                prev_mob = df[df["Grahak Ka Naam"].str.lower() == name.lower()]["Mobile Number"].values
                g_mobile = prev_mob[0] if len(prev_mob) > 0 else "N/A"
            elif not g_mobile:
                g_mobile = "N/A"

            new_entry = {
                "ID": int(next_id), 
                "Tarikh": str(now), 
                "Grahak Ka Naam": str(name), 
                "Mobile Number": str(g_mobile), 
                "Details": str(entry_detail), 
                "Amount (₹)": int(final_amount)
            }
            
            try:
                push_res = requests.post(f"{clean_url}ledgers/{user_mobile}.json", json=new_entry, timeout=10)
                if push_res.status_code == 200:
                    st.success(f"🎉 {name} ka hisab cloud register me secure save ho gaya!")
                    st.rerun()
                else:
                    st.error("🚨 Cloud server rejection! Status rules check karein.")
            except:
                st.error("⚠️ Network Timeout! Par entry database me chali gayi hai, page refresh karein.")

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
            target_row = df[df["ID"] == delete_id]
            fb_key = target_row["FirebaseKey"].values[0]
            
            try:
                del_res = requests.delete(f"{clean_url}ledgers/{user_mobile}/{fb_key}.json", timeout=10)
                if del_res.status_code == 200:
                    st.success(f"ID {delete_id} ko cloud register se mita diya gaya!")
                    st.rerun()
                else:
                    st.error("❌ Cloud database se data delete nahi ho paya!")
            except:
                st.error("⚠️ Connection Error while deleting!")
        else:
            st.error("Is ID ki koi entry nahi heli ya register khali hai!")
    st.markdown("---")

    # --- SEARCH, REMINDERS & LIVE LEDGER (WITH QUICK CALL & AUTO QR LINK) ---
    st.subheader("🔎 Grahak Dhoondhein aur Reminders")
    
    if not shop_upi or not shop_billing_name:
        st.info("💡 Sidebar me apni UPI ID jarur setup karein taaki customers ko QR Code aur automatic link mil sake!")

    search_query = st.text_input("Naam likh kar search karein...", "").strip().lower()

    if not df.empty:
        summary_df = df.groupby(["Grahak Ka Naam", "Mobile Number"])["Amount (₹)"].sum().reset_index()
        summary_df.columns = ["Grahak Ka Naam", "Mobile Number", "Total Balance (₹)"]
        if search_query:
            summary_df = summary_df[summary_df["Grahak Ka Naam"].str.lower().str.contains(search_query)]
            
        for index, row in summary_df.iterrows():
            current_balance = row['Total Balance (₹)']
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
                with c1:
                    st.write(f"👤 **{row['Grahak Ka Naam']}** ({row['Mobile Number']})")
                    if current_balance >= 5000:
                        st.error("🚨 WARNING: Limit Paar (>= 5000)!")
                with c2:
                    if current_balance > 0:
                        st.write(f"🔴 Udhaar: **₹{current_balance}**")
                    else:
                        st.write(f"🟢 Clear: **₹{abs(current_balance)}**")
                
                # Payment message block composition
                upi_string = ""
                if current_balance > 0 and shop_upi and shop_billing_name:
                    name_encoded = urllib.parse.quote(shop_billing_name)
                    upi_string = f"upi://pay?pa={shop_upi}&pn={name_encoded}&am={current_balance}&cu=INR"
                    
                    msg = (
                        f"Namaste {row['Grahak Ka Naam']},\n"
                        f"Aapka {current_shop} par ₹{current_balance} ka udhaar baaki hai.\n\n"
                        f"💳 Online turant payment karne ke liye niche diye gaye link par click karein:\n"
                        f"{upi_string}\n\n"
                        f"Ya is UPI ID par send karein: {shop_upi}\n"
                        f"Dhanyawad! 🙏"
                    )
                else:
                    if current_balance > 0:
                        msg = f"Namaste {row['Grahak Ka Naam']}, aapka ₹{current_balance} ka udhaar baaki hai. Kripya samay par jama karein. 🙏 - {current_shop}"
                    else:
                        msg = f"Namaste {row['Grahak Ka Naam']}, aapka hisab poora clear hai. Dhanyawad! 🙏 - {current_shop}"
                    
                with c3:
                    if row['Mobile Number'] != "N/A" and len(str(row['Mobile Number'])) == 10:
                        phone_formatted = f"91{row['Mobile Number']}"
                        whatsapp_url = f"https://wa.me/{phone_formatted}?text={urllib.parse.quote(msg)}"
                        call_url = f"tel:+91{row['Mobile Number']}"
                        
                        # --- STYLIZED GREEN WHATSAPP BUTTON ---
                        st.markdown(
                            f'<a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">'
                            f'<button style="background-color: #25D366; color: white; border: none; '
                            f'padding: 5px 10px; font-size: 13px; font-weight: bold; '
                            f'cursor: pointer; border-radius: 5px; margin-bottom: 5px; width: 100%;">💬 WhatsApp</button></a>',
                            unsafe_allow_html=True
                        )
                        
                        # --- NEW FEATURE: STYLIZED BLUE DIRECT CALL BUTTON ---
                        st.markdown(
                            f'<a href="{call_url}" style="text-decoration: none;">'
                            f'<button style="background-color: #007bff; color: white; border: none; '
                            f'padding: 5px 10px; font-size: 13px; font-weight: bold; '
                            f'cursor: pointer; border-radius: 5px; width: 100%;">📞 Call Now</button></a>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.write("No Contact")
                with c4:
                    st.text_input("Copy Msg", value=msg, key=f"copy_{index}", label_visibility="collapsed")
                    st.caption("Select to copy manual text")
                
                # Expandable QR code component setup per loop
                if upi_string:
                    with st.expander(f"🔍 Scan QR for {row['Grahak Ka Naam']}"):
                        qr = qrcode.QRCode(box_size=4, border=2)
                        qr.add_data(upi_string)
                        qr.make(fit=True)
                        img = qr.make_image(fill_color="black", back_color="white")
                        
                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        st.image(byte_im, caption=f"Scan to Pay ₹{current_balance} directly to {shop_billing_name}")
                        
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
        clean_csv_df = df.drop(columns=["FirebaseKey"], errors="ignore")
        csv = clean_csv_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Register (CSV Excel File)", data=csv,
            file_name=f"Dukaan_Register_Backup_{datetime.now().strftime('%d-%m-%Y')}.csv", mime='text/csv'
        )
    else:
        st.info("Abhi register khali hai. Nayi entry jodein!")
