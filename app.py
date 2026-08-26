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

# מילון מונחים דו-לשוני מקיף
T = {
    "title": "⚡ Renewable Energy Logistics & Landed Cost Calculator",
    "caption": "Enterprise Project Cargo Calculator incorporating Supply Chain Costs, Incoterms, DG Compliance, Battery Passports & EPR" if not is_hebrew else "מחשבון פרויקטלי ארגוני לניהול עלויות יעד, Incoterms, רגולציה מלאה, חומ\"ס DG, דרכון סוללה ואחריות סביבתית",
    "scenario_header": "🗂️ Scenario & Incoterm Setup" if not is_hebrew else "🗂️ הגדרות תרחיש ותנאי סחר (Incoterms)",
    "incoterm_label": "Commercial Incoterm (Supplier Scope):" if not is_hebrew else "תנאי סחר מסחרי (אחריות ספק):",
    "currency_label": "Dashboard Main Currency:" if not is_hebrew else "מטבע הצגה ראשי בדשבורד:",
    "tab1": "📋 Cargo & Destination" if not is_hebrew else "📋 פרטי מטען, יעד ומיקום",
    "tab2": "⚓ Supply Chain & Incoterms" if not is_hebrew else "⚓ שרשרת אספקה ותנאי סחר",
    "tab3": "📦 Storage & Site Drayage" if not is_hebrew else "📦 אחסנה, השהיות והובלת אתר",
    "tab4": "⚖️ DG Compliance, Customs & EoL Regulation" if not is_hebrew else "⚖️ רגולציית חומ\"ס DG, מכס, דרכון סוללה וסוף חיים",
    "tab5_eu": "🗺️ Illustrative Route Comparison" if not is_hebrew else "🗺️ השוואת מסלולים אינדיקטיבית",
    "tab_summary": "📊 Financial & Regulatory Summary" if not is_hebrew else "📊 דוח בקרה פיננסית ורגולטורית",
    "cargo_type": "Cargo Type / Equipment:" if not is_hebrew else "סוג ציוד / מערכת אגירה:",
    "bess_capacity": "Total Project Capacity (MWh):" if not is_hebrew else "קיבולת אגירה כוללת לפרויקט (MWh):",
    "container_cnt": "Container Count:" if not is_hebrew else "כמות מכולות:",
    "system_cnt": "BESS System Count:" if not is_hebrew else "כמות מערכות BESS:",
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

usd_to_eur = st.sidebar.number_input("USD to EUR Rate:", value=0.92, step=0.01, min_value=0.0001)
usd_to_ils = st.sidebar.number_input("USD to ILS Rate:", value=3.70, step=0.01, min_value=0.0001)

if usd_to_eur <= 0 or usd_to_ils <= 0:
    st.error("Exchange rates must be greater than zero.")
    st.stop()

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

# =========================================================
# הגדרת ממשק משתמש (קלט הנתונים בכל הלשוניות קודם)
# =========================================================
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

        applied_vat = st.number_input(f"VAT Rate ({dest_country}) %:", value=float(VAT_RATES[dest_country]), step=0.5, min_value=0.0, max_value=100.0)

    with col2:
        cargo_type = st.selectbox(T["cargo_type"], list(CUSTOMS_DUTIES["EU"].keys()))
        
        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            system_count = st.number_input(T["system_cnt"], min_value=1, value=10, step=1)
        with sub_c2:
            container_count = st.number_input(T["container_cnt"], min_value=1, value=10, step=1)

        bess_mwh = st.number_input(T["bess_capacity"], value=40.0, step=5.0, min_value=0.1)
        
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

        un_number = st.selectbox("UN Number (Dangerous Goods Classification):" if not is_hebrew else "מספר UN (סיווג מטען מסוכן):", ["UN3536 (Cargo Transport Unit containing lithium ion batteries)", "UN3480 (Lithium ion batteries)", "UN3481 (Lithium ion batteries packed with equipment)", "Non-DG / Other"])
        is_dg = ("UN3536" in un_number or "UN3480" in un_number or "UN3481" in un_number)

        exw_value_usd = st.number_input(T["exw_val"], value=500000.0, step=10000.0, min_value=0.0)

with tab2:
    st.subheader("Full Supply Chain & Incoterms Allocation" if not is_hebrew else "שרשרת אספקה מלאה והקצאת עלויות לפי Incoterms")
    st.info(f"💡 Current commercial Incoterm: **{incoterm}**. Defines seller's price scope including customs and local delivery under DDP." if not is_hebrew else f"💡 תנאי הסחר המסחרי: **{incoterm}**. מגדיר את היקף מחיר הספק, לרבות מכס והובלה לאתר תחת DDP.")

    col_a, col_b = st.columns(2)
    with col_a:
        selected_carrier = st.selectbox("Shipping Carrier:" if not is_hebrew else "חברת ספנות מובילה:", list(CARRIER_FUEL_SURCHARGES.keys()), index=0)
        base_freight_per_unit = st.number_input("Base Ocean Freight per Container ($):" if not is_hebrew else "מחיר הובלה ימית בסיס ליחידה ($):", value=float(suggested_freight), step=500.0, min_value=0.0)
        baf_surcharge = st.number_input(f"Bunker Surcharge ({CARRIER_FUEL_SURCHARGES[selected_carrier]['code']}) ($):", value=float(CARRIER_FUEL_SURCHARGES[selected_carrier]["baf"]), step=50.0, min_value=0.0)
        dest_thc_port_fee = st.number_input("Destination THC / Port Fee per Container ($):" if not is_hebrew else "אגרות ותעריפי נמל יעד (Destination THC / Wharfage) ליחידה ($):", value=380.0, step=20.0, min_value=0.0)
        
    with col_b:
        china_inland_drayage = st.number_input("China Inland Transport + Export Customs ($):" if not is_hebrew else "הובלה פנימית בסין + עמילות יצוא (USD סה\"כ):", value=2200.0, step=300.0, min_value=0.0)
        china_origin_thc = st.number_input("China Origin THC & Port Fees ($):" if not is_hebrew else "אגרות ותעריפי נמל מוצא בסין (Origin THC סה\"כ):", value=1300.0, step=200.0, min_value=0.0)
        heavy_lift_survey = st.number_input("Heavy Lift / Route Survey ($):" if not is_hebrew else "סקר הנדסי / היטל הובלה חריגה פרויקטלית ($ סה\"כ):", value=2500.0, step=500.0, min_value=0.0)
        
        region_key = "Israel" if dest_country == "Israel" else "EU"
        customs_duty_pct = st.number_input("Indicative Import Customs Duty (%):" if not is_hebrew else "שיעור מכס אינדיקטיבי (%):", value=float(CUSTOMS_DUTIES[region_key][cargo_type]["duty_pct"]), step=0.1, min_value=0.0, max_value=100.0)
        insurance_pct = st.number_input("Marine Insurance (% of CIF base):" if not is_hebrew else "פרמיית ביטוח ימי (% מערך ה-CIF):", value=DEFAULT_INSURANCE_RATES.get(dest_country, 0.15), step=0.01, min_value=0.0)

    supplier_quote_available = st.checkbox("Enter actual supplier commercial quote" if not is_hebrew else "הזן הצעת מחיר מסחרית אמיתית מהספק", value=False)
    if supplier_quote_available:
        supplier_quoted_price = st.number_input("Supplier Quoted Price under Selected Incoterm (USD):" if not is_hebrew else "מחיר ספק מוצע תחת תנאי הסחר הנבחר (USD):", min_value=0.0, value=exw_value_usd)

with tab3:
    st.subheader("Port Demurrage, Storage & Inland Drayage" if not is_hebrew else "קנסות נמל, אחסנה חיצונית והובלה יבשתית לאתר")
    col_x, col_y = st.columns(2)
    with col_x:
        free_days = st.number_input("Port Free Days:" if not is_hebrew else "ימים חופשיים בנמל (Free Days):", value=DEFAULT_FREE_DAYS.get(dest_country, 7), step=1, min_value=0)
        actual_port_days = st.number_input("Actual Port Dwell Days:" if not is_hebrew else "ימי אחסנה בפועל בנמל:", value=12, step=1, min_value=0)
        demurrage_daily_rate = st.number_input("Daily Demurrage Rate per DG Container ($):" if not is_hebrew else "קנס השהיה יומי ממוצע למכולת חומ\"ס ($):", value=250.0 if is_dg else 150.0, step=10.0, min_value=0.0)
        
    with col_y:
        use_external_storage = st.checkbox("External Staging Yard" if not is_hebrew else "שימוש בחצר אחסנה חיצונית / שטח היערכות", value=True)
        ext_storage_days = st.number_input("External Storage Days:" if not is_hebrew else "ימי אחסנה בפועל בחצר החיצונית:", value=15, step=1, min_value=0)
        ext_storage_daily_rate = st.number_input("External Storage Daily Rate ($):" if not is_hebrew else "עלות אחסנה יומית בחצר החיצונית למכולה ($):", value=65.0 if is_dg else 45.0, step=5.0, min_value=0.0)
        
        default_drayage = 1850.0 if "Burgas" in dest_port else 600.0
        inland_drayage_per_unit = st.number_input("Inland Drayage from Port to Site ($ per container):" if not is_hebrew else "הובלה יבשתית מהנמל לאתר הפרויקט ($ למכולה):", value=default_drayage, step=50.0, min_value=0.0)

    st.markdown("---")
    col_ddp1, col_ddp2 = st.columns(2)
    with col_ddp1:
        site_crane_unloading = st.number_input("Site Crane & Pad Offloading ($):" if not is_hebrew else "מנוף פריקה כבד באתר + הצבה ($ סה\"כ):", value=8500.0, step=500.0, min_value=0.0)
    with col_ddp2:
        ddp_contingency_pct = st.number_input("Project Risk Contingency (%):" if not is_hebrew else "מקדם סיכון ובלתי מתוכנן פרויקטלי (%):", value=5.0, step=1.0, min_value=0.0, max_value=100.0)

with tab4:
    st.subheader("🛡️ DG Compliance, Battery Passports & End-of-Life Regulation" if not is_hebrew else "🛡️ רגולציית חומ\"ס DG, דרכון סוללה ותקנות סוף חיים (EoL)")
    
    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        st.markdown("### 📦 Dangerous Goods & Safety Permits" if not is_hebrew else "### 📦 מטענים מסוכנים והיתרי בטיחות")
        if dest_country == "Israel":
            st.info("💡 **Israel Regulatory Requirements (Potential):** Import of BESS may require a Ministry of Environmental Protection Poisons Permit, Fire & Rescue Authority safety approval. Verify applicability with a licensed customs broker." if not is_hebrew else "💡 **דרישות רגולטוריות אפשריות בישראל:** יבוא מערכות BESS עשוי לדרוש היתר רעלים מהמשרד להגנת הסביבה ואישור כיבוי אש. יש לאמת את תחולתן מול עמיל מכס מורשה.")
        else:
            st.info("💡 **EU Battery Regulation Compliance (Potential):** Shipments into the EU may require adherence to the EU Battery Regulation. Verify applicability with a licensed customs broker." if not is_hebrew else "💡 **ציות אפשרי לרגולציית הסוללות באיחוד:** משלוחים לאירופה עשויים לחייב עמידה ברגולציית הסוללות. יש לאמת את תחולתה מול עמיל מכס מורשה.")

        local_regulatory_permits = st.number_input("Hazardous Permits & DG Clearance ($):" if not is_hebrew else "אישורי חומ\"ס, היתר רעלים ואישורי כיבוי ($ סה\"כ):", value=1500.0 if is_dg else 400.0, step=100.0, min_value=0.0)

    with col_reg2:
        st.markdown("### ♻️ Battery Passport, EPR & End-of-Life (EoL)" if not is_hebrew else "### ♻️ דרכון סוללה, EPR וסוף חיים (EoL)")
        include_epr_costs = st.checkbox("Include EPR & Battery Passport in current financial calculation" if not is_hebrew else "כלול אגרות EPR ודרכון סוללה בחישוב הפיננסי הנוכחי", value=True)
        
        epr_fee_per_unit = st.number_input("EPR / Battery Recycling Fee per Unit ($):" if not is_hebrew else "אגרת מיחזור סוללות / EPR ליחידה ($):", value=450.0 if "BESS" in cargo_type else 80.0, step=50.0, min_value=0.0, disabled=not include_epr_costs)
        battery_passport_fee = st.number_input("Battery Passport & Carbon Audit Fee ($):" if not is_hebrew else "עלות הפקת דרכון סוללה ובדיקת טביעת רגל פחמנית ($ סה\"כ):", value=1200.0 if "BESS" in cargo_type else 200.0, step=100.0, min_value=0.0, disabled=not include_epr_costs)

    requires_heavy_lift = st.checkbox("Heavy-haul / abnormal-load handling required" if not is_hebrew else "נדרשת הובלה חריגה / מטען כבד", value=(cargo_type == "BESS Container (UN3536 Class 9)"))

if show_route_optimization:
    with tab5:
        display_site = site_address if site_address else ("Unnamed Site" if not is_hebrew else "אתר ללא שם")
        st.subheader(f"🗺️ Illustrative Route Comparison ({dest_country})" if not is_hebrew else f"🗺️ השוואת מסלולים אינדיקטיבית ({dest_country})")
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

# =========================================================
# מנוע החישוב הפיננסי (מופעל לאחר שכל משתני ה-UI הוגדרו)
# =========================================================
total_ocean_freight = (base_freight_per_unit + baf_surcharge) * float(container_count)
cif_valuation_base = exw_value_usd + china_inland_drayage + china_origin_thc + total_ocean_freight
insurance_total_usd = cif_valuation_base * (insurance_pct / 100.0)

customs_valuation_base_usd = cif_valuation_base + insurance_total_usd
customs_duty_usd = customs_valuation_base_usd * (customs_duty_pct / 100.0)
destination_thc_total = dest_thc_port_fee * float(container_count)

overdue_days = max(0, actual_port_days - free_days)
demurrage_total_usd = float(overdue_days) * demurrage_daily_rate * float(container_count)
external_storage_total_usd = (float(ext_storage_days) * ext_storage_daily_rate * float(container_count)) if use_external_storage else 0.0
inland_drayage_total_usd = inland_drayage_per_unit * float(container_count)

epr_recycling_total_usd = ((epr_fee_per_unit * float(container_count)) + battery_passport_fee) if include_epr_costs else 0.0
regulatory_permits_total_usd = local_regulatory_permits
regulatory_total_usd = epr_recycling_total_usd + regulatory_permits_total_usd

effective_heavy_lift = heavy_lift_survey if requires_heavy_lift else 0.0

if supplier_quote_available:
    supplier_commercial_price = supplier_quoted_price
else:
    est_inland_drayage_calc = inland_drayage_per_unit * float(container_count)
    supplier_commercial_price_options = {
        "EXW (Ex Works)": exw_value_usd,
        "FOB (Free on Board)": exw_value_usd + china_inland_drayage + china_origin_thc,
        "CIF (Cost, Insurance & Freight)": exw_value_usd + china_inland_drayage + china_origin_thc + total_ocean_freight + insurance_total_usd,
        "DDP (Delivered Duty Paid)": (
            exw_value_usd + china_inland_drayage + china_origin_thc + total_ocean_freight + insurance_total_usd
            + customs_duty_usd + destination_thc_total + est_inland_drayage_calc + site_crane_unloading + effective_heavy_lift + regulatory_total_usd
        )
    }
    supplier_commercial_price = supplier_commercial_price_options.get(incoterm, exw_value_usd)

vat_base_import_usd = customs_valuation_base_usd + customs_duty_usd + destination_thc_total
vat_total_usd = vat_base_import_usd * (applied_vat / 100.0)

buyer_supply_chain_total = (
    exw_value_usd
    + china_inland_drayage
    + china_origin_thc
    + total_ocean_freight
    + insurance_total_usd
    + customs_duty_usd
    + destination_thc_total
    + demurrage_total_usd
    + external_storage_total_usd
    + inland_drayage_total_usd
    + site_crane_unloading
    + regulatory_total_usd
    + effective_heavy_lift
)

contingency_usd = buyer_supply_chain_total * (ddp_contingency_pct / 100.0)
total_landed_cost_ex_vat = buyer_supply_chain_total + contingency_usd
vat_recoverable = vat_total_usd
total_cash_requirement_incl_vat = total_landed_cost_ex_vat + vat_recoverable

total_kwh = bess_mwh * 1000.0 if bess_mwh > 0 else 1.0
total_supply_chain_cost_per_kwh = total_landed_cost_ex_vat / total_kwh

logistics_only_usd = (
    china_inland_drayage
    + china_origin_thc
    + total_ocean_freight
    + insurance_total_usd
    + destination_thc_total
    + inland_drayage_total_usd
    + demurrage_total_usd
    + external_storage_total_usd
    + site_crane_unloading
    + regulatory_total_usd
    + effective_heavy_lift
)
logistics_cost_per_kwh = logistics_only_usd / total_kwh

# המרות מטבע לתצוגה
display_val, curr_symbol = convert_from_usd(total_landed_cost_ex_vat, display_currency)
supplier_val, _ = convert_from_usd(supplier_commercial_price, display_currency)
cash_val, _ = convert_from_usd(total_cash_requirement_incl_vat, display_currency)
freight_display, _ = convert_from_usd(total_ocean_freight, display_currency)
customs_display, _ = convert_from_usd(customs_duty_usd, display_currency)
kwh_cost_display, _ = convert_from_usd(total_supply_chain_cost_per_kwh, display_currency)
logistics_kwh_display, _ = convert_from_usd(logistics_cost_per_kwh, display_currency)

# ----- T Summary -----
with (tab6 if show_route_optimization else tab6):
    st.subheader(f"📊 Financial & Regulatory Control Dashboard - {incoterm} ({display_currency})")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Buyer Landed Cost (ex-VAT)", f"{curr_symbol} {display_val:,.2f}")
    m2.metric("Supplier Price Scope", f"{curr_symbol} {supplier_val:,.2f}", help=f"Based on {incoterm}")
    m3.metric("Total Cash Flow (incl. VAT)", f"{curr_symbol} {cash_val:,.2f}", help="Includes recoverable VAT")
    m4.metric("Total Supply Chain Cost / kWh", f"{curr_symbol} {kwh_cost_display:.4f} /kWh")
    m5.metric("Logistics Cost / kWh", f"{curr_symbol} {logistics_kwh_display:.4f} /kWh", help="Excludes equipment cost")
    
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
        "DG Permits, Battery Passports & EPR / EoL" if not is_hebrew else "אישורי חומ\"ס, דרכון סוללה ואגרות מיחזור EPR",
        "Port Demurrage Charges" if not is_hebrew else "קנסות השהיה בנמל (Demurrage)",
        "External Staging Yard Storage" if not is_hebrew else "אחסנה חיצונית בחצר היערכות",
        "Inland Drayage (Port to Site)" if not is_hebrew else "הובלה יבשתית (מהנמל לאתר)",
        "Site Crane & Pad Offloading" if not is_hebrew else "מנוף פריקה והצבה באתר",
        "Project Risk Contingency" if not is_hebrew else "מקדם סיכון ובלתי מתוכנן פרויקטלי",
        "Import VAT (Recoverable Cash Item)" if not is_hebrew else "מע\"מ יבוא (ניתן לקיזוז)"
    ]
    
    amounts_no_vat = [
        exw_value_usd, china_inland_drayage, china_origin_thc, 
        total_ocean_freight, insurance_total_usd, customs_duty_usd, 
        destination_thc_total, regulatory_total_usd, demurrage_total_usd, 
        external_storage_total_usd, inland_drayage_total_usd, site_crane_unloading, contingency_usd
    ]
    
    df_summary = pd.DataFrame({
        "Cost Component" if not is_hebrew else "רכיב עלות": cost_labels,
        "Amount (USD)": amounts_no_vat + [vat_total_usd]
    })
    
    pct_list = [(amt / total_landed_cost_ex_vat) * 100.0 for amt in amounts_no_vat] + [0.0]
    df_summary["% of Landed Cost"] = [f"{p:.2f}%" for p in pct_list]
    
    st.dataframe(df_summary, use_container_width=True)
    
    st.markdown("---")
    csv_data = df_summary.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Export Financial & Regulatory Report (CSV/Excel)" if not is_hebrew else "📥 הורד דוח פיננסי ורגולטורי מלא (CSV/Excel)",
        data=csv_data,
        file_name=f"BESS_Regulatory_Financial_Report_{incoterm.split(' ')[0]}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Renewable Energy Logistics & Landed Cost Calculator — Enterprise Edition.")
