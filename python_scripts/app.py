import streamlit as st
import pandas as pd
import traceback

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="IntelliWealth",
    layout="wide"
)

st.title("📊 Mutual Funds")

# =====================================
# SESSION STATE
# =====================================
if "extracted" not in st.session_state:
    st.session_state.extracted = False

# =====================================
# FILE UPLOAD
# =====================================
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


# =====================================
# LOAD FILES (ONLY SIP ADDED)
# =====================================
def load_files(files):

    cams_inv = None
    cams_trans = None
    kfin_inv = None
    kfin_trans = None
    sip_file = None   # NEW ADDITION

    for file in files:

        filename = file.name.lower()

        # CAMS Investor Master
        if "cams" in filename and "inv" in filename:
            cams_inv = pd.read_excel(file)

        # CAMS Transaction
        elif "cams" in filename and "trans" in filename:
            cams_trans = pd.read_excel(file)

        # KFIN Investor Master
        elif "kfin" in filename and "investor" in filename:
            kfin_inv = pd.read_excel(file)

        # KFIN Transaction
        elif "kfin" in filename and "trans" in filename:
            kfin_trans = pd.read_excel(file)

        # =========================
        # SIP FILE (NEW)
        # =========================
        elif "sip" in filename:
            sip_file = file

    return cams_inv, cams_trans, kfin_inv, kfin_trans, sip_file


# =====================================
# EXTRACT
# =====================================
if btn_extract:

    try:

        if not uploaded_files:
            st.warning("⚠️ Please upload at least one Excel file.")
            st.stop()

        st.info("📦 Reading uploaded files...")

        cams_inv, cams_trans, kfin_inv, kfin_trans, sip_file = load_files(uploaded_files)

        uploaded_count = sum(
            x is not None
            for x in [
                cams_inv,
                cams_trans,
                kfin_inv,
                kfin_trans,
                sip_file   # NEW
            ]
        )

        if uploaded_count == 0:
            st.error("❌ No valid files detected.")
            st.stop()

        st.success(f"✅ {uploaded_count} valid file(s) detected.")

        from etl_investor_master import process_investor_master
        from etl_trans import process_transactions
        from etl_sip import process_sip   # NEW

        # =====================================
        # INVESTOR MASTER
        # =====================================
        if cams_inv is not None or kfin_inv is not None:

            try:

                st.info("📥 Loading Investor Master...")

                process_investor_master(
                    cams=cams_inv,
                    kfin=kfin_inv
                )

                st.success("✅ Investor Master Loaded")

            except Exception:

                st.error("❌ Investor Master ETL Failed")

                st.code(traceback.format_exc())

        # =====================================
        # TRANSACTION
        # =====================================
        if cams_trans is not None or kfin_trans is not None:

            try:

                st.info("📥 Loading Transactions...")

                process_transactions(
                    cams=cams_trans,
                    kfin=kfin_trans
                )

                st.success("✅ Transaction Table Loaded")

            except Exception:

                st.error("❌ Transaction ETL Failed")

                st.code(traceback.format_exc())

        # =====================================
        # SIP (MINIMAL ADDITION)
        # =====================================
        if sip_file is not None:

             try:

                st.info("📥 Loading SIP Data...")

                from etl_sip import process_sip   # already correct

                process_sip(sip_file)   # ✅ FIXED (removed engine)

                st.success("✅ SIP Loaded into Bronze")

             except Exception:

                st.error("❌ SIP ETL Failed")
                st.code(traceback.format_exc())

                st.session_state.extracted = True

                st.success("🎉 Extraction Completed Successfully.")

    except Exception:

        st.error("❌ Extraction Failed")

        st.code(traceback.format_exc())


# =====================================
# TRANSFORM
# =====================================
if btn_transform:

    if not st.session_state.extracted:
        st.warning("⚠️ Run Extract first.")
        st.stop()

    try:
        from transformations.transform import load_silver

        st.info("🟡 Running Silver Transformation...")

        # EXISTING
        load_silver()


    except Exception:
        st.error("❌ Transform Failed")
        st.code(traceback.format_exc())