# ==============================
# INVESTOR MASTER COLUMN MAPPING
# ==============================

INVESTOR_MASTER_MAPPING = {

    "source": ["source"],

    # ================= CORE IDENTIFIERS =================
    "folio_no": ["foliochk", "folio", "FOLIO", "FOLIO_NO"],
    "investor_name": ["inv_name", "INV_NAME", "investor_name"],
    "joint_name_1": ["jnt_name1", "jtname1", "JOINT_NAME_1"],
    "joint_name_2": ["jnt_name2", "jtname2", "JOINT_NAME_2"],

    # ================= ADDRESS =================
    "address1": ["address1", "add1"],
    "address2": ["address2", "add2"],
    "address3": ["address3", "add3"],
    "city": ["city"],
    "state": ["state"],
    "country": ["country"],
    "pincode": ["pincode", "pin"],

    # ================= PERSONAL =================
    "dob": ["dob", "inv_dob"],
    "mobile_no": ["mobile_no", "mobile"],
    "email": ["email"],
    "phone_res": ["phone_res", "rphone"],
    "phone_off": ["phone_off", "ophone"],
 
    # ================= TAX / PAN =================
    "tax_status": ["tax_status", "status"],
    "holding_nature": ["holding_nature"],
    "pan_no": ["pan_no", "pangno", "pan"],
    "joint1_pan": ["joint1_pan"],
    "joint2_pan": ["joint2_pan"],
    "guardian_pan": ["guardian_pan", "guard_pan"],

    # ================= BANK =================
    "bank_name": ["bank_name", "bname"],
    "bank_account_no": ["bank_account_no", "bnkacno"],
    "account_type": ["account_type", "bnkactype"],
    "branch": ["branch"],
    "ifsc_code": ["ifsc_code"],

    "bank_address1": ["bank_address1", "badd1"],
    "bank_address2": ["bank_address2", "badd2"],
    "bank_address3": ["bank_address3", "badd3"],
    "bank_city": ["bank_city", "bcity"],
    "bank_state": ["bank_state"],
    "bank_country": ["bank_country"],

    # ================= NOMINEE 1 =================
    "nominee1_name": ["nominee1_name", "nom_name"],
    "nominee1_relation": ["nominee1_relation", "relation"],
    "nominee1_address1": ["nominee1_address1", "nom_addr1"],
    "nominee1_address2": ["nominee1_address2", "nom_addr2"],
    "nominee1_address3": ["nominee1_address3", "nom_addr3"],
    "nominee1_city": ["nominee1_city", "nom_city"],
    "nominee1_state": ["nominee1_state", "nom_state"],
    "nominee1_pincode": ["nominee1_pincode", "nom_pincode"],
    "nominee1_phone": ["nominee1_phone", "nom_ph_off", "nom_ph_res"],
    "nominee1_email": ["nominee1_email", "nom_email"],
    "nominee1_percentage": ["nominee1_percentage", "nom_percentage"],

    # ================= NOMINEE 2 =================
    "nominee2_name": ["nominee2_name", "nom2_name"],
    "nominee2_relation": ["nominee2_relation", "nom2_relation"],
    "nominee2_address1": ["nominee2_address1", "nom2_addr1"],
    "nominee2_address2": ["nominee2_address2", "nom2_addr2"],
    "nominee2_address3": ["nominee2_address3", "nom2_addr3"],
    "nominee2_city": ["nominee2_city", "nom2_city"],
    "nominee2_state": ["nominee2_state", "nom2_state"],
    "nominee2_pincode": ["nominee2_pincode", "nom2_pincode"],
    "nominee2_phone": ["nominee2_phone", "nom2_ph_off", "nom2_ph_res"],
    "nominee2_email": ["nominee2_email", "nom2_email"],
    "nominee2_percentage": ["nominee2_percentage", "nom2_percentage"],

    # ================= NOMINEE 3 =================
    "nominee3_name": ["nominee3_name", "nom3_name"],
    "nominee3_relation": ["nominee3_relation", "nom3_relation"],
    "nominee3_address1": ["nominee3_address1", "nom3_addr1"],
    "nominee3_address2": ["nominee3_address2", "nom3_addr2"],
    "nominee3_address3": ["nominee3_address3", "nom3_addr3"],
    "nominee3_city": ["nominee3_city", "nom3_city"],
    "nominee3_state": ["nominee3_state", "nom3_state"],
    "nominee3_pincode": ["nominee3_pincode", "nom3_pincode"],
    "nominee3_phone": ["nominee3_phone", "nom3_ph_off", "nom3_ph_res"],
    "nominee3_email": ["nominee3_email", "nom3_email"],
    "nominee3_percentage": ["nominee3_percentage", "nom3_percentage"],
        # ================= KYC / BROKER =================
    "broker_code": ["broker_code", "brokcode", "td_agent", "td_broker"],
    "dp_id": ["dp_id"],
    "demat_flag": ["demat_flag", "demat", "Demat Folio flag"],
    "ckyc_no": ["ckyc_no", "fh_ckyc_no", "CKYC NO"],
    "jh1_ckyc": ["jh1_ckyc"],
    "jh2_ckyc": ["jh2_ckyc"],
    "guardian_ckyc_no": ["guardian_ckyc_no", "g_ckyc_no"],
    "guardian_name": ["guardian_name", "guardian"],

    # ================= SYSTEM =================
    "report_date": ["report_date", "rep_date", "Report Date"],
    "report_time": ["report_time", "time1"],
    "folio_date": ["folio_date"],
    "occupation": ["occupation", "occpn", "occ_code"],
    "occupation_description": ["occupation_description"],

    # ================= PRODUCT / SCHEME =================
    "product_code": ["product_code", "product", "prod"],
    "scheme_name": ["scheme_name", "scheme", "sch_name"],
    "closing_balance": ["closing_balance", "clos_bal"],
    "rupee_balance": ["rupee_balance", "rupee_bal"],

    # ================= ADDITIONAL SOURCE COLUMNS =================
    "foliochk": ["foliochk"],
    "product": ["product", "prod"],
    "sch_name": ["sch_name", "scheme"],
    "rep_date": ["rep_date"],
    "clos_bal": ["clos_bal"],
    "rupee_bal": ["rupee_bal"],
    "uin_no": ["uin_no"],
    "inv_iin": ["inv_iin"],
    "subbroker": ["subbroker", "subbrok"],
    "brokcode": ["brokcode", "broker_code"],
    "reinv_flag": ["reinv_flag", "reinvest_f"],
    "b_pincode": ["b_pincode", "bpin"],
    "nom_ph_off": ["nom_ph_off"],
    "nom2_ph_off": ["nom2_ph_off"],
    "nom3_ph_off": ["nom3_ph_off"],
    "tpa_linked": ["tpa_linked"],
    "g_ckyc_no": ["g_ckyc_no"],
    "jh1_dob": ["jh1_dob"],
    "jh2_dob": ["jh2_dob"],
    "guardian_dob": ["guardian_dob"],
    "amc_code": ["amc_code"],
    "gst_state_code": ["gst_state_code", "gst_state_"],
    "folio_old": ["folio_old", "old_folio"],
    "scheme_folio_number": ["scheme_folio_number", "scheme_fol"],
    "fund": ["fund", "td_fund"],
    "folio": ["folio", "folio_no"],
    "fund_description": ["fund_description"],
        # ================= HOLDER DETAILS =================
    "tpin": ["tpin"],
    "f_name": ["f_name"],
    "m_name": ["m_name"],

    # ================= CONTACT DETAILS =================
    "phone_res1": ["phone_res1", "rphone1"],
    "phone_res2": ["phone_res2", "rphone2"],
    "phone_off1": ["phone_off1", "ophone1"],
    "phone_off2": ["phone_off2", "ophone2"],
    "fax_residence": ["fax_residence", "fax"],
    "fax_office": ["fax_office", "faxoff"],

    # ================= OCCUPATION / BANK =================
    "occ_code": ["occ_code", "occpn"],
    "bank_phone": ["bank_phone", "bphone"],

    # ================= INVESTOR DETAILS =================
    "investor_id": ["investor_id", "invid"],
    "client_id": ["client_id"],
    "dividend_option": ["dividend_option", "divopt"],
    "mode_of_holding_description": [
        "mode_of_holding_description",
        "holding_nature"
    ],
    "mapin_id": ["mapin_id"],
    "pan2": ["pan2"],
    "pan3": ["pan3"],

    # ================= CATEGORY =================
    "category": ["category"],
    "categorydesc": ["categorydesc"],
    "statusdesc": ["statusdesc"],

    # ================= KYC FLAGS =================
    "kyc1flag": ["kyc1flag"],
    "kyc2flag": ["kyc2flag"],
    "kyc3flag": ["kyc3flag"],
    "lastupdateddate": ["lastupdateddate"],

    # ================= COMMON ACCOUNT =================
    "commonaccno": ["commonaccno"],

    # ================= AADHAAR =================
    "holder_1_aadhaar_info": ["holder_1_aadhaar_info"],
    "holder_2_aadhaar_info": ["holder_2_aadhaar_info"],
    "holder_3_aadhaar_info": ["holder_3_aadhaar_info"],
    "guardian_aadhaar_info": ["guardian_aadhaar_info"],

    # ================= JOINT HOLDER CONTACT =================
    "joint_holder_1st_resi_phone_no": [
        "joint_holder_1st_resi_phone_no"
    ],
    "joint_holder_2nd_resi_phone_no": [
        "joint_holder_2nd_resi_phone_no"
    ],
    "joint_holder_1_contact_number": [
        "joint_holder_1_contact_number"
    ],
    "joint_holder_2_contact_number": [
        "joint_holder_2_contact_number"
    ],
    "joint_holder_1_email_id": [
        "joint_holder_1_email_id"
    ],
    "joint_holder_2_email_id": [
        "joint_holder_2_email_id"
    ],

    # ================= ADDITIONAL DETAILS =================
    "investors_resi_faxno": [
        "investors_resi_faxno",
        "fax"
    ],
    "kycgflag": ["kycgflag"],

    # ================= NOMINEE =================
    "nominee_opt_out_flag": ["nominee_opt_out_flag"],
    "nominee_dob": ["nominee_dob"],
    "nominee_guardian_name": ["nominee_guardian_name"],

    # ================= COMMUNICATION =================
    "emailconcern": ["emailconcern"],
    "emailrelationship": ["emailrelationship"],
    "mobilerelationship": ["mobilerelationship"],

    # ================= META =================
    "flag": [],
    "created_at": [],
    "updated_at": []
}

# =========================================================
# TRANSACTION MASTER MAPPING (CAMS + KFIN SAFE UNION)
# Target: bronze.transaction_master
# =========================================================

TRANSACTION_MASTER_MAPPING = {
 
    # =====================================================
    # 1-10
    # =====================================================
    "source_system": [],
 
    "prod": ["prod", "fmcode"],
    "folio_no": ["folio_no", "td_acno"],
    "scheme": ["scheme", "funddesc"],
    "investor_name": ["investor_name", "inv_name", "invname"],
    "transaction_type": ["transaction_type", "trxntype", "td_trtype"],
    "transaction_no": ["transaction_no", "trxnno", "td_trno"],
    "transaction_mode": ["transaction_mode", "trxnmode", "trnmode"],
    "transaction_status": ["transaction_status", "trxnstat", "trnstat"],
    "trade_date": ["trade_date", "traddate", "td_trdt"],
 
    # =====================================================
    # 11-20
    # =====================================================
    "post_date": ["post_date", "postdate", "td_prdt"],
    "units": ["units", "td_units"],
    "amount": ["amount", "td_amt"],
    "broker_code": ["broker_code", "brokcode", "td_agent"],
    "broker_percent": ["broker_percent", "brokperc", "brokper"],
    "broker_commission": ["broker_commission", "brokcomm"],
    "location": ["location", "td_branch"],
    "tax_status": ["tax_status", "status"],
    "load_amount": ["load", "load1"],
    "bank_name": ["bank_name", "bname"],
 
    # =====================================================
    # 21-30
    # =====================================================
    "account_no": ["account_no", "ac_no", "bnkacno"],
    "report_date": ["rep_date", "crdate"],
    "pan": ["pan", "pangno"],
    "prodcode": ["prodcode"],
    "usercode": ["usercode"],
    "usrtrxno": ["usrtrxno"],
    "purprice": ["purprice"],
    "subbrok": ["subbrok"],
    "altfolio": ["altfolio"],
    "time1": ["time1"],
 
    # =====================================================
    # 31-40
    # =====================================================
    "trxnsubtyp": ["trxnsubtyp"],
    "applicatio": ["applicatio"],
    "trxn_natur": ["trxn_natur"],
    "tax": ["tax"],
    "total_tax": ["total_tax"],
    "te_15h": ["te_15h"],
    "micr_no": ["micr_no"],
    "remarks": ["remarks"],
    "swflag": ["swflag"],
    "old_folio": ["old_folio"],
 
    # =====================================================
    # 41-50
    # =====================================================
    "seq_no": ["seq_no"],
    "reinvest_f": ["reinvest_f"],
    "mult_brok": ["mult_brok"],
    "stt": ["stt"],
    "scheme_typ": ["scheme_typ"],
    "scanrefno": ["scanrefno"],
    "inv_iin": ["inv_iin"],
    "targ_src_s": ["targ_src_s"],
    "trxn_type_": ["trxn_type_"],
    "ticob_trty": ["ticob_trty"],
 
    # =====================================================
    # 51-55
    # =====================================================
    "ticob_trno": ["ticob_trno"],
    "ticob_post": ["ticob_post"],
    "dp_id": ["dp_id"],
    "trxn_charg": ["trxn_charg"],
    "eligib_amt": ["eligib_amt"],
        # =====================================================
    # 56-60
    # =====================================================
    "src_of_txn": ["src_of_txn"],
    "trxn_suffi": ["trxn_suffi"],
    "siptrxnno": ["siptrxnno"],
    "ter_locati": ["ter_locati"],
    "euin": ["euin"],
 
    # =====================================================
    # 61-70
    # =====================================================
    "euin_valid": ["euin_valid"],
    "euin_opted": ["euin_opted"],
    "sub_brk_ar": ["sub_brk_ar"],
    "exch_dc_fl": ["exch_dc_fl"],
    "src_brk_co": ["src_brk_co"],
    "sys_regn_d": ["sys_regn_d"],
    "reversal_c": ["reversal_c"],
    "exchange_f": ["exchange_f"],
    "ca_initiat": ["ca_initiat"],
    "gst_state_": ["gst_state_"],
 
    # =====================================================
    # 71-80
    # =====================================================
    "igst_amoun": ["igst_amoun"],
    "cgst_amoun": ["cgst_amoun"],
    "sgst_amoun": ["sgst_amoun"],
    "rev_remark": ["rev_remark"],
    "original_t": ["original_t"],
    "stamp_duty": ["stamp_duty"],
    "folio_old": ["folio_old", "old_folio"],
    "scheme_fol": ["scheme_fol"],
    "amc_ref_no": ["amc_ref_no"],
    "request_re": ["request_re"],
 
    # =====================================================
    # 81-90
    # =====================================================
    "transmissi": ["transmissi"],
    "sno": ["sno"],
    "fmcode": ["fmcode", "prod"],
    "td_fund": ["td_fund"],
    "schpln": ["schpln"],
    "divopt": ["divopt"],
    "td_purred": ["td_purred"],
    "smcode": ["smcode"],
    "chqno": ["chqno"],
    "jtname1": ["jtname1"],
 
    # =====================================================
    # 91-100
    # =====================================================
    "jtname2": ["jtname2"],
    "add1": ["add1"],
    "add2": ["add2"],
    "add3": ["add3"],
    "city": ["city"],
    "pin": ["pin"],
    "state": ["state"],
    "country": ["country"],
    "dob": ["dob"],
    "rphone": ["rphone"],
 
    # =====================================================
    # 101-110
    # =====================================================
    "rphone1": ["rphone1"],
    "rphone2": ["rphone2"],
    "mobile": ["mobile"],
    "ophone": ["ophone"],
    "ophone1": ["ophone1"],
    "ophone2": ["ophone2"],
    "fax": ["fax"],
    "faxoff": ["faxoff"],
    "status": ["status"],
    "occpn": ["occpn"],
    # =====================================================
    # 111-120
    # =====================================================
    "email": ["email"],
    "bnkacno": ["bnkacno", "account_no", "ac_no"],
    "bname": ["bname", "bank_name"],
    "bnkactype": ["bnkactype"],
    "branch": ["branch"],
    "badd1": ["badd1"],
    "badd2": ["badd2"],
    "badd3": ["badd3"],
    "bcity": ["bcity"],
    "bphone": ["bphone"],
 
    # =====================================================
    # 121-130
    # =====================================================
    "pangno": ["pangno", "pan"],
    "isctrno": ["isctrno"],
    "td_pop": ["td_pop"],
    "loadper": ["loadper"],
    "td_agent": ["td_agent", "broker_code"],
    "td_broker": ["td_broker"],
    "invid": ["invid"],
    "crtime": ["crtime"],
    "trnsub": ["trnsub"],
    "td_appno": ["td_appno"],
 
    # =====================================================
    # 131-140
    # =====================================================
    "unqno": ["unqno"],
    "trdesc": ["trdesc"],
    "purdate": ["purdate"],
    "puramt": ["puramt"],
    "purunits": ["purunits"],
    "trflag": ["trflag"],
    "sfunddt": ["sfunddt"],
    "chqdate": ["chqdate"],
    "chqbank": ["chqbank"],
    "nctremarks": ["nctremarks"],
 
    # =====================================================
    # 141-149
    # =====================================================
    "td_scheme": ["td_scheme"],
    "td_plan": ["td_plan"],
    "td_nav": ["td_nav"],
    "annper": ["annper"],
    "annamt": ["annamt"],
    "td_ptrno": ["td_ptrno"],
    "td_pbranch": ["td_pbranch"],
    "oldacno": ["oldacno"],
 
    # =====================================================
    # AUDIT COLUMNS
    # =====================================================
    "flag": [],
    "created_at": [],
    "updated_at": []
}

# =========================================================
# SIP MASTER MAPPING
# Target: bronze.sip_master_new
# =========================================================

SIP_MASTER_MAPPING = {

    # =====================================================
    # SOURCE
    # =====================================================
    "source": ["source"],

    # =====================================================
    # PRODUCT
    # =====================================================
    "product": ["PRODUCT"],
    "scheme": ["SCHEME"],

    # =====================================================
    # INVESTOR
    # =====================================================
    "folio_no": ["FOLIO_NO"],
    "inv_name": ["INV_NAME"],
    "pan": ["PAN"],

    # =====================================================
    # AUTO TRANSACTION
    # =====================================================
    "aut_trntyp": ["AUT_TRNTYP"],
    "auto_trno": ["AUTO_TRNO"],
    "auto_amount": ["AUTO_AMOUNT"],

    # =====================================================
    # DATES
    # =====================================================
    "from_date": ["FROM_DATE"],
    "to_date": ["TO_DATE"],
    "cease_date": ["CEASE_DATE"],
    "reg_date": ["REG_DATE"],
    "pause_from_date": ["PAUSE_FROM_DATE"],
    "pause_to_date": ["PAUSE_TO_DATE"],

    # =====================================================
    # PERIODICITY
    # =====================================================
    "periodicity": ["PERIODICITY"],
    "period_day": ["PERIOD_DAY"],

    # =====================================================
    # INVESTOR DETAILS
    # =====================================================
    "inv_iin": ["INV_IIN"],
    "payment_mode": ["PAYMENT_MODE"],

    # =====================================================
    # TARGET SCHEME
    # =====================================================
    "target_scheme": ["TARGET_SCHEME"],
    "target_scheme_code": ["TARGET_SCHEME_CODE"],

    # =====================================================
    # BROKER
    # =====================================================
    "subbroker": ["SUBBROKER"],
    "sub_arn_code": ["SUB_ARN_CODE"],
    "euin": ["EUIN"],
    "ter_location": ["TER_LOCATION"],

    # =====================================================
    # REMARKS
    # =====================================================
    "remarks": ["REMARKS"],

    # =====================================================
    # TOP UP
    # =====================================================
    "top_up_frq": ["TOP_UP_FRQ"],
    "top_up_amt": ["TOP_UP_AMT"],
    "top_up_perc": ["TOP_UP_PERC"],

    # =====================================================
    # BANK
    # =====================================================
    "ac_type": ["AC_TYPE"],
    "bank": ["BANK"],
    "branch": ["BRANCH"],
    "instrm_no": ["INSTRM_NO"],
    "cheq_micr_no": ["CHEQ_MICR_NO"],
    "ac_holder_name": ["AC_HOLDER_NAME"],

    # =====================================================
    # SCHEME DETAILS
    # =====================================================
    "scheme_code": ["SCHEME_CODE"],
    "amc_code": ["AMC_CODE"],
    "user_code": ["USER_CODE"],
    "package_name": ["PACKAGE_NAME"],
    "special_product": ["SPECIAL_PRODUCT"],
    "subtrxndesc": ["SUBTRXNDESC"],

    # =====================================================
    # ADDITIONAL
    # =====================================================
    "folio_old": ["FOLIO_OLD"],
    "ft_sip_regno": ["FT_SIP_REGNO"],
    "scheme_folio_number": ["SCHEME_FOLIO_NUMBER"],
    "request_ref_no": ["REQUEST_REF_NO"]

}
