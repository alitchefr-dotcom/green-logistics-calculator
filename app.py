import io
import openpyxl
import pandas as pd
import plotly.express as px
import streamlit as st
from openpyxl.styles import Font

# ---------------------------------------------------------
# הגדרות עמוד
# ---------------------------------------------------------
st.set_page_config(
    page_title="Green-Logistics Customs & Landed Cost Calculator",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Green-Logistics Customs & Landed Cost Calculator")
st.markdown(
    "מחשבון עלויות יבוא, מכס ומיסוי לתשתיות אנרגיה מתחדשת (**BESS**,"
    " פאנלים סולאריים, ממירים ושנאים)."
)
st.divider()

# ---------------------------------------------------------
# סרגל צד - הזנת נתונים
# ---------------------------------------------------------
st.sidebar.header("🌍 מדינות מסלול השינוע")

origin_country = st.sidebar.selectbox(
    "מדינת מוצא (Origin Country)",
    [
        "China (China)",
        "Germany (Germany)",
        "USA (USA)",
        "India (India)",
        "Japan (Japan)",
        "South Korea (South Korea)",
        "Other (אחר)",
    ],
    index=0,
)

dest_country = st.sidebar.selectbox(
    "מדינת יעד (Destination Country)",
    [
        "Israel (ישראל)",
        "Greece (יוון)",
        "Bulgaria (בולגריה)",
        "Finland (פינלנד)",
        "Romania (רומניה)",
        "Other EU Country (מדינה אחרת באיחוד האירופי)",
    ],
    index=0,
)

st.sidebar.divider()
st.sidebar.header("📋 פרטי המטען והרכיבים")

equipment_type = st.sidebar.selectbox(
    "סוג הציוד (Equipment Category)",
    [
        "BESS Container (מערכות אגירה)",
        "Solar Panels (פאנלים סולאריים)",
        "Inverters & Transformers (ממירים ושנאים)",
        "Wind Turbine Components (טורבינות רוח)",
    ],
)

# מיפוי ברירת מחדל של קוד HS לפי סוג הציוד
hs_defaults = {
    "BESS Container (מערכות אגירה)": "8507.60",
    "Solar Panels (פאנלים סולאריים)": "8541.43",
    "Inverters & Transformers (ממירים ושנאים)": "8504.40",
    "Wind Turbine Components (טורבינות רוח)": "8502.31",
}

hs_code = st.sidebar.text_input(
    "קוד מכס (HS Code)", value=hs_defaults.get(equipment_type, "8507.60")
)

cargo_value = st.sidebar.number_input(
    "ערך הסחורה במקור - Cargo Value ($)",
    min_value=0.0,
    value=150000.0,
    step=1000.0,
)
units_count = st.sidebar.number_input(
    "כמות יחידות/מכולות", min_value=1, value=5, step=1
)

st.sidebar.divider()
st.sidebar.header("🚢 עלויות שרשרת האספקה")

freight_cost = st.sidebar.number_input(
    "הובלה ראשת ימית/אווירית ($)", min_value=0.0, value=12000.0, step=500.0
)
insurance_rate = (
    st.sidebar.number_input(
        "שיעור ביטוח ימי (% Marine Insurance)",
        min_value=0.0,
        value=0.3,
        step=0.05,
    )
    / 100
)
origin_expenses = st.sidebar.number_input(
    "הוצאות במקור ($)", min_value=0.0, value=1500.0, step=100.0
)

st.sidebar.divider()
st.sidebar.header("🏛️ מכס ומיסוי")

customs_rate_input = st.sidebar.number_input(
    "שיעור מכס רשמי (% Customs Duty)", min_value=0.0, value=6.0, step=0.5
)
fta_active = st.sidebar.checkbox(
    "הסכם סחר חופשי פעיל (FTA Exemption)", value=True
)
green_exemption = st.sidebar.checkbox(
    "פטור/הטבה ירוקה ייעודית (Green Incentive)", value=False
)
vat_rate = (
    st.sidebar.number_input(
        'שיעור מע"מ מקומי (% Local VAT)', min_value=0.0, value=17.0, step=1.0
    )
    / 100
)

st.sidebar.divider()
st.sidebar.header("⚓ עלויות נמל ושחרור")

port_handling = st.sidebar.number_input(
    "אגרות נמל ו-THC ($)", min_value=0.0, value=1800.0, step=100.0
)
brokerage_fees = st.sidebar.number_input(
    "עמילות מכס ואישורים ($)", min_value=0.0, value=850.0, step=50.0
)
inland_transport = st.sidebar.number_input(
    "הובלה יבשתית מיוחדת ($)", min_value=0.0, value=3500.0, step=250.0
)

# ---------------------------------------------------------
# מנוע החישובים
# ---------------------------------------------------------
insurance_cost = cargo_value * insurance_rate
cif_value = cargo_value + freight_cost + origin_expenses + insurance_cost

effective_customs_rate = (
    0.0 if (fta_active or green_exemption) else (customs_rate_input / 100)
)
customs_duty_amount = cif_value * effective_customs_rate

vat_base = cif_value + customs_duty_amount
vat_amount = vat_base * vat_rate

local_clearance_total = port_handling + brokerage_fees + inland_transport
total_landed_cost_gross = (
    cif_value + customs_duty_amount + vat_amount + local_clearance_total
)
total_landed_cost_net = total_landed_cost_gross - vat_amount
cost_per_unit = total_landed_cost_net / units_count

# ---------------------------------------------------------
# תצוגת תוצאות בדף + קישורי מכס דינמיים
# ---------------------------------------------------------
st.info(
    f"📍 **מסלול יבוא:** מ-**{origin_country}** ל-**{dest_country}** | **HS Code"
    f" מוגדר:** `{hs_code}`"
)

# קישור דינמי למס/מכס לפי מדינת היעד
clean_hs = hs_code.replace(".", "").strip()

if "Israel" in dest_country:
  customs_url = f"https://www.gov.il/he/departments/dynamiccollectors/customs-tariff?tariffNumber={clean_hs}"
  link_text = "🔗 לחץ כאן לבדיקת שיעורי מכס ופטורים בתעריף המכס הישראלי (רשות המסים)"
else:
  customs_url = f"https://trade.ec.europa.eu/access-to-markets/en/home?product_code={clean_hs}"
  link_text = f"🔗 לחץ כאן לבדיקת שיעורי מכס והסכמי סחר בפורטל Access2Markets עבור {dest_country}"

st.markdown(f"[{link_text}]({customs_url})")

if "BESS" in equipment_type:
  st.warning(
      "⚠️ **התראת שינוע תשתיות אגירה (BESS):** מכולות BESS מחייבות בדיקת עומסי"
      " סרנים, היתרי מעבר מיוחדים בכבישים ותיאום מלווים מראש."
  )

col1, col2, col3, col4 = st.columns(4)
col1.metric("ערך CIF כולל", f"${cif_value:,.2f}")
col2.metric(
    "תשלום מכס אפקטיבי",
    f"${customs_duty_amount:,.2f}",
    f"{effective_customs_rate*100:.1f}%",
)
col3.metric('מע"מ לתשלום', f"${vat_amount:,.2f}")
col4.metric('עלות Landed Cost נטו (ללא מע"מ)', f"${total_landed_cost_net:,.2f}")

st.divider()

left_col, right_col = st.columns([1, 1])

with left_col:
  st.subheader("📊 התפלגות עלויות היבוא (Landed Cost Breakdown)")
  cost_data = pd.DataFrame({
      "רכיב עלות": [
          "ערך ציוד (FOB)",
          "הובלה ימית וביטוח",
          "מכס",
          "עלויות נמל ושחרור",
          "הובלה יבשתית (Inland)",
      ],
      "סכום ($)": [
          cargo_value,
          freight_cost + origin_expenses + insurance_cost,
          customs_duty_amount,
          port_handling + brokerage_fees,
          inland_transport,
      ],
  })
  fig = px.pie(
      cost_data,
      values="סכום ($)",
      names="רכיב עלות",
      hole=0.4,
      color_discrete_sequence=px.colors.qualitative.Pastel,
  )
  fig.update_traces(textposition="inside", textinfo="percent+label")
  st.plotly_chart(fig, use_container_width=True)

with right_col:
  st.subheader("📑 טבלת סיכום שלבי החישוב")
  summary_df = pd.DataFrame([
      {"שלב": "מדינת מוצא / מדינת יעד", "סכום ($)": f"{origin_country} ➔ {dest_country}"},
      {"שלב": "קוד מכס (HS Code)", "סכום ($)": hs_code},
      {"שלב": "ערך הסחורה (FOB/EXW)", "סכום ($)": f"${cargo_value:,.2f}"},
      {
          "שלב": "הובלה ימית + הוצאות במקור",
          "סכום ($)": f"${freight_cost + origin_expenses:,.2f}",
      },
      {"שלב": "ביטוח ימי", "סכום ($)": f"${insurance_cost:,.2f}"},
      {"שלב": "ערך CIF כולל (בסיס למכס)", "סכום ($)": f"${cif_value:,.2f}"},
      {"שלב": "מכס אפקטיבי לתשלום", "סכום ($)": f"${customs_duty_amount:,.2f}"},
      {'שלב': 'בסיס לחישוב מע"מ', "סכום ($)": f"${vat_base:,.2f}"},
      {'שלב': 'מע"מ מקומי לתשלום', "סכום ($)": f"${vat_amount:,.2f}"},
      {
          "שלב": "אגרות נמל, THC ועמילות",
          "סכום ($)": f"${port_handling + brokerage_fees:,.2f}",
      },
      {
          "שלב": "הובלה יבשתית לאתר הפרויקט",
          "סכום ($)": f"${inland_transport:,.2f}",
      },
      {
          'שלב': 'עלות כוללת ליחידה/מכולה (נטו)',
          "סכום ($)": f"${cost_per_unit:,.2f}",
      },
  ])
  st.dataframe(
      summary_df,
      use_container_width=True,
      hide_index=True,
  )

st.divider()


# ---------------------------------------------------------
# פונקציה לייצוא Excel
# ---------------------------------------------------------
def generate_excel_bytes():
  wb = openpyxl.Workbook()
  ws = wb.active
  ws.title = "Landed Cost Summary"
  ws.views.sheetView[0].showGridLines = True

  ws["A1"] = "Green-Logistics Customs & Landed Cost Report"
  ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="16A085")

  headers = ["שלב / רכיב עלות", "ערך / סכום ($)", "הערות"]
  ws.append([])
  ws.append(headers)

  data = [
      ["מדינת מוצא", origin_country, "Origin"],
      ["מדינת יעד", dest_country, "Destination"],
      ["קוד מכס (HS Code)", hs_code, "Classification"],
      ["ערך הסחורה במקור (FOB/EXW)", cargo_value, "חשבונית ספק"],
      [
          "הובלה ימית + הוצאות במקור",
          freight_cost + origin_expenses,
          "הובלה וטיפול במקור",
      ],
      ["ביטוח ימי", insurance_cost, f"שיעור {insurance_rate*100:.2f}%"],
      ["ערך CIF כולל (בסיס למכס)", cif_value, "בסיס למכס בנמל"],
      [
          "מכס אפקטיבי לתשלום",
          customs_duty_amount,
          (
              "פטור הסכם סחר"
              if effective_customs_rate == 0
              else f"{effective_customs_rate*100}%"
          ),
      ],
      ['מע"מ מקומי לתשלום', vat_amount, f'{vat_rate*100}% מע"מ'],
      ["אגרות נמל ועמילות", port_handling + brokerage_fees, "THC ועמילות מכס"],
      [
          "הובלה יבשתית לאתר הפרויקט",
          inland_transport,
          "הובלה כבדה / מיוחדת",
      ],
      [
          'עלות Landed Cost נטו (ללא מע"מ)',
          total_landed_cost_net,
          "עלות יבוא מחושבת נטו",
      ],
      [
          "עלות ממוצעת ליחידה/מכולה",
          cost_per_unit,
          f"חלוקה ל-{units_count} יחידות",
      ],
  ]

  for row in data:
    ws.append(row)

  output = io.BytesIO()
  wb.save(output)
  return output.getvalue()


# ---------------------------------------------------------
# כפתור הורדה Excel בממשק
# ---------------------------------------------------------
st.subheader("📥 ייצוא נתונים")

st.download_button(
    label="📊 הורד דוח Excel מחושב",
    data=generate_excel_bytes(),
    file_name=f"Green_Logistics_Landed_Cost_{clean_hs}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
