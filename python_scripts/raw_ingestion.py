from etl_investor_master import build_investor_master
from etl_trans import build_transaction_master


def extract_and_push(uploaded_files):

    transaction_files = []
    investor_files = []

    for file in uploaded_files:

        name = file.name.lower()

        if "trans" in name:
            transaction_files.append(file)

        elif "inv" in name:
            investor_files.append(file)

    if transaction_files:
        build_transaction_master(
            transaction_files
        )

    if investor_files:
        build_investor_master(
            investor_files
        )

    return (
        len(transaction_files),
        len(investor_files)
    )