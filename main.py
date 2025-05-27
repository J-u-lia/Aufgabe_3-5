import streamlit as st
import read_data # Ergänzen Ihr eigenes Modul
# Paket zum anzeigen der Bilder
from PIL import Image
from read_data import find_person_data_by_name

# Eine Überschrift der ersten Ebene
st.write("# EKG APP")

# Eine Überschrift der zweiten Ebene
st.write("## Versuchsperson auswählen")

# Session State wird leer angelegt, solange er noch nicht existiert
if 'current_user' not in st.session_state:
    st.session_state.current_user = 'None'

# Dieses Mal speichern wir die Auswahl als Session State

# Legen Sie eine neue Liste mit den Personennamen an indem Sie ihre 
# Funktionen aufrufen
person_dict = read_data.load_person_data()
person_names = read_data.get_person_list(person_dict)
# bzw: wenn Sie nicht zwei separate Funktionen haben
# person_names = read_data.get_person_list()

# Nutzen Sie ihre neue Liste anstelle der hard-gecodeten Lösung
st.session_state.current_user = st.selectbox(
    'Versuchsperson',
    options = person_names, key="sbVersuchsperson")

st.write("Der Name ist: ", st.session_state.current_user) 


# Bild einfügen

# Test
# Finden der Person - den String haben wir im Session state
current_person = find_person_data_by_name(st.session_state.current_user)
# Auslesen des Pfades aus dem zurückgegebenen Dictionary
current_picture_path = current_person["picture_path"]
print(current_picture_path)

# Laden eines Bilds
image = Image.open(current_picture_path)
# Anzeigen eines Bilds mit Caption
st.image(image, caption=st.session_state.current_user)