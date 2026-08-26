import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# הגדרת תצורת עמוד ושפה
# ---------------------------------------------------------
st.set_page_config(
    page_title="BESS Logistics & Landed Cost Control Tower",
    page_icon="⚡",
    layout="wide"
)

# מתג שפה בסרגל הצד
st.sidebar.header("🌐 Language / שפה")
lang = st.sidebar.radio("Select Language / בחר שפה:", ["Hebrew (עברית)", "English"], index=0)
is_hebrew = (lang == "Hebrew (עברית)")

# מילון מונחים דו-לשוני מקיף
T = {
    "title": "⚡ BESS Logistics & Landed Cost Control Tower",
    "caption": "Enterprise Project Cargo Calculator incorporating Full Supply Chain Costs, Incoterms, and Tax Bases" if not is_hebrew else "מחשבון פרויקטלי ארגוני לניהול עלויות יעד, שרשרת אספקה מלאה, Incoterms ובסיסי מס",
    "scenario_header": "🗂️ Scenario & Incoterm Setup" if not is_hebrew else "🗂️ הגדרות תרחיש ותנאי סחר (Incoterms)",
    "incoterm_label": "Commercial Incoterm (Supplier Scope):" if not is_hebrew else "תנאי סחר מסחרי (אחריות ספק):",
    "currency_label": "Dashboard Main Currency:" if not is_hebrew else "מטבע הצגה ראשי בדשבורד:",
    "tab1": "📋 Cargo & Destination" if not is_hebrew else "📋 פרטי מטען, יעד ומיקום",
    "tab2": "⚓ Supply Chain & Incoterms" if not is_hebrew else "⚓ שרשרת אספקה ותנאי סחר",
    "tab3": "📦 Storage & Site Drayage" if not is_hebrew else "📦 אחסנה, השהיות והובלת אתר",
    "tab4": "⚖️ Customs & Regulation" if not is_hebrew else "⚖️ מכס, מיסים ורגולציה",
    "tab5_eu": "🗺️ Route Optimization" if not is_hebrew else "🗺️ ניתוח מסלולים באירופה",
    "tab_summary": "📊 Financial Control Summary" if not is_hebrew else "📊 דוח בקרה פיננסית וסיכום",
    "cargo_type": "Cargo Type / Equipment:" if not is_hebrew else "סוג ציוד / מערכת אגירה:",
    "bess_capacity": "Total Project Capacity (MWh):" if not is_hebrew else "קיבולת אגירה כוללת לפרויקט (MWh):",
    "container_cnt": "Container / Unit Count:" if not is_hebrew else "כמות מכולות / יחידות פרויקט:",
    "exw_val": "EXW Equipment Value (USD):" if not is_hebrew else "ערך ציוד בבית המפעל בסין (EXW USD):",
    "origin_port": "Port of Loading (China):" if not is_hebrew else "נמל מוצא (סין):",
    "dest_port": "Port of Discharge:" if not is_hebrew else "נמל יעד ימי (Port of Discharge):",
    "dest_country": "Final Project Country:" if not is_hebrew else "מדינת יעד סופית (אתר הפרויקט):",
    "site_address": "Project Site Name / Location:" if not is_hebrew else "שם / מיקום אתר הפרויקט:",
    "site_coords": "GPS Coordinates (Lat, Long):" if not is_hebrew else "קואורדינטות GPS (רוחב, אורך):",
    "site_zip": "Postal / Zip Code:" if not is_hebrew else "מיקוד / קוד דואר:",
}

st.title(T["title"])
st.caption(T["caption"])

# ---------------------------------------------------------
# נתונים ופרמטרים רגולטוריים
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
incoterm = st.sidebar.selectbox(T["incoterm_label"], ["DDP (Delivered Duty Paid)", "CIF (Cost, Insurance & Freight)", "FOB (Free on Board)", "EXW (Ex Works)"])
display_currency = st.sidebar.selectbox(T["currency_label"], ["USD ($)", "EUR (€)", "ILS (₪)"])

usd_to_eur = st.sidebar.number_input("USD to EUR Rate:", value=0.92, step=0.01)
usd_to_ils = st.sidebar.number_input("USD to ILS Rate:", value=3.70, step=0.01)

def convert_from_usd(amount_usd, target_curr):
    if target_curr == "USD ($)": return amount_usd, "$"
    if target_curr == "EUR (€)": return amount_usd * usd_to_eur, "€"
    if target_curr == "ILS (₪)": return amount_usd * usd_to_ils, "₪"
    return amount_usd, "$"

st.sidebar.markdown("---")
dest_country = st.sidebar.selectbox(T["dest_country"], list(VAT_RATES.keys()), index=0)

if 'last_country' not in st.session_state:
    st.session_state.last_country = dest_country

if st.session_state.last_country != dest_country:
    st.session_state.last_country = dest_country
    st.session_state.site_name_input = ""
    st.session_state.site_coords_input = ""
    st.session_state.site_zip_input = ""

show_route_optimization = (dest_country != "Israel")

if show_route_optimization:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab5_eu"], T["tab_summary"]])
else:
    tab1, tab2, tab3, tab4, tab6 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab_summary"]])

# ----- T1: פרטי מטען ויעד -----
with tab1:
    st.subheader("Equipment Specification & Site Destination" if not is_hebrew else "מפרט ציוד, מאפייני פרויקט ומיקום אתר")
    col1, col2 = st.columns(2)
    
    with col1:
        origin_port = st.selectbox(T["origin_port"], ["Shanghai", "Ningbo", "Shenzhen / Yantian", "Guangzhou / Nansha", "Custom Origin Port"])
        
        if dest_country == "Israel":
            dest_port = st.selectbox(T["dest_port"], ["Haifa / Ashdod, Israel", "Custom Destination Port"])
        else:
            dest_port = st.selectbox(T["dest_port"], [
                "Burgas, Bulgaria (Burgas Transit to Romania)", 
                "Constanța, Romania", 
                "Piraeus / Thessaloniki, Greece", 
                "Hamburg / Rotterdam, North Europe", 
                "Custom Destination Port"
            ])

        site_address = st.text_input(T["site_address"], key="site_name_input", placeholder="e.g. Ashalim / Iepurești")
        
        sub_col_a, sub_col_b = st.columns(2)
        with sub_col_a:
            site_coords = st.text_input(T["site_coords"], key="site_coords_input", placeholder="Lat, Long")
        with sub_col_b:
            site_zip = st.text_input(T["site_zip"], key="site_zip_input", placeholder="Postal Code")

        applied_vat = st.number_input(f"VAT Rate ({dest_country}) %:", value=float(VAT_RATES[dest_country]), step=0.5)

    with col2:
        cargo_type = st.selectbox(T["cargo_type"], list(CUSTOMS_DUTIES["EU"].keys()))
        container_count = st.number_input(T["container_cnt"], min_value=1, value=10, step=1)
        bess_mwh = st.number_input(T["bess_capacity"], value=40.0, step=5.0)
        
        if container_count > 0:
            mwh_per_unit = bess_mwh / container_count
            if mwh_per_unit > 8.0:
                st.warning(f"⚠️ High capacity per unit ({mwh_per_unit:.2f} MWh/container). Please verify container count vs total MWh." if not is_hebrew else f"⚠️ קיבולת גבוהה יחסית ליחידה ({mwh_per_unit:.2f} MWh למכולה). מומלץ לוודא את נתוני התכנון.")

        if cargo_type == "BESS Container (UN3536 Class 9)":
            weight_tier = st.selectbox("Weight Tier (MTS / Ton):" if not is_hebrew else "מדרגת משקל ליחידת BESS (MTS / Ton):", [
                "Below 27 MTS ($6,300)", "27.0 - 34.9 MTS ($12,600)", "35.0 - 44.9 MTS ($18,375)", "45.0 - 48.0 MTS ($21,000)"
            ], index=3)
            suggested_freight = 6300.0 if "Below 27" in weight_tier else (12600.0 if "27.0" in weight_tier else (18375.0 if "35.0" in weight_tier else 21000.0))
        else:
            suggested_freight = 3360.0

        is_dg = st.checkbox("Dangerous Goods (DG Class 9)" if not is_hebrew else "מטען חומ\"ס (DG Class 9)", value=True if "BESS" in cargo_type else False)
        exw_value_usd = st.number_input(T["exw_val"], value=500000.0, step=10000.0)

# ----- T2: שרשרת אספקה ותנאי סחר (הפרדת Supplier Price מ-Buyer Landed Cost) -----
with tab2:
    st.subheader("Full Supply Chain & Incoterms Allocation" if not is_hebrew else "שרשרת אספקה מלאה והקצאת עלויות לפי Incoterms")
    st.info(f"💡 Current commercial Incoterm: **{incoterm}**. This defines the seller's price scope, while the buyer's Landed Cost includes the full end-to-end chain." if not is_hebrew else f"💡 תנאי הסחר המסחרי: **{incoterm}**. הגדרה זו קובעת את מחיר הספק, בעוד עלות היעד הכוללת (Landed Cost) משקללת את כל שרשרת האספקה עד לאתר.")

    col_a, col_b = st.columns(2)
    with col_a:
        selected_carrier = st.selectbox("Shipping Carrier:" if not is_hebrew else "חברת ספנות מובילה:", list(CARRIER_FUEL_SURCHARGES.keys()), index=0)
        base_freight_per_unit = st.number_input("Base Ocean Freight per Container ($):" if not is_hebrew else "מחיר הובלה ימית בסיס ליחידה ($):", value=float(suggested_freight), step=500.0)
        baf_surcharge = st.number_input(f"Bunker Surcharge ({CARRIER_FUEL_SURCHARGES[selected_carrier]['code']}) ($):", value=float(CARRIER_FUEL_SURCHARGES[selected_carrier]["baf"]), step=50.0)
        dest_thc_port_fee = st.number_input("Destination THC / Port Fee per Container ($):" if not is_hebrew else "אגרות ותעריפי נמל יעד (Destination THC / Wharfage) ליחידה ($):", value=380.0, step=20.0)
        
    with col_b:
        china_inland_drayage = st.number_input("China Inland Transport + Export Customs ($):" if not is_hebrew else "הובלה פנימית בסין + עמילות יצוא (USD סה\"כ):", value=2200.0, step=300.0)
        china_origin_thc = st.number_input("China Origin THC & Port Fees ($):" if not is_hebrew else "אגרות ותעריפי נמל מוצא בסין (Origin THC סה\"כ):", value=1300.0, step=200.0)
        heavy_lift_survey = st.number_input("Heavy Lift / Route Survey ($):" if not is_hebrew else "סקר הנדסי / היטל הובלה חריגה פרויקטלית ($ סה\"כ):", value=2500.0, step=500.0)
        
        region_key = "Israel" if dest_country == "Israel" else "EU"
        customs_duty_pct = st.number_input("Indicative Import Customs Duty (%):" if not is_hebrew else "שיעור מכס אינדיקטיבי (%):", value=float(CUSTOMS_DUTIES[region_key][cargo_type]["duty_pct"]), step=0.1)
        insurance_pct = st.number_input("Marine Insurance (% of CIF base):" if not is_hebrew else "פרמיית ביטוח ימי (% מערך ה-CIF):", value=DEFAULT_INSURANCE_RATES.get(dest_country, 0.15), step=0.01)

    # חישוב רכיבי השרשרת המלאים
    full_supply_chain = {
        "equipment": exw_value_usd,
        "china_inland": china_inland_drayage,
        "origin_thc": china_origin_thc,
        "ocean_freight": base_freight_per_unit * float(container_count),
        "baf": baf_surcharge * float(container_count),
        "destination_thc": dest_thc_port_fee * float(container_count),
        "heavy_lift": heavy_lift_survey
    }
    
    total_ocean_freight = full_supply_chain["ocean_freight"] + full_supply_chain["baf"]

    # מטריצת אחריות ספק לפי Incoterm
    supplier_included_scope = {
        "EXW (Ex Works)": ["equipment"],
        "FOB (Free on Board)": ["equipment", "china_inland", "origin_thc"],
        "CIF (Cost, Insurance & Freight)": ["equipment", "china_inland", "origin_thc", "ocean_freight", "baf"],
        "DDP (Delivered Duty Paid)": list(full_supply_chain.keys()) + ["destination_thc", "heavy_lift"]
    }

    current_scope = supplier_included_scope.get(incoterm, ["equipment"])
    supplier_commercial_price = sum(full_supply_chain[k] for k in current_scope if k in full_supply_chain)

# ----- T3: אחסנה והובלה יבשתית (הפרדה מלאה) -----
with tab3:
    st.subheader("Port Demurrage, Storage & Inland Drayage" if not is_hebrew else "קנסות נמל, אחסנה חיצונית והובלה יבשתית לאתר")
    col_x, col_y = st.columns(2)
    with col_x:
        free_days = st.number_input("Port Free Days:" if not is_hebrew else "ימים חופשיים בנמל (Free Days):", value=DEFAULT_FREE_DAYS.get(dest_country, 7), step=1)
        actual_port_days = st.number_input("Actual Port Dwell Days:" if not is_hebrew else "ימי אחסנה בפועל בנמל:", value=12, step=1)
        demurrage_daily_rate = st.number_input("Daily Demurrage Rate per DG Container ($):" if not is_hebrew else "קנס השהיה יומי ממוצע למכולת חומ\"ס ($):", value=250.0 if is_dg else 150.0, step=10.0)
        
    with col_y:
        use_external_storage = st.checkbox("External Staging Yard" if not is_hebrew else "שימוש בחצר אחסנה חיצונית / שטח היערכות", value=True)
        ext_storage_days = st.number_input("External Storage Days:" if not is_hebrew else "ימי אחסנה בפועל בחצר החיצונית:", value=15, step=1)
        ext_storage_daily_rate = st.number_input("External Storage Daily Rate ($):" if not is_hebrew else "עלות אחסנה יומית בחצר החיצונית למכולה ($):", value=65.0 if is_dg else 45.0, step=5.0)
        
        default_drayage = 1850.0 if "Burgas" in dest_port else 600.0
        inland_drayage_per_unit = st.number_input("Inland Drayage from Port to Site ($ per container):" if not is_hebrew else "הובלה יבשתית מהנמל לאתר הפרויקט ($ למכולה):", value=default_drayage, step=50.0)

    st.markdown("---")
    col_ddp1, col_ddp2 = st.columns(2)
    with col_ddp1:
        site_crane_unloading = st.number_input("Site Crane & Pad Offloading ($):" if not is_hebrew else "מנוף פריקה כבד באתר + הצבה ($ סה\"כ):", value=8500.0, step=500.0)
    with col_ddp2:
        ddp_contingency_pct = st.number_input("Project Risk Contingency (%):" if not is_hebrew else "מקדם סיכון ובלתי מתוכנן פרויקטלי (%):", value=5.0, step=1.0)

    overdue_days = max(0, actual_port_days - free_days)
    demurrage_total_usd = float(overdue_days) * demurrage_daily_rate * float(container_count)
    external_storage_total_usd = (float(ext_storage_days) * ext_storage_daily_rate * float(container_count)) if use_external_storage else 0.0
    inland_drayage_total_usd = inland_drayage_per_unit * float(container_count)

# ----- T4: מכס ורגולציה -----
with tab4:
    display_site = site_address if site_address else ("Unnamed Site" if not is_hebrew else "אתר ללא שם")
    display_coords = site_coords if site_coords else "N/A"
    display_zip = site_zip if site_zip else "N/A"

    if dest_country == "Israel":
        st.subheader("🇮🇱 Customs, Taxes & Permits in Israel" if not is_hebrew else "🇮🇱 מכס, מיסים ורגולציה בישראל")
        col_il1, col_il2 = st.columns(2)
        with col_il1:
            st.markdown(f"**HS Code (Israel):** `{CUSTOMS_DUTIES['Israel'][cargo_type]['hs_code']}`")
            st.markdown(f"**Customs Duty:** `{customs_duty_pct}%` (Indicative rate)")
            st.markdown(f"**Import VAT:** `{applied_vat}%` (Recoverable Cash Item)")
            st.markdown(f"**Site Location:** `{display_site}` (GPS: `{display_coords}`, Zip: `{display_zip}`)")
            st.info("💡 **Regulatory Note (Israel):** Indicative rates only. Must verify exact classification, origin rules, and Poisons Permit requirements with a licensed customs broker." if not is_hebrew else "💡 **הערה רגולטורית (ישראל):** שיעורים אינדיקטיביים בלבד. חובה לאמת פרט מכס, כללי מקור והיתר רעלים מול עמיל מכס מורשה.")

        with col_il2:
            st.markdown("**Local Regulation & Environmental Permits**" if not is_hebrew else "**אישורים ורגולציה מקומית בישראל**")
            epr_fee_per_unit = st.number_input("Environmental / Battery Fee ($):" if not is_hebrew else "אגרת איכות הסביבה / טיפול בסוללות ליחידה ($):", value=200.0 if "BESS" in cargo_type else 50.0, step=50.0)
            local_regulatory_permits = st.number_input("Dangerous Goods (DG) & Hazardous Permits ($):" if not is_hebrew else "אישורי חומ\"ס, היתר רעלים וכיבוי ($ סה\"כ):", value=1500.0 if is_dg else 400.0, step=100.0)
    else:
        st.subheader("🇪🇺 EU Customs & TARIC Lookup" if not is_hebrew else "🇪🇺 מכס באירופה ובדיקת TARIC")
        hs_code_eu = CUSTOMS_DUTIES["EU"][cargo_type]["hs_code"]
        taric_url = f"https://ec.europa.eu/taxation_customs/dds2/taric/taric_consultation.jsp?Lang=en&Taric={hs_code_eu}"
        col_eu1, col_eu2 = st.columns(2)
        with col_eu1:
            st.markdown(f"**HS Code:** `{hs_code_eu}`")
            st.markdown(f"**EU Duty Rate:** `{customs_duty_pct}%` (Indicative)")
            st.markdown(f"**Project Site:** `{display_site}` (GPS: `{display_coords}`, Zip: `{display_zip}`)")
            st.link_button("🔗 Open Official EU TARIC Database (Verify manually)" if not is_hebrew else "🔗 פתח מסד נתונים רשמי EU TARIC (לשם אימות ידני)", taric_url)
        with col_eu2:
            st.markdown("**EPR Fees & Environmental Regulation**" if not is_hebrew else "**אגרות EPR ורגולציה סביבתית**")
            epr_fee_per_unit = st.number_input("EPR / EoL Recycling Fee ($):" if not is_hebrew else "אגרת מיחזור סוללות / אחריות יצרן מורחבת ליחידה ($):", value=450.0 if "BESS" in cargo_type else 80.0, step=50.0)
            local_regulatory_permits = st.number_input("Dangerous Goods (DG) & Hazardous Permits ($):" if not is_hebrew else "אישורים רגולטוריים / היתרי חומ\"ס מקומיים ($ סה\"כ):", value=1200.0 if is_dg else 300.0, step=100.0)

    epr_total_usd = (epr_fee_per_unit * float(container_count)) + local_regulatory_permits

# ----- T5: ניתוח מסלולים באירופה -----
if show_route_optimization:
    with tab5:
        st.subheader(f"🗺️ Illustrative Port Route Comparison ({dest_country})" if not is_hebrew else f"🗺️ ניתוח מסלולים אינדיקטיבי ({dest_country})")
        st.caption(f"Route comparison for site: {display_site}" if not is_hebrew else f"השוואת מסלולים לאתר הפרויקט: {display_site}")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("### 🇧🇬 Route A: via Burgas Port (Bulgaria)")
            st.markdown("* **Ocean Freight:** ~$18,375 / unit")
            st.markdown(f"* **Cross-Border Drayage to {display_site}:** ~$1,850 / container")
            st.markdown("* **Key Advantage:** Fast DG Class 9 port clearance")
        with col_r2:
            st.markdown("### 🇷🇴 Route B: via Constanța Port (Romania)")
            st.markdown("* **Ocean Freight:** ~$19,500 / unit")
            st.markdown(f"* **Inland Drayage to {display_site}:** ~$850 / container")
            st.markdown("* **Key Advantage:** Direct discharge in destination country")

# ----- חישוב פיננסי מדויק (בהתאם להערות קלות') -----
# בסיס הערכת מכס תמיד כולל את כל הוצאות ההובלה והביטוח עד גבול היבוא (ללא תלות ב-Incoterm)
cif_valuation_base = exw_value_usd + china_inland_drayage + china_origin_thc + total_ocean_freight
insurance_total_usd = cif_valuation_base * (insurance_pct / 100.0)

customs_valuation_base_usd = cif_valuation_base + insurance_total_usd
customs_duty_usd = customs_valuation_base_usd * (customs_duty_pct / 100.0)

# בסיס מע"מ יבוא נקי (מכס + ערך סחורה + הובלה ימית + היטלים בנמל)
vat_base_import_usd = customs_valuation_base_usd + customs_duty_usd + (dest_thc_port_fee * float(container_count))
vat_total_usd = vat_base_import_usd * (applied_vat / 100.0)

# סך כל עלויות שרשרת האספקה של הקונה (Buyer Landed Cost)
buyer_supply_chain_total = (
    exw_value_usd
    + china_inland_drayage
    + china_origin_thc
    + total_ocean_freight
    + insurance_total_usd
    + customs_duty_usd
    + (dest_thc_port_fee * float(container_count))
    + demurrage_total_usd
    + external_storage_total_usd
    + inland_drayage_total_usd
    + site_crane_unloading
    + epr_total_usd
    + heavy_lift_survey
)

contingency_usd = buyer_supply_chain_total * (ddp_contingency_pct / 100.0)
total_landed_cost_ex_vat = buyer_supply_chain_total + contingency_usd
total_cash_requirement_incl_vat = total_landed_cost_ex_vat + vat_total_usd

total_kwh = bess_mwh * 1000.0 if bess_mwh > 0 else 1.0
total_supply_chain_cost_per_kwh = total_landed_cost_ex_vat / total_kwh

logistics_only_usd = (
    china_inland_drayage
    + china_origin_thc
    + total_ocean_freight
    + insurance_total_usd
    + (dest_thc_port_fee * float(container_count))
    + inland_drayage_total_usd
    + demurrage_total_usd
    + external_storage_total_usd
    + site_crane_unloading
    + local_regulatory_permits
    + epr_total_usd
    + heavy_lift_survey
)
logistics_cost_per_kwh = logistics_only_usd / total_kwh

# המרות מטבע לתצוגה
display_val, curr_symbol = convert_from_usd(total_landed_cost_ex_vat, display_currency)
supplier_val, _ = convert_from_usd(supplier_commercial_price, display_currency)
cash_val, _ = convert_from_usd(total_cash_requirement_incl_vat, display_currency)
freight_display, _ = convert_from_usd(total_ocean_freight, display_currency)
customs_display, _ = convert_from_usd(customs_duty_usd, display_currency)
kwh_cost_display, _ = convert_from_usd(total_supply_chain_cost_per_kwh, display_currency)

# ----- T Summary -----
with (tab6 if show_route_optimization else tab6):
    st.subheader(f"📊 Financial Control Dashboard - {incoterm} ({display_currency})")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Buyer Landed Cost (ex-VAT)", f"{curr_symbol} {display_val:,.2f}")
    m2.metric("Supplier Price Scope", f"{curr_symbol} {supplier_val:,.2f}", help=f"Based on {incoterm}")
    m3.metric("Total Cash Flow (incl. VAT)", f"{curr_symbol} {cash_val:,.2f}", help="Includes recoverable VAT")
    m4.metric("Customs Duty", f"{curr_symbol} {customs_display:,.2f}")
    m5.metric("Supply Chain Cost / kWh", f"{curr_symbol} {kwh_cost_display:.4f} /kWh")
    
    st.markdown("---")
    st.subheader("Detailed Cost Breakdown (USD Base)" if not is_hebrew else "פילוח עלויות מפורט (USD Base)")
    
    cost_labels = [
        "Equipment Value (EXW)" if not is_hebrew else "ערך ציוד (EXW)",
        "China Inland Transport & Export" if not is_hebrew else "הובלה פנימית בסין + עמילות יצוא",
        "China Origin THC & Port Fees" if not is_hebrew else "אגרות נמל מוצא בסין (Origin THC)",
        f"Ocean Freight + BAF ({selected_carrier})" if not is_hebrew else f"הובלה ימית + BAF ({selected_carrier})",
        "Marine Insurance" if not is_hebrew else "ביטוח ימי",
        "Indicative Import Customs Duty" if not is_hebrew else "מכס יבוא אינדיקטיבי",
        "Destination THC & Wharfage" if not is_hebrew else "אגרות נמל יעד (Dest THC)",
        "EPR & Environmental Recycling" if not is_hebrew else "אגרות EPR ורגולציה סביבתית",
        "Port Demurrage Charges" if not is_hebrew else "קנסות השהיה בנמל (Demurrage)",
        "External Staging Yard Storage" if not is_hebrew else "אחסנה חיצונית בחצר היערכות",
        "Inland Drayage (Port to Site)" if not is_hebrew else "הובלה יבשתית (מהנמל לאתר)",
        "Site Crane & Pad Offloading" if not is_hebrew else "מנוף פריקה והצבה באתר",
        "Project Risk Contingency" if not is_hebrew else "מקדם סיכון ובלתי מתוכנן פרויקטלי",
        "Import VAT (Recoverable Cash Item)" if not is_hebrew else "מע\"מ יבוא (ניתן לקיזוז)"
    ]
    
    df_summary = pd.DataFrame({
        "Cost Component" if not is_hebrew else "רכיב עלות": cost_labels,
        "Amount (USD)": [
            exw_value_usd, china_inland_drayage, china_origin_thc, 
            total_ocean_freight, insurance_total_usd, customs_duty_usd, 
            (dest_thc_port_fee * float(container_count)), epr_total_usd, demurrage_total_usd, 
            external_storage_total_usd, inland_drayage_total_usd, site_crane_unloading, contingency_usd, vat_total_usd
        ]
    })
    
    df_summary["% of Landed Cost ex-VAT"] = (df_summary["Amount (USD)[:-1]"] / total_landed_cost_ex_vat) * 100.0 if len(df_summary) > 0 else 0.0
    # תיקון אחוזי פילוח מול ex-VAT בלבד (הערת קלות')
    amounts_no_vat = [
        exw_value_usd, china_inland_drayage, china_origin_thc, 
        total_ocean_freight, insurance_total_usd, customs_duty_usd, 
        (dest_thc_port_fee * float(container_count)), epr_total_usd, demurrage_total_usd, 
        external_storage_total_usd, inland_drayage_total_usd, site_crane_unloading, contingency_usd
    ]
    df_summary["% of Landed Cost"] = [(amt / total_landed_cost_ex_vat) * 100.0 for amt in amounts_no_vat] + [0.0]
    df_summary["% of Landed Cost"] = df_summary["% of Landed Cost"].map("{:.2f}%".format)
    
    st.dataframe(df_summary, use_container_width=True)
    
    st.markdown("---")
    csv_data = df_summary.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Export Financial Breakdown Report (CSV/Excel)" if not is_hebrew else "📥 הורד דוח פיננסי מלא (CSV/Excel)",
        data=csv_data,
        file_name=f"BESS_Financial_Report_{incoterm.split(' ')[0]}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("BESS Logistics Control Tower — Enterprise Edition.")
