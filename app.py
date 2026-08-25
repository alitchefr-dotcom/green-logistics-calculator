import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# הגדרת תצורת עמוד ושפה
# ---------------------------------------------------------
st.set_page_config(
    page_title="Renewable Energy Logistics & Landed Cost Calculator",
    page_icon="⚡",
    layout="wide"
)

# מתג שפה בסרגל הצד
st.sidebar.header("🌐 Language / שפה")
lang = st.sidebar.radio("Select Language / בחר שפה:", ["Hebrew (עברית)", "English"], index=0)
is_hebrew = (lang == "Hebrew (עברית)")

# מילון מונחים דו-לשוני
T = {
    "title": "⚡ Renewable Energy Logistics & Landed Cost Calculator",
    "caption": "Calculates Landed Cost, Customs, Regulation & Storage for Renewable Energy & BESS Projects" if not is_hebrew else "מחשבון עלויות יעד, מכס, רגולציה, קיימות ואחסנה לציוד אנרגיה מתחדשת ו-BESS",
    "scenario_header": "🗂️ Scenario & Currency Setup" if not is_hebrew else "🗂️ הגדרות תרחיש ומטבע",
    "incoterm_label": "Incoterm:" if not is_hebrew else "תנאי סחר (Incoterm):",
    "currency_label": "Dashboard Main Currency:" if not is_hebrew else "מטבע הצגה ראשי בדשבורד:",
    "rates_header": "Exchange Rates (USD Base)" if not is_hebrew else "שערי המרה (בסיס USD)",
    "tab1": "📋 Cargo & Destination" if not is_hebrew else "📋 פרטי מטען, נמלים ויעד",
    "tab2": "⚓ Shipping, BAF & THC" if not is_hebrew else "⚓ ספנות, BAF ותעריפי נמלים",
    "tab3": "📦 Storage & Drayage" if not is_hebrew else "📦 אחסנה, השהיות ו-Last Mile",
    "tab4": "⚖️ Customs & Regulation" if not is_hebrew else "⚖️ מכס, מיסים ורגולציה",
    "tab5_eu": "🗺️ Route Optimization" if not is_hebrew else "🗺️ ניתוח מסלולי נמלים באירופה",
    "tab_summary": "📊 Landed Cost Summary" if not is_hebrew else "📊 Landed Cost & Summary",
    "cargo_type": "Cargo Type:" if not is_hebrew else "סוג ציוד:",
    "bess_capacity": "Total Project BESS Capacity (MWh):" if not is_hebrew else "קיבולת אגירה כוללת של הפרויקט (MWh):",
    "container_cnt": "Container / Unit Count:" if not is_hebrew else "כמות מכולות / יחידות:",
    "exw_val": "EXW Equipment Value (USD):" if not is_hebrew else "ערך ציוד בבית המפעל בסין (EXW USD):",
    "origin_port": "Port of Loading (China):" if not is_hebrew else "נמל מוצא (סין):",
    "dest_port": "Port of Discharge:" if not is_hebrew else "נמל יעד ימי (Port of Discharge):",
    "dest_country": "Final Project Country:" if not is_hebrew else "מדינת יעד סופית (אתר הפרויקט):",
    "site_address": "Project Site Location / Region:" if not is_hebrew else "כתובת / אזור אתר הפרויקט במדינה:",
    "inland_drayage": "Inland Drayage to Site per Container ($):" if not is_hebrew else "שינוע יבשתי מנמל היעד לאתר הפרויקט ($ למכולה):",
}

st.title(T["title"])
st.caption(T["caption"])

# ---------------------------------------------------------
# טבלאות נתונים
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

DEFAULT_INSURANCE_RATES = {"Israel": 0.08, "Romania": 0.15, "Germany": 0.15, "Spain": 0.15, "Italy": 0.15, "Greece": 0.15, "Poland": 0.15, "Other / Custom": 0.15}
DEFAULT_FREE_DAYS = {"Israel": 4, "Romania": 7, "Germany": 7, "Spain": 7, "Italy": 7, "Greece": 7, "Poland": 7, "Other / Custom": 7}
CARRIER_FUEL_SURCHARGES = {
    "ZIM (Integrated Shipping)": {"baf": 843.0, "code": "NBF / EFS"},
    "Hapag-Lloyd": {"baf": 780.0, "code": "MFR / EFS"},
    "COSCO Shipping": {"baf": 720.0, "code": "FAF / Bunker"},
    "MSC": {"baf": 750.0, "code": "BRS / BAF"},
    "Maersk": {"baf": 760.0, "code": "EFF / BAF"},
    "Custom Carrier": {"baf": 450.0, "code": "Custom BAF"}
}

# ---------------------------------------------------------
# סרגל צד: תרחיש ומטבע
# ---------------------------------------------------------
st.sidebar.subheader(T["scenario_header"])
incoterm = st.sidebar.selectbox(T["incoterm_label"], ["DDP (Delivered Duty Paid)", "CIF (Cost, Insurance & Freight)", "FOB (Free on Board)"])
display_currency = st.sidebar.selectbox(T["currency_label"], ["USD ($)", "EUR (€)", "ILS (₪)"])

st.sidebar.subheader(T["rates_header"])
usd_to_eur = st.sidebar.number_input("USD to EUR Rate:", value=0.92, step=0.01)
usd_to_ils = st.sidebar.number_input("USD to ILS Rate:", value=3.70, step=0.01)

def convert_from_usd(amount_usd, target_curr):
    if target_curr == "USD ($)": return amount_usd, "$"
    if target_curr == "EUR (€)": return amount_usd * usd_to_eur, "€"
    if target_curr == "ILS (₪)": return amount_usd * usd_to_ils, "₪"
    return amount_usd, "$"

st.sidebar.markdown("---")
dest_country = st.sidebar.selectbox(T["dest_country"], list(VAT_RATES.keys()), index=0)

# בדיקה אם היעד אינו ישראל לצורך הצגת לשונית אופטימיזציית מסלולים
show_route_optimization = (dest_country != "Israel")

# יצירת הלשוניות באופן דינמי
if show_route_optimization:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab5_eu"], T["tab_summary"]])
else:
    tab1, tab2, tab3, tab4, tab6 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab_summary"]])

# ----- T1: פרטי מטען ויעד -----
with tab1:
    st.subheader("Equipment Specification & Destination" if not is_hebrew else "מפרט הציוד, נמלי מוצא/יעד ומדינת היעד")
    col1, col2 = st.columns(2)
    
    with col1:
        origin_port = st.selectbox(T["origin_port"], ["Shanghai", "Ningbo", "Shenzhen / Yantian", "Guangzhou / Nansha", "Custom Origin Port"])
        
        if dest_country == "Israel":
            dest_port = st.selectbox(T["dest_port"], ["Haifa / Ashdod, Israel", "Custom Destination Port"])
            site_address = st.text_input(T["site_address"], value="Negev / Galilee Region" if not is_hebrew else "אזור הנגב / גליל")
        else:
            dest_port = st.selectbox(T["dest_port"], [
                "Burgas, Bulgaria (Burgas Transit to Romania)", 
                "Constanța, Romania", 
                "Piraeus / Thessaloniki, Greece", 
                "Hamburg / Rotterdam, North Europe", 
                "Custom Destination Port"
            ])
            site_address = st.text_input(T["site_address"], value="Iepurești / Ghimpați Site, Giurgiu County, Romania")
            
        applied_vat = st.number_input(f"VAT Rate ({dest_country}) %:", value=float(VAT_RATES[dest_country]), step=0.5)

    with col2:
        cargo_type = st.selectbox(T["cargo_type"], list(CUSTOMS_DUTIES["EU"].keys()))
        container_count = st.number_input(T["container_cnt"], min_value=1, value=10, step=1)
        bess_mwh = st.number_input(T["bess_capacity"], value=40.0, step=5.0)
        
        if cargo_type == "BESS Container (UN3536 Class 9)":
            weight_tier = st.selectbox("Weight Tier (MTS / Ton):" if not is_hebrew else "מדרגת משקל ליחידת BESS (MTS / Ton):", [
                "Below 27 MTS ($6,300)", "27.0 - 34.9 MTS ($12,600)", "35.0 - 44.9 MTS ($18,375)", "45.0 - 48.0 MTS ($21,000)"
            ], index=3)
            suggested_freight = 6300.0 if "Below 27" in weight_tier else (12600.0 if "27.0" in weight_tier else (18375.0 if "35.0" in weight_tier else 21000.0))
        else:
            suggested_freight = 3360.0

        is_dg = st.checkbox("Dangerous Goods (DG Class 9)" if not is_hebrew else "מטען חומ\"ס (DG Class 9)", value=True if "BESS" in cargo_type else False)
        exw_value_usd = st.number_input(T["exw_val"], value=500000.0, step=10000.0)

# ----- T2: ספנות, BAF ותעריפי נמלים -----
with tab2:
    st.subheader("Carrier Selection, Port THC & Insurance" if not is_hebrew else "בחירת חברת ספנות, תעריפי נמלים (Origin/Dest THC) וביטוח")
    col_a, col_b = st.columns(2)
    with col_a:
        selected_carrier = st.selectbox("Shipping Carrier:" if not is_hebrew else "חברת ספנות מובילה:", list(CARRIER_FUEL_SURCHARGES.keys()), index=0)
        base_freight_per_unit = st.number_input("Base Ocean Freight per Container ($):" if not is_hebrew else "מחיר הובלה ימית בסיס ליחידה ($):", value=float(suggested_freight) if incoterm != "FOB (Free on Board)" else 0.0, step=500.0, disabled=(incoterm == "FOB (Free on Board)"))
        baf_surcharge = st.number_input(f"Bunker Surcharge ({CARRIER_FUEL_SURCHARGES[selected_carrier]['code']}) ($):", value=float(CARRIER_FUEL_SURCHARGES[selected_carrier]["baf"]) if incoterm != "FOB (Free on Board)" else 0.0, step=50.0, disabled=(incoterm == "FOB (Free on Board)"))
        dest_thc_port_fee = st.number_input("Destination THC / Port Fee per Container ($):" if not is_hebrew else "אגרות ותעריפי נמל יעד (Destination THC / Wharfage) ליחידה ($):", value=380.0 if incoterm != "FOB (Free on Board)" else 0.0, step=20.0)
        
    with col_b:
        china_inland_drayage = st.number_input("China Inland Transport + Export Customs ($):" if not is_hebrew else "הובלה פנימית בסין + עמילות יצוא ואישורי חומ\"ס (USD סה\"כ):", value=2200.0, step=300.0)
        china_origin_thc = st.number_input("China Origin THC & Port Fees ($):" if not is_hebrew else "אגרות ותעריפי נמל מוצא בסין (Origin THC & Port Fees סה\"כ):", value=1300.0, step=200.0)
        heavy_lift_survey = st.number_input("Heavy Lift / Route Survey ($):" if not is_hebrew else "סקר הנדסי / היטל הובלה חריגה פרויקטלית ($ סה\"כ):", value=2500.0 if incoterm != "FOB (Free on Board)" else 0.0, step=500.0)
        
        region_key = "Israel" if dest_country == "Israel" else "EU"
        customs_duty_pct = st.number_input("Import Customs Duty (%):" if not is_hebrew else "שיעור מכס / מיסי יבוא (%):", value=float(CUSTOMS_DUTIES[region_key][cargo_type]["duty_pct"]), step=0.1)
        insurance_pct = st.number_input("Marine Insurance (% of CIF):" if not is_hebrew else "פרמיית ביטוח ימי (% מערך ה-CIF):", value=DEFAULT_INSURANCE_RATES.get(dest_country, 0.15) if incoterm != "FOB (Free on Board)" else 0.0, step=0.01)

    china_first_mile_total = china_inland_drayage + china_origin_thc
    total_freight_usd = (base_freight_per_unit + baf_surcharge + dest_thc_port_fee) * float(container_count) + heavy_lift_survey if incoterm != "FOB (Free on Board)" else 0.0

# ----- T3: אחסנה ו-Drayage -----
with tab3:
    st.subheader("Port Demurrage, Storage & Site Drayage" if not is_hebrew else "אחסנה חיצונית, השהיות והובלת DDP לאתר (Cross-Border / Last Mile Drayage)")
    col_x, col_y = st.columns(2)
    with col_x:
        free_days = st.number_input("Port Free Days:" if not is_hebrew else "ימים חופשיים בנמל (Free Days):", value=DEFAULT_FREE_DAYS.get(dest_country, 7), step=1, help="In Israel standard free days are 4" if not is_hebrew else "בישראל מוגדרים 4 ימים חופשיים מול הנמלים")
        actual_port_days = st.number_input("Actual Port Dwell Days:" if not is_hebrew else "ימי אחסנה בפועל בנמל:", value=12, step=1)
        demurrage_daily_rate = st.number_input("Daily Demurrage Rate per DG Container ($):" if not is_hebrew else "קנס השהיה יומי ממוצע למכולת חומ\"ס ($):", value=250.0 if is_dg else 150.0, step=10.0)
        
    with col_y:
        use_external_storage = st.checkbox("External Staging Yard" if not is_hebrew else "שימוש בחצר אחסנה חיצונית / שטח היערכות פרויקטלי", value=True)
        ext_storage_daily_rate = st.number_input("External Storage Daily Rate ($):" if not is_hebrew else "עלות אחסנה יומית בחצר חיצונית למכולה ($):", value=65.0 if is_dg else 45.0, step=5.0)
        default_cross_border_drayage = 1850.0 if "Burgas" in dest_port else (850.0 if suggested_freight == 21000.0 else 600.0)
        ext_drayage_cost = st.number_input(T["inland_drayage"], value=default_cross_border_drayage, step=50.0, help="הובלה יבשתית מנמל הפריקה עד לאתר הפרויקט")

    st.markdown("---")
    col_ddp1, col_ddp2 = st.columns(2)
    with col_ddp1:
        site_crane_unloading = st.number_input("Site Crane & Pad Offloading ($):" if not is_hebrew else "מנוף פריקה כבד באתר + הצבה על משטחי בטון ($ סה\"כ):", value=8500.0 if incoterm == "DDP (Delivered Duty Paid)" else 0.0, step=500.0, disabled=(incoterm != "DDP (Delivered Duty Paid)"))
    with col_ddp2:
        ddp_contingency_pct = st.number_input("DDP Risk Contingency (%):" if not is_hebrew else "מקדם סיכון ובלתי מתוכנן DDP (%):", value=5.0 if incoterm == "DDP (Delivered Duty Paid)" else 0.0, step=1.0, disabled=(incoterm != "DDP (Delivered Duty Paid)"))

    overdue_days = max(0, actual_port_days - free_days)
    demurrage_total_usd = float(overdue_days) * demurrage_daily_rate * float(container_count)
    ext_storage_total_usd = ((float(actual_port_days) * ext_storage_daily_rate * float(container_count)) + (ext_drayage_cost * float(container_count))) if use_external_storage else 0.0

# ----- T4: מכס ורגולציה -----
with tab4:
    if dest_country == "Israel":
        st.subheader("🇮🇱 Customs, Taxes & Permits in Israel" if not is_hebrew else "🇮🇱 מכס, מיסים ורגולציה בישראל")
        col_il1, col_il2 = st.columns(2)
        with col_il1:
            st.markdown(f"**HS Code (Israel):** `{CUSTOMS_DUTIES['Israel'][cargo_type]['hs_code']}`")
            st.markdown(f"**Customs Duty:** `0.0%` (Exempt)")
            st.markdown(f"**Import VAT:** `{applied_vat}%`")
            st.markdown(f"**Site Location:** `{site_address}`")
        with col_il2:
            epr_fee_per_unit = st.number_input("Environmental / Battery Fee ($):" if not is_hebrew else "אגרת איכות הסביבה / טיפול בסוללות ליחידה ($):", value=200.0 if "BESS" in cargo_type else 50.0, step=50.0)
            local_regulatory_permits = st.number_input("Poisons Permit & Fire Inspection ($):" if not is_hebrew else "אישורי היתר רעלים, סוקר חומ\"ס ואישורי כיבוי ($ סה\"כ):", value=1500.0 if is_dg else 400.0, step=100.0)
    else:
        st.subheader("🇪🇺 EU Customs & TARIC Live Lookup" if not is_hebrew else "🇪🇺 מכס באירופה, בדיקת TARIC בלייב ורגולציה")
        hs_code_eu = CUSTOMS_DUTIES["EU"][cargo_type]["hs_code"]
        taric_url = f"https://ec.europa.eu/taxation_customs/dds2/taric/taric_consultation.jsp?Lang=en&SimDate=20260825&Taric={hs_code_eu}"
        col_eu1, col_eu2 = st.columns(2)
        with col_eu1:
            st.markdown(f"**HS Code:** `{hs_code_eu}`")
            st.markdown(f"**EU Duty Rate:** `{CUSTOMS_DUTIES['EU'][cargo_type]['duty_pct']}%`")
            st.markdown(f"**Project Site:** `{site_address}`")
            st.link_button("🔗 Open Official EU TARIC Database" if not is_hebrew else "🔗 פתח בדיקת מכס רשמית ב-EU TARIC Database", taric_url)
        with col_eu2:
            epr_fee_per_unit = st.number_input("EPR / EoL Recycling Fee ($):" if not is_hebrew else "אגרת מיחזור סוללות / אחריות יצרן מורחבת (EPR / EoL Fee) ליחידה ($):", value=450.0 if "BESS" in cargo_type else 80.0, step=50.0)
            local_regulatory_permits = st.number_input("Local Permits / DG Approvals ($):" if not is_hebrew else "אישורים רגולטוריים / היתרי חומ\"ס מקומיים ($ סה\"כ):", value=1200.0 if is_dg else 300.0, step=100.0)

    epr_total_usd = (epr_fee_per_unit * float(container_count)) + local_regulatory_permits

# ----- T5: ניתוח מסלולים באירופה (מוצג רק כשהיעד אינו ישראל) -----
if show_route_optimization:
    with tab5:
        st.subheader(f"🗺️ Port Route Optimization ({dest_country} Projects)" if not is_hebrew else f"🗺️ ניתוח השוואתי: מסלולי נמלים עבור אתר הפרויקט: {site_address}")
        st.caption(f"Route comparison derived for project site location: {site_address}" if not is_hebrew else f"השוואת מסלולי נמלים מותאמת למיקום האתר: {site_address}")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("### 🇧🇬 Route A: via Burgas Port (Bulgaria)")
            st.markdown("* **Ocean Freight:** ~$18,375 / unit")
            st.markdown(f"* **Cross-Border Drayage to {site_address}:** ~$1,850 / container")
            st.markdown("* **Key Advantage:** Fast DG Class 9 port clearance, lower congestion")
        with col_r2:
            st.markdown("### 🇷🇴 Route B: via Constanța Port (Romania)")
            st.markdown("* **Ocean Freight:** ~$19,500 / unit")
            st.markdown(f"* **Inland Drayage to {site_address}:** ~$850 / container")
            st.markdown("* **Key Advantage:** Direct discharge in destination country, no customs transit border cross")

# ----- חישובים מסכמים -----
cif_value_usd = exw_value_usd + china_first_mile_total + total_freight_usd
insurance_total_usd = (cif_value_usd * (insurance_pct / 100.0))
customs_duty_usd = ((cif_value_usd + total_freight_usd) * (customs_duty_pct / 100.0))
vat_total_usd = ((cif_value_usd + total_freight_usd + customs_duty_usd) * (applied_vat / 100.0))

subtotal_ddp = cif_value_usd + insurance_total_usd + customs_duty_usd + demurrage_total_usd + ext_storage_total_usd + site_crane_unloading + epr_total_usd
contingency_usd = subtotal_ddp * (ddp_contingency_pct / 100.0)
total_landed_usd = subtotal_ddp + contingency_usd

total_kwh = bess_mwh * 1000.0 if bess_mwh > 0 else 1.0
logistics_only_usd = total_freight_usd + demurrage_total_usd + ext_storage_total_usd + site_crane_unloading + epr_total_usd
cost_per_kwh_usd = logistics_only_usd / total_kwh

display_val, curr_symbol = convert_from_usd(total_landed_usd, display_currency)
freight_display, _ = convert_from_usd(total_freight_usd, display_currency)
customs_display, _ = convert_from_usd(customs_duty_usd, display_currency)
storage_display, _ = convert_from_usd(demurrage_total_usd + ext_storage_total_usd, display_currency)
kwh_cost_display, _ = convert_from_usd(cost_per_kwh_usd, display_currency)

# ----- T Summary -----
with (tab6 if show_route_optimization else tab6):
    st.subheader(f"📊 Summary Dashboard - {incoterm} ({display_currency})")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Landed Cost", f"{curr_symbol} {display_val:,.2f}")
    m2.metric("Ocean Freight & THC", f"{curr_symbol} {freight_display:,.2f}")
    m3.metric("Customs & Duty", f"{curr_symbol} {customs_display:,.2f}")
    m4.metric("Storage & Drayage", f"{curr_symbol} {storage_display:,.2f}")
    m5.metric("Logistics Cost / kWh", f"{curr_symbol} {kwh_cost_display:.4f} /kWh")
    
    st.markdown("---")
    st.subheader("Detailed Cost Breakdown (USD Base)" if not is_hebrew else "פילוח עלויות מפורט (USD Base)")
    
    df_summary = pd.DataFrame({
        "Cost Component" if not is_hebrew else "רכיב עלות": [
            "Equipment Value (EXW)", "China Inland Transport & Export", "China Origin THC & Port Fees", 
            f"Ocean Freight + BAF + Dest THC ({selected_carrier}) [{dest_port}]", "Route Survey / Heavy Lift", 
            "Marine Insurance", "Import Customs Duty", "EPR & Environmental Recycling", 
            "Port Demurrage Charges", "Inland Drayage to Site", "Site Crane & Pad Offloading", 
            "DDP Risk Contingency", "Import VAT (Claimable)"
        ],
        "Amount (USD)": [
            exw_value_usd, china_inland_drayage, china_origin_thc, 
            (base_freight_per_unit + baf_surcharge + dest_thc_port_fee) * float(container_count) if incoterm != "FOB (Free on Board)" else 0.0, 
            heavy_lift_survey, insurance_total_usd, customs_duty_usd, epr_total_usd, demurrage_total_usd, 
            ext_storage_total_usd, site_crane_unloading, contingency_usd, vat_total_usd
        ]
    })
    
    df_summary["% of Total Cost"] = (df_summary["Amount (USD)"] / total_landed_usd) * 100.0
    df_summary["% of Total Cost"] = df_summary["% of Total Cost"].map("{:.2f}%".format)
    st.dataframe(df_summary, use_container_width=True)
    
    st.markdown("---")
    csv_data = df_summary.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Export Full Cost Breakdown Report (CSV/Excel)" if not is_hebrew else "📥 הורד דוח ניתוח עלויות מלא (CSV/Excel)",
        data=csv_data,
        file_name=f"Landed_Cost_Report_{incoterm.split(' ')[0]}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Developed for Renewable Energy Infrastructure & Storage Projects.")
