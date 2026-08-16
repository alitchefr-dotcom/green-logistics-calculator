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
    "cargo_header": (
        "📋 פרטי המטען, משקל וקוד מכס"
        if is_heb
        else "📋 Cargo Specifications & Classification"
    ),
    "equipment": "סוג הציוד" if is_heb else "Equipment Category",
    "hs": "קוד מכס (HS Code)" if is_heb else "HS Code",
    "units": "כמות יחידות/מכולות" if is_heb else "Number of Units / Containers",
    "weight": (
        "משקל ברוטו ליחידה (טון)"
        if is_heb
        else "Gross Weight per Unit (Tonnes)"
    ),
    "cargo_val": (
        "ערך הסחורה במקור ($)" if is_heb else "Cargo FOB / EXW Value ($)"
    ),
    "freight_header": (
        "🚢 עלויות שרשרת האספקה הימית"
        if is_heb
        else "🚢 Freight & Supply Chain Costs"
    ),
    "freight": "הובלה ימית ראשת ($)" if is_heb else "Main Ocean Freight ($)",
    "insurance": (
        "שיעור ביטוח ימי (%)" if is_heb else "Marine Insurance Rate (%)"
    ),
    "origin_exp": (
        "הוצאות במקור ($)" if is_heb else "Origin Local Expenses ($)"
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
    "port_fees": "אגרות נמל וסדרנות ($)" if is_heb else "Port Wharfage & Handling ($)",
    "thc": (
        "דמי טיפול במסוף (THC) ליחידה ($)"
        if is_heb
        else "Terminal Handling Charge (THC) per Unit ($)"
    ),
    "brokerage": (
        "עמילות מכס ואישורים ($)"
        if is_heb
        else "Customs Brokerage, Classification & Permits ($)"
    ),
    "inland": (
        "הובלה יבשתית מיוחדת/חורגת ($)"
        if is_heb
        else "Special Heavy Inland Haulage ($)"
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
    [
        "China",
        "Germany",
        "USA",
        "India",
        "Japan",
        "South Korea",
        "Other / אחר",
    ],
    index=0,
)

port_defaults = {
    "Port of Haifa / Bayport (Israel)": {"dest": "Israel", "vat": 18.0},
    "Port of Ashdod (Israel)": {"dest": "Israel", "vat": 18.0},
    "Port of Burgas (Bulgaria)": {
        "dest": "Bulgaria / Transit to Romania",
        "vat": 20.0,
    },
    "Port of Piraeus / Thessaloniki (Greece)": {
        "dest": "Greece",
        "vat": 24.0,
    },
    "Port of Rauma / Vuosaari (Finland)": {"dest": "Finland", "vat": 25.5},
    "Port of Constanta (Romania)": {"dest": "Romania", "vat": 19.0},
    "Port of Rotterdam / Antwerp (EU Main Port)": {
        "dest": "EU Main Port",
        "vat": 21.0,
    },
    "Other Port": {"dest": "Other", "vat": 18.0},
}

selected_port = st.sidebar.selectbox(
    t["port"], list(port_defaults.keys()), index=0
)

dest_info = port_defaults[selected_port]
dest_country = st.sidebar.text_input(t["dest"], value=dest_info["dest"])

final_destination = st.sidebar.text_input(
    t["final_dest"],
    value="Carmiel Industrial Zone / GPS: 32.9199, 35.2901",
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

hs_defaults = {
    "BESS Container (Battery Energy Storage Systems)": "8507.60",
    "MVS - Medium Voltage Stations / Skids": "8504.22",
    "MVS Accessories & Switchgear": "8537.20",
    "Solar Panels (PV Modules)": "8541.43",
    "Inverters & Transformers": "8504.40",
    "Wind Turbine Components": "8502.31",
}

# Real MFN Duty Rates for EU/Non-Israel (BESS = 2.7%, Solar = 0.0%, MVS = 2.1%)
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

units_count = st.sidebar.number_input(
    t["units"], min_value=1, value=5, step=1
)

container_weight = st.sidebar.number_input(
    t["weight"],
    min_value=1.0,
    max_value=100.0,
    value=35.0 if "MVS" in equipment_type else 45.0,
    step=1.0,
)

total_weight = container_weight * units_count

cargo_value = st.sidebar.number_input(
    t["cargo_val"], min_value=0.0, value=150000.0, step=1000.0
)

st.sidebar.divider()
st.sidebar.header(t["freight_header"])

freight_cost = st.sidebar.number_input(
    t["freight"], min_value=0.0, value=12000.0, step=500.0
)
insurance_rate = (
    st.sidebar.number_input(
        t["insurance"], min_value=0.0, value=0.3, step=0.05
    )
    / 100
)
origin_expenses = st.sidebar.number_input(
    t["origin_exp"], min_value=0.0, value=1500.0, step=100.0
)

st.sidebar.divider()
st.sidebar.header(t["tax_header"])

# Dynamic Duty logic: 0% for Israel; real EU MFN rate (e.g. 2.7% for BESS) otherwise
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
green_exemption = st.sidebar.checkbox(t["green"], value=False)

vat_rate = (
    st.sidebar.number_input(
        t["vat"],
        min_value=0.0,
        value=float(dest_info["vat"]),
        step=0.5,
    )
    / 100
)

st.sidebar.divider()
st.sidebar.header(t["port_header"])

port_fees = st.sidebar.number_input(
    t["port_fees"], min_value=0.0, value=1200.0, step=50.0
)
thc_fees = st.sidebar.number_input(
    t["thc"], min_value=0.0, value=350.0, step=25.0
)
total_thc = thc_fees * units_count

brokerage_fees = st.sidebar.number_input(
    t["brokerage"], min_value=0.0, value=850.0, step=50.0
)
inland_transport = st.sidebar.number_input(
    t["inland"], min_value=0.0, value=4500.0, step=250.0
)

# ---------------------------------------------------------
# Calculations
# ---------------------------------------------------------
insurance_cost = cargo_value * insurance_rate
cif_value = cargo_value + freight_cost + origin_expenses + insurance_cost

effective_customs_rate = (
    0.0
    if (fta_active or green_exemption or "Israel" in dest_country)
    else (customs_rate_input / 100)
)
customs_duty_amount = cif_value * effective_customs_rate

vat_base = cif_value + customs_duty_amount
vat_amount = vat_base * vat_rate

local_clearance_total = (
    port_fees + total_thc + brokerage_fees + inland_transport
)
total_landed_cost_gross = (
    cif_value + customs_duty_amount + vat_amount + local_clearance_total
)
total_landed_cost_net = total_landed_cost_gross - vat_amount
cost_per_unit = total_landed_cost_net / units_count

# ---------------------------------------------------------
# UI Display & Alerts
# ---------------------------------------------------------
if is_heb:
  st.info(
      f"📍 **מסלול:** מ-**{origin_country}** דרך **{selected_port}** ➔"
      f" **{dest_country}** | **אתר מסירה:** `{final_destination}` | **HS"
      f" Code:** `{hs_code}`"
  )
else:
  st.info(
      f"📍 **Route:** From **{origin_country}** via **{selected_port}** ➔"
      f" **{dest_country}** | **Site:** `{final_destination}` | **HS"
      f" Code:** `{hs_code}`"
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

if "Israel" in dest_country:
  if is_heb:
    st.success(
        "💡 **הערת מכס ישראל:** BESS, MVS וציוד סולארי פטורים ממכס בישראל (0%"
        ' מכס). שיעור המע"מ הינו **18%**.'
    )
  else:
    st.success(
        "💡 **Israel Customs Note:** BESS, MVS, and Solar equipment are duty"
        " exempt (0% Duty) in Israel. VAT is **18%**."
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
col1.metric(t["cif_metric"], f"${cif_value:,.2f}")
col2.metric(
    t["duty_metric"],
    f"${customs_duty_amount:,.2f}",
    f"{effective_customs_rate*100:.1f}%",
)
col3.metric(f"{t['vat_metric']} ({vat_rate*100:.1f}%)", f"${vat_amount:,.2f}")
col4.metric(t["landed_metric"], f"${total_landed_cost_net:,.2f}")

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
      "Amount ($)": [
          cargo_value,
          freight_cost + origin_expenses + insurance_cost,
          customs_duty_amount,
          port_fees + total_thc,
          brokerage_fees,
          inland_transport,
      ],
  })
  fig = px.pie(
      cost_data,
      values="Amount ($)",
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
          "Value": f"{origin_country} ➔ {selected_port}",
      },
      {"Detail": "Equipment / ציוד", "Value": equipment_type},
      {"Detail": "Site / יעד", "Value": final_destination},
      {"Detail": "HS Code", "Value": hs_code},
      {
          "Detail": "Total Weight / משקל",
          "Value": f"{total_weight:.1f} Tonnes ({container_weight} T/unit)",
      },
      {"Detail": "FOB Value / ערך ציוד", "Value": f"${cargo_value:,.2f}"},
      {
          "Detail": "Ocean Freight / הובלה ימית",
          "Value": f"${freight_cost + origin_expenses:,.2f}",
      },
      {"Detail": "Insurance / ביטוח", "Value": f"${insurance_cost:,.2f}"},
      {"Detail": "CIF Value / ערך CIF", "Value": f"${cif_value:,.2f}"},
      {"Detail": "Customs Duty / מכס", "Value": f"${customs_duty_amount:,.2f}"},
      {
          "Detail": f"Local VAT ({vat_rate*100:.1f}%)",
          "Value": f"${vat_amount:,.2f}",
      },
      {"Detail": "Port Wharfage / אגרות נמל", "Value": f"${port_fees:,.2f}"},
      {
          "Detail": f"Total THC ({units_count} units)",
          "Value": f"${total_thc:,.2f}",
      },
      {"Detail": "Brokerage / עמילות", "Value": f"${brokerage_fees:,.2f}"},
      {"Detail": "Inland Haulage / הובלה יבשתית", "Value": f"${inland_transport:,.2f}"},
      {
          "Detail": "Net Cost per Unit / עלות ליחידה",
          "Value": f"${cost_per_unit:,.2f}",
      },
  ])
  st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.divider()


# ---------------------------------------------------------
# Excel Report Generation
# ---------------------------------------------------------
def generate_excel_bytes():
  wb = openpyxl.Workbook()
  ws = wb.active
  ws.title = "Landed Cost Summary"
  ws.views.sheetView[0].showGridLines = True

  ws["A1"] = "Green-Logistics Customs & Landed Cost Report"
  ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="16A085")

  headers = ["Cost Element / Detail", "Value / Amount ($)", "Notes"]
  ws.append([])
  ws.append(headers)

  data = [
      ["Origin Country", origin_country, "Origin"],
      ["Equipment Category", equipment_type, "Equipment Category"],
      ["Port of Discharge", selected_port, "Discharge Port"],
      ["Final Destination Country", dest_country, "Destination Country"],
      ["Final Site Location", final_destination, "Delivery Location"],
      ["HS Code", hs_code, "Tariff Classification"],
      [
          "Unit Weight",
          f"{container_weight} Tonnes",
          f"Total {total_weight} Tonnes for {units_count} units",
      ],
      ["FOB Value", cargo_value, "Commercial Invoice"],
      [
          "Freight + Origin Fees",
          freight_cost + origin_expenses,
          "Main Freight & Origin",
      ],
      ["Marine Insurance", insurance_cost, f"Rate: {insurance_rate*100:.2f}%"],
      ["Total CIF Value", cif_value, "Duty Valuation Base"],
      [
          "Customs Duty",
          customs_duty_amount,
          "Duty Free (Israel) / FTA Exemption",
      ],
      ["Local VAT", vat_amount, f"{vat_rate*100:.1f}% VAT at Port of Entry"],
      ["Port Wharfage & Handling", port_fees, "Port Terminal Fees"],
      ["Total THC", total_thc, f"${thc_fees}/unit x {units_count} units"],
      ["Brokerage & Permits", brokerage_fees, "Customs Brokerage & Clearance"],
      ["Inland Heavy Haulage", inland_transport, "Special Heavy Transport"],
      [
          "Total Net Landed Cost (excl. VAT)",
          total_landed_cost_net,
          "Total Net Import Cost",
      ],
      [
          "Cost per Unit / Container",
          cost_per_unit,
          f"Divided across {units_count} units",
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
