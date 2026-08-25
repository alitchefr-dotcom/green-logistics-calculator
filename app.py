import streamlit as st
import pandas as pd

# הגדרת תצורת עמוד
st.set_page_config(
    page_title="Green-Logistics Customs & Landed Cost Calculator",
    page_icon="🚢",
    layout="wide"
)

st.title("🚢 Green-Logistics Customs & Landed Cost Calculator")
st.caption("מחשבון עלויות יעד, מכס, רגולציה ואחסנה לציוד אנרגיה מתחדשת ו-BESS")

# ---------------------------------------------------------
# טבלאות נתונים, חברות ספנות והיטלי דלק (BAF/NBF/MFR)
# ---------------------------------------------------------
VAT_RATES = {
    "Israel": 17.0,
    "Romania": 19.0,
    "Germany": 19.0,
    "Spain": 21.0,
    "Italy": 22.0,
    "Greece": 24.0,
    "Poland": 23.0,
    "Other / Custom": 0.0
}

# היטלי דלק וסביבה רשמיים לפי חברת ספנות לקווי המזרח הרחוק (למכולת 40FT / BESS)
CARRIER_FUEL_SURCHARGES = {
    "ZIM (Integrated Shipping)": {"baf": 843.0, "code": "NBF / EFS"},
    "Hapag-Lloyd": {"baf": 780.0, "code": "MFR / EFS"},
    "COSCO Shipping": {"baf": 720.0, "code": "FAF / Bunker"},
    "MSC": {"baf": 750.0, "code": "BRS / BAF"},
    "Maersk": {"baf": 760.0, "code": "EFF / BAF"},
    "Custom Carrier": {"baf": 450.0, "code": "Custom BAF"}
}

# ---------------------------------------------------------
# סרגל צד: הגדרות מטבע ותנאי סחר
# ---------------------------------------------------------
st.sidebar.header("🗂️ הגדרות תרחיש ומטבע")
incoterm = st.sidebar.selectbox("תנאי סחר (Incoterm):", ["DDP (Delivered Duty Paid)", "CIF (Cost, Insurance & Freight)", "FOB (Free on Board)"])
display_currency = st.sidebar.selectbox("מטבע הצגה ראשי בדשבורד:", ["USD ($)", "EUR (€)", "ILS (₪)"])

st.sidebar.subheader("שערי המרה (בסיס USD)")
usd_to_eur = st.sidebar.number_input("שער USD ל-EUR:", value=0.92, step=0.01)
usd_to_ils = st.sidebar.number_input("שער USD ל-ILS:", value=3.70, step=0.01)

def convert_from_usd(amount_usd, target_curr):
    if target_curr == "USD ($)": return amount_usd, "$"
    if target_curr == "EUR (€)": return amount_usd * usd_to_eur, "€"
    if target_curr == "ILS (₪)": return amount_usd * usd_to_ils, "₪"
    return amount_usd, "$"

# ---------------------------------------------------------
# לשוניות ראשיות
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 פרטי מטען ויעד", 
    "⚓ ספנות, BAF והיטלי נמל", 
    "📦 אחסנה, השהיות ו-Last Mile", 
    "📊 Landed Cost & Incoterms Summary"
])

# ----- T1: פרטי מטען ויעד -----
with tab1:
    st.subheader("מפרט הציוד, נמלים ותנאי המכירה")
    col1, col2 = st.columns(2)
    
    with col1:
        origin_port = st.selectbox("נמל מוצא (סין):", [
            "Shanghai (שנחאי)", 
            "Ningbo (נינגבו)", 
            "Shenzhen / Yantian / Shekou (דרום סין)", 
            "Guangzhou / Nansha (דרום סין)", 
            "Custom Origin Port"
        ])
        dest_country = st.selectbox("מדינת יעד:", list(VAT_RATES.keys()), index=0)
        
        default_vat = VAT_RATES[dest_country]
        applied_vat = st.number_input(f"שיעור מע\"מ מוגדר ({dest_country}) %:", value=default_vat, step=0.5)

    with col2:
        cargo_type = st.selectbox("סוג ציוד:", [
            "BESS Container (UN3536 Class 9)", 
            "Solar PV Modules", 
            "Transformers / Heavy Equipment", 
            "Inverters / MV Station"
        ])
        container_count = st.number_input("כמות מכולות / יחידות:", min_value=1, value=10, step=1)
        
        if cargo_type == "BESS Container (UN3536 Class 9)":
            weight_tier = st.selectbox("מדרגת משקל ליחידת BESS (MTS / Ton):", [
                "Below 27 MTS ($6,300 Sell Rate)",
                "27.0 - 34.9 MTS ($12,600 Sell Rate)",
                "35.0 - 44.9 MTS ($18,375 Sell Rate)",
                "45.0 - 48.0 MTS ($21,000 Sell Rate)"
            ], index=3)
            
            if "Below 27" in weight_tier: suggested_freight = 6300
            elif "27.0" in weight_tier: suggested_freight = 12600
            elif "35.0" in weight_tier: suggested_freight = 18375
            else: suggested_freight = 21000
        else:
            suggested_freight = 3360

        is_dg = st.checkbox("מטען חומ\"ס (DG Class 9)", value=True if "BESS" in cargo_type else False)
        exw_value_usd = st.number_input("ערך ציוד בבית המפעל בסין (EXW USD):", value=1500000, step=10000)

# ----- T2: ספנות, BAF והיטלי נמל -----
with tab2:
    st.subheader("בחירת חברת ספנות, BAF והיטלים")
    
    col_a, col_b = st.columns(2)
    with col_a:
        selected_carrier = st.selectbox("חברת ספנות מובילה:", list(CARRIER_FUEL_SURCHARGES.keys()), index=0)
        
        base_freight_per_unit = st.number_input(
            "מחיר מכירה/בסיס להובלה ימית ליחידה ($):", 
            value=suggested_freight if incoterm != "FOB" else 0, 
            step=500,
            disabled=(incoterm == "FOB"),
            help="ב-FOB הלקוח משלם את הים ישירות"
        )
        
        # BAF אוטומטי לפי Carrier
        carrier_baf_default = CARRIER_FUEL_SURCHARGES[selected_carrier]["baf"]
        baf_surcharge = st.number_input(
            f"היטל דלק / סביבה ({CARRIER_FUEL_SURCHARGES[selected_carrier]['code']}) ליחידה ($):", 
            value=carrier_baf_default if incoterm != "FOB" else 0.0, 
            step=50,
            disabled=(incoterm == "FOB")
        )
        
        thc_port_fee = st.number_input("אגרת נמל יעד / דמי סבלות (THC/Wharfage) ליחידה ($):", value=380 if incoterm != "FOB" else 0, step=20)
        
    with col_b:
        china_first_mile = st.number_input("הובלה יבשתית בסין + מכס יצוא ואישורי חומ\"ס (USD סה\"כ):", value=3500, step=500)
        heavy_lift_survey = st.number_input("סקר הנדסי / היטל הובלה חריגה פרויקטלית ($ סה\"כ):", value=2500 if incoterm != "FOB" else 0, step=500)
        customs_duty_pct = st.number_input("שיעור מכס / מיסי יבוא (%):", value=0.0 if incoterm == "FOB" else 0.0, step=0.5)
        insurance_pct = st.number_input("פרמיית ביטוח ימי (% מערך ה-CIF):", value=0.35 if incoterm != "FOB" else 0.0, step=0.05)

    total_freight_usd = (base_freight_per_unit + baf_surcharge + thc_port_fee) * container_count + heavy_lift_survey if incoterm != "FOB" else 0.0

# ----- T3: אחסנה, השהיות ו-Last Mile -----
with tab3:
    st.subheader("אחסנה חיצונית, השהיות והובלת DDP לאתר (Last Mile)")
    
    col_x, col_y = st.columns(2)
    with col_x:
        free_days = st.number_input("ימי חסד בנמל (Free Days):", value=7, step=1)
        actual_port_days = st.number_input("ימי אחסנה בפועל בנמל:", value=12, step=1)
        demurrage_daily_rate = st.number_input("קנס השהיה יומי ממוצע למכולת חומ\"ס ($):", value=250 if is_dg else 150, step=10)
        
    with col_y:
        use_external_storage = st.checkbox("שימוש בחצר אחסנה חיצונית / שטח היערכות פרויקטלי", value=True)
        ext_storage_daily_rate = st.number_input("עלות אחסנה יומית בחצר חיצונית למכולה ($):", value=65 if is_dg else 45, step=5)
        ext_drayage_cost = st.number_input("שינוע יבשתי נמל-חצר-אתר (Drayage) למכולה ($):", value=850 if "21,000" in str(suggested_freight) else 600, step=50)

    st.markdown("---")
    st.subheader("הרחבות DDP (פריקה מנוף וסיכוני אתר)")
    col_ddp1, col_ddp2 = st.columns(2)
    with col_ddp1:
        site_crane_unloading = st.number_input("מנוף פריקה כבד באתר + הצבה על משטחי בטון ($ סה\"כ):", value=8500 if incoterm == "DDP (Delivered Duty Paid)" else 0, step=500, disabled=(incoterm != "DDP (Delivered Duty Paid)"))
    with col_ddp2:
        ddp_contingency_pct = st.number_input("מקדם סיכון ובלתי מתוכנן DDP (%):", value=5.0 if incoterm == "DDP (Delivered Duty Paid)" else 0.0, step=1.0, disabled=(incoterm != "DDP (Delivered Duty Paid)"))

    overdue_days = max(0, actual_port_days - free_days)
    demurrage_total_usd = overdue_days * demurrage_daily_rate * container_count
    
    if use_external_storage:
        ext_storage_total_usd = (actual_port_days * ext_storage_daily_rate * container_count) + (ext_drayage_cost * container_count)
    else:
        ext_storage_total_usd = 0.0

# ----- חישובים מסכמים -----
cif_value_usd = exw_value_usd + china_first_mile + total_freight_usd
insurance_total_usd = (cif_value_usd * (insurance_pct / 100))
customs_duty_usd = ((cif_value_usd + total_freight_usd) * (customs_duty_pct / 100))
vat_total_usd = ((cif_value_usd + total_freight_usd + customs_duty_usd) * (applied_vat / 100))

subtotal_ddp = cif_value_usd + insurance_total_usd + customs_duty_usd + demurrage_total_usd + ext_storage_total_usd + site_crane_unloading
contingency_usd = subtotal_ddp * (ddp_contingency_pct / 100)
total_landed_usd = subtotal_ddp + contingency_usd

display_val, curr_symbol = convert_from_usd(total_landed_usd, display_currency)
freight_display, _ = convert_from_usd(total_freight_usd, display_currency)
customs_display, _ = convert_from_usd(customs_duty_usd, display_currency)
vat_display, _ = convert_from_usd(vat_total_usd, display_currency)
storage_display, _ = convert_from_usd(demurrage_total_usd + ext_storage_total_usd, display_currency)

# ----- T4: Summary Dashboard -----
with tab4:
    st.subheader(f"📊 Summary Dashboard - {incoterm} ({display_currency})")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"עלות כוללת לפי {incoterm.split(' ')[0]}", f"{curr_symbol} {display_val:,.2f}")
    m2.metric("הובלה ימית + BAF", f"{curr_symbol} {freight_display:,.2f}")
    m3.metric("מכס ומיסים", f"{curr_symbol} {customs_display:,.2f}")
    m4.metric("אחסנה, השהיות ו-Last Mile", f"{curr_symbol} {storage_display:,.2f}")
    
    st.markdown("---")
    
    st.subheader("פילוח עלויות מפורט (USD Base)")
    df_summary = pd.DataFrame({
        "רכיב עלות": [
            "ערך ציוד (EXW)", 
            "הובלה פנימית בסין + מכס יצוא", 
            f"הובלה ימית + {CARRIER_FUEL_SURCHARGES[selected_carrier]['code']} ({selected_carrier})", 
            "סקר הנדסי / מטען כבד", 
            "ביטוח ימי", 
            "מכס ומיסי יבוא", 
            "קנסות השהיה בנמל (Demurrage)", 
            "אחסנה ושינוע יבשתי ביעד", 
            "מנוף פריקה והצבה באתר (DDP Scope)", 
            "מקדם סיכון DDP Contingency", 
            "מע\"מ (ניתן לקיזוז)"
        ],
        "עלות ב-USD ($)": [
            exw_value_usd, 
            china_first_mile, 
            (base_freight_per_unit + baf_surcharge + thc_port_fee) * container_count if incoterm != "FOB" else 0.0, 
            heavy_lift_survey, 
            insurance_total_usd, 
            customs_duty_usd, 
            demurrage_total_usd, 
            ext_storage_total_usd, 
            site_crane_unloading, 
            contingency_usd, 
            vat_total_usd
        ]
    })
    
    df_summary["אחוז מסך העלות"] = (df_summary["עלות ב-USD ($)"] / total_landed_usd) * 100
    df_summary["אחוז מסך העלות"] = df_summary["אחוז מסך העלות"].map("{:.2f}%".format)
    
    st.dataframe(df_summary, use_container_width=True)

st.markdown("---")
st.caption("Developed for Green-Logistics Renewable Infrastructure & Storage Projects.")
