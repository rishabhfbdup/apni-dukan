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
    df = conn.read(spreadsheet=sheet_url, ttl="0m")
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
