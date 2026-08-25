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
    "cost_per_kwh": "Logistics Cost per kWh:" if not is_hebrew else "עלות לוגיסטית ל-kWh:",
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

# ---------------------------------------------------------
# הגדרת לשוניות דינמיות לפי מדינת היעד
# ---------------------------------------------------------
# נאסוף קודם נתון מוביל מלשונית 1 או נבחן תנאי יעד

# הגדרת הלשוניות בדינמיות
# נתחיל מברירת מחדל של טעינת T1 לקבלת המדינה
