import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# =========================
# POSTGRES CONNECTION
# =========================
engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/tr_project"
)

# =========================
# CLEAN FUNCTIONS
# =========================
def clean_columns(df):
    df = df.copy()

    df.columns = (
        df.columns.astype(str)
        .str.lower()
        .str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace("#", "", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
    )

    return df


def clean_value(v):

    if pd.isna(v):
        return ""

    if isinstance(v, pd.Timestamp):
        return str(v.date())

    return str(v).strip()


def get(df, col):

    if col in df.columns:
        return df[col]

    return pd.Series([""] * len(df), index=df.index)


def normalize(df):

    df = df.copy()

    for col in df.columns:

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df[col] = (
            df[col]
            .replace("nan", "")
            .replace("None", "")
            .replace("<NA>", "")
        )

    return df


# =========================
# MAIN FUNCTION
# =========================
def process_investor_master(cams=None, kfin=None):

    dfs = []

    # =========================
    # CAMS
    # =========================
    if cams is not None:

        cams = clean_columns(cams)

        cams_df = pd.DataFrame({

            "folio_no": get(cams, "foliochk"),
            "amc_code": get(cams, "amc_code"),
            "scheme_name": get(cams, "sch_name"),
            "investor_name": get(cams, "inv_name"),
            "joint_name_1": get(cams, "jnt_name1"),
            "joint_name_2": get(cams, "jnt_name2"),
            "address1": get(cams, "address1"),
            "address2": get(cams, "address2"),
            "address3": get(cams, "address3"),
            "city": get(cams, "city"),
            "state": get(cams, "gst_state_code"),
            "country": get(cams, "country"),
            "pincode": get(cams, "pincode"),
            "dob": get(cams, "inv_dob"),
            "mobile_no": get(cams, "mobile_no"),
            "email": get(cams, "email"),
            "phone_res": get(cams, "phone_res"),
            "phone_off": get(cams, "phone_off"),
            "tax_status": get(cams, "tax_status"),
            "pan_no": get(cams, "pan_no"),
            "joint1_pan": get(cams, "joint1_pan"),
            "joint2_pan": get(cams, "joint2_pan"),
            "guardian_pan": get(cams, "guard_pan"),
            "holding_nature": get(cams, "holding_nature"),
            "occupation": get(cams, "occupation"),
            "broker_code": get(cams, "broker_code"),
            "bank_name": get(cams, "bank_name"),
            "branch": get(cams, "branch"),
            "account_type": get(cams, "ac_type"),
            "bank_account_no": get(cams, "ac_no"),
            "ifsc_code": get(cams, "ifsc_code"),
            "dp_id": get(cams, "dp_id"),
            "demat_flag": get(cams, "demat"),
            "report_date": get(cams, "rep_date"),
            "closing_balance": get(cams, "clos_bal"),
            "rupee_balance": get(cams, "rupee_bal"),
            "foliochk": get(cams, "foliochk"),
            "product": get(cams, "product"),
            "sch_name": get(cams, "sch_name"),
            "rep_date": get(cams, "rep_date"),
            "clos_bal": get(cams, "clos_bal"),
            "rupee_bal": get(cams, "rupee_bal"),
            "uin_no": get(cams, "uin_no"),
            "inv_iin": get(cams, "inv_iin"),
            "subbroker": get(cams, "subbroker"),
            "brokcode": get(cams, "brokcode"),
            "reinv_flag": get(cams, "reinv_flag"),
            "b_pincode": get(cams, "b_pincode"),
            "tpa_linked": get(cams, "tpa_linked"),
            "g_ckyc_no": get(cams, "g_ckyc_no"),
            "jh1_dob": get(cams, "jh1_dob"),
            "jh2_dob": get(cams, "jh2_dob"),
            "guardian_dob": get(cams, "guardian_dob"),
            "folio_old": get(cams, "folio_old"),
            "scheme_folio_number": get(cams, "scheme_folio_number"),
            "source": "CAMS"

        })

        cams_df = normalize(cams_df)

        dfs.append(cams_df)

    # =========================
    # KFIN
    # =========================
    if kfin is not None:

        kfin = clean_columns(kfin)

        kfin_df = pd.DataFrame({

            "folio_no": get(kfin, "folio"),
            "fund": get(kfin, "fund"),
            "scheme_name": get(kfin, "fund_description"),
            "fund_description": get(kfin, "fund_description"),
            "investor_name": get(kfin, "investor_name"),
            "joint_name_1": get(kfin, "joint_name_1"),
            "joint_name_2": get(kfin, "joint_name_2"),
            "address1": get(kfin, "address_1"),
            "address2": get(kfin, "address_2"),
            "address3": get(kfin, "address_3"),
            "city": get(kfin, "city"),
            "state": get(kfin, "state"),
            "country": get(kfin, "country"),
            "pincode": get(kfin, "pincode"),
            "dob": get(kfin, "date_of_birth"),
            "mobile_no": get(kfin, "mobile_number"),
            "email": get(kfin, "email"),
            "phone_res": get(kfin, "phone_residence"),
            "phone_off": get(kfin, "phone_office"),
            "tax_status": get(kfin, "tax_status"),
            "pan_no": get(kfin, "pan_number"),
            "holding_nature": get(kfin, "mode_of_holding_description"),
            "occupation": get(kfin, "occupation_description"),
            "occupation_description": get(kfin, "occupation_description"),
            "broker_code": get(kfin, "broker_code"),
            "bank_name": get(kfin, "bank_name"),
            "branch": get(kfin, "branch"),
            "account_type": get(kfin, "account_type"),
            "bank_account_no": get(kfin, "bankaccno"),
            "ifsc_code": get(kfin, "ifsc_code"),
            "dp_id": get(kfin, "dpid"),
            "demat_flag": get(kfin, "demat_folio_flag"),
            "report_date": get(kfin, "report_date"),
            "report_time": get(kfin, "report_time"),
            "tpin": get(kfin, "tpin"),
            "f_name": get(kfin, "f_name"),
            "m_name": get(kfin, "m_name"),
            "phone_res1": get(kfin, "phone_res1"),
            "phone_res2": get(kfin, "phone_res2"),
            "phone_off1": get(kfin, "phone_off1"),
            "phone_off2": get(kfin, "phone_off2"),
            "fax_residence": get(kfin, "fax_residence"),
            "fax_office": get(kfin, "fax_office"),
            "occ_code": get(kfin, "occ_code"),
            "bank_phone": get(kfin, "bank_phone"),
            "investor_id": get(kfin, "investor_id"),
            "client_id": get(kfin, "client_id"),
            "dividend_option": get(kfin, "dividend_option"),
            "mode_of_holding_description": get(kfin, "mode_of_holding_description"),
            "mapin_id": get(kfin, "mapin_id"),
            "pan2": get(kfin, "pan2"),
            "pan3": get(kfin, "pan3"),
            "category": get(kfin, "category"),
            "guardian_name": get(kfin, "guardianname"),
            "categorydesc": get(kfin, "categorydesc"),
            "statusdesc": get(kfin, "statusdesc"),
            "kyc1flag": get(kfin, "kyc1flag"),
            "kyc2flag": get(kfin, "kyc2flag"),
            "kyc3flag": get(kfin, "kyc3flag"),
            "lastupdateddate": get(kfin, "lastupdateddate"),
            "commonaccno": get(kfin, "commonaccno"),
            "holder_1_aadhaar_info": get(kfin, "holder_1_aadhaar_info"),
            "holder_2_aadhaar_info": get(kfin, "holder_2_aadhaar_info"),
            "holder_3_aadhaar_info": get(kfin, "holder_3_aadhaar_info"),
            "guardian_aadhaar_info": get(kfin, "guardian_aadhaar_info"),
            "joint_holder_1st_resi_phone_no": get(kfin, "joint_holder_1st_resi_phone_no"),
            "joint_holder_2nd_resi_phone_no": get(kfin, "joint_holder_2nd_resi_phone_no"),
            "joint_holder_1_contact_number": get(kfin, "joint_holder_1_contact_number"),
            "joint_holder_2_contact_number": get(kfin, "joint_holder_2_contact_number"),
            "joint_holder_1_email_id": get(kfin, "joint_holder_1_email_id"),
            "joint_holder_2_email_id": get(kfin, "joint_holder_2_email_id"),
            "investors_resi_faxno": get(kfin, "investors_resi_faxno"),
            "kycgflag": get(kfin, "kycgflag"),
            "nominee_opt_out_flag": get(kfin, "nominee_opt_out_flag"),
            "nominee_dob": get(kfin, "nominee_dob"),
            "nominee_guardian_name": get(kfin, "nominee_guardian_name"),
            "emailconcern": get(kfin, "emailconcern"),
            "emailrelationship": get(kfin, "emailrelationship"),
            "mobilerelationship": get(kfin, "mobilerelationship"),
            "source": "KFIN"

        })

        kfin_df = normalize(kfin_df)

        dfs.append(kfin_df)
        
    # =========================
    # NO FILES
    # =========================
    if not dfs:
        print("No files found.")
        return

    # =========================
    # COMBINE DATA
    # =========================
    df = pd.concat(dfs, ignore_index=True)

    # Clean values
    df = df.apply(lambda col: col.map(clean_value))
    df = normalize(df)

    # =========================
    # LOAD EXISTING DATA
    # =========================
    existing = pd.read_sql(
        "SELECT * FROM investor_master",
        engine
    )

    existing = normalize(existing)

    # =========================
    # MATCH DB STRUCTURE
    # =========================
    df = df.reindex(columns=existing.columns, fill_value="")

    existing = existing.reindex(columns=df.columns, fill_value="")

    # Convert everything to string
    df = df.fillna("").astype(str)

    existing = existing.fillna("").astype(str)

    # Remove leading/trailing spaces
    for col in df.columns:
        df[col] = df[col].str.strip()

    for col in existing.columns:
        existing[col] = existing[col].str.strip()

    # =========================
    # REMOVE DUPLICATES
    # Skip only when EVERY COLUMN matches
    # =========================
    existing_rows = set(
        map(tuple, existing.values.tolist())
    )

    new_rows = df[
        ~df.apply(tuple, axis=1).isin(existing_rows)
    ]

    print(f"Incoming rows : {len(df)}")
    print(f"Existing rows : {len(existing)}")
    print(f"New rows      : {len(new_rows)}")

    # =========================
    # INSERT NEW ROWS
    # =========================
    if not new_rows.empty:

        new_rows.to_sql(
            "investor_master",
            engine,
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi"
        )

        print(f"{len(new_rows)} rows inserted successfully.")

    else:
        print("No new rows found. Skipped duplicate records.")

    print("Investor Master Loaded Successfully.")