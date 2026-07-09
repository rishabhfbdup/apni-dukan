import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Apni Dukaan Register", layout="centered")

st.title("🏪 Apni Dukaan Ka Digital Register")
st.write("Ab diary chhodo, digital hisab rakho!")

# Session state use karenge demo ke liye taaki bina error ke data add/delete ho sake
if "dukaan_data" not in st.session_state:
    st.session_state.dukaan_data = pd.DataFrame(columns=["ID", "Grahak Ka Naam", "Mobile Number", "Amount (₹)"])

df = st.session_state.dukaan_data

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
        next_id = int(df["ID"].max() + 1) if not df.empty else 1
        
        # Create new row
        new_data = pd.DataFrame([{
            "ID": next_id,
            "Grahak Ka Naam": name,
            "Mobile Number": mobile if mobile else "N/A",
            "Amount (₹)": amount
        }])
        
        # Append to session state
        st.session_state.dukaan_data = pd.concat([df, new_data], ignore_index=True)
        st.success(f"🎉 {name} ka hisab kamyabi se save ho gaya!")
        st.rerun()

# --- DISPLAY TABLE ---
st.subheader("📊 Sabhi Grahakon Ka Hisab")
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # --- DELETE ENTRY ---
    st.markdown("---")
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
