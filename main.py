import streamlit as st
from PIL import Image
import read_data  # Dein Modul
from read_data import find_person_data_by_name
import pandas as pd
import numpy as np
import plotly.express as px
from read_pandas import read_my_csv, make_plot, zone_colors, zonen_Farben_erstellen, hr_zonen_definieren
from ekgdata import EKGdata


# Tabs
tab1, tab2, tab3 = st.tabs(["Startseite", "Leistungsdaten", "EKG-Daten"])

# TAB 1 – STARTSEITE
with tab1:
    st.title("EKG Analyse App")
    st.markdown("## Willkommen zur EKG-Analyse-APP")
    st.write("Bitte wählen Sie eine Versuchsperson aus.")

    # Personen laden und Auswahl anzeigen
    person_dict = read_data.load_person_data()
    person_names = read_data.get_person_list(person_dict)

    selected_person = st.selectbox("Versuchsperson auswählen", options=person_names, key="person_select")

    if selected_person:
        st.session_state.current_user = selected_person
        current_person = find_person_data_by_name(selected_person)

        if current_person and "picture_path" in current_person:
            image = Image.open(current_person["picture_path"])
            st.image(image, caption=selected_person)
        else:
            st.warning("Kein Bild für diese Person gefunden.")
        st.markdown(f"**Name:** {current_person['firstname']} {current_person['lastname']}")
        st.markdown(f"**Geburtsdatum:** {current_person['date_of_birth']}")
        st.markdown(f"**Geschlecht:** {current_person['gender']}")
        st.markdown(f"**ID:** {current_person['id']}")

    # Auswahl für den Leistungstest (z.B. immer nur einer)
    # Testauswahl – Leistungstest (statisch, bleibt wie gehabt)
    st.markdown("## Leistungstest auswählen:")
    leistungstests = ["Test 1"]
    selected_test = st.selectbox("Vorhandene Leistungstests:", leistungstests, key="test_select")
    st.session_state.selected_test = selected_test

    # EKG-Testauswahl anhand verfügbarer EKG-Tests in JSON
    st.markdown("## EKG Analyse auswählen:")
    if "ekg_tests" in current_person:
        ekg_tests = current_person["ekg_tests"]
        ekg_test_options = [f"Test {i+1}" for i in range(len(ekg_tests))]
        selected_ekg_test = st.selectbox("Vorhandene EKG-Tests:", ekg_test_options, key="ekg_test_select")
        st.session_state.selected_test_index = ekg_test_options.index(selected_ekg_test)
    else:
        st.warning("Keine EKG-Tests vorhanden.")



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


# TAB 3 – EKG-DATEN
with tab3:
    if "current_user" not in st.session_state or "selected_test_index" not in st.session_state:
        st.warning("Bitte wähle zuerst eine Person und einen EKG-Test auf der Startseite aus.")
    else:
        st.subheader("EKG Analyse")

        current_person = find_person_data_by_name(st.session_state.current_user)
        test_index = st.session_state.selected_test_index

        try:
            ekg_dict = current_person["ekg_tests"][test_index]
            ekg = EKGdata(ekg_dict)

            # Peaks und Herzfrequenz berechnen
            peaks = ekg.find_peaks(threshold=340, respacing_factor=5)
            heart_rates, avg_hr = ekg.estimate_heart_rate(peaks)

            # Plot
            min_val = st.number_input(
                'Untere Grenze eingeben:',
                min_value=0,
                max_value=len(ekg.df) - 1,
                value=0,
                step=1
            )

            max_val = st.number_input(
                'Obere Grenze eingeben:',
                min_value=min_val + 1,
                max_value=len(ekg.df),
                value=min(len(ekg.df), min_val + 100),
                step=1
            )
            st.write(f'Daten von Index {min_val} bis {max_val}')

            # Daten im gewählten Zeitfenster extrahieren
            df_plot = ekg.df.iloc[min_val:max_val]
            fig = px.line(df_plot, x="Zeit in ms", y="Messwerte in mV", title="EKG-Signal mit markierten Peaks")

            # Peaks als Marker hinzufügen, korrekt in Bezug auf den Original-Index
            peaks_in_range = [p for p in peaks if min_val <= p < max_val]
            if peaks_in_range:
                peak_times = ekg.df["Zeit in ms"].iloc[peaks_in_range]
                peak_values = ekg.df["Messwerte in mV"].iloc[peaks_in_range]

                fig.add_scatter(
                    x=peak_times,
                    y=peak_values,
                    mode="markers",
                    marker=dict(color="red", size=6),
                    name="Peaks"
                )

            st.plotly_chart(fig, use_container_width=True)

            #st.markdown(f"**Anzahl erkannter Peaks:** {len(peaks)}")

            if avg_hr:
                st.markdown(f"**geschätzte Herzfrequenz auf Basis der Peaks:** {avg_hr:.2f} bpm")
            else:
                st.warning("Keine Peaks erkannt - Herzfrequenz konnte nicht berechnet werden.")

        except (IndexError, KeyError):
            st.error("Der gewählte Test konnte nicht geladen werden.")
