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
# טבלאות נתונים ומילוני ערכים
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

DEFAULT_FX_RATES = {
    "USD": 1.0,
    "EUR": 1.08,
    "ILS": 0.27
}

# ---------------------------------------------------------
# סרגל צד: הגדרות מטבע ושערי חליפין
# ---------------------------------------------------------
st.sidebar.header("🗂️ הגדרות מטבע ושערים")
display_currency = st.sidebar.selectbox("מטבע הצגה ראשי בדשבורד:", ["USD ($)", "EUR (€)", "ILS (₪)"])

st.sidebar.subheader("שערי המרה (בסיס USD)")
usd_to_eur = st.sidebar.number_input("שער USD ל-EUR:", value=0.92, step=0.01)
usd_to_ils = st.sidebar.number_input("שער USD ל-ILS:", value=3.70, step=0.01)

# פונקציית המרה
def convert_to_usd(amount, curr):
    if curr == "USD": return amount
    if curr == "EUR": return amount / usd_to_eur
    if curr == "ILS": return amount / usd_to_ils
    return amount

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
    "⚓ הובלה ימית והיטלים", 
    "📦 אחסנה, השהיות ושינוע", 
    "📊 Total Landed Cost Summary"
])

# ----- T1: פרטי מטען ויעד -----
with tab1:
    st.subheader("מפרט הציוד ומדינת היעד")
    col1, col2 = st.columns(2)
    
    with col1:
        origin_port = st.selectbox("נמל מוצא:", ["Shanghai, China", "Ningbo, China", "Shenzhen, China", "Custom Port"])
        dest_country = st.selectbox("מדינת יעד:", list(VAT_RATES.keys()), index=0)
        
        # מעמ אוטומטי לפי מדינה
        default_vat = VAT_RATES[dest_country]
        applied_vat = st.number_input(f"שיעור מע\"מ מוגדר ({dest_country}) %:", value=default_vat, step=0.5)

    with col2:
        cargo_type = st.selectbox("סוג ציוד:", ["BESS Container (20ft/40ft)", "Solar PV Modules", "Transformers / Heavy Equipment", "Inverters / MV Station"])
        container_count = st.number_input("כמות מכולות / יחידות:", min_value=1, value=10, step=1)
        is_dg = st.checkbox("מטען חומ\"ס (DG Class 9 / UN3536)", value=True if "BESS" in cargo_type else False)
        cif_value_usd = st.number_input("ערך ציוד בנמל מוצא (CIF USD):", value=1500000, step=10000)

# ----- T2: הובלה ימית והיטלים ("מייקרים") -----
with tab2:
    st.subheader("תמחור הובלה ימית והיטלי ספנות / נמל")
    
    col_a, col_b = st.columns(2)
    with col_a:
        base_freight_per_unit = st.number_input("מחיר בסיס להובלה ימית ליחידה ($):", value=3200, step=100)
        baf_surcharge = st.number_input("היטל דלק / סביבה (BAF/LSS) ליחידה ($):", value=250, step=50)
        thc_port_fee = st.number_input("אגרת נמל / דמי סבלות (THC/Wharfage) ליחידה ($):", value=380, step=20)
        
    with col_b:
        heavy_lift_survey = st.number_input("סקר הנדסי / היטל הובלה חריגה פרויקטלית ($ סה\"כ):", value=2500, step=500)
        customs_duty_pct = st.number_input("שיעור מכס / מיסי יבוא (%):", value=0.0, step=0.5, help="בדוק זכאות לפטור/הסכם סחר FTA")
        insurance_pct = st.number_input("פרמיית ביטוח ימי (% מערך ה-CIF):", value=0.35, step=0.05)

    total_freight_usd = (base_freight_per_unit + baf_surcharge + thc_port_fee) * container_count + heavy_lift_survey

# ----- T3: אחסנה, השהיות ושינוע -----
with tab3:
    st.subheader("אחסנה חיצונית, חצר היערכות וחישוב השהיות (Demurrage)")
    
    col_x, col_y = st.columns(2)
    with col_x:
        free_days = st.number_input("ימי חסד בנמל (Free Days):", value=7, step=1)
        actual_port_days = st.number_input("ימי אחסנה בפועל בנמל:", value=12, step=1)
        demurrage_daily_rate = st.number_input("קנס השהיה יומי ממוצע למכולה ($):", value=150, step=10)
        
    with col_y:
        use_external_storage = st.checkbox("שימוש בחצר אחסנה חיצונית / שטח היערכות פרויקטלי", value=True)
        ext_storage_daily_rate = st.number_input("עלות אחסנה יומית בחצר חיצונית למכולה ($):", value=45, step=5)
        ext_drayage_cost = st.number_input("שינוע יבשתי נמל-חצר-אתר (Drayage) למכולה ($):", value=600, step=50)

    # חישוב השהיות
    overdue_days = max(0, actual_port_days - free_days)
    demurrage_total_usd = overdue_days * demurrage_daily_rate * container_count
    
    if use_external_storage:
        ext_storage_total_usd = (actual_port_days * ext_storage_daily_rate * container_count) + (ext_drayage_cost * container_count)
    else:
        ext_storage_total_usd = 0.0

# ---------------------------------------------------------
# חישובים מסכמים (Landed Cost Engine)
# ---------------------------------------------------------
insurance_total_usd = (cif_value_usd * (insurance_pct / 100))
customs_duty_usd = ((cif_value_usd + total_freight_usd) * (customs_duty_pct / 100))
vat_total_usd = ((cif_value_usd + total_freight_usd + customs_duty_usd) * (applied_vat / 100))

total_landed_usd = cif_value_usd + total_freight_usd + insurance_total_usd + customs_duty_usd + demurrage_total_usd + ext_storage_total_usd

# המרה למטבע תצוגה נבחר
display_val, curr_symbol = convert_from_usd(total_landed_usd, display_currency)
freight_display, _ = convert_from_usd(total_freight_usd, display_currency)
customs_display, _ = convert_from_usd(customs_duty_usd, display_currency)
vat_display, _ = convert_from_usd(vat_total_usd, display_currency)
storage_display, _ = convert_from_usd(demurrage_total_usd + ext_storage_total_usd, display_currency)

# ----- T4: Summary Dashboard -----
with tab4:
    st.subheader(f"📊 Total Landed Cost Summary ({display_currency})")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("עלות יעד כוללת (Landed Cost)", f"{curr_symbol} {display_val:,.2f}")
    m2.metric("סה\"כ הובלה והיטלים", f"{curr_symbol} {freight_display:,.2f}")
    m3.metric("סה\"כ מכס ומיסים", f"{curr_symbol} {customs_display:,.2f}")
    m4.metric("אחסנה, השהיות ושינוע", f"{curr_symbol} {storage_display:,.2f}")
    
    st.markdown("---")
    
    st.subheader("פילוח עלויות מפורט (USD Base)")
    df_summary = pd.DataFrame({
        "רכיב עלות": [
            "ערך ציוד (CIF)", 
            "הובלה ימית + BAF + THC", 
            "סקר הנדסי / מטען כבד", 
            "ביטוח ימי", 
            "מכס ומיסי יבוא", 
            "קנסות השהיה בנמל (Demurrage)", 
            "אחסנה ושינוע חיצוני", 
            "מע\"מ (ניתן לקיזוז)"
        ],
        "עלות ב-USD ($)": [
            cif_value_usd, 
            (base_freight_per_unit + baf_surcharge + thc_port_fee) * container_count, 
            heavy_lift_survey, 
            insurance_total_usd, 
            customs_duty_usd, 
            demurrage_total_usd, 
            ext_storage_total_usd, 
            vat_total_usd
        ]
    })
    
    df_summary["אחוז מסך העלות"] = (df_summary["עלות ב-USD ($)"] / total_landed_usd) * 100
    df_summary["אחוז מסך העלות"] = df_summary["אחוז מסך העלות"].map("{:.2f}%".format)
    
    st.dataframe(df_summary, use_container_width=True)

st.markdown("---")
st.caption("Developed for Green-Logistics Renewable Infrastructure & Storage Projects.")
