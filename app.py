import io
import openpyxl
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from openpyxl.styles import Font

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Green-Logistics Customs & Landed Cost Calculator",
    page_icon="⚡",
    layout="wide",
)

# ---------------------------------------------------------
# Language Selector & Translations
# ---------------------------------------------------------
lang = st.sidebar.radio("🌐 Language / שפה", ["עברית", "English"])
is_heb = lang == "עברית"

t = {
    "title": (
        "⚡ מחשבון עלויות יבוא, מכס ו-Green Landed Cost"
        if is_heb
        else "⚡ Green-Logistics Customs & Landed Cost Calculator"
    ),
    "subtitle": (
        "מחשבון עלויות יבוא, מכס, רגולציה, מחזור (EPR), פליטות פחמן (CO₂e)"
        " ו-Landed Cost לתשתיות אנרגיה (**BESS**, **MVS**, פאנלים סולאריים,"
        " ממירים ושנאים)."
        if is_heb
        else (
            "Import Duty, Tax, Battery Recycling (EPR), Carbon Emissions"
            " (CO₂e) & Landed Cost Calculator for Renewable Energy"
            " Infrastructure (**BESS**, **MVS Skids**, Solar Panels, Inverters &"
            " Transformers)."
        )
    ),
    "route_header": (
        "🌍 מסלול השינוע והנמלים" if is_heb else "🌍 Shipping Route & Ports"
    ),
    "origin": "מדינת מוצא" if is_heb else "Origin Country",
    "origin_custom": (
        "הזן מדינת מוצא ידנית" if is_heb else "Enter Custom Origin Country"
    ),
    "port": "נמל פקידה / שחרור" if is_heb else "Port of Discharge",
    "port_custom": "הזן שם נמל ידני" if is_heb else "Enter Custom Port Name",
    "dest": "מדינת יעד סופית" if is_heb else "Final Destination Country",
    "final_dest": (
        "יעד מסירה סופי באתר (שם/קואורדינטות)"
        if is_heb
        else "Final Delivery Location (Site Name / GPS)"
    ),
    "currency_header": (
        "🔱 מטבע מקומי ושערי חליפין"
        if is_heb
        else "🔱 Local Currency & Exchange Rates"
    ),
    "ex_rate_label": (
        "שער המרה מדולר ($) למטבע מקומי"
        if is_heb
        else "Exchange Rate (USD to Local Currency)"
    ),
    "cargo_header": (
        "📋 פרטי המטען, מכולות ויחידות ציוד"
        if is_heb
        else "📋 Cargo, Containers & Equipment Units"
    ),
    "equipment": "סוג הציוד" if is_heb else "Equipment Category",
    "container_type": (
        "סוג מכולה / סיווג בטיחות"
        if is_heb
        else "Container Type & Safety Classification"
    ),
    "hs": "קוד מכס (HS Code)" if is_heb else "HS Code",
    "num_containers": "כמות מכולות" if is_heb else "Number of Containers",
    "bess_capacity": (
        "קיבולת BESS כוללת (MWh)"
        if is_heb
        else "Total BESS System Capacity (MWh)"
    ),
    "cargo_units": (
        "סה\"כ יחידות ציוד (למשל פאנלים/ממירים)"
        if is_heb
        else "Total Equipment Units (e.g., Panels/Inverters)"
    ),
    "weight": (
        "משקל ברוטו למכולה (טון)"
        if is_heb
        else "Gross Weight per Container (Tonnes)"
    ),
    "cargo_val": (
        "ערך הסחורה במקור ($ USD)"
        if is_heb
        else "Cargo FOB / EXW Value ($ USD)"
    ),
    "freight_header": (
        "🚢 עלויות הובלה וביטוח ימי"
        if is_heb
        else "🚢 Ocean Freight & Insurance"
    ),
    "freight": (
        "הובלה ימית ראשת ($ USD)" if is_heb else "Main Ocean Freight ($ USD)"
    ),
    "ins_basis": "בסיס חישוב ביטוח" if is_heb else "Insurance Calculation Basis",
    "insurance_rate": (
        "שיעור ביטוח ימי (%)" if is_heb else "Marine Insurance Rate (%)"
    ),
    "origin_exp": (
        "הוצאות במקור ($ USD)" if is_heb else "Origin Local Expenses ($ USD)"
    ),
    "tax_header": (
        "🏛️ מכס, הסכמי סחר ומיסוי"
        if is_heb
        else "🏛️ Customs, Duties & Taxation"
    ),
    "customs_rate": (
        "שיעור מכס רשמי (%)" if is_heb else "Official Customs Duty Rate (%)"
    ),
    "duty_incentive": "הטבת מכס / פטור" if is_heb else "Customs Duty Incentive",
    "vat": (
        'שיעור מע"מ מקומי במדינת השחרור (%)'
        if is_heb
        else "Local VAT Rate at Port of Clearance (%)"
    ),
    "port_header": (
        "⚓ עלויות נמל, THC ועמילות בארץ היעד"
        if is_heb
        else "⚓ Destination Port, THC & Brokerage"
    ),
    "port_fees": (
        "אגרות נמל וסדרנות ($ USD)"
        if is_heb
        else "Port Wharfage & Handling ($ USD)"
    ),
    "thc": (
        "דמי טיפול במסוף (THC) למכולה ($ USD)"
        if is_heb
        else "Terminal Handling Charge (THC) per Container ($ USD)"
    ),
    "brokerage": (
        "עמילות מכס ואישורים ($ USD)"
        if is_heb
        else "Customs Brokerage & Permits ($ USD)"
    ),
    "inland_per_unit": (
        "הובלה יבשתית למכולה ($ USD)"
        if is_heb
        else "Special Heavy Inland Haulage per Container ($ USD)"
    ),
    "demurrage_header": (
        "⏱️ ניהול סיכוני השהיה בנמל (Demurrage Risk)"
        if is_heb
        else "⏱️ Port Demurrage Risk Estimator"
    ),
    "free_days": (
        "ימים חופשיים בנמל (Free Days)"
        if is_heb
        else "Port Free Days Included"
    ),
    "est_port_days": (
        "ימי השהיה בפועל בנמל (משוער)"
        if is_heb
        else "Estimated Actual Port Dwell Days"
    ),
    "demurrage_rate": (
        "עלות השהיה יומית למכולה ($/Day)"
        if is_heb
        else "Daily Demurrage Rate per Container ($/Day)"
    ),
    "recycling_header": (
        "♻️ מחזור סוללות ואחריות יצרן באירופה (EPR / Battery Reg)"
        if is_heb
        else "♻️ EU Battery Recycling & EPR Fee (EU 2023/1542)"
    ),
    "recycling_rate": (
        "הפרשת מחזור סוף חיים ($/kWh)"
        if is_heb
        else "End-of-Life Recycling Provision ($/kWh)"
    ),
    "green_header": (
        "🌱 מדדי קיימות ופליטות פחמן (CO₂e)"
        if is_heb
        else "🌱 Sustainability & Carbon Emissions (CO₂e)"
    ),
    "sea_dist": "מרחק שינוע ימי (ק\"מ)" if is_heb else "Ocean Distance (km)",
    "land_dist": "מרחק שינוע יבשתי (ק\"מ)" if is_heb else "Inland Distance (km)",
    "cif_metric": "ערך CIF כולל" if is_heb else "Total CIF Value",
    "duty_metric": "תשלום מכס אפקטיבי" if is_heb else "Effective Duty",
    "vat_metric": 'מע"מ לתשלום' if is_heb else "VAT Payable",
    "landed_metric": (
        'עלות Landed Cost נטו (ללא מע"מ)'
        if is_heb
        else "Net Landed Cost (excl. VAT)"
    ),
    "breakdown_title": (
        "📊 ניתוח הצטברות עלויות (Waterfall Chart)"
        if is_heb
        else "📊 Cost Accumulation (Waterfall Chart)"
    ),
    "summary_title": (
        "📑 טבלת סיכום שלבי החישוב" if is_heb else "📑 Step-by-Step Summary Table"
    ),
    "export_title": "📥 ייצוא נתונים" if is_heb else "📥 Export Data",
    "btn_excel": (
        "📊 הורד דוח Excel מחושב מפורט"
        if is_heb
        else "📊 Download Detailed Excel Landed Cost Report"
    ),
}

st.title(t["title"])
st.markdown(t["subtitle"])
st.divider()

# ---------------------------------------------------------
# Sidebar Inputs
# ---------------------------------------------------------
st.sidebar.header(t["route_header"])

origin_selection = st.sidebar.selectbox(
    t["origin"],
    ["China", "Germany", "USA", "India", "Japan", "South Korea", "Other / אחר"],
    index=0,
)

if origin_selection == "Other / אחר":
  origin_country = st.sidebar.text_input(t["origin_custom"], value="Vietnam")
else:
  origin_country = origin_selection

port_defaults = {
    "Port of Haifa / Bayport (Israel)": {
        "dest": "Israel",
        "vat": 18.0,
        "curr": "₪ ILS",
        "sym": "₪",
        "rate": 3.70,
        "site": "Carmiel Industrial Zone / GPS: 32.9199, 35.2901",
        "sea_km": 15000,
        "land_km": 60,
    },
    "Port of Ashdod (Israel)": {
        "dest": "Israel",
        "vat": 18.0,
        "curr": "₪ ILS",
        "sym": "₪",
        "rate": 3.70,
        "site": "Carmiel Industrial Zone / GPS: 32.9199, 35.2901",
        "sea_km": 15200,
        "land_km": 170,
    },
    "Port of Burgas (Bulgaria)": {
        "dest": "Bulgaria / Transit to Romania",
        "vat": 20.0,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "Iepuresti Solar Plant, Romania",
        "sea_km": 14200,
        "land_km": 320,
    },
    "Port of Constanta (Romania)": {
        "dest": "Romania",
        "vat": 19.0,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "Ghimpati Solar Plant, Romania",
        "sea_km": 14500,
        "land_km": 280,
    },
    "Port of Piraeus (Greece)": {
        "dest": "Greece",
        "vat": 24.0,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "Athens Substation Site",
        "sea_km": 13800,
        "land_km": 40,
    },
    "Port of Thessaloniki (Greece)": {
        "dest": "Greece",
        "vat": 24.0,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "Northern Greece Substation",
        "sea_km": 14000,
        "land_km": 80,
    },
    "Port of Rauma (Finland)": {
        "dest": "Finland",
        "vat": 25.5,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "Tuovila BESS Site, Finland",
        "sea_km": 18500,
        "land_km": 210,
    },
    "Port of Vuosaari / Helsinki (Finland)": {
        "dest": "Finland",
        "vat": 25.5,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "Pyhäsalmi BESS Site, Finland",
        "sea_km": 18300,
        "land_km": 450,
    },
    "Port of Rotterdam (Netherlands)": {
        "dest": "Netherlands / EU",
        "vat": 21.0,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "EU Central Hub",
        "sea_km": 18000,
        "land_km": 100,
    },
    "Port of Antwerp-Bruges (Belgium)": {
        "dest": "Belgium / EU",
        "vat": 21.0,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "EU Distribution Center",
        "sea_km": 18100,
        "land_km": 120,
    },
    "Other Port": {
        "dest": "Other",
        "vat": 18.0,
        "curr": "$ USD",
        "sym": "$",
        "rate": 1.00,
        "site": "",
        "sea_km": 15000,
        "land_km": 100,
    },
}

selected_port_key = st.sidebar.selectbox(
    t["port"], list(port_defaults.keys()), index=0
)

if selected_port_key == "Other Port":
  selected_port = st.sidebar.text_input(
      t["port_custom"], value="Port of Limassol"
  )
else:
  selected_port = selected_port_key

dest_info = port_defaults[selected_port_key]
dest_country = st.sidebar.text_input(t["dest"], value=dest_info["dest"])

final_destination = st.sidebar.text_input(
    t["final_dest"],
    value=dest_info["site"],
    key=f"final_site_{selected_port_key}",
)

# Route Validation Warning
if (
    "Israel" in dest_country
    and "Haifa" not in selected_port
    and "Ashdod" not in selected_port
):
  st.sidebar.warning(
      "⚠️ **Route Alert:** Selected port is outside Israel while Destination"
      " Country is set to Israel (Transit Shipment assumed)."
  )

st.sidebar.divider()
st.sidebar.header(t["currency_header"])

curr_symbol = dest_info["sym"]
ex_rate = st.sidebar.number_input(
    f"{t['ex_rate_label']} (1 USD ➔ {dest_info['curr']})",
    min_value=0.1,
    value=float(dest_info["rate"]),
    step=0.01,
)

st.sidebar.divider()
st.sidebar.header(t["cargo_header"])

equipment_type = st.sidebar.selectbox(
    t["equipment"],
    [
        "BESS Container (Battery Energy Storage Systems - DG Class 9)",
        "MVS - Medium Voltage Stations / Skids (Non-Hazmat / Non-DG)",
        "MVS Accessories & Switchgear (Non-Hazmat)",
        "Solar Panels (PV Modules)",
        "Inverters & Transformers",
        "Wind Turbine Components",
    ],
)

is_bess = "BESS" in equipment_type
is_mvs = "MVS" in equipment_type

if is_bess:
  container_options = {
      "20ft SOC BESS (DG Class 9 / Hazmat)": 520.0,
      "40ft / 40HC SOC BESS (DG Class 9 / Hazmat)": 580.0,
  }
elif is_mvs:
  container_options = {
      "20ft SOC MVS Skid (Non-Hazmat / Standard Cargo)": 350.0,
      "40ft / 40HC SOC MVS Skid (Non-Hazmat / Standard Cargo)": 450.0,
      "Special Equipment MVS (Flat Rack / Open Top)": 480.0,
  }
else:
  container_options = {
      "40ft / 40HC Standard Dry Container": 280.0,
      "Special Equipment (Open Top / Flat Rack)": 480.0,
  }

container_type = st.sidebar.selectbox(
    t["container_type"], list(container_options.keys()), index=0
)

default_thc_value = container_options[container_type]

hs_defaults = {
    "BESS Container (Battery Energy Storage Systems - DG Class 9)": "8507.60",
    "MVS - Medium Voltage Stations / Skids (Non-Hazmat / Non-DG)": "8504.22",
    "MVS Accessories & Switchgear (Non-Hazmat)": "8537.20",
    "Solar Panels (PV Modules)": "8541.43",
    "Inverters & Transformers": "8504.40",
    "Wind Turbine Components": "8502.31",
}

eu_mfn_customs_rates = {
    "BESS Container (Battery Energy Storage Systems - DG Class 9)": 2.7,
    "MVS - Medium Voltage Stations / Skids (Non-Hazmat / Non-DG)": 2.1,
    "MVS Accessories & Switchgear (Non-Hazmat)": 2.1,
    "Solar Panels (PV Modules)": 0.0,
    "Inverters & Transformers": 2.1,
    "Wind Turbine Components": 2.7,
}

hs_code = st.sidebar.text_input(
    t["hs"], value=hs_defaults.get(equipment_type, "8507.60")
)
num_containers = st.sidebar.number_input(
    t["num_containers"], min_value=1, value=5, step=1
)

# Capacity for BESS system if BESS selected
if is_bess:
  bess_mwh_capacity = st.sidebar.number_input(
      t["bess_capacity"], min_value=0.1, value=10.0, step=0.5
  )
  total_cargo_units = int(bess_mwh_capacity * 1000)  # Total kWh
else:
  bess_mwh_capacity = 0.0
  default_units_per_container = 1 if is_mvs else (600 if "Solar" in equipment_type else 20)
  total_cargo_units = st.sidebar.number_input(
      t["cargo_units"],
      min_value=1,
      value=int(num_containers * default_units_per_container),
      step=10,
  )

container_weight = st.sidebar.number_input(
    t["weight"],
    min_value=1.0,
    max_value=100.0,
    value=30.0 if is_mvs else 45.0,
    step=1.0,
)
total_weight = container_weight * num_containers
cargo_value_usd = st.sidebar.number_input(
    t["cargo_val"], min_value=0.0, value=150000.0, step=1000.0
)

st.sidebar.divider()
st.sidebar.header(t["freight_header"])
freight_cost_usd = st.sidebar.number_input(
    t["freight"], min_value=0.0, value=12000.0, step=500.0
)
origin_expenses_usd = st.sidebar.number_input(
    t["origin_exp"], min_value=0.0, value=1500.0, step=100.0
)

insurance_basis = st.sidebar.selectbox(
    t["ins_basis"],
    ["FOB Cargo Value Only", "CIF Base (FOB + Freight + 10% Uplift)"],
    index=1,
)

insurance_rate = (
    st.sidebar.number_input(
        t["insurance_rate"], min_value=0.0, value=0.3, step=0.05
    )
    / 100
)

st.sidebar.divider()
st.sidebar.header(t["tax_header"])

default_customs = (
    0.0
    if (
        "Israel" in dest_country
        or "Haifa" in selected_port
        or "Ashdod" in selected_port
    )
    else eu_mfn_customs_rates.get(equipment_type, 2.7)
)
customs_rate_input = st.sidebar.number_input(
    t["customs_rate"], min_value=0.0, value=default_customs, step=0.1
)

duty_incentive = st.sidebar.selectbox(
    t["duty_incentive"],
    [
        "No Incentive (Full Duty)",
        "Preferential FTA Exemption (COO Available)",
        "Green Incentive (50% Duty Reduction)",
        "Full Regulatory Exemption (0% Duty)",
    ],
    index=1 if default_customs == 0 else 0,
)

vat_rate = (
    st.sidebar.number_input(
        t["vat"], min_value=0.0, value=float(dest_info["vat"]), step=0.5
    )
    / 100
)

st.sidebar.divider()
st.sidebar.header(t["port_header"])
port_fees_usd = st.sidebar.number_input(
    t["port_fees"], min_value=0.0, value=1200.0, step=50.0
)

thc_fees_usd = st.sidebar.number_input(
    t["thc"],
    min_value=0.0,
    value=float(default_thc_value),
    step=25.0,
    key=f"thc_{container_type}",
)
total_thc_usd = thc_fees_usd * num_containers

brokerage_fees_usd = st.sidebar.number_input(
    t["brokerage"], min_value=0.0, value=850.0, step=50.0
)

inland_per_container_usd = st.sidebar.number_input(
    t["inland_per_unit"], min_value=0.0, value=900.0, step=50.0
)
total_inland_transport_usd = inland_per_container_usd * num_containers

st.sidebar.divider()
st.sidebar.header(t["demurrage_header"])
free_days = st.sidebar.number_input(t["free_days"], min_value=0, value=14, step=1)
est_port_days = st.sidebar.number_input(
    t["est_port_days"], min_value=0, value=16, step=1
)
demurrage_daily_rate = st.sidebar.number_input(
    t["demurrage_rate"], min_value=0.0, value=120.0, step=10.0
)

# EPR & Battery Recycling Provision (For BESS Cargo)
st.sidebar.divider()
st.sidebar.header(t["recycling_header"])

if is_bess:
  recycling_rate_per_kwh = st.sidebar.number_input(
      t["recycling_rate"], min_value=0.0, value=12.0, step=1.0
  )
  total_recycling_provision_usd = (
      bess_mwh_capacity * 1000 * recycling_rate_per_kwh
  )
else:
  recycling_rate_per_kwh = 0.0
  total_recycling_provision_usd = 0.0

st.sidebar.divider()
st.sidebar.header(t["green_header"])
sea_dist_km = st.sidebar.number_input(
    t["sea_dist"], min_value=0, value=int(dest_info["sea_km"]), step=500
)
land_dist_km = st.sidebar.number_input(
    t["land_dist"], min_value=0, value=int(dest_info["land_km"]), step=10
)

# ---------------------------------------------------------
# Calculations Engine
# ---------------------------------------------------------
if insurance_basis == "FOB Cargo Value Only":
  insurance_cost_usd = cargo_value_usd * insurance_rate
else:
  insurance_cost_usd = (
      (cargo_value_usd + freight_cost_usd + origin_expenses_usd)
      * 1.10
      * insurance_rate
  )

cif_value_usd = (
    cargo_value_usd + freight_cost_usd + origin_expenses_usd + insurance_cost_usd
)

if (
    "Full Regulatory Exemption" in duty_incentive
    or "Preferential FTA" in duty_incentive
    or "Israel" in dest_country
):
  effective_customs_rate = 0.0
elif "Green Incentive (50%" in duty_incentive:
  effective_customs_rate = (customs_rate_input / 100) * 0.5
else:
  effective_customs_rate = customs_rate_input / 100

customs_duty_amount_usd = cif_value_usd * effective_customs_rate
vat_base_usd = cif_value_usd + customs_duty_amount_usd + port_fees_usd
vat_amount_usd = vat_base_usd * vat_rate

local_clearance_total_usd = (
    port_fees_usd
    + total_thc_usd
    + brokerage_fees_usd
    + total_inland_transport_usd
)

demurrage_excess_days = max(0, est_port_days - free_days)
total_demurrage_usd = (
    demurrage_excess_days * demurrage_daily_rate * num_containers
)

total_landed_cost_gross_usd = (
    cif_value_usd
    + customs_duty_amount_usd
    + vat_amount_usd
    + local_clearance_total_usd
    + total_demurrage_usd
    + total_recycling_provision_usd
)
total_landed_cost_net_usd = total_landed_cost_gross_usd - vat_amount_usd

cost_per_container_usd = total_landed_cost_net_usd / num_containers
cost_per_cargo_unit_usd = (
    total_landed_cost_net_usd / total_cargo_units if total_cargo_units > 0 else 0
)

# Sustainability & CO2e Engine
sea_co2e_tons = (total_weight * sea_dist_km * 0.010) / 1000
road_co2e_tons = (total_weight * land_dist_km * 0.062) / 1000
total_co2e_tons = sea_co2e_tons + road_co2e_tons

# Local currency conversions
cif_value_loc = cif_value_usd * ex_rate
customs_duty_loc = customs_duty_amount_usd * ex_rate
vat_amount_loc = vat_amount_usd * ex_rate
landed_net_loc = total_landed_cost_net_usd * ex_rate

# ---------------------------------------------------------
# UI Display & Safety Alerts
# ---------------------------------------------------------
site_display = final_destination if final_destination else "N/A"
if is_heb:
  st.info(
      f"📍 **מסלול:** מ-**{origin_country}** דרך **{selected_port}** ➔"
      f" **{dest_country}** | **ציוד:** `{equipment_type}` | **כמות:**"
      f" `{num_containers}` מכולות | **פליטת פחמן:** `{total_co2e_tons:.2f} Ton"
      " CO₂e`"
  )
else:
  st.info(
      f"📍 **Route:** From **{origin_country}** via **{selected_port}** ➔"
      f" **{dest_country}** | **Cargo:** `{equipment_type}` | **Volume:**"
      f" `{num_containers}` Containers | **Carbon Footprint:**"
      f" `{total_co2e_tons:.2f} Ton CO₂e`"
  )

if is_bess:
  if is_heb:
    st.warning(
        "🔥 **התראת חומרים מסוכנים ודרכון סוללה (BESS - DG Class 9 / EU"
        " 2023/1542):**\n* **DG Handling:** סוללות ליתיום-יוון מוגדרות כחומר"
        " מסוכן (UN 3536). דורש הצהרת מסוכנים (DGD) ואישור איחסון מסוכנים"
        " בנמל.\n* **EU Battery Passport & EPR:** באיחוד האירופי מחויב רישום"
        " דרכון סוללה דיגיטלי והפרשת תשלום מחזור סוף חיים (EPR Provision)."
    )
  else:
    st.warning(
        "🔥 **Dangerous Goods & EU Battery Passport Alert (BESS - DG Class 9 /"
        " EU 2023/1542):**\n* **DG Handling:** Lithium-ion batteries (UN 3536)"
        " require DGD documentation and port permits.\n* **EU Battery"
        " Passport & EPR:** EU regulations mandate a digital battery passport"
        " and EoL recycling financial provision."
    )

if container_weight >= 40.0:
  if is_heb:
    st.error(
        f"🚨 **התראת משקל כבד ({container_weight} טון למכולה | סה\"כ"
        f' {total_weight} טון):**\n* **בישראל:** מחייב אישור מיוחד מ**משרד'
        " התחבורה (אגף מטענים)**, בדיקת עומס סרנים בגשרים וליווי.\n* **באירופה:**"
        " מחייב היתר הובלה מיוחדת (Special Transport Permit) מול רשויות"
        " הדרכים."
    )
  else:
    st.error(
        f"🚨 **Heavy Cargo Alert ({container_weight} Tonnes/Unit | Total:"
        f" {total_weight} Tonnes):**\n* **In Israel:** Requires special permit"
        " from the **Ministry of Transport**, axle load checks, and escort.\n*"
        " **In Europe:** Requires Special Transport Permits from local road"
        " authorities."
    )

clean_hs = hs_code.replace(".", "").strip()
if (
    "Israel" in dest_country
    or "Haifa" in selected_port
    or "Ashdod" in selected_port
):
  customs_url = f"https://www.gov.il/he/departments/dynamiccollectors/customs-tariff?tariffNumber={clean_hs}"
  link_text = (
      "🔗 חיפוש בתעריף המכס הישראלי"
      if is_heb
      else "🔗 Search Israel Customs Tariff Database"
  )
else:
  customs_url = f"https://trade.ec.europa.eu/access-to-markets/en/home?product_code={clean_hs}"
  link_text = (
      f"🔗 חיפוש בפורטל Access2Markets עבור {dest_country}"
      if is_heb
      else f"🔗 Access EU Access2Markets Tariff Portal for {dest_country}"
  )

st.markdown(f"[{link_text}]({customs_url})")

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    t["cif_metric"],
    f"${cif_value_usd:,.2f}",
    f"{curr_symbol}{cif_value_loc:,.2f}",
)
col2.metric(
    t["duty_metric"],
    f"${customs_duty_amount_usd:,.2f}",
    f"{curr_symbol}{customs_duty_loc:,.2f} ({effective_customs_rate*100:.1f}%)",
)
col3.metric(
    f"{t['vat_metric']} ({vat_rate*100:.1f}%)",
    f"${vat_amount_usd:,.2f}",
    f"{curr_symbol}{vat_amount_loc:,.2f}",
)
col4.metric(
    t["landed_metric"],
    f"${total_landed_cost_net_usd:,.2f}",
    f"{curr_symbol}{landed_net_loc:,.2f}",
)

st.divider()

left_col, right_col = st.columns([1, 1])

# ---------------------------------------------------------
# Waterfall Chart Visualization
# ---------------------------------------------------------
with left_col:
  st.subheader(t["breakdown_title"])

  x_labels = (
      [
          "ציוד FOB",
          "הובלה ימית",
          "ביטוח",
          "מכס",
          "נמל ו-THC",
          "עמילות",
          "הובלה יבשתית",
          "סיכון השהיות",
          "הפרשת מחזור",
          "Landed Cost נטו",
      ]
      if is_heb
      else [
          "FOB Equipment",
          "Freight",
          "Insurance",
          "Customs Duty",
          "Port & THC",
          "Brokerage",
          "Inland Haulage",
          "Demurrage Risk",
          "Recycling Provision",
          "Net Landed Cost",
      ]
  )

  fig = go.Figure(
      go.Waterfall(
          name="Landed Cost",
          orientation="v",
          measure=[
              "relative",
              "relative",
              "relative",
              "relative",
              "relative",
              "relative",
              "relative",
              "relative",
              "relative",
              "total",
          ],
          x=x_labels,
          textposition="outside",
          text=[
              f"${cargo_value_usd:,.0f}",
              f"${freight_cost_usd+origin_expenses_usd:,.0f}",
              f"${insurance_cost_usd:,.0f}",
              f"${customs_duty_amount_usd:,.0f}",
              f"${port_fees_usd+total_thc_usd:,.0f}",
              f"${brokerage_fees_usd:,.0f}",
              f"${total_inland_transport_usd:,.0f}",
              f"${total_demurrage_usd:,.0f}",
              f"${total_recycling_provision_usd:,.0f}",
              f"${total_landed_cost_net_usd:,.0f}",
          ],
          y=[
              cargo_value_usd,
              freight_cost_usd + origin_expenses_usd,
              insurance_cost_usd,
              customs_duty_amount_usd,
              port_fees_usd + total_thc_usd,
              brokerage_fees_usd,
              total_inland_transport_usd,
              total_demurrage_usd,
              total_recycling_provision_usd,
              0,
          ],
          connector={"line": {"color": "rgb(63, 63, 63)"}},
      )
  )
  fig.update_layout(
      showlegend=False,
      height=480,
      margin=dict(l=20, r=20, t=30, b=20),
  )
  st.plotly_chart(fig, use_container_width=True)

with right_col:
  st.subheader(t["summary_title"])
  summary_df = pd.DataFrame([
      {
          "Detail": "Route / מסלול",
          "Value ($ USD)": f"{origin_country} ➔ {selected_port}",
          f"Local ({curr_symbol})": dest_info["curr"],
      },
      {
          "Detail": "Equipment / ציוד",
          "Value ($ USD)": equipment_type,
          f"Local ({curr_symbol})": container_type,
      },
      {
          "Detail": "Containers vs Units",
          "Value ($ USD)": f"{num_containers} Containers",
          f"Local ({curr_symbol})": (
              f"{bess_mwh_capacity} MWh" if is_bess else f"{total_cargo_units} Units"
          ),
      },
      {
          "Detail": "FOB Cargo Value",
          "Value ($ USD)": f"${cargo_value_usd:,.2f}",
          f"Local ({curr_symbol})": f"{curr_symbol}{cargo_value_usd*ex_rate:,.2f}",
      },
      {
          "Detail": "Ocean Freight + Origin",
          "Value ($ USD)": f"${freight_cost_usd + origin_expenses_usd:,.2f}",
          f"Local ({curr_symbol})": (
              f"{curr_symbol}{(freight_cost_usd + origin_expenses_usd)*ex_rate:,.2f}"
          ),
      },
      {
          "Detail": "Marine Insurance",
          "Value ($ USD)": f"${insurance_cost_usd:,.2f}",
          f"Local ({curr_symbol})": (
              f"{curr_symbol}{insurance_cost_usd*ex_rate:,.2f}"
          ),
      },
      {
          "Detail": "Total CIF Value",
          "Value ($ USD)": f"${cif_value_usd:,.2f}",
          f"Local ({curr_symbol})": f"{curr_symbol}{cif_value_loc:,.2f}",
      },
      {
          "Detail": "Customs Duty",
          "Value ($ USD)": f"${customs_duty_amount_usd:,.2f}",
          f"Local ({curr_symbol})": f"{curr_symbol}{customs_duty_loc:,.2f}",
      },
      {
          "Detail": f"Local VAT ({vat_rate*100:.1f}%)",
          "Value ($ USD)": f"${vat_amount_usd:,.2f}",
          f"Local ({curr_symbol})": f"{curr_symbol}{vat_amount_loc:,.2f}",
      },
      {
          "Detail": f"Port Wharfage & THC ({num_containers} cont.)",
          "Value ($ USD)": f"${port_fees_usd + total_thc_usd:,.2f}",
          f"Local ({curr_symbol})": (
              f"{curr_symbol}{(port_fees_usd + total_thc_usd)*ex_rate:,.2f}"
          ),
      },
      {
          "Detail": f"Inland Heavy Haulage ({num_containers} cont.)",
          "Value ($ USD)": f"${total_inland_transport_usd:,.2f}",
          f"Local ({curr_symbol})": (
              f"{curr_symbol}{total_inland_transport_usd*ex_rate:,.2f}"
          ),
      },
      {
          "Detail": f"Est. Demurrage Risk ({demurrage_excess_days} days)",
          "Value ($ USD)": f"${total_demurrage_usd:,.2f}",
          f"Local ({curr_symbol})": (
              f"{curr_symbol}{total_demurrage_usd*ex_rate:,.2f}"
          ),
      },
      {
          "Detail": (
              f"EU Battery Recycling EPR Provision"
              f" (${recycling_rate_per_kwh}/kWh)"
          ),
          "Value ($ USD)": f"${total_recycling_provision_usd:,.2f}",
          f"Local ({curr_symbol})": (
              f"{curr_symbol}{total_recycling_provision_usd*ex_rate:,.2f}"
          ),
      },
      {
          "Detail": "Cost per Container / מכולה",
          "Value ($ USD)": f"${cost_per_container_usd:,.2f}",
          f"Local ({curr_symbol})": (
              f"{curr_symbol}{cost_per_container_usd*ex_rate:,.2f}"
          ),
      },
      {
          "Detail": "Total Carbon Footprint",
          "Value ($ USD)": f"{total_co2e_tons:.2f} Ton CO₂e",
          f"Local ({curr_symbol})": (
              f"Sea: {sea_co2e_tons:.1f}t | Road: {road_co2e_tons:.1f}t"
          ),
      },
  ])
  st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.divider()


# ---------------------------------------------------------
# Dynamic Excel Report Generation
# ---------------------------------------------------------
def generate_excel_bytes():
  wb = openpyxl.Workbook()
  ws = wb.active
  ws.title = "Landed Cost Summary"
  ws.views.sheetView[0].showGridLines = True

  title_str = (
      "דוח מחשבון עלויות יבוא, פחמן ומחזור - Green Logistics"
      if is_heb
      else "Green-Logistics Customs, Carbon & EPR Recycling Report"
  )
  ws["A1"] = title_str
  ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="16A085")

  headers = [
      "רכיב עלות / פרט" if is_heb else "Cost Element / Detail",
      "סכום ($ USD)" if is_heb else "Amount ($ USD)",
      f"סכום במטבע מקומי ({curr_symbol})"
      if is_heb
      else f"Amount ({curr_symbol} Local)",
      "הערות / מדדי קיימות ו-EPR" if is_heb else "Notes, EPR & Sustainability",
  ]
  ws.append([])
  ws.append(headers)

  data = [
      [
          "מדינת מוצא" if is_heb else "Origin Country",
          origin_country,
          origin_country,
          "Origin Location",
      ],
      [
          "סוג הציוד" if is_heb else "Equipment Category",
          equipment_type,
          equipment_type,
          "Equipment Type",
      ],
      [
          "סוג מכולה / סיווג" if is_heb else "Container Type",
          container_type,
          container_type,
          "Safety Category",
      ],
      [
          "כמות מכולות vs נפח" if is_heb else "Containers vs Volume",
          f"{num_containers} Containers",
          (
              f"{bess_mwh_capacity} MWh Capacity"
              if is_bess
              else f"{total_cargo_units} Equipment Units"
          ),
          "Cargo Volume",
      ],
      [
          "נמל פקידה" if is_heb else "Port of Discharge",
          selected_port,
          selected_port,
          "Discharge Port",
      ],
      [
          "מדינת יעד" if is_heb else "Final Destination Country",
          dest_country,
          dest_country,
          "Destination",
      ],
      [
          "יעד סופי באתר" if is_heb else "Final Site Location",
          site_display,
          site_display,
          "Delivery Site",
      ],
      [
          "קוד מכס" if is_heb else "HS Code",
          hs_code,
          hs_code,
          "Tariff Classification",
      ],
      [
          "ערך הסחורה במקור (FOB)" if is_heb else "FOB Cargo Value",
          cargo_value_usd,
          cargo_value_usd * ex_rate,
          "Invoice Amount",
      ],
      [
          "הובלה ימית וטיפול במקור" if is_heb else "Freight & Origin Fees",
          freight_cost_usd + origin_expenses_usd,
          (freight_cost_usd + origin_expenses_usd) * ex_rate,
          "Freight Charges",
      ],
      [
          "ביטוח ימי" if is_heb else "Marine Insurance",
          insurance_cost_usd,
          insurance_cost_usd * ex_rate,
          f"Basis: {insurance_basis}",
      ],
      [
          "ערך CIF כולל" if is_heb else "Total CIF Value",
          cif_value_usd,
          cif_value_loc,
          "Duty Base",
      ],
      [
          "מכס אפקטיבי" if is_heb else "Customs Duty",
          customs_duty_amount_usd,
          customs_duty_loc,
          f"{duty_incentive} ({effective_customs_rate*100:.1f}%)",
      ],
      [
          'מע"מ מקומי' if is_heb else "Local VAT Amount",
          vat_amount_usd,
          vat_amount_loc,
          f"{vat_rate*100:.1f}% Local VAT",
      ],
      [
          "דמי טיפול במסוף (THC)" if is_heb else "Total THC Charges",
          total_thc_usd,
          total_thc_usd * ex_rate,
          f"${thc_fees_usd}/cont. x {num_containers}",
      ],
      [
          "אגרות נמל ועמילות" if is_heb else "Port Fees & Brokerage",
          port_fees_usd + brokerage_fees_usd,
          (port_fees_usd + brokerage_fees_usd) * ex_rate,
          "Port Handling & Clearance",
      ],
      [
          "הובלה יבשתית מיוחדת" if is_heb else "Inland Heavy Haulage",
          total_inland_transport_usd,
          total_inland_transport_usd * ex_rate,
          f"Heavy Haulage ({num_containers} cont.)",
      ],
      [
          "סיכון השהיה בנמל (Demurrage)" if is_heb else "Estimated Demurrage",
          total_demurrage_usd,
          total_demurrage_usd * ex_rate,
          f"{demurrage_excess_days} Excess Days Risk",
      ],
      [
          "הפרשת מחזור סוללות באירופה (EPR)" if is_heb else "EU EPR Battery Recycling Provision",
          total_recycling_provision_usd,
          total_recycling_provision_usd * ex_rate,
          f"${recycling_rate_per_kwh}/kWh End-of-Life Provision",
      ],
      [
          'עלות Landed Cost נטו (ללא מע"מ)'
          if is_heb
          else "Total Net Landed Cost",
          total_landed_cost_net_usd,
          landed_net_loc,
          "Excluding VAT",
      ],
      [
          "עלות ממוצעת למכולה" if is_heb else "Cost per Container",
          cost_per_container_usd,
          cost_per_container_usd * ex_rate,
          f"Divided by {num_containers} containers",
      ],
      [
          "פליטת פחמן כוללת (CO₂e)" if is_heb else "Total Carbon Footprint",
          f"{total_co2e_tons:.2f} Ton CO₂e",
          f"{total_co2e_tons:.2f} Ton CO₂e",
          f"Sea: {sea_co2e_tons:.1f}t | Road: {road_co2e_tons:.1f}t",
      ],
  ]

  for row in data:
    ws.append(row)

  output = io.BytesIO()
  wb.save(output)
  return output.getvalue()


st.subheader(t["export_title"])
st.download_button(
    label=t["btn_excel"],
    data=generate_excel_bytes(),
    file_name=f"Green_Logistics_Landed_Cost_{clean_hs}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
