import streamlit as st
from PIL import Image
import read_data  # Dein Modul
from read_data import find_person_data_by_name
import pandas as pd
import plotly.express as px
from read_pandas import read_my_csv, make_plot, zone_colors, zonen_Farben_erstellen, hr_zonen_definieren

# Tabs
tab1, tab2 = st.tabs(["Startseite", "Daten"])

# TAB 1 – STARTSEITE
with tab1:
    st.title("EKG Analyse App")
    st.markdown("## Willkommen zur EKG-Analyse-APP")
    st.write("Bitte wählen Sie eine Versuchsperson aus.")

    # Personen laden und Auswahl anzeigen
    person_dict = read_data.load_person_data()
    person_names = read_data.get_person_list(person_dict)

    # Auswahl merken
    selected_person = st.selectbox("Versuchsperson auswählen", options=person_names, key="person_select")

    if selected_person:
        # Speichern in session_state
        st.session_state.current_user = selected_person

        current_person = find_person_data_by_name(selected_person)
        if current_person and "picture_path" in current_person:
            image = Image.open(current_person["picture_path"])
            st.image(image, caption=selected_person)
        else:
            st.warning("Kein Bild für diese Person gefunden.")

        # Testauswahl
        st.markdown("## Test auswählen:")
        testliste = ["Test 1", "Test 2", "Test 3"]
        selected_test = st.selectbox("Vorhandene Tests:", testliste, key="test_select")
        
        # Speichern in session_state
        st.session_state.selected_test = selected_test

# TAB 2 – DATEN
with tab2:
    if "current_user" not in st.session_state or "selected_test" not in st.session_state:
        st.warning("Bitte wählen Sie zuerst eine Person und einen Test auf der Startseite aus.")
    else:
        st.subheader(f"Testauswertung für: {st.session_state.current_user}")
        st.markdown(f"**Ausgewählter Test:** {st.session_state.selected_test}")

        # CSV laden
        df = read_my_csv()

        # HR_max eingeben
        st.markdown("### Herzfrequenzzonen:")
        HR_max_input = st.number_input("Maximale Herzfrequenz eingeben:",
                                       min_value=100, max_value=220,
                                       value=int(df["HeartRate"].max()))

        if st.button("Aktualisieren"):
            df = hr_zonen_definieren(df, HR_max_input)
            st.markdown("### Herzfrequenz- und Leistungsdiagramm:")
            fig = make_plot(df, zone_colors)
            fig.update_layout(shapes=zonen_Farben_erstellen(df, zone_colors))
            st.plotly_chart(fig, use_container_width=True)

            # Leistungsdaten
            st.markdown("### Leistungsdaten:")
            st.markdown(f"**Mittelwert Leistung:** {df['PowerOriginal'].mean():.2f} W")
            st.markdown(f"**Maximale Leistung:** {df['PowerOriginal'].max():.2f} W")

            # Zeit in Zonen
            st.markdown("### Verbrachte Zeit in Zonen (Sekunden):")
            zone_counts = df["Zone"].value_counts().sort_index()
            zone_times = zone_counts * 1  # 1 Sekunde pro Zeile
            st.dataframe(zone_times.rename("Dauer (s)"))

            # Durchschnittswerte
            st.markdown("### Durchschnittswerte pro Zone:")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Durchschnittliche Herzfrequenz (bpm)**")
                mean_hr = df.groupby("Zone")["HeartRate"].mean()
                st.dataframe(mean_hr.rename("Herzfrequenz (bpm)"))
            with col2:
                st.markdown("**Durchschnittliche Leistung (W)**")
                mean_power = df.groupby("Zone")["PowerOriginal"].mean()
                st.dataframe(mean_power.rename("Leistung (W)"))
        else:
            st.info("Bitte klicken Sie auf 'Aktualisieren', nachdem die maximale Herzfrequenz geändert wurde.")
