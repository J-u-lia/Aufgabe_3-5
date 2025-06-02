# Paket für Bearbeitung von Tabellen
import pandas as pd
import numpy as np

# Paket
## zuvor !pip install plotly
## ggf. auch !pip install nbformat
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"


def read_my_csv():
    # Einlesen eines Dataframes
    ## "\t" steht für das Trennzeichen in der txt-Datei (Tabulator anstelle von Beistrich)
    ## header = None: es gibt keine Überschriften in der txt-Datei
    df = pd.read_csv('data/activities/activity.csv')
    

    t_end = len(df)
    zeit = np.arange(0, t_end) 
    df["Zeit"] = zeit


    # Gibt den geladen Dataframe zurück
    return df


# Definition der Farben für die Herzfrequenzzonen
zone_colors = {
    "Zone 1": "rgba(173,216,230,0.3)",  # Blau
    "Zone 2": "rgba(144,238,144,0.3)",  # Grün
    "Zone 3": "rgba(255,255,0,0.3)",    # Gelb
    "Zone 4": "rgba(255,165,0,0.3)",    # Orange
    "Zone 5": "rgba(255,99,71,0.3)",    # Rot
}

# Funktion, die die Herzfrequenzzonen definiert und dem DataFrame eine neue Spalte "Zone" hinzufügt

# Grenzen der Herzfrequenzzonen definieren, damit die Zonen korrekt zugeordnet werden
def hr_zonen_definieren(df, HR_max):
    def get_zone(hr):
        if hr < 0.6 * HR_max:
            return "Zone 1"
        elif hr < 0.7 * HR_max:
            return "Zone 2"
        elif hr < 0.8 * HR_max:
            return "Zone 3"
        elif hr < 0.9 * HR_max:
            return "Zone 4"
        else:
            return "Zone 5"
    df = df.copy()  # Kopiere den DataFrame, um Originaldaten nicht zu verändern    
    df["Zone"] = df["HeartRate"].apply(get_zone)
    return df

# Funktion die die Hintergrundfarben der Zonen erstellt; sie analysiert die Spalte "Zone" und erstellt für jede Zone ein Rechteck, das den Hintergrund einfärbt; Sie gibt eine Liste von Shapes zurück, die in der Plotly-Figur verwendet werden
def zonen_Farben_erstellen(df, zone_colors):
    shapes = [] # Liste für die Shapes, die die Zonen darstellen
    current_zone = None  # zeigt in welcher aktuellen Zone man sich befindet
    start_time = 0 # Startzeit für die aktuelle Zone

    for i in range(len(df)):    # iteriere über alle Zeilen des DataFrames
        zone = df.iloc[i]["Zone"] # aktuelle Zone aus der Spalte "Zone" des DataFrames
        if zone != current_zone: # != heißt ungleich --> Wenn die Zone sich geändert hat, wird ein neues Rechteck erstellt
            if current_zone is not None: # prüfe, ob es eine vorherige Zone gibt, wenn ja, dann füge ein Rechteck für die vorherige Zone hinzu
                shapes.append(dict(  # Rechteck hinzufügen
                    type="rect",  # was soll es für Form sein --> Rechteck
                    xref="x",  # die x-Achse ist Zeitabhängig, sie basiert auf Daten aus der Spalte "Zeit" aus dem DataFrame
                    yref="paper",  # y-Achse ist auf die gesamte Höhe des Plots bezogen
                    x0=start_time,  # Startzeit der vorherigen Zone
                    x1=i,  # Endzeit der vorherigen Zone (aktueller Index)
                    y0=0, # y0 und y1 sind auf die gesamte Höhe des Plots bezogen, damit das Rechteck den gesamten Plot ausfüllt
                    y1=1,  # Höhe des Plots
                    fillcolor=zone_colors[current_zone], # Farbe der Zone, wird aus Dictionary zone_colors entnommen
                    line=dict(width=0),   # keine Linienbreite, damit es nur ein gefülltes Rechteck ist
                    layer="below"  # Rechteck soll unter den Datenlinien liegen
                ))
            current_zone = zone
            start_time = i

    # Füge die letzte Zone hinzu nach der Schleife
    shapes.append(dict(
        type="rect",
        xref="x",
        yref="paper",
        x0=start_time,
        x1=len(df),
        y0=0,
        y1=1,
        fillcolor=zone_colors[current_zone],
        line=dict(width=0),
        layer="below"
    ))
    return shapes



def make_plot(df, zone_colors):
    fig = go.Figure()

    # Linien für Herzfrequenz und Leistung
    fig.add_trace(go.Scatter(x=df["Zeit"], y=df["HeartRate"], mode="lines", name="Herzfrequenz", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df["Zeit"], y=df["PowerOriginal"], mode="lines", name="Leistung", line=dict(color="black")))

    # Hintergrundzonen
    shapes = zonen_Farben_erstellen(df, zone_colors)
    fig.update_layout(shapes=shapes)

    # Legende für Zonen
    for zone, color in zone_colors.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color.replace("0.3", "1")),  # volle Farbe für Legende
            legendgroup=zone,
            showlegend=True,
            name=zone
        ))

    fig.update_layout(title="Leistung & Herzfrequenz mit Herzfrequenz-Zonen",
                      xaxis_title="Zeit (s)",
                      yaxis_title="Wert",
                      legend_title="Legende")
    return fig

if __name__ == "__main__":
    df = read_my_csv()
    HR_max = df['HeartRate'].max()
    df = hr_zonen_definieren(df, HR_max)
    
    zone_colors = {
        "Zone 1": "rgba(173,216,230,0.3)",
        "Zone 2": "rgba(144,238,144,0.3)",
        "Zone 3": "rgba(255,255,0,0.3)",
        "Zone 4": "rgba(255,165,0,0.3)",
        "Zone 5": "rgba(255,99,71,0.3)",
    }

    fig = make_plot(df, zone_colors)
    fig.show()