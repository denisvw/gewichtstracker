
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="Mijn Gewicht", layout="centered")

# Basisparameters
startgewicht = 102.3
streefgewicht = 89.0
startdatum = datetime(2025, 7, 7)
verlies_per_week = 0.64
dagelijkse_verlies = verlies_per_week / 7

# Bestand opslaan
def save_data(df):
    df.to_csv("gewicht_log.csv", index=False)

# Bestand inladen
def load_data():
    try:
        return pd.read_csv("gewicht_log.csv", parse_dates=["Datum"])
    except:
        return pd.DataFrame(columns=["Datum", "Gewicht"])

st.title("📉 Mijn Gewicht – Dagelijkse Logging")

st.markdown("Log hier je gewicht, bekijk je voortgang en vergelijk met je doel (89 kg tegen eind november).")

# 1. Invoergewicht
gewicht = st.number_input("📥 Vul je gewicht in (kg)", min_value=60.0, max_value=150.0, step=0.1)
datum = st.date_input("📅 Datum", datetime.today())

if st.button("✅ Gewicht loggen"):
    df = load_data()
    df = df.append({"Datum": datum, "Gewicht": gewicht}, ignore_index=True)
    df = df.drop_duplicates(subset="Datum", keep="last").sort_values("Datum")
    save_data(df)
    st.success(f"{gewicht} kg geregistreerd voor {datum.strftime('%d-%m-%Y')}")

# 2. Data laden
df = load_data()

if not df.empty:
    # 3. Dashboard
    laatst = df.iloc[-1]["Gewicht"]
    verschil = round(startgewicht - laatst, 1)
    resterend = round(laatst - streefgewicht, 1)
    st.markdown("### 📊 Dashboard")
    st.markdown(f"- Huidig gewicht: **{laatst:.1f} kg**")
    st.markdown(f"- Totaal verloren: **{verschil:.1f} kg**")
    st.markdown(f"- Nog te gaan: **{resterend:.1f} kg**")

    # 4. Projectielijn
    min_datum = df["Datum"].min()
    max_datum = df["Datum"].max()
    projectiedata = []
    dagen = (max_datum - startdatum.date()).days
    for i in range(dagen + 1):
        datum_p = startdatum + timedelta(days=i)
        gewicht_p = startgewicht - (i * dagelijkse_verlies)
        gewicht_p = max(gewicht_p, streefgewicht)
        projectiedata.append({"Datum": datum_p, "Projectie": gewicht_p})
    df_proj = pd.DataFrame(projectiedata)

    # 5. Grafiek
    fig, ax = plt.subplots()
    ax.plot(df["Datum"], df["Gewicht"], marker='o', label="Jouw gewicht", color="blue")
    ax.plot(df_proj["Datum"], df_proj["Projectie"], linestyle="--", label="Doellijn", color="green")
    ax.axhline(y=streefgewicht, color="red", linestyle=":", label="Streefgewicht (89 kg)")
    ax.set_title("📈 Evolutie gewicht")
    ax.set_xlabel("Datum")
    ax.set_ylabel("Gewicht (kg)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    # 6. Downloadknop
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Gewicht Log")
    st.download_button(
        label="📥 Download als Excel",
        data=buffer,
        file_name="gewicht_log.xlsx",
        mime="application/vnd.ms-excel"
    )

else:
    st.info("Log je eerste gewicht om te starten.")
