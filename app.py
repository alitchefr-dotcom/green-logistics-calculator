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
    "מחשבון עלויות יבוא, מכס, רגולציה ו-Landed Cost לתשתיות אנרגיה מתחדשת"
    " (**BESS**, פאנלים סולאריים, ממירים ושנאים)."
)
st.divider()

# ---------------------------------------------------------
# סרגל צד - הזנת נתונים
# ---------------------------------------------------------
st.sidebar.header("🌍 מסלול השינוע והנמלים")

origin_country = st.sidebar.selectbox(
    "מדינת מוצא (Origin Country)",
    [
        'China (סין)',
        'Germany (גרמניה)',
        'USA (ארה"ב)',
        "India (הודו)",
        "Japan (יפן)",
        "South Korea (קוריאה)",
        "Other (אחר)",
    ],
    index=0,
)

# מיפוי נמלי פקידה נפוצים ומע"מ אוטומטי
port_defaults = {
    "Port of Haifa / Bayport (נמל חיפה / המפרץ - ישראל)": {
        "dest": "Israel (ישראל)",
        "vat": 18.0,
    },
    "Port of Ashdod (נמל אשדוד - ישראל)": {
        "dest": "Israel (ישראל)",
        "vat": 18.0,
    },
    "Port of Burgas (נמל בורגס - בולגריה)": {
        "dest": "Bulgaria (בולגריה / מעבר לרומניה)",
        "vat": 20.0,
    },
    "Port of Piraeus / Thessaloniki (יוון)": {
        "dest": "Greece (יוון)",
        "vat": 24.0,
    },
    "Port of Rauma / Vuosaari (פינלנד)": {
        "dest": "Finland (פינלנד)",
        "vat": 25.5,
    },
    "Port of Constanta (רומניה)": {"dest": "Romania (רומניה)", "vat": 19.0},
    "Port of Rotterdam / Antwerp (אירופה - כללי)": {
        "dest": "EU Main Port",
        "vat": 21.0,
    },
    "Other Port (נמל אחר)": {"dest": "Other", "vat": 18.0},
}

selected_port = st.sidebar.selectbox(
    "נמל פקידה / שחרור (Port of Discharge)",
    list(port_defaults.keys()),
    index=0,
)

dest_info = port_defaults[selected_port]
dest_country = st.sidebar.text_input(
    "מדינת יעד סופית (Destination Country)", value=dest_info["dest"]
)

# הזנת יעד יבשתי סופי (שם אתר או קואורדינטות)
final_destination = st.sidebar.text_input(
    "יעד מסירה סופי באתר (שם אתר / קואורדינטות GPS)",
    value="Carmiel Industrial Zone / Coordinates: 32.9199, 35.2901",
    help="תוכל להזין שם אתר, יישוב או קואורדינטות GPS מפורטות",
)

st.sidebar.divider()
st.sidebar.header("📋 פרטי המטען, משקל וקוד מכס")

equipment_type = st.sidebar.selectbox(
    "סוג הציוד (Equipment Category)",
    [
        "BESS Container (מערכות אגירה)",
        "Solar Panels (פאנלים סולאריים)",
        "Inverters & Transformers (ממירים ושנאים)",
        "Wind Turbine Components (טורבינות רוח)",
    ],
)

hs_defaults = {
    "BESS Container (מערכות אגירה)": "8507.60",
    "Solar Panels (פאנלים סולאריים)": "8541.43",
    "Inverters & Transformers (ממירים ושנאים)": "8504.40",
    "Wind Turbine Components (טורבינות רוח)": "8502.31",
}

hs_code = st.sidebar.text_input(
    "קוד מכס (HS Code)", value=hs_defaults.get(equipment_type, "8507.60")
)

units_count = st.sidebar.number_input(
    "כמות יחידות/מכולות", min_value=1, value=5, step=1
)

# משקל מכולה / יחידה
container_weight = st.sidebar.number_input(
    "משקל ברוטו ליחידה/מכולה (טון/Tonnes)",
    min_value=1.0,
    max_value=100.0,
    value=45.0,
    step=1.0,
    help="למשל: BESS containers משקלים נפוצים של 43, 45, 48, או 55 טון",
)

total_weight = container_weight * units_count

cargo_value = st.sidebar.number_input(
    "ערך הסחורה במקור - Cargo Value ($)",
    min_value=0.0,
    value=150000.0,
    step=1000.0,
)

st.sidebar.divider()
st.sidebar.header("🚢 עלויות שרשרת האספקה הימית")

freight_cost = st.sidebar.number_input(
    "הובלה ימית ראשת ($)", min_value=0.0, value=12000.0, step=500.0
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
st.sidebar.header("🏛️ מכס, הסכמי סחר ומיסוי")

# בדיקת ברירת מחדל למכס בישראל (פטור)
default_customs = (
    0.0
    if (
        "Israel" in dest_country
        or "ישראל" in dest_country
        or "Port of Haifa" in selected_port
        or "Port of Ashdod" in selected_port
    )
    else 6.0
)

customs_rate_input = st.sidebar.number_input(
    "שיעור מכס רשמי (% Customs Duty)",
    min_value=0.0,
    value=default_customs,
    step=0.5,
)

fta_active = st.sidebar.checkbox(
    "הסכם סחר חופשי פעיל (FTA Exemption)",
    value=True if default_customs == 0 else False,
)
green_exemption = st.sidebar.checkbox(
    "פטור/הטבה ירוקה ייעודית (Green Incentive)", value=False
)

# מע"מ מחובר אוטומטית לנמל פקידה עם אפשרות עריכה
vat_rate = (
    st.sidebar.number_input(
        'שיעור מע"מ מקומי במדינת השחרור (% Local VAT)',
        min_value=0.0,
        value=float(dest_info["vat"]),
        step=0.5,
        help=(
            'המע"מ מעודכן אוטומטית לפי נמל הפקידה שנבחר (למשל: ישראל 18%,'
            " בולגריה 20%, יוון 24%)"
        ),
    )
    / 100
)

st.sidebar.divider()
st.sidebar.header("⚓ עלויות נמל, THC ועמילות בארץ היעד")

port_fees = st.sidebar.number_input(
    "אגרות נמל וסדרנות ($)", min_value=0.0, value=1200.0, step=50.0
)
thc_fees = st.sidebar.number_input(
    "דמי טיפול במסוף - THC ליחידה/מכולה ($)",
    min_value=0.0,
    value=350.0,
    step=25.0,
)
total_thc = thc_fees * units_count

brokerage_fees = st.sidebar.number_input(
    "עמילות מכס, סיווג ואישורים ($)", min_value=0.0, value=850.0, step=50.0
)
inland_transport = st.sidebar.number_input(
    "הובלה יבשתית מיוחדת/חורגת לאתר ($)",
    min_value=0.0,
    value=4500.0,
    step=250.0,
)

# ---------------------------------------------------------
# מנוע החישובים
# ---------------------------------------------------------
insurance_cost = cargo_value * insurance_rate
cif_value = cargo_value + freight_cost + origin_expenses + insurance_cost

effective_customs_rate = (
    0.0
    if (
        fta_active
        or green_exemption
        or "Israel" in dest_country
        or "ישראל" in dest_country
    )
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
# תצוגת תוצאות בדף + התראות רגולציה
# ---------------------------------------------------------
st.info(
    f"📍 **מסלול שינוע:** מ-**{origin_country}** דרך **{selected_port}** ➔"
    f" **{dest_country}** | **יעד סופי:** `{final_destination}` | **HS"
    f" Code:** `{hs_code}`"
)

# התראת משקל חורג ורגולציית משרד התחבורה
if container_weight >= 40.0:
  st.error(
      f"🚨 **התראת משקל כבד / מטען חורג ({container_weight} טון למכולה | סה\"כ"
      f' {total_weight} טון):**\n* **בישראל:** מכולות/יחידות מעל משקל מותר'
      " מחייבות אישור מיוחד של **משרד התחבורה (אגף מטענים)**, תיאום נתיב"
      " נסיעה, היתר הובלה כבדה, בדיקת עומסי סרנים בגשרים וליווי משטרתי/פרטי"
      " מראש.\n* **באירופה (בולגריה/רומניה/יוון):** מחייב היתר הובלה מיוחדת"
      " (Special Transport Permit / Overweight Authorization) מול רשויות"
      " הדרכים המקומיות (למשל RIA בבולגריה או CNAIR ברומניה) ובדיקת מגבלות עומס"
      " על גשרים ותשתיות."
  )

if "Israel" in dest_country or "ישראל" in dest_country:
  st.success(
      "💡 **הערת מכס ישראל:** מוצרי אגירה (BESS) ופאנלים סולאריים תחת פרט מכס"
      ' 8507.60 / 8541.43 פטורים ממכס בישראל (0% מכס), בכפוף להסכמי סחר/תעריף'
      ' המכס הרשמי. שיעור המע"מ הרשמי בישראל הינו **18%**.'
  )

# קישור דינמי למס/מכס לפי נמל ומדינת היעד
clean_hs = hs_code.replace(".", "").strip()
if (
    "Israel" in dest_country
    or "ישראל" in dest_country
    or "Haifa" in selected_port
    or "Ashdod" in selected_port
):
  customs_url = f"https://www.gov.il/he/departments/dynamiccollectors/customs-tariff?tariffNumber={clean_hs}"
  link_text = "🔗 לחץ כאן לבדיקת שיעורי מכס ופטורים בתעריף המכס הישראלי (רשות המסים)"
else:
  customs_url = f"https://trade.ec.europa.eu/access-to-markets/en/home?product_code={clean_hs}"
  link_text = (
      "🔗 לחץ כאן לבדיקת שיעורי מכס, מע\"מ והסכמי סחר בפורטל Access2Markets עבור"
      f" {dest_country}"
  )

st.markdown(f"[{link_text}]({customs_url})")

col1, col2, col3, col4 = st.columns(4)
col1.metric("ערך CIF כולל", f"${cif_value:,.2f}")
col2.metric(
    "תשלום מכס אפקטיבי",
    f"${customs_duty_amount:,.2f}",
    f"{effective_customs_rate*100:.1f}%",
)
col3.metric(f'מע"מ לתשלום ({vat_rate*100:.1f}%)', f"${vat_amount:,.2f}")
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
          "אגרות נמל ו-THC",
          "עמילות מכס ואישורים",
          "הובלה יבשתית (Inland)",
      ],
      "סכום ($)": [
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
      values="סכום ($)",
      names="רכיב עלות",
      hole=0.4,
      color_discrete_sequence=px.colors.qualitative.Pastel,
  )
  fig.update_traces(textposition="inside", textinfo="percent+label")
  st.plotly_chart(fig, use_container_width=True)

with right_col:
  st.subheader("📑 טבלת סיכום שלבי החישוב והלוגיסטיקה")
  summary_df = pd.DataFrame([
      {
          "שלב / פרט": "מסלול שחרור",
          "ערך / סכום": f"{origin_country} ➔ {selected_port}",
      },
      {"שלב / פרט": "יעד סופי באתר", "ערך / סכום": final_destination},
      {"שלב / פרט": "קוד מכס (HS Code)", "ערך / סכום": hs_code},
      {
          "שלב / פרט": "משקל כולל למטען",
          "ערך / סכום": (
              f"{total_weight:.1f} טון ({container_weight} טון/יחידה)"
          ),
      },
      {"שלב / פרט": "ערך הסחורה (FOB/EXW)", "ערך / סכום": f"${cargo_value:,.2f}"},
      {
          "שלב / פרט": "הובלה ימית + הוצאות במקור",
          "ערך / סכום": f"${freight_cost + origin_expenses:,.2f}",
      },
      {"שלב / פרט": "ביטוח ימי", "ערך / סכום": f"${insurance_cost:,.2f}"},
      {
          "שלב / פרט": "ערך CIF כולל (בסיס למכס)",
          "ערך / סכום": f"${cif_value:,.2f}",
      },
      {
          "שלב / פרט": "מכס אפקטיבי לתשלום",
          "ערך / סכום": f"${customs_duty_amount:,.2f}",
      },
      {
          "שלב / פרט": f'מע"מ מקומי לתשלום ({vat_rate*100:.1f}%)',
          "ערך / סכום": f"${vat_amount:,.2f}",
      },
      {"שלב / פרט": "אגרות נמל וסדרנות", "ערך / סכום": f"${port_fees:,.2f}"},
      {
          "שלב / פרט": f"דמי THC כולל ({units_count} מכולות)",
          "ערך / סכום": f"${total_thc:,.2f}",
      },
      {
          "שלב / פרט": "עמילות מכס, סיווג ואישורים",
          "ערך / סכום": f"${brokerage_fees:,.2f}",
      },
      {
          "שלב / פרט": "הובלה יבשתית מיוחדת/חורגת",
          "ערך / סכום": f"${inland_transport:,.2f}",
      },
      {
          "שלב / פרט": "עלות כוללת ליחידה/מכולה (נטו)",
          "ערך / סכום": f"${cost_per_unit:,.2f}",
      },
  ])
  st.dataframe(summary_df, use_container_width=True, hide_index=True)

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

  headers = ["שלב / רכיב עלות", "ערך / סכום ($)", "הערות רגולציה ולוגיסטיקה"]
  ws.append([])
  ws.append(headers)

  data = [
      ["מדינת מוצא", origin_country, "Origin"],
      ["נמל פקידה / שחרור", selected_port, "Port of Discharge"],
      ["מדינת יעד סופית", dest_country, "Destination Country"],
      ["יעד סופי באתר (שם/GPS)", final_destination, "Final Delivery Location"],
      ["קוד מכס (HS Code)", hs_code, "Customs Tariff Classification"],
      [
          "משקל ברוטו ליחידה",
          f"{container_weight} Tonnes",
          f'סה"כ {total_weight} טון ל-{units_count} יחידות',
      ],
      ["ערך הסחורה במקור (FOB/EXW)", cargo_value, "חשבונית ספק"],
      [
          "הובלה ימית + הוצאות במקור",
          freight_cost + origin_expenses,
          "הובלה ימית וטיפול במקור",
      ],
      ["ביטוח ימי", insurance_cost, f"שיעור {insurance_rate*100:.2f}%"],
      ["ערך CIF כולל (בסיס למכס)", cif_value, "בסיס למכס בנמל"],
      ["מכס אפקטיבי לתשלום", customs_duty_amount, "פטור מכס בישראל / הסכם סחר"],
      [
          'מע"מ מקומי לתשלום',
          vat_amount,
          f'{vat_rate*100:.1f}% מע"מ במדינת השחרור',
      ],
      ["אגרות נמל וסדרנות", port_fees, "Port Wharfage & Handling"],
      ["דמי טיפול במסוף - THC", total_thc, f"${thc_fees} למכולה x {units_count}"],
      ["עמילות מכס ואישורים", brokerage_fees, "Customs Brokerage & Permits"],
      [
          "הובלה יבשתית מיוחדת/חורגת",
          inland_transport,
          "Heavy Haulage Transport",
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
    label="📊 הורד דוח Excel מחושב מפורט",
    data=generate_excel_bytes(),
    file_name=f"Green_Logistics_Landed_Cost_{clean_hs}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
