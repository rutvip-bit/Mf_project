import streamlit as st
import pandas as pd
import traceback

st.set_page_config(page_title="IntelliWealth", layout="wide")
st.title("📊 Mutual Funds")

if "extracted" not in st.session_state:
    st.session_state.extracted = False

uploaded_files = st.file_uploader(
    "📂 Upload CAMS / KFintech Files",
    type=["xlsx"],
    accept_multiple_files=True
)

st.markdown("---")

col1, col2 = st.columns(2)

btn_extract = col1.button("🟢 Extract Raw Data")
btn_transform = col2.button("🟡 Transform Data")

st.markdown("---")

def load_files(files):

    cams_inv = None
    cams_trans = None
    kfin_inv = None
    kfin_trans = None
    sip_file = None

    for file in files:

        filename = file.name.lower()

        if "cams" in filename and "inv" in filename:
            cams_inv = pd.read_excel(file)

        elif "cams" in filename and "trans" in filename:
            cams_trans = pd.read_excel(file)

        elif "kfin" in filename and "investor" in filename:
            kfin_inv = pd.read_excel(file)

        elif "kfin" in filename and "trans" in filename:
            kfin_trans = pd.read_excel(file)

        elif "sip" in filename:
            sip_file = file

    return cams_inv, cams_trans, kfin_inv, kfin_trans, sip_file

def is_valid(df):
    return df is not None and not df.empty


if btn_extract:

    try:

        if not uploaded_files:
            st.warning("⚠️ Please upload files")
            st.stop()

        st.info("📦 Reading files...")

        cams_inv, cams_trans, kfin_inv, kfin_trans, sip_file = load_files(uploaded_files)

        # ✅ FIXED CHECK (NO DataFrame ambiguity)
        uploaded_count = sum([
            is_valid(cams_inv),
            is_valid(cams_trans),
            is_valid(kfin_inv),
            is_valid(kfin_trans),
            sip_file is not None
        ])

        if uploaded_count == 0:
            st.error("❌ No valid files detected")
            st.stop()

        st.success(f"✅ {uploaded_count} file(s) detected")

        from etl_investor_master import process_investor_master
        from etl_trans import process_transactions
        from etl_sip import process_sip

        # INVESTOR
        if is_valid(cams_inv) or is_valid(kfin_inv):
            st.info("📥 Investor Master...")
            process_investor_master(cams=cams_inv, kfin=kfin_inv)
            st.success("✅ Investor Loaded")

        # TRANSACTION
        if is_valid(cams_trans) or is_valid(kfin_trans):
            st.info("📥 Transactions...")
            process_transactions(cams=cams_trans, kfin=kfin_trans)
            st.success("✅ Transactions Loaded")

        # SIP (silent skip if missing)
        if sip_file is not None:
            st.info("📥 SIP...")
            process_sip(sip_file)
            st.success("✅ SIP Loaded")

        st.session_state.extracted = True
        st.success("🎉 Extraction Completed")

    except Exception:
        st.error("❌ Extraction Failed")
        st.code(traceback.format_exc())

if btn_transform:

    if not st.session_state.extracted:
            st.warning("⚠️ Run Extract first.")
            st.stop()

    try:
        from transformations.transform import load_silver

        st.info("🟡 Transforming...")
        load_silver()

        st.success("✅ Transformation Done")

    except Exception:
        st.error("❌ Transform Failed")
        st.code(traceback.format_exc())