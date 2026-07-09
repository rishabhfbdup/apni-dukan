import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Apni Dukaan Register", layout="centered")

# Aapki Google Sheet ka CSV download link (Public data manipulation ke liye)
sheet_id = "1Wnqs6X46Pu2QiO7uTYKeg8KTKfWiWCa2DquBWGLKEYE"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
form_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/formResponse"

st.title("🏪 Apni Dukaan Ka Digital Register")
st.write("Ab aapka saara data Google Sheets me permanent save ho raha hai!")

# Read Data safely
try:
    df = pd.read_csv(csv_url)
    # Filter out completely empty rows
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

import requests
if submit_button:
    if name.strip() == "":
        st.error("Kripya Grahak ka naam zaroor dalein!")
    else:
        # Calculate new ID safely
        if not df.empty and "ID" in df.columns:
            try:
                next_id = int(pd.to_numeric(df["ID"]).max() + 1)
            except:
                next_id = len(df) + 1
        else:
            next_id = 1
            
        # Google Form ke throug ya direct submission bypass link setup
        st.warning("Google Sheet configuration security verification mandatory hai. Chalo direct connection ko easy banate hain!")
