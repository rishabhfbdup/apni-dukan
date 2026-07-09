import streamlit as st
import pandas as pd
import urllib.parse

# Page configuration
st.set_page_config(page_title="Apni Dukaan Register", layout="centered")

st.title("🏪 Apni Dukaan Ka Digital Register")
st.write("Ab diary chhodo, digital hisab rakho aur WhatsApp par reminder bhejo!")

# Session state use karenge data save rakhne ke liye
if "dukaan_data" not in st.session_state:
    st.session_state.dukaan_data = pd.DataFrame(columns=["ID", "Grahak Ka Naam", "Mobile Number", "Amount (₹)"])

df = st.session_state.dukaan_data

# --- ENTRY FORM ---
st.subheader("📝 Nayi Entry Jodein")
with st.form(key="entry_form", clear_on_submit=True):
    name = st.text_input("Grahak Ka Naam (Required)")
    mobile = st.text_input("Mobile Number (Optional - WhatsApp ke liye zaroori hai)", max_chars=10)
    amount = st.number_input("Amount (₹)", min_value=0, step=1)
    submit_button = st.form_submit_button(label="Register me Save Karein")

if submit_button:
    if name.strip() == "":
        st.error("Kripya Grahak ka naam zaroor dalein!")
    else:
        next_id = int(df["ID"].max() + 1) if not df.empty else 1
        
        new_data = pd.DataFrame([{
            "ID": next_id,
            "Grahak Ka Naam": name,
            "Mobile Number": mobile if mobile else "N/A",
            "Amount (₹)": amount
        }])
        
        st.session_state.dukaan_data = pd.concat([df, new_data], ignore_index=True)
        st.success(f"🎉 {name} ka hisab kamyabi se save ho gaya!")
        st.rerun()

# --- DISPLAY TABLE & WHATSAPP BUTTON ---
st.subheader("📊 Sabhi Grahakon Ka Hisab")
if not df.empty:
    # Har row ke liye dukaandar ko option denge WhatsApp bhejne ka
    for index, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            with col1:
                st.write(f"#{row['ID']}")
            with col2:
                st.write(f"**{row['Grahak Ka Naam']}**")
            with col3:
                st.write(f"₹ {row['Amount (₹)']}")
            with col4:
                # Agar mobile no. valid hai toh WhatsApp link banayein
                if row['Mobile Number'] != "N/A" and len(str(row['Mobile Number'])) == 10:
                    msg = f"Namaste {row['Grahak Ka Naam']}, aapke ₹{row['Amount (₹)']} hamare digital khate me jode gaye hain. Kripya dhyan rakhein. 🙏 - Apni Dukaan"
                    encoded_msg = urllib.parse.quote(msg)
                    whatsapp_url = f"https://wa.me/91{row['Mobile Number']}?text={encoded_msg}"
                    st.markdown(f"[💬 Send Reminder]({whatsapp_url})", unsafe_allow_html=True)
                else:
                    st.write("🚫 No Number")
        st.markdown("---")
        
    # --- DELETE ENTRY ---
    st.subheader("🗑️ Entry Delete Karein")
    delete_id = st.number_input("Delete karne ke liye ID daalye", min_value=1, step=1)
    delete_button = st.button("Register se Mitayein")
    
    if delete_button:
        if delete_id in df["ID"].values:
            st.session_state.dukaan_data = df[df["ID"] != delete_id]
            st.success(f"ID {delete_id} ko kamyabi se mita diya gaya!")
            st.rerun()
        else:
            st.error("Is ID ki koi entry nahi mili!")
else:
    st.info("Abhi register khali hai. Nayi entry jodein!")
