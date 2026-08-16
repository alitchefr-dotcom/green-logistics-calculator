import io
import openpyxl
import pandas as pd
import plotly.express as px
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
        "⚡ מחשבון עלויות יבוא, מכס ו-Landed Cost"
        if is_heb
        else "⚡ Green-Logistics Customs & Landed Cost Calculator"
    ),
    "subtitle": (
        "מחשבון עלויות יבוא, מכס, רגולציה ו-Landed Cost לתשתיות אנרגיה"
        " מתחדשת (**BESS**, **MVS**, פאנלים סולאריים, ממירים ושנאים)."
        if is_heb
        else (
            "Import Duty, Tax, Regulatory & Landed Cost Calculator for"
            " Renewable Energy Infrastructure (**BESS**, **MVS Skids**, Solar"
            " Panels, Inverters & Transformers)."
        )
    ),
    "route_header": (
        "🌍 מסלול השינוע והנמלים" if is_heb else "🌍 Shipping Route & Ports"
    ),
    "origin": "מדינת מוצא" if is_heb else "Origin Country",
    "port": "נמל פקידה / שחרור" if is_heb else "Port of Discharge",
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
        "📋 פרטי המטען, מכולות וקוד מכס"
        if is_heb
        else "📋 Cargo, Container Specifications & Classification"
    ),
    "equipment": "סוג הציוד" if is_heb else "Equipment Category",
    "container_type": (
        "סוג מכולה / רמת סיכון"
        if is_heb
        else "Container Type & Hazard Category"
    ),
    "hs": "קוד מכס (HS Code)" if is_heb else "HS Code",
    "units": "כמות יחידות/מכולות" if is_heb else "Number of Units / Containers",
    "weight": (
        "משקל ברוטו ליחידה (טון)"
        if is_heb
        else "Gross Weight per Unit (Tonnes)"
    ),
    "cargo_val": (
        "ערך הסחורה במקור ($ USD)"
        if is_heb
        else "Cargo FOB / EXW Value ($ USD)"
    ),
    "freight_header": (
        "🚢 עלויות שרשרת האספקה הימית"
        if is_heb
        else "🚢 Freight & Supply Chain Costs"
    ),
    "freight": (
        "הובלה ימית ראשת ($ USD)" if is_heb else "Main Ocean Freight ($ USD)"
    ),
    "insurance": (
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
    "fta": (
        "הסכם סחר חופשי פעיל (FTA)"
        if is_heb
        else "Free Trade Agreement (FTA Exemption)"
    ),
    "fta_note": (
        "⚠️ דורש תעודת מקור תקפה (EUR.1 / COO)"
        if is_heb
        else "⚠️ Requires valid Certificate of Origin (EUR.1 / COO)"
    ),
    "green": (
        "פטור/הטבה ירוקה ייעודית"
        if is_heb
        else "Green Incentive / Special Exemption"
    ),
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
        "דמי טיפול במסוף (THC) ליחידה ($ USD)"
        if is_heb
        else "Terminal Handling Charge (THC) per Unit ($ USD)"
    ),
    "brokerage": (
        "עמילות מכס ואישורים ($ USD)"
        if is_heb
        else "Customs Brokerage & Permits ($ USD)"
    ),
    "inland_per_unit": (
        "הובלה יבשתית מיוחדת ליחידה ($ USD)"
        if is_heb
        else "Special Heavy Inland Haulage per Unit ($ USD)"
    ),
    "demurrage_header": (
        "⏱️ ניהול סיכוני השהיה בנמל (Demurrage)"
        if is_heb
        else "⏱️ Port Demurrage Risk Estimator"
    ),
    "free_days": (
        "ימים חופשיים בנמל (Free Days)"
        if is_heb
        else "Port Free Days Included"
    ),
    "demurrage_rate": (
        "עלות השהיה יומית למכולה ($/Day)"
        if is_heb
        else "Daily Demurrage Rate per Container ($/Day)"
    ),
    "cif_metric": "ערך CIF כולל" if is_heb else "Total CIF Value",
    "duty_metric": "תשלום מכס אפקטיבי" if is_heb else "Effective Duty",
    "vat_metric": 'מע"מ לתשלום' if is_heb else "VAT Payable",
    "landed_metric": (
        'עלות Landed Cost נטו (ללא מע"מ)'
        if is_heb
        else "Net Landed Cost (excl. VAT)"
    ),
    "breakdown_title": (
        "📊 התפלגות עלויות היבוא" if is_heb else "📊 Landed Cost Breakdown"
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

origin_country = st.sidebar.selectbox(
    t["origin"],
    ["China", "Germany", "USA", "India", "Japan", "South Korea", "Other / אחר"],
    index=0,
)

port_defaults = {
    "Port of Haifa / Bayport (Israel)": {
        "dest": "Israel",
        "vat": 18.0,
        "curr": "₪ ILS",
        "sym": "₪",
        "rate": 3.70,
        "site": "Carmiel Industrial Zone / GPS: 32.9199, 35.2901",
    },
    "Port of Ashdod (Israel)": {
        "dest": "Israel",
        "vat": 18.0,
        "curr": "₪ ILS",
        "sym": "₪",
        "rate": 3.70,
        "site": "Carmiel Industrial Zone / GPS: 32.9199, 35.2901",
    },
    "Port of Burgas (Bulgaria)": {
        "dest": "Bulgaria / Transit to Romania",
        "vat": 20.0,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "",
    },
    "Port of Piraeus / Thessaloniki (Greece)": {
        "dest": "Greece",
        "vat": 24.0,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "",
    },
    "Port of Rauma / Vuosaari (Finland)": {
        "dest": "Finland",
        "vat": 25.5,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "",
    },
    "Port of Constanta (Romania)": {
        "dest": "Romania",
        "vat": 19.0,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "",
    },
    "Port of Rotterdam / Antwerp (EU Main Port)": {
        "dest": "EU Main Port",
        "vat": 21.0,
        "curr": "€ EUR",
        "sym": "€",
        "rate": 0.92,
        "site": "",
    },
    "Other Port": {
        "dest": "Other",
        "vat": 18.0,
        "curr": "$ USD",
        "sym": "$",
        "rate": 1.00,
        "site": "",
    },
}

selected_port = st.sidebar.selectbox(
    t["port"], list(port_defaults.keys()), index=0
)
dest_info = port_defaults[selected_port]
dest_country = st.sidebar.text_input(t["dest"], value=dest_info["dest"])

final_destination = st.sidebar.text_input(
    t["final_dest"],
    value=dest_info["site"],
    key=f"final_site_{selected_port}",
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
        "BESS Container (Battery Energy Storage Systems)",
        "MVS - Medium Voltage Stations / Skids",
        "MVS Accessories & Switchgear",
        "Solar Panels (PV Modules)",
        "Inverters & Transformers",
        "Wind Turbine Components",
    ],
)

container_thc_defaults = {
    "20ft SOC Container (BESS / MVS Skids)": 350.0,
    "40ft / 40HC Standard Dry Container": 280.0,
    "40ft / 40HC Dangerous Goods (DG / Hazmat Class 9)": 520.0,
    "Special Equipment (Open Top / Flat Rack)": 480.0,
}

container_type = st.sidebar.selectbox(
    t["container_type"],
    list(container_thc_defaults.keys()),
    index=0 if "BESS" in equipment_type or "MVS" in equipment_type else 1,
)

default_thc_value = container_thc_defaults[container_type]

hs_defaults = {
    "BESS Container (Battery Energy Storage Systems)": "8507.60",
    "MVS - Medium Voltage Stations / Skids": "8504.22",
    "MVS Accessories & Switchgear": "8537.20",
    "Solar Panels (PV Modules)": "8541.43",
    "Inverters & Transformers": "8504.40",
    "Wind Turbine Components": "8502.31",
}

eu_mfn_customs_rates = {
    "BESS Container (Battery Energy Storage Systems)": 2.7,
    "MVS - Medium Voltage Stations / Skids": 2.1,
    "MVS Accessories & Switchgear": 2.1,
    "Solar Panels (PV Modules)": 0.0,
    "Inverters & Transformers": 2.1,
    "Wind Turbine Components": 2.7,
}

hs_code = st.sidebar.text_input(
    t["hs"], value=hs_defaults.get(equipment_type, "8507.60")
)
units_count = st.sidebar.number_input(t["units"], min_value=1, value=5, step=1)
container_weight = st.sidebar.number_input(
    t["weight"],
    min_value=1.0,
    max_value=100.0,
    value=35.0 if "MVS" in equipment_type else 45.0,
    step=1.0,
)
total_weight = container_weight * units_count
cargo_value_usd = st.sidebar.number_input(
    t["cargo_val"], min_value=0.0, value=150000.0, step=1000.0
)

st.sidebar.divider()
st.sidebar.header(t["freight_header"])
freight_cost_usd = st.sidebar.number_input(
    t["freight"], min_value=0.0, value=12000.0, step=500.0
)
insurance_rate = (
    st.sidebar.number_input(t["insurance"], min_value=0.0, value=0.3, step=0.05)
    / 100
)
origin_expenses_usd = st.sidebar.number_input(
    t["origin_exp"], min_value=0.0, value=1500.0, step=100.0
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
fta_active = st.sidebar.checkbox(
    t["fta"], value=True if default_customs == 0 else False
)
if fta_active:
  st.sidebar.caption(t["fta_note"])

green_exemption = st.sidebar.checkbox(t["green"], value=False)
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
total_thc_usd = thc_fees_usd * units_count

brokerage_fees_usd = st.sidebar.number_input(
    t["brokerage"], min_value=0.0, value=850.0, step=50.0
)

inland_per_unit_usd = st.sidebar.number_input(
    t["inland_per_unit"], min_value=0.0, value=900.0, step=50.0
)
total_inland_transport_usd = inland_per_unit_usd * units_count

st.sidebar.divider()
st.sidebar.header(t["demurrage_header"])

# Allows 0 port free days
free_days = st.sidebar.number_input(t["free_days"], min_value=0, value=14, step=1)

demurrage_daily_rate = st.sidebar.number_input(
    t["demurrage_rate"], min_value=0.0, value=120.0, step=10.0
)

# ---------------------------------------------------------
# Calculations
# ---------------------------------------------------------
insurance_cost_usd = cargo_value_usd * insurance_rate
cif_value_usd = (
    cargo_value_usd + freight_cost_usd + origin_expenses_usd + insurance_cost_usd
)

effective_customs_rate = (
    0.0
    if (fta_active or green_exemption or "Israel" in dest_country)
    else (customs_rate_input / 100)
)
customs_duty_amount_usd = cif_value_usd * effective_customs_rate

vat_base_usd = cif_value_usd + customs_duty_amount_usd
vat_amount_usd = vat_base_usd * vat_rate

local_clearance_total_usd = (
    port_fees_usd
    + total_thc_usd
    + brokerage_fees_usd
    + total_inland_transport_usd
)
total_landed_cost_gross_usd = (
    cif_value_usd
    + customs_duty_amount_usd
    + vat_amount_usd
    + local_clearance_total_usd
)
total_landed_cost_net_usd = total_landed_cost_gross_usd - vat_amount_usd
cost_per_unit_usd = total_landed_cost_net_usd / units_count

# Local currency conversions
cif_value_loc = cif_value_usd * ex_rate
customs_duty_loc = customs_duty_amount_usd * ex_rate
vat_amount_loc = vat_amount_usd * ex_rate
landed_net_loc = total_landed_cost_net_usd * ex_rate
cost_per_unit_loc = cost_per_unit_usd * ex_rate

# ---------------------------------------------------------
# UI Display & Alerts
# ---------------------------------------------------------
site_display = final_destination if final_destination else "N/A"
if is_heb:
  st.info(
      f"📍 **מסלול:** מ-**{origin_country}** דרך **{selected_port}** ➔"
      f" **{dest_country}** | **סוג מכולה:** `{container_type}` | **אתר"
      f" מסירה:** `{site_display}`"
  )
else:
  st.info(
      f"📍 **Route:** From **{origin_country}** via **{selected_port}** ➔"
      f" **{dest_country}** | **Container:** `{container_type}` | **Site:**"
      f" `{site_display}`"
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

with left_col:
  st.subheader(t["breakdown_title"])
  cost_data = pd.DataFrame({
      "Cost Element": [
          "FOB Equipment" if not is_heb else "ערך ציוד (FOB)",
          "Freight & Ins." if not is_heb else "הובלה וביטוח",
          "Customs Duty" if not is_heb else "מכס",
          "Port & THC" if not is_heb else "אגרות נמל ו-THC",
          "Brokerage" if not is_heb else "עמילות מכס",
          "Inland Haulage" if not is_heb else "הובלה יבשתית",
      ],
      "Amount ($ USD)": [
          cargo_value_usd,
          freight_cost_usd + origin_expenses_usd + insurance_cost_usd,
          customs_duty_amount_usd,
          port_fees_usd + total_thc_usd,
          brokerage_fees_usd,
          total_inland_transport_usd,
      ],
  })
  fig = px.pie(
      cost_data,
      values="Amount ($ USD)",
      names="Cost Element",
      hole=0.4,
      color_discrete_sequence=px.colors.qualitative.Pastel,
  )
  fig.update_traces(textposition="inside", textinfo="percent+label")
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
          "Detail": "Site / יעד",
          "Value ($ USD)": site_display,
          f"Local ({curr_symbol})": f"Ex-Rate: {ex_rate}",
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
          "Detail": "Port Wharfage & Handling",
          "Value ($ USD)": f"${port_fees_usd:,.2f}",
          f"Local ({curr_symbol})": (
              f"{curr_symbol}{port_fees_usd*ex_rate:,.2f}"
          ),
      },
      {
          "Detail": f"Total THC ({units_count} units)",
          "Value ($ USD)": f"${total_thc_usd:,.2f}",
          f"Local ({curr_symbol})": (
              f"{curr_symbol}{total_thc_usd*ex_rate:,.2f}"
          ),
      },
      {
          "Detail": "Brokerage & Permits",
          "Value ($ USD)": f"${brokerage_fees_usd:,.2f}",
          f"Local ({curr_symbol})": (
              f"{curr_symbol}{brokerage_fees_usd*ex_rate:,.2f}"
          ),
      },
      {
          "Detail": f"Inland Heavy Haulage ({units_count} units)",
          "Value ($ USD)": f"${total_inland_transport_usd:,.2f}",
          f"Local ({curr_symbol})": (
              f"{curr_symbol}{total_inland_transport_usd*ex_rate:,.2f}"
          ),
      },
      {
          "Detail": "Net Landed Cost per Unit",
          "Value ($ USD)": f"${cost_per_unit_usd:,.2f}",
          f"Local ({curr_symbol})": f"{curr_symbol}{cost_per_unit_loc:,.2f}",
      },
  ])
  st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.divider()


# ---------------------------------------------------------
# Dynamic Language Excel Report Generation
# ---------------------------------------------------------
def generate_excel_bytes():
  wb = openpyxl.Workbook()
  ws = wb.active
  ws.title = "Landed Cost Summary"
  ws.views.sheetView[0].showGridLines = True

  title_str = (
      "דוח מחשבון עלויות יבוא - Green Logistics"
      if is_heb
      else "Green-Logistics Customs & Landed Cost Report"
  )
  ws["A1"] = title_str
  ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="16A085")

  headers = [
      "רכיב עלות / פרט" if is_heb else "Cost Element / Detail",
      "סכום ($ USD)" if is_heb else "Amount ($ USD)",
      f"סכום במטבע מקומי ({curr_symbol})"
      if is_heb
      else f"Amount ({curr_symbol} Local)",
      "הערות רגולציה" if is_heb else "Notes",
  ]
  ws.append([])
  ws.append(headers)

  data = [
      [
          "מדינת מוצא" if is_heb else "Origin Country",
          origin_country,
          origin_country,
          "Shipping Origin",
      ],
      [
          "סוג הציוד" if is_heb else "Equipment Category",
          equipment_type,
          equipment_type,
          "Cargo Type",
      ],
      [
          "סוג מכולה / סיווג" if is_heb else "Container Type",
          container_type,
          container_type,
          "Container Category",
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
          "Delivery Location",
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
          "ערך CIF כולל" if is_heb else "Total CIF Value",
          cif_value_usd,
          cif_value_loc,
          "Duty Base",
      ],
      [
          "מכס אפקטיבי" if is_heb else "Customs Duty",
          customs_duty_amount_usd,
          customs_duty_loc,
          f"{effective_customs_rate*100:.1f}% Rate",
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
          f"${thc_fees_usd}/unit x {units_count}",
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
          f"Heavy Haulage ({units_count} units)",
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
          "עלות ממוצעת ליחידה" if is_heb else "Net Cost per Unit",
          cost_per_unit_usd,
          cost_per_unit_loc,
          f"Divided by {units_count} units",
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
