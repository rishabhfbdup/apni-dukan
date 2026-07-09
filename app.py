import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- DATABASE SETUP ---
conn = sqlite3.connect("hisab_kitab.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        phone_number TEXT,
        amount REAL,
        type TEXT,
        date TEXT
    )
''')
conn.commit()

# --- APP INTERFACE (UI) ---
st.set_page_config(page_title="Dukaan Hisab Register", page_icon="🏪", layout="centered")
st.title("🏪 Apni Dukaan Digital Register")
st.write("Ab diary chhodo, digital hisab rakho!")
st.markdown("---")

# --- INPUT FORM ---
st.subheader("📝 Nayi Entry Karein")

col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input("Grahak (Customer) ka Naam")
with col2:
    phone_number = st.text_input("Mobile Number (Optional)", max_chars=10)

col3, col4 = st.columns(2)
with col3:
    amount = st.number_input("Rupaye (Amount)", min_value=0, step=1)
with col4:
    type_options = ["Udhaar Diya (Given 🔴)", "Jama Kiya (Received 🟢)"]
    transaction_type = st.selectbox("Len-Den ka Type", type_options)

if st.button("Register me Save Karein", use_container_width=True):
    if customer_name and amount > 0:
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        phone_val = phone_number if phone_number else "N/A"
        cursor.execute(
            "INSERT INTO transactions (customer_name, phone_number, amount, type, date) VALUES (?, ?, ?, ?, ?)",
            (customer_name, phone_val, amount, transaction_type, current_date)
        )
        conn.commit()
        st.success(f"✅ {customer_name} ke naam par ₹{amount} ka hisab save ho gaya!")
        st.rerun()
    else:
        st.error("❌ Kripya Grahak ka naam aur sahi amount dalein.")

st.markdown("---")

# --- DISPLAY DATA & SUMMARY ---
st.subheader("📊 Aaj ka Saara Hisab-Kitab")

df = pd.read_sql_query("SELECT id as 'ID', customer_name as 'Grahak', phone_number as 'Mobile', amount as 'Rupaye', type as 'Type', date as 'Tareekh' FROM transactions ORDER BY id DESC", conn)

if not df.empty:
    total_udhaar = df[df['Type'] == "Udhaar Diya (Given 🔴)"]['Rupaye'].sum()
    total_jama = df[df['Type'] == "Jama Kiya (Received 🟢)"]['Rupaye'].sum()
    
    m1, m2 = st.columns(2)
    m1.metric(label="Total Udhaar Baaki (🔴)", value=f"₹{total_udhaar}")
    m2.metric(label="Total Cash Aaya (🟢)", value=f"₹{total_jama}")
    
    # Table Display
    st.dataframe(df.set_index('ID'), use_container_width=True)
    
    # --- DELETE ENTRY FEATURE ---
    st.markdown("---")
    st.subheader("🗑️ Entry Delete Karein")
    delete_id = st.number_input("Delete karne ke liye table se 'ID' dekh kar dalein", min_value=1, step=1)
    if st.button("Entry Delete Mootein", type="primary"):
        cursor.execute("DELETE FROM transactions WHERE id = ?", (delete_id,))
        conn.commit()
        st.success(f"Entry ID {delete_id} successfully delete ho gayi!")
        st.rerun()
else:
    st.info("Abhi tak koi entry nahi ki gayi hai. Pehli entry upar karein!")
    import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Page configuration
st.set_page_config(page_title="Apni Dukaan Register", layout="centered")

# Aapki Google Sheet ka Link
sheet_url = "https://docs.google.com/spreadsheets/d/1Wnqs6X46Pu2QiO7uTYKeg8KTKfWiWCa2DquBWGLKEYE/edit?usp=sharing"

st.title("🏪 Apni Dukaan Ka Digital Register")
st.write("Ab aapka saara data Google Sheets me permanent save ho raha hai!")

# Connect to Google Sheet
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Read existing data
    df = conn.read(spreadsheet=sheet_url, ttl="0m")
    # Clean empty rows/columns if any
    df = df.dropna(how="all")
except Exception as e:
    df = pd.DataFrame(columns=["ID", "Grahak Ka Naam", "Mobile Number", "Amount (₹)"])

# --- ENTRY FORM ---
st.subheader("📝 Nayi Entry Jodein")
with st.form(key="entry_form", clear_on_submit=True):
    name = st.text_input("Grahak Ka Naam (Required)")
    mobile = st.text_input("Mobile Number (Optional)", max_chars=10)
    amount = st.number_input("Amount (₹)", min_value=0, step=1)
    submit_button = st.form_submit_button(label="Register me Save Karein")

if submit_button:
    if name.strip() == "":
        st.error("Kripya Grahak ka naam zaroor dalein!")
    else:
        # Calculate new ID
        if not df.empty and "ID" in df.columns:
            # Handle string or numeric IDs safely
            try:
                next_id = int(pd.to_numeric(df["ID"]).max() + 1)
            except:
                next_id = len(df) + 1
        else:
            next_id = 1
        
        # Create new row
        new_data = pd.DataFrame([{
            "ID": next_id,
            "Grahak Ka Naam": name,
            "Mobile Number": mobile if mobile else "N/A",
            "Amount (₹)": amount
        }])
        
        # Append and Update Sheet
        if df.empty:
            updated_df = new_data
        else:
            updated_df = pd.concat([df, new_data], ignore_index=True)
            
        conn.update(spreadsheet=sheet_url, data=updated_df)
        st.success(f"🎉 {name} ka hisab kamyabi se save ho gaya!")
        st.rerun()

# --- DISPLAY TABLE ---
st.subheader("📊 Sabhi Grahakon Ka Hisab")
if not df.empty and len(df) > 0:
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # --- DELETE ENTRY ---
    st.markdown("---")
    st.subheader("🗑️ Entry Delete Karein")
    delete_id = st.number_input("Delete karne ke liye ID daalye", min_value=1, step=1)
    delete_button = st.button("Register se Mitayein")
    
    if delete_button:
        # Safely check ID
        df["ID"] = pd.to_numeric(df["ID"], errors='coerce')
        if delete_id in df["ID"].values:
            updated_df = df[df["ID"] != delete_id]
            conn.update(spreadsheet=sheet_url, data=updated_df)
            st.success(f"ID {delete_id} ko kamyabi se mita diya gaya!")
            st.rerun()
        else:
            st.error("Is ID ki koi entry nahi mili!")
else:
    st.info("Abhi register khali hai. Nayi entry jodein!")
    
