import streamlit as st
import pandas as pd
import traceback

st.set_page_config(
    page_title="Intelliwealth",
    page_icon="📊",
    layout="wide"
)

# ==============================
# HEADER (UNCHANGED UI)
# ==============================
st.markdown(
    "<h1 style='text-align:center;'>📊 Mutual Funds Dashboard</h1>",
    unsafe_allow_html=True
)

st.divider()

# ==============================
# SESSION STATE
# ==============================
if "extracted" not in st.session_state:
    st.session_state.extracted = False

if "transformed" not in st.session_state:
    st.session_state.transformed = False

if "bronze_data" not in st.session_state:
    st.session_state.bronze_data = {}

if "silver_data" not in st.session_state:
    st.session_state.silver_data = {}

# ==============================
# SAFE CHECK (FIXED)
# ==============================
def is_valid(df):
    return isinstance(df, pd.DataFrame) and not df.empty


# ==============================
# FILE UPLOAD UI (FIXED RESET)
# ==============================
st.subheader("📂 Upload CAMS / KFintech Excel Files")

# initialize uploader key (IMPORTANT)
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

top_col1, top_col2 = st.columns([10, 2])

with top_col1:
    uploaded_files = st.file_uploader(
        "Upload Files",
        type=["xlsx"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}"   # 🔥 THIS IS THE FIX
    )

with top_col2:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    if st.button("🗑 Clear", use_container_width=True):

        # 🔥 increment key → forces full reset of uploader
        st.session_state.uploader_key += 1

        # reset everything
        st.session_state.extracted = False
        st.session_state.transformed = False
        st.session_state.bronze_data = {}
        st.session_state.silver_data = {}

        st.rerun()

st.divider()

# ==============================
# FILE LOADER
# ==============================
def load_files(files):

    cams_inv = cams_trans = kfin_inv = kfin_trans = None
    sip_file = None

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
            sip_file = file

    return cams_inv, cams_trans, kfin_inv, kfin_trans, sip_file


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

    try:

        if not uploaded_files:
            st.warning("⚠ Please upload files first")
            st.stop()

        st.info("Reading files...")

        cams_inv, cams_trans, kfin_inv, kfin_trans, sip_file = load_files(uploaded_files)

        from etl_investor_master import process_investor_master
        from etl_trans import process_transactions
        from etl_sip import process_sip

        # INVESTOR
        if is_valid(cams_inv) or is_valid(kfin_inv):
            process_investor_master(cams=cams_inv, kfin=kfin_inv)

        # TRANSACTION
        if is_valid(cams_trans) or is_valid(kfin_trans):
            process_transactions(cams=cams_trans, kfin=kfin_trans)

        # SIP (SAFE FIX)
        if sip_file is not None:
            process_sip(sip_file)

        # STORE ONLY DATAFRAMES FOR UI
        st.session_state.bronze_data = {
            "Investor Master": cams_inv if is_valid(cams_inv) else kfin_inv,
            "Transactions": cams_trans if is_valid(cams_trans) else kfin_trans,
            "SIP": pd.read_excel(sip_file) if sip_file else None
        }

        st.session_state.extracted = True

        st.success("✔ Extraction Completed")

    except Exception:
        st.error("❌ Extraction Failed")
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

            from transformations.transform import load_silver
            load_silver()

            st.session_state.silver_data = st.session_state.bronze_data
            st.session_state.transformed = True

            st.success("✔ Transformation Completed")

        except Exception:
            st.error("❌ Transformation Failed")
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

if st.session_state.transformed and st.session_state.silver_data:
    data_to_show = st.session_state.silver_data
    title = "✨ Silver Layer Preview"

elif st.session_state.extracted and st.session_state.bronze_data:
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