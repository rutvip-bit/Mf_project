import streamlit as st
import pandas as pd
import traceback
from transformations.transform import load_silver
from utils.db import read_table

st.set_page_config(
    page_title="Mutual Fund",
    page_icon="📊",
    layout="wide"
)

# ==============================
# HEADER
# ==============================
st.markdown(
    "<h1 style='text-align:center;'>📊 Mutual Funds Dashboard</h1>",
    unsafe_allow_html=True
)

st.divider()

# ==============================
# SESSION STATE
# ==============================
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "extracted" not in st.session_state:
    st.session_state.extracted = False

if "transformed" not in st.session_state:
    st.session_state.transformed = False

if "bronze_data" not in st.session_state:
    st.session_state.bronze_data = {}

if "silver_data" not in st.session_state:
    st.session_state.silver_data = {}

if "current_layer" not in st.session_state:
    st.session_state.current_layer = "bronze"


# ==============================
# HELPERS
# ==============================
def is_valid(df):
    return df is not None and isinstance(df, pd.DataFrame) and not df.empty


# ==============================
# FILE UPLOAD UI
# ==============================
st.subheader("📂 Upload CAMS / KFintech Excel Files")

col1, col2 = st.columns([10, 2], vertical_alignment="center")

with col1:
    uploaded_files = st.file_uploader(
        "Upload Files",
        type=["xlsx"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🗑 Clear", use_container_width=True):

        # 🔥 HARD RESET (IMPORTANT FIX)
        st.session_state.uploader_key += 1
        st.session_state.extracted = False
        st.session_state.transformed = False
        st.session_state.current_layer = "bronze"
        st.session_state.bronze_data = {}
        st.session_state.silver_data = {}

        # extra safety reset
        st.session_state.uploaded_types = {}

        st.rerun()

st.divider()


# ==============================
# FILE LOADER
# ==============================
def load_files(files):

    cams_inv = cams_trans = kfin_inv = kfin_trans = sip_df = None

    for file in files:

        name = file.name.lower()

        if "cams" in name and "inv" in name:
            cams_inv = pd.read_excel(file)

        elif "cams" in name and "trans" in name:
            cams_trans = pd.read_excel(file)

        elif "kfin" in name and "investor" in name:
            kfin_inv = pd.read_excel(file)

        elif "kfin" in name and "trans" in name:
            kfin_trans = pd.read_excel(file)

        elif "sip" in name:
            sip_df = pd.read_excel(file)

    return cams_inv, cams_trans, kfin_inv, kfin_trans, sip_df


# ==============================
# BUTTONS
# ==============================
col1, col2 = st.columns(2)

extract_btn = col1.button("🟢 Extract Raw Data", use_container_width=True)
transform_btn = col2.button("🟡 Transform Data", use_container_width=True)

st.divider()


# ==============================
# EXTRACT LOGIC
# ==============================
if extract_btn:

    st.session_state.transformed = False
    st.session_state.current_layer = "bronze"
    st.session_state.silver_data = {}

    try:

        if not uploaded_files:
            st.warning("⚠ Please upload files first.")
            st.stop()

        st.info("Reading files...")

        cams_inv, cams_trans, kfin_inv, kfin_trans, sip_df = load_files(uploaded_files)

        uploaded = sum([
            is_valid(cams_inv),
            is_valid(cams_trans),
            is_valid(kfin_inv),
            is_valid(kfin_trans),
            is_valid(sip_df)
        ])

        st.success(f"✔ {uploaded} dataset(s) detected")

        # ==============================
        # ETL CALLS
        # ==============================
        from etl_investor_master import process_investor_master
        from etl_trans import process_transactions
        from etl_sip import process_sip

        investor_df = cams_inv if is_valid(cams_inv) else kfin_inv
        transaction_df = cams_trans if is_valid(cams_trans) else kfin_trans

        st.session_state.uploaded_types = {
            "investor": is_valid(investor_df),
            "transaction": is_valid(transaction_df),
            "sip": is_valid(sip_df)
        }

        # INVESTOR
        if is_valid(cams_inv) or is_valid(kfin_inv):
             process_investor_master(
        cams=cams_inv,
        kfin=kfin_inv
    )

        # TRANSACTIONS
        if is_valid(cams_trans) or is_valid(kfin_trans):
            process_transactions(cams=cams_trans, kfin=kfin_trans)

        # SIP (FIXED CALL)
        if is_valid(sip_df):
            process_sip(sip_df)

        # ==============================
        # LOAD BRONZE PREVIEW
        # ==============================
        bronze_data = {}

        if st.session_state.uploaded_types["investor"]:
            bronze_data["Investor Master"] = read_table("bronze", "investor_master")

        if st.session_state.uploaded_types["transaction"]:
            bronze_data["Transactions"] = read_table("bronze", "transaction_master")

        if st.session_state.uploaded_types["sip"]:
            bronze_data["SIP"] = read_table("bronze", "sip_master")

        st.session_state.bronze_data = bronze_data
        st.session_state.extracted = True
        st.session_state.current_layer = "bronze"

        st.success("✔ Extraction Completed + DB Load Done")

    except Exception:
        st.error("Extraction Failed")
        st.code(traceback.format_exc())


# ==============================
# TRANSFORM LOGIC
# ==============================
if transform_btn:

    if not st.session_state.extracted:
        st.warning("⚠ Run Extract First")

    else:
        try:

            st.info("Running transformation layer...")

            load_silver()

            uploaded = st.session_state.uploaded_types

            silver_data = {}

            if uploaded["investor"]:
                silver_data["Investor Master"] = read_table("silver", "investor_master")

            if uploaded["transaction"]:
                silver_data["Transactions"] = read_table("silver", "transaction_master")

            if uploaded["sip"]:
                silver_data["SIP"] = read_table("silver", "sip_master")

            st.session_state.silver_data = silver_data
            st.session_state.transformed = True
            st.session_state.current_layer = "silver"

            st.success("✔ Transformation Completed + Silver Loaded to DB")

        except Exception:
            st.error("Transformation Failed")
            st.code(traceback.format_exc())


# ==============================
# PREVIEW
# ==============================
pretty_names = {
    "Investor Master": "📘 Master Table (Investor)",
    "Transactions": "📊 Transaction Table",
    "SIP": "📈 SIP Table"
}

data_to_show = None
title = None

if st.session_state.current_layer == "silver" and st.session_state.silver_data:
    data_to_show = st.session_state.silver_data
    title = "✨ Silver Layer Preview"

elif st.session_state.current_layer == "bronze" and st.session_state.bronze_data:
    data_to_show = st.session_state.bronze_data
    title = "📄 Bronze Layer Preview"

st.markdown(f"## {title if title else '📄 No Data Yet'}")

if data_to_show:

    for name, df in data_to_show.items():

        if is_valid(df):

            with st.container(border=True):

                st.markdown(f"### {pretty_names.get(name, name)}")

                c1, c2 = st.columns(2)
                c1.metric("Rows", len(df))
                c2.metric("Columns", len(df.columns))

                st.dataframe(df, use_container_width=True, height=300)

                st.divider()