from etl_investor_master import build_investor_master
from etl_trans import build_transaction_master
from etl_sip import extract_sip


def extract_and_push(uploaded_files):

    transaction_files = []
    investor_files = []
    sip_files = []

    for file in uploaded_files:

        name = file.name.lower()

        # -------------------------
        # TRANSACTION FILES
        # -------------------------
        if "trans" in name:
            transaction_files.append(file)

        # -------------------------
        # INVESTOR FILES
        # -------------------------
        elif "inv" in name:
            investor_files.append(file)

        # -------------------------
        # SIP FILES (NEW)
        # -------------------------
        elif "sip" in name:
            sip_files.append(file)

    # -------------------------
    # PROCESS TRANSACTION
    # -------------------------
    if transaction_files:
        build_transaction_master(transaction_files)

    # -------------------------
    # PROCESS INVESTOR
    # -------------------------
    if investor_files:
        build_investor_master(investor_files)

    # -------------------------
    # PROCESS SIP (NEW)
    # -------------------------
    if sip_files:
        for file in sip_files:
            extract_sip(file)

    return (
        len(transaction_files),
        len(investor_files),
        len(sip_files)
    )