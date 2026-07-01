import streamlit as st
import pandas as pd
import traceback

st.set_page_config(
    page_title="Intelliwealth",
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
if "extracted" not in st.session_state:
    st.session_state.extracted = False

if "transformed" not in st.session_state:
    st.session_state.transformed = False

if "bronze_data" not in st.session_state:
    st.session_state.bronze_data = {}

if "silver_data" not in st.session_state:
    st.session_state.silver_data = {}

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# ==============================
# SAFE CHECK
# ==============================
def is_valid(df):
    return isinstance(df, pd.DataFrame) and not df.empty

# ==============================
# FILE UPLOADER
# ==============================
st.subheader("📂 Upload CAMS / KFintech Excel Files")

col1_u, col2_u = st.columns([10, 2])

with col1_u:
    uploaded_files = st.file_uploader(
        "Upload Files",
        type=["xlsx"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}"
    )

with col2_u:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    if st.button("🗑 Clear", use_container_width=True, key="clear_btn"):

        st.session_state.uploader_key += 1
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

    cams_inv = None
    cams_trans = None
    kfin_inv = None
    kfin_trans = None
    sip_file = None

    for file in files:

        name = file.name.lower()

        if "cams" in name and "inv" in name:
            cams_inv = pd.read_excel(file, dtype=str, keep_default_na=False)

        elif "cams" in name and "trans" in name:
            cams_trans = pd.read_excel(file, dtype=str, keep_default_na=False)

        elif "kfin" in name and "investor" in name:
            kfin_inv = pd.read_excel(file, dtype=str, keep_default_na=False)

        elif "kfin" in name and "trans" in name:
            kfin_trans = pd.read_excel(file, dtype=str, keep_default_na=False)

        elif "sip" in name:
            sip_file = file

    return cams_inv, cams_trans, kfin_inv, kfin_trans, sip_file


# ==============================
# BUTTONS (ONLY ONCE - FIX)
# ==============================
col1, col2 = st.columns(2)

extract_btn = col1.button(
    "🟢 Extract Raw Data",
    use_container_width=True,
    key="extract_btn"
)

transform_btn = col2.button(
    "🟡 Transform Data",
    use_container_width=True,
    key="transform_btn"
)

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

        # ----------------------
        # INVESTOR MASTER
        # ----------------------
        if is_valid(cams_inv) or is_valid(kfin_inv):
            process_investor_master(
                cams=cams_inv,
                kfin=kfin_inv
            )

        # ----------------------
        # TRANSACTIONS
        # ----------------------
        if is_valid(cams_trans) or is_valid(kfin_trans):
            process_transactions(
                cams=cams_trans,
                kfin=kfin_trans
            )

        # ----------------------
        # SIP
        # ----------------------
        if sip_file is not None:
            process_sip(sip_file)

        # ----------------------
        # STORE FOR UI
        # ----------------------
        st.session_state.bronze_data = {
            "Investor Master": cams_inv if is_valid(cams_inv) else kfin_inv,
            "Transactions": cams_trans if is_valid(cams_trans) else kfin_trans,
            "SIP": pd.read_excel(sip_file, dtype=str, keep_default_na=False)
            if sip_file else None
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

# Decide which layer to show
if st.session_state.transformed and st.session_state.silver_data:
    data_to_show = st.session_state.silver_data
    title = "✨ Silver Layer Preview"

elif st.session_state.extracted and st.session_state.bronze_data:
    data_to_show = st.session_state.bronze_data
    title = "📄 Bronze Layer Preview"

# Header
st.markdown(f"## {title if title else '📄 No Data Yet'}")

# ==============================
# DISPLAY TABLES
# ==============================
if data_to_show:

    for name, df in data_to_show.items():

        if is_valid(df):

            with st.container(border=True):

                st.markdown(f"### {pretty_names.get(name, name)}")

                col1, col2 = st.columns(2)

                col1.metric("Rows", len(df))
                col2.metric("Columns", len(df.columns))

                st.dataframe(
                    df,
                    use_container_width=True,
                    height=300
                )