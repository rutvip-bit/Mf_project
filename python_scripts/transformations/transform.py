import pandas as pd
from sqlalchemy import create_engine
 
engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/InteliWealth"
)
 
 
def load_silver():
 
    # --------------------------
    # Investor Master
    # --------------------------
    investor_df = pd.read_sql(
        """
        SELECT *
        FROM bronze.investor_master
        WHERE flag = 0
        """,
        engine
    )
 
    # Apply transformation
    investor_df = transform_investor_master(investor_df)
 
    # Round decimal columns
    investor_df = round_decimal_columns(investor_df)
 
    # Drop flag after transformation
    investor_df = investor_df.drop(columns=["flag"], errors="ignore")
 
    investor_df.to_sql(
        "investor_master",
        engine,
        schema="silver",
        if_exists="replace",
        index=False,
        chunksize=5000,
        method="multi"
    )
    # --------------------------
    # Transaction
    # --------------------------
    transaction_df = pd.read_sql(
        """
        SELECT *
        FROM bronze.transaction
        WHERE flag = 0
        """,
        engine
    )
 
    transaction_df = transform_transaction(transaction_df)
 
    # Round decimal columns
    transaction_df = round_decimal_columns(transaction_df)
 
    transaction_df = transaction_df.drop(columns=["flag"], errors="ignore")
 
    transaction_df.to_sql(
        "transaction",
        engine,
        schema="silver",
        if_exists="replace",
        index=False,
        chunksize=5000,
        method="multi"
    )
 
    # --------------------------
    # SIP
    # --------------------------
    sip_df = pd.read_sql(
        """
        SELECT *
        FROM bronze.sip_info
        WHERE flag = 0
        """,
        engine
    )
 
    sip_df = transform_sip_info(sip_df)
 
    # Round decimal columns
    sip_df = round_decimal_columns(sip_df)
 
    sip_df = sip_df.drop(columns=["flag"], errors="ignore")
 
    sip_df.to_sql(
        "sip_info",
        engine,
        schema="silver",
        if_exists="replace",
        index=False,
        chunksize=5000,
        method="multi"
    )
    print("Silver Layer Loaded Successfully.")
 
 
 
def transform_investor_master(df):
    """
    Bronze -> Silver Transformation
    """
 
    df = df.copy()
 
    # =====================================================
    # 1. Remove duplicate records
    # =====================================================
    df = df.drop_duplicates()
 
    # =====================================================
    # 2. Trim all string columns
    # =====================================================
    object_cols = df.select_dtypes(include="object").columns
 
    for col in object_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()
 
    # =====================================================
    # 3. Standardize State
    # =====================================================
    state_mapping = {
        "GUJARAT": "Gujarat",
        "MAHARASHTRA": "Maharashtra",
        "OTHERS": "Others"
    }
 
    if "state" in df.columns:
        df["state"] = (
            df["state"]
            .str.upper()
            .map(state_mapping)
            .fillna(df["state"].str.title())
        )
 
    # =====================================================
    # 4. Standardize Account Type
    # =====================================================
    account_mapping = {
        "SAV": "Savings",
        "SAVINGS": "Savings",
        "CURRENT": "Current",
        "CUR": "Current",
        "NRE": "NRE",
        "NRO": "NRO"
    }
 
    if "account_type" in df.columns:
        df["account_type"] = (
            df["account_type"]
            .str.upper()
            .map(account_mapping)
            .fillna(df["account_type"])
        )
 
    # =====================================================
    # 5. Standardize Tax Status
    # =====================================================
    tax_mapping = {
        "I": "Individual",
        "1": "Individual",
        "INDIVIDUAL": "Individual",
        "N": "N"
    }
 
    if "tax_status" in df.columns:
        df["tax_status"] = (
            df["tax_status"]
            .str.upper()
            .map(tax_mapping)
            .fillna(df["tax_status"])
        )
 
    # =====================================================
    # 6. Standardize Holding Nature
    # =====================================================
    if "holding_nature" in df.columns:
        df["holding_nature"] = (
            df["holding_nature"]
            .str.title()
        )
 
    # =====================================================
    # 7. Standardize IFSC
    # =====================================================
    if "ifsc_code" in df.columns:
        df["ifsc_code"] = df["ifsc_code"].str.upper()
 
    # =====================================================
    # 8. Standardize PAN
    # =====================================================
    pan_cols = [
        "pan_no",
        "joint1_pan",
        "joint2_pan",
        "guardian_pan"
    ]
 
    for col in pan_cols:
        if col in df.columns:
            df[col] = df[col].str.upper()
 
    # =====================================================
    # 9. Lowercase Email
    # =====================================================
    email_cols = [
        "email",
        "nominee1_email",
        "nominee2_email",
        "nominee3_email"
    ]
 
    for col in email_cols:
        if col in df.columns:
            df[col] = df[col].str.lower()
 
    # =====================================================
    # 10. Remove spaces from Mobile Numbers
    # =====================================================
    mobile_cols = [
        "mobile_no",
        "phone_res",
        "phone_off"
    ]
 
    for col in mobile_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .str.replace(" ", "", regex=False)
                .str.replace("-", "", regex=False)
            )
 
    # =====================================================
    # 11. Date Formatting
    # =====================================================
    date_cols = [
        "dob",
        "report_date",
        "folio_date"
    ]
 
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            ).dt.date
 
    # =====================================================
    # 12. Replace Empty Strings with NULL
    # =====================================================
    df = df.replace("", None)
 
    return df
 
 
 
 
# transaction table
 
def transform_transaction(df):
 
    df = df.copy()
 
    # Remove duplicates
    df = df.drop_duplicates()
 
    # Trim spaces
    object_cols = df.select_dtypes(include="object").columns
 
    for col in object_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()
 
    # Source System
    if "source_system" in df.columns:
        df["source_system"] = df["source_system"].str.upper()
 
    # State/Location
    if "location" in df.columns:
        df["location"] = df["location"].str.title()
 
    # Bank Name
    bank_mapping = {
        "HDFCBANK": "HDFC Bank",
        "HDFC BANK": "HDFC Bank",
        "HDFC BANK LTD": "HDFC Bank",
        "HDFC BANK LIMITED": "HDFC Bank",
        "STATE BANK OF INDIA": "State Bank of India",
        "SBI": "State Bank of India",
        "KOTAK MAHINDRA BANK LIMITED": "Kotak Mahindra Bank",
        "KOTAK BANK": "Kotak Mahindra Bank",
        "AXIS BANK": "Axis Bank",
        "AXIS BANK LTD": "Axis Bank",
        "BANK OF INDIA": "Bank of India",
        "BANKOFBARODA": "Bank of Baroda",
        "BANK OF BARODA": "Bank of Baroda",
        "ICICI BANK": "ICICI Bank",
        "ICICI BANK LIMITED": "ICICI Bank"
    }
 
    if "bank_name" in df.columns:
        df["bank_name"] = (
            df["bank_name"]
            .str.upper()
            .map(bank_mapping)
            .fillna(df["bank_name"].str.title())
        )
 
    # Tax Status
    tax_mapping = {
        "I": "Individual",
        "1": "Individual",
        "INDIVIDUAL": "Individual",
        "N": "NRI",
        "NRI - REPATRIATION": "NRI - Repatriation"
    }
 
    if "tax_status" in df.columns:
        df["tax_status"] = (
            df["tax_status"]
            .str.upper()
            .map(tax_mapping)
            .fillna(df["tax_status"])
        )
 
    # Broker Code
    if "broker_code" in df.columns:
        df["broker_code"] = df["broker_code"].str.upper()
 
    # PAN
    if "pan" in df.columns:
        df["pan"] = df["pan"].str.upper()
 
    # Email
    if "email" in df.columns:
        df["email"] = df["email"].str.lower()
 
    # Phone Numbers
    for col in ["mobile", "rphone", "ophone"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .str.replace(" ", "", regex=False)
                .str.replace("-", "", regex=False)
            )
 
    # Dates
    for col in [
        "trade_date",
        "post_date",
        "report_date",
        "purdate",
        "chqdate",
        "sys_regn_d"
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
 
    # Numeric Columns
    for col in [
        "units",
        "amount",
        "load_amount",
        "broker_percent",
        "broker_commission",
        "purprice",
        "stamp_duty"
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
 
    # Replace blanks with NULL
    df = df.replace("", None)
 
    return df
 
 
#SIP Transformation
 
def transform_sip_info(df):
    """
    Bronze -> Silver Transformation for SIP Info
    """
 
    df = df.copy()
 
    # =====================================================
    # 1. Remove Duplicate Records
    # =====================================================
    df = df.drop_duplicates()
 
    # =====================================================
    # 2. Trim all String Columns
    # =====================================================
    object_cols = df.select_dtypes(include="object").columns
 
    for col in object_cols:
        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )
 
    # =====================================================
    # 3. Standardize Text Columns
    # =====================================================
 
    title_cols = [
        "location",
        "investor_name",
        "agent_name",
        "subbroker",
        "scheme_name",
        "to_scheme_name",
        "ecs_bank_name",
        "ecs_holder_name",
        "dp_inv_name"
    ]
 
    for col in title_cols:
        if col in df.columns:
            df[col] = df[col].str.title()
 
    # =====================================================
    # 4. Uppercase PAN
    # =====================================================
 
    if "pan" in df.columns:
        df["pan"] = df["pan"].str.upper()
 
    # =====================================================
    # 5. Uppercase Codes
    # =====================================================
 
    upper_cols = [
        "zone",
        "branch",
        "ihno",
        "folio",
        "agent_code",
        "fund_code",
        "product_code",
        "to_product_code",
        "ecsno",
        "reg_slno",
        "inv_dp_id",
        "inv_client_id",
        "umrncode"
    ]
 
    for col in upper_cols:
        if col in df.columns:
            df[col] = df[col].str.upper()
 
    # =====================================================
    # 6. Standardize Plan
    # =====================================================
 
    plan_mapping = {
        "REGULAR": "Regular",
        "DIRECT": "Direct"
    }
 
    for col in ["plan", "to_plan"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .str.upper()
                .map(plan_mapping)
                .fillna(df[col].str.title())
            )
 
    # =====================================================
    # 7. Standardize SIP Type
    # =====================================================
 
    if "sip_type" in df.columns:
        df["sip_type"] = df["sip_type"].str.title()
 
    # =====================================================
    # 8. Standardize SIP Mode
    # =====================================================
 
    sip_mode_mapping = {
        "AUTO-DEBIT": "Auto Debit",
        "AUTO DEBIT": "Auto Debit",
        "NACH": "NACH",
        "ECS": "ECS"
    }
 
    if "sip_mode" in df.columns:
        df["sip_mode"] = (
            df["sip_mode"]
            .str.upper()
            .map(sip_mode_mapping)
            .fillna(df["sip_mode"].str.title())
        )
 
    # =====================================================
    # 9. Standardize Frequency
    # =====================================================
 
    if "frequency" in df.columns:
        df["frequency"] = df["frequency"].str.title()
 
    # =====================================================
    # 10. Standardize Transaction Type
    # =====================================================
 
    if "trtype" in df.columns:
        df["trtype"] = df["trtype"].str.title()
 
    # =====================================================
    # 11. Standardize Status
    # =====================================================
 
    if "status" in df.columns:
        df["status"] = df["status"].str.title()
 
    # =====================================================
    # 12. Standardize Modify Flag
    # =====================================================
 
    modify_mapping = {
        "Y": "Yes",
        "N": "No"
    }
 
    if "modify_flag" in df.columns:
        df["modify_flag"] = (
            df["modify_flag"]
            .str.upper()
            .map(modify_mapping)
            .fillna(df["modify_flag"])
        )
 
    # =====================================================
    # 13. Remove Spaces from ECS Account Number
    # =====================================================
 
    if "ecs_acno" in df.columns:
        df["ecs_acno"] = (
            df["ecs_acno"]
            .str.replace(" ", "", regex=False)
        )
 
    # =====================================================
    # 14. Date Formatting
    # =====================================================
 
    date_cols = [
        "registration_date",
        "start_date",
        "end_date",
        "terminate_date"
    ]
 
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            ).dt.date
 
    # =====================================================
    # 15. Numeric Formatting
    # =====================================================
 
    numeric_cols = [
        "amount",
        "no_of_installments"
    ]
 
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )
 
    # =====================================================
    # 16. Replace Empty Strings with NULL
    # =====================================================
 
    df = df.replace("", None)
 
    return df
 
def round_decimal_columns(df):
    """
    Round all float/decimal columns to 2 decimal places.
    Does not modify integer columns.
    """
 
    df = df.copy()
 
    float_cols = df.select_dtypes(include=["float64", "float32"]).columns
 
    for col in float_cols:
        df[col] = df[col].round(2)
 
    return df
 