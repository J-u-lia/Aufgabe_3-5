import streamlit as st
from PIL import Image
import read_data  # Dein Modul
from read_data import find_person_data_by_name
import pandas as pd
import plotly.express as px
from read_pandas import read_my_csv, make_plot, zone_colors, zonen_Farben_erstellen, hr_zonen_definieren

# Startwert für die Seite setzen
if "page" not in st.session_state:
    st.session_state.page = "start"

# Navigation mit Buttons
def go_to(page_name):
    st.session_state.page = page_name

# Startseite
def zeige_startseite():
    st.title("EKG Analyse App")
    st.markdown("## Willkommen zur EKG-Analyse-APP")
    st.write("Bitte wählen Sie eine Versuchsperson aus.")

    person_dict = read_data.load_person_data()
    person_names = read_data.get_person_list(person_dict)

    person = st.selectbox("Versuchsperson auswählen", options=person_names, key="person_select")
    
    if st.button("zur Auswertung"):
        st.session_state.current_user = person
        go_to("person")

# Detailansicht für die Person
def zeige_person_detailseite():
    st.button("Zurück zur Startseite", on_click=lambda: go_to("start"))

    current_person = find_person_data_by_name(st.session_state.current_user)
    if current_person == {}:
        st.error("Keine Personendaten gefunden!")
        return
    
    st.subheader(f"Ausgewählte Person: {st.session_state.current_user}")
    image = Image.open(current_person["picture_path"])
    st.image(image, caption=st.session_state.current_user)

    st.markdown("## Test auswählen oder neuen Test anlegen:")

    # Hier kannst du später echte Tests aus JSON oder CSV laden
    testliste = ["Test 1", "Test 2", "Test 3"]
    test_auswahl = st.selectbox("Vorhandene Tests:", testliste)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Test anzeigen"):
            st.session_state.selected_test = test_auswahl
            go_to("diagramm")

    with col2:
        if st.button("Neuen Test anlegen"):
            st.info("Neue Test-Funktionalität ist in Arbeit!")

# Funktion zum Anzeigen des Diagramms
def zeige_test_auswertung():
    st.button("Zurück zu Person", on_click=lambda: go_to("person"))
    st.subheader(f"Testauswertung für: {st.session_state.current_user}")
    st.markdown(f"**Ausgewählter Test:** {st.session_state.selected_test}")

    # CSV laden
    df = read_my_csv()
    
    # HR_max berechnen lassen oder manuell eingeben
    st.markdown("### Herzfrequenzzonen:")
    HR_max_input = st.number_input("Maximale Herzfrequenz eingeben:", min_value=100, max_value=220, value=int(df["HeartRate"].max()))
    

    aktualisieren = st.button("Aktualisieren")
    if aktualisieren:
        df = hr_zonen_definieren(df, HR_max_input)
        # Diagramm anzeigen
        st.markdown("### Herzfrequenz- und Leistungsdiagramm:")
        
        fig = make_plot(df, zone_colors)
        fig.update_layout(shapes=zonen_Farben_erstellen(df, zone_colors))
        st.plotly_chart(fig, use_container_width=True)

        # mittle und maximale Leistung berechnen
        st.markdown("### mittlere Leistungsdaten:")
        mean_power = df["PowerOriginal"].mean()
        max_power = df["PowerOriginal"].max()
        st.markdown(f"**Mittelwert Leistung:** {mean_power:.2f} W")
        st.markdown(f"**Maximale Leistung:** {max_power:.2f} W")

        # Zeit verbracht in welcher Zonen berechnen und anzeigen
        zone_counts = df["Zone"].value_counts().sort_index()
        zone_times = zone_counts * 1  # Annahme: jede Zeile entspricht 1 Sekunde
        st.markdown("### Verbrachte Zeit in Zonen (Sekunden):")
        st.dataframe(zone_times.rename("Dauer (s)"))

        # Durchschnittliche Herzfrequenz und Leistung pro Zone, nebeneinander
        st.markdown("### Durchschnittswerte pro Zone:")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Durchschnittliche Herzfrequenz (bpm)**")
            mean_hr_per_zone = df.groupby("Zone")["HeartRate"].mean()
            st.dataframe(mean_hr_per_zone.rename("Herzfrequenz (bpm)"))
        with col2:
            st.markdown("**Durchschnittliche Leistung (W)**")
            mean_power_per_zone = df.groupby("Zone")["PowerOriginal"].mean()
            st.dataframe(mean_power_per_zone.rename("Leistung (W)"))
    else:
        st.info("Bitte klicken Sie auf 'Aktualisieren', nachdem die maximale Herzfrequenz geändert wurde.")
    


# Struktur der App
if st.session_state.page == "start":
    zeige_startseite()
elif st.session_state.page == "person":
    zeige_person_detailseite()
elif st.session_state.page == "diagramm":
    zeige_test_auswertung()
