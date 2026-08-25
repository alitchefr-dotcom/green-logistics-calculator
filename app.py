import streamlit as st
import pandas as pd

# הגדרת תצורת עמוד
st.set_page_config(
    page_title="Renewable Energy Logistics & Landed Cost Calculator",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Renewable Energy Logistics & Landed Cost Calculator")
st.caption("מחשבון עלויות יעד, מכס, רגולציה, קיימות ואחסנה לציוד אנרגיה מתחדשת ו-BESS")

# ---------------------------------------------------------
# טבלאות נתונים, חברות ספנות, מכס באירופה/ישראל והיטלי דלק
# ---------------------------------------------------------
VAT_RATES = {
    "Israel": 18.0,
    "Romania": 19.0,
    "Germany": 19.0,
    "Spain": 21.0,
    "Italy": 22.0,
    "Greece": 24.0,
    "Poland": 23.0,
    "Other / Custom": 0.0
}

# שיעורי מכס תקניים (EU vs Israel)
CUSTOMS_DUTIES = {
    "EU": {
        "BESS Container (UN3536 Class 9)": {"duty_pct": 2.7, "hs_code": "8507600000"},
        "Solar PV Modules": {"duty_pct": 0.0, "hs_code": "8541400000"},
        "Transformers / Heavy Equipment": {"duty_pct": 3.7, "hs_code": "8504230000"},
        "Inverters / MV Station / Power Skids": {"duty_pct": 0.0, "hs_code": "8504409000"},
        "E-House Units": {"duty_pct": 2.1, "hs_code": "8537200000"}
    },
    "Israel": {
        "BESS Container (UN3536 Class 9)": {"duty_pct": 0.0, "hs_code": "8507.60.00"},
        "Solar PV Modules": {"duty_pct": 0.0, "hs_code": "8541.40.00"},
        "Transformers / Heavy Equipment": {"duty_pct": 0.0, "hs_code": "8504.23.00"},
        "Inverters / MV Station / Power Skids": {"duty_pct": 0.0, "hs_code": "8504.40.90"},
        "E-House Units": {"duty_pct": 0.0, "hs_code": "8537.20.00"}
    }
}

DEFAULT_INSURANCE_RATES = {
    "Israel": 0.08,
    "Romania": 0.15,
    "Germany": 0.15,
    "Spain": 0.15,
    "Italy": 0.15,
    "Greece": 0.15,
    "Poland": 0.15,
    "Other / Custom": 0.15
}

DEFAULT_FREE_DAYS = {
    "Israel": 4,
    "Romania": 7,
    "Germany": 7,
    "Spain": 7,
    "Italy": 7,
    "Greece": 7,
    "Poland": 7,
    "Other / Custom": 7
}

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
# לשוניות ראשיות (דינמיות לפי מדינת יעד)
# ---------------------------------------------------------
# קביעה אם היעד הוא ישראל או אירופה
# נבדוק בהמשך בלשוניות

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 פרטי מטען, נמלים ויעד", 
    "⚓ ספנות, BAF ותעריפי נמלים", 
    "📦 אחסנה, השהיות ו-Last Mile", 
    "⚖️ מכס, מיסים ורגולציה", 
    "📊 Landed Cost & Incoterms Summary"
])

# ----- T1: פרטי מטען ויעד -----
with tab1:
    st.subheader("מפרט הציוד, נמלי מוצא/יעד ומדינת היעד")
    col1, col2 = st.columns(2)
    
    with col1:
        origin_port = st.selectbox("נמל מוצא (סין):", [
            "Shanghai (שנחאי)", 
            "Ningbo (נינגבו)", 
            "Shenzhen / Yantian / Shekou (דרום סין)", 
            "Guangzhou / Nansha (דרום סין)", 
            "Custom Origin Port"
        ])
        
        dest_port = st.selectbox("נמל יעד ימי (Port of Discharge):", [
            "Burgas, Bulgaria (בורגס - מעבר יבשתי לרומניה)", 
            "Constanța, Romania (קונסטנצה)", 
            "Haifa / Ashdod, Israel (חיפה / אשדוד)", 
            "Piraeus / Thessaloniki, Greece", 
            "Hamburg / Rotterdam, North Europe", 
            "Custom Destination Port"
        ])
        
        # התאמת מדינת יעד דינמית לפי נמל הפריקה
        default_country_idx = 0 if "Israel" in dest_port else (1 if "Burgas" in dest_port or "Constanța" in dest_port else 0)
        dest_country = st.selectbox("מדינת יעד סופית (אתר הפרויקט):", list(VAT_RATES.keys()), index=default_country_idx)
        
        default_vat = float(VAT_RATES[dest_country])
        applied_vat = st.number_input(f"שיעור מע\"מ מוגדר ({dest_country}) %:", value=default_vat, step=0.5)

    with col2:
        cargo_type = st.selectbox("סוג ציוד:", list(CUSTOMS_DUTIES["EU"].keys()))
        container_count = st.number_input("כמות מכולות / יחידות:", min_value=1, value=10, step=1)
        
        if cargo_type == "BESS Container (UN3536 Class 9)":
            weight_tier = st.selectbox("מדרגת משקל ליחידת BESS (MTS / Ton):", [
                "Below 27 MTS ($6,300)",
                "27.0 - 34.9 MTS ($12,600)",
                "35.0 - 44.9 MTS ($18,375)",
                "45.0 - 48.0 MTS ($21,000)"
            ], index=3)
            
            if "Below 27" in weight_tier: suggested_freight = 6300.0
            elif "27.0" in weight_tier: suggested_freight = 12600.0
            elif "35.0" in weight_tier: suggested_freight = 18375.0
            else: suggested_freight = 21000.0
        else:
            suggested_freight = 3360.0

        is_dg = st.checkbox("מטען חומ\"ס (DG Class 9)", value=True if "BESS" in cargo_type else False)
        exw_value_usd = st.number_input("ערך ציוד בבית המפעל בסין (EXW USD):", value=500000.0, step=10000.0)

# ----- T2: ספנות, BAF ותעריפי נמלים -----
with tab2:
    st.subheader("בחירת חברת ספנות, תעריפי נמלים (Origin/Dest THC) וביטוח")
    
    col_a, col_b = st.columns(2)
    with col_a:
        selected_carrier = st.selectbox("חברת ספנות מובילה:", list(CARRIER_FUEL_SURCHARGES.keys()), index=0)
        
        base_freight_per_unit = st.number_input(
            "מחיר הובלה ימית בסיס ליחידה ($):", 
            value=float(suggested_freight) if incoterm != "FOB (Free on Board)" else 0.0, 
            step=500.0,
            disabled=(incoterm == "FOB (Free on Board)"),
            help="ב-FOB הלקוח משלם את ההובלה הימית ישירות"
        )
        
        carrier_baf_default = float(CARRIER_FUEL_SURCHARGES[selected_carrier]["baf"])
        baf_surcharge = st.number_input(
            f"היטל דלק / סביבה ({CARRIER_FUEL_SURCHARGES[selected_carrier]['code']}) ליחידה ($):", 
            value=carrier_baf_default if incoterm != "FOB (Free on Board)" else 0.0, 
            step=50.0,
            disabled=(incoterm == "FOB (Free on Board)")
        )
        
        dest_thc_port_fee = st.number_input(
            "אגרות ותעריפי נמל יעד (Destination THC / Wharfage) ליחידה ($):", 
            value=380.0 if incoterm != "FOB (Free on Board)" else 0.0, 
            step=20.0,
            help="תעריפי פריקה מנמל היעד אל המסוף"
        )
        
    with col_b:
        st.markdown("**עלויות מוצא בסין (China Origin Scope):**")
        china_inland_drayage = st.number_input("הובלה פנימית בסין + עמילות יצוא ואישורי חומ\"ס (USD סה\"כ):", value=2200.0, step=300.0)
        china_origin_thc = st.number_input("אגרות ותעריפי נמל מוצא בסין (Origin THC & Port Fees סה\"כ):", value=1300.0, step=200.0)
        
        st.markdown("**מיסים וביטוח:**")
        heavy_lift_survey = st.number_input("סקר הנדסי / היטל הובלה חריגה פרויקטלית ($ סה\"כ):", value=2500.0 if incoterm != "FOB (Free on Board)" else 0.0, step=500.0)
        
        # מכס דינמי - 0% לישראל, 2.7% לאירופה (עבור BESS)
        region_key = "Israel" if dest_country == "Israel" else "EU"
        default_duty = CUSTOMS_DUTIES[region_key][cargo_type]["duty_pct"]
        customs_duty_pct = st.number_input("שיעור מכס / מיסי יבוא (%):", value=float(default_duty), step=0.1)
        
        default_ins_rate = DEFAULT_INSURANCE_RATES.get(dest_country, 0.15)
        insurance_pct = st.number_input(
            "פרמיית ביטוח ימי (% מערך ה-CIF):", 
            value=default_ins_rate if incoterm != "FOB (Free on Board)" else 0.0, 
            step=0.01,
            help=f"עודכן אוטומטית לפי מדינת היעד שנבחרה ({dest_country})"
        )

    china_first_mile_total = china_inland_drayage + china_origin_thc
    total_freight_usd = (base_freight_per_unit + baf_surcharge + dest_thc_port_fee) * float(container_count) + heavy_lift_survey if incoterm != "FOB (Free on Board)" else 0.0

# ----- T3: אחסנה, השהיות ו-Last Mile -----
with tab3:
    st.subheader("אחסנה חיצונית, השהיות והובלת DDP לאתר (Cross-Border / Last Mile Drayage)")
    
    col_x, col_y = st.columns(2)
    with col_x:
        default_fd = DEFAULT_FREE_DAYS.get(dest_country, 7)
        free_days = st.number_input("ימים חופשיים בנמל (Free Days):", value=default_fd, step=1, help="בישראל מוגדרים 4 ימים חופשיים מול הנמלים")
        actual_port_days = st.number_input("ימי אחסנה בפועל בנמל:", value=12, step=1)
        demurrage_daily_rate = st.number_input("קנס השהיה יומי ממוצע למכולת חומ\"ס ($):", value=250.0 if is_dg else 150.0, step=10.0)
        
    with col_y:
        use_external_storage = st.checkbox("שימוש בחצר אחסנה חיצונית / שטח היערכות פרויקטלי", value=True)
        ext_storage_daily_rate = st.number_input("עלות אחסנה יומית בחצר חיצונית למכולה ($):", value=65.0 if is_dg else 45.0, step=5.0)
        
        default_cross_border_drayage = 1850.0 if "Burgas" in dest_port else (850.0 if suggested_freight == 21000.0 else 600.0)
        ext_drayage_cost = st.number_input(
            "שינוע יבשתי מנמל היעד לאתר הפרויקט (Inland Drayage to Site) למכולה ($):", 
            value=default_cross_border_drayage, 
            step=50.0, 
            help="הובלה יבשתית מנמל הפריקה עד לאתר הפרויקט"
        )

    st.markdown("---")
    st.subheader("הרחבות DDP (פריקה מנוף וסיכוני אתר)")
    col_ddp1, col_ddp2 = st.columns(2)
    with col_ddp1:
        site_crane_unloading = st.number_input("מנוף פריקה כבד באתר + הצבה על משטחי בטון ($ סה\"כ):", value=8500.0 if incoterm == "DDP (Delivered Duty Paid)" else 0.0, step=500.0, disabled=(incoterm != "DDP (Delivered Duty Paid)"))
    with col_ddp2:
        ddp_contingency_pct = st.number_input("מקדם סיכון ובלתי מתוכנן DDP (%):", value=5.0 if incoterm == "DDP (Delivered Duty Paid)" else 0.0, step=1.0, disabled=(incoterm != "DDP (Delivered Duty Paid)"))

    overdue_days = max(0, actual_port_days - free_days)
    demurrage_total_usd = float(overdue_days) * demurrage_daily_rate * float(container_count)
    
    if use_external_storage:
        ext_storage_total_usd = (float(actual_port_days) * ext_storage_daily_rate * float(container_count)) + (ext_drayage_cost * float(container_count))
    else:
        ext_storage_total_usd = 0.0

# ----- T4: מכס, מיסים ורגולציה (מותאם דינמית - ישראל vs אירופה) -----
with tab4:
    if dest_country == "Israel":
        st.subheader("🇮🇱 מכס, מיסים ורגולציה בישראל")
        
        hs_code_israel = CUSTOMS_DUTIES["Israel"][cargo_type]["hs_code"]
        
        col_il1, col_il2 = st.columns(2)
        with col_il1:
            st.markdown(f"**פרט מכס ישראלי (HS Code):** `{hs_code_israel}`")
            st.markdown(f"**שיעור מכס בסיסי:** `0.0%` (פטור לפי צו תעריף המכס הישראלי)")
            st.markdown(f"**מע\"מ יבוא בישראל:** `{applied_vat}%` (ניתן לקיזוז תשומות)")
            st.markdown(f"**נמל פריקה:** `{dest_port}`")
            
            st.info("💡 **הערה רגולטורית (ישראל):** יבוא מתקני אנרגיה מתחדשת ואגירה (BESS) פטור ממכס וממס קנייה, אך כפוף לאישור היתר רעלים ורישוי המשרד להגנת הסביבה/כבאות.")

        with col_il2:
            st.markdown("**אישורים ורגולציה מקומית בישראל**")
            epr_fee_per_unit = st.number_input("אגרת איכות הסביבה / טיפול בסוללות ליחידה ($):", value=200.0 if "BESS" in cargo_type else 50.0, step=50.0)
            local_regulatory_permits = st.number_input("אישורי היתר רעלים, סוקר חומ\"ס ואישורי כיבוי ($ סה\"כ):", value=1500.0 if is_dg else 400.0, step=100.0)

    else:
        st.subheader("🇪🇺 מכס באירופה, בדיקת TARIC בלייב ורגולציה")
        
        hs_code_eu = CUSTOMS_DUTIES["EU"][cargo_type]["hs_code"]
        taric_url = f"https://ec.europa.eu/taxation_customs/dds2/taric/taric_consultation.jsp?Lang=en&SimDate=20260825&Taric={hs_code_eu}"
        
        col_eu1, col_eu2 = st.columns(2)
        with col_eu1:
            st.markdown(f"**סיווג פרט מכס רגולטורי (HS Code):** `{hs_code_eu}`")
            st.markdown(f"**שיעור מכס בסיס באיחוד האירופי:** `{CUSTOMS_DUTIES['EU'][cargo_type]['duty_pct']}%`")
            st.markdown(f"**נמל פריקה:** `{dest_port}` | **מדינת יעד סופית:** `{dest_country}`")
            
            st.link_button("🔗 פתח בדיקת מכס רשמית ב-EU TARIC Database", taric_url)
            st.caption("הקישור יפתח את עמוד הבדיקה הרשמי של נציבות האיחוד האירופי עבור פרט המכס שנבחר.")

        with col_eu2:
            st.markdown("**אגרות EPR ורגולציה סביבתית**")
            epr_fee_per_unit = st.number_input("אגרת מיחזור סוללות / אחריות יצרן מורחבת (EPR / EoL Fee) ליחידה ($):", value=450.0 if "BESS" in cargo_type else 80.0, step=50.0)
            local_regulatory_permits = st.number_input("אישורים רגולטוריים / היתרי חומ\"ס מקומיים ($ סה\"כ):", value=1200.0 if is_dg else 300.0, step=100.0)

    epr_total_usd = (epr_fee_per_unit * float(container_count)) + local_regulatory_permits

# ----- חישובים מסכמים -----
cif_value_usd = exw_value_usd + china_first_mile_total + total_freight_usd
insurance_total_usd = (cif_value_usd * (insurance_pct / 100.0))
customs_duty_usd = ((cif_value_usd + total_freight_usd) * (customs_duty_pct / 100.0))
vat_total_usd = ((cif_value_usd + total_freight_usd + customs_duty_usd) * (applied_vat / 100.0))

subtotal_ddp = cif_value_usd + insurance_total_usd + customs_duty_usd + demurrage_total_usd + ext_storage_total_usd + site_crane_unloading + epr_total_usd
contingency_usd = subtotal_ddp * (ddp_contingency_pct / 100.0)
total_landed_usd = subtotal_ddp + contingency_usd

display_val, curr_symbol = convert_from_usd(total_landed_usd, display_currency)
freight_display, _ = convert_from_usd(total_freight_usd, display_currency)
customs_display, _ = convert_from_usd(customs_duty_usd, display_currency)
vat_display, _ = convert_from_usd(vat_total_usd, display_currency)
storage_display, _ = convert_from_usd(demurrage_total_usd + ext_storage_total_usd, display_currency)

# ----- T5: Summary Dashboard -----
with tab5:
    st.subheader(f"📊 Summary Dashboard - {incoterm} ({display_currency})")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"עלות כוללת לפי {incoterm.split(' ')[0]}", f"{curr_symbol} {display_val:,.2f}")
    m2.metric("הובלה ימית + BAF + THC יעד", f"{curr_symbol} {freight_display:,.2f}")
    m3.metric("מכס ומיסים", f"{curr_symbol} {customs_display:,.2f}")
    m4.metric("אחסנה, השהיות ו-Inland Drayage", f"{curr_symbol} {storage_display:,.2f}")
    
    st.markdown("---")
    
    st.subheader("פילוח עלויות מפורט (USD Base)")
    df_summary = pd.DataFrame({
        "רכיב עלות": [
            "ערך ציוד (EXW)", 
            "הובלה פנימית בסין + עמילות יצוא", 
            "אגרות נמל מוצא בסין (Origin THC & Port Fees)", 
            f"הובלה ימית + {CARRIER_FUEL_SURCHARGES[selected_carrier]['code']} + THC יעד ({selected_carrier}) [{dest_port}]", 
            "סקר הנדסי / מטען כבד", 
            "ביטוח ימי", 
            "מכס ומיסי יבוא", 
            "אגרות EPR, מיחזור ורגולציה סביבתית",
            "קנסות השהיה בנמל (Demurrage)", 
            "שינוע יבשתי מנמל היעד לאתר הפרויקט (Inland Drayage)", 
            "מנוף פריקה והצבה באתר (DDP Scope)", 
            "מקדם סיכון DDP Contingency", 
            "מע\"מ (ניתן לקיזוז)"
        ],
        "עלות ב-USD ($)": [
            exw_value_usd, 
            china_inland_drayage, 
            china_origin_thc, 
            (base_freight_per_unit + baf_surcharge + dest_thc_port_fee) * float(container_count) if incoterm != "FOB (Free on Board)" else 0.0, 
            heavy_lift_survey, 
            insurance_total_usd, 
            customs_duty_usd, 
            epr_total_usd, 
            demurrage_total_usd, 
            ext_storage_total_usd, 
            site_crane_unloading, 
            contingency_usd, 
            vat_total_usd
        ]
    })
    
    df_summary["אחוז מסך העלות"] = (df_summary["עלות ב-USD ($)"] / total_landed_usd) * 100.0
    df_summary["אחוז מסך העלות"] = df_summary["אחוז מסך העלות"].map("{:.2f}%".format)
    
    st.dataframe(df_summary, use_container_width=True)
    
    st.markdown("---")
    csv_data = df_summary.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 הורד דוח ניתוח עלויות מלא (CSV/Excel)",
        data=csv_data,
        file_name=f"Landed_Cost_Report_{incoterm.split(' ')[0]}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Developed for Renewable Energy Infrastructure & Storage Projects.")
