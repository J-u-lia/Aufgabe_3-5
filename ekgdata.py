import json
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default = "browser"

# Klasse EKG-Data für Peakfinder, die uns ermöglicht peaks zu finden

class EKGdata:

## Konstruktor der Klasse soll die Daten einlesen

    @staticmethod
    def load_EKG_data():
        """A Function that knows where te person Database is and returns a Dictionary with the Persons"""
        file = open("data/person_db.json")
        person_data = json.load(file)
        return person_data

    @staticmethod    
    def load_by_id(such_id):
        person_data = EKGdata.load_EKG_data()
        if such_id == "None":
            return {}

        for eintrag in person_data:
            if (eintrag["id"] == such_id):
                return eintrag
        else:
            return {}

    def find_peaks(self, threshold, respacing_factor=5):
        """
        A function to find the peaks in a series
        Args:
            - series (pd.Series): The series to find the peaks in
            - threshold (float): The threshold for the peaks
            - respacing_factor (int): The factor to respace the series
        Returns:
            - peaks (list): A list of the indices of the peaks
        """
        
        series = self.df['Messwerte in mV'].iloc[::respacing_factor]
        
        # Filter the series
        series = series[series>threshold]


        peaks = []
        last = 0
        current = 0
        next = 0

        for index, row in series.items():
            last = current
            current = next
            next = row

            if last < current and current > next and current > threshold:
                peaks.append(index-respacing_factor)
        return peaks

    def estimate_heart_rate(self, peaks):
        heart_rates = []
        zeit_in_ms = self.df["Zeit in ms"]
        for i in range(len(peaks) - 1):
            interval = zeit_in_ms.iloc[peaks[i+1]] - zeit_in_ms.iloc[peaks[i]]
            if interval > 0:
                bpm = 60000 / interval
                heart_rates.append(bpm)
        avg_heart_rate = sum(heart_rates) / len(heart_rates) if heart_rates else 0
        return heart_rates, avg_heart_rate


    def __init__(self, ekg_dict):
        #pass
        self.id = ekg_dict["id"]
        self.date = ekg_dict["date"]
        self.data = ekg_dict["result_link"]
        self.df = pd.read_csv(self.data, sep='\t', header=None, names=['Messwerte in mV','Zeit in ms',]) 


    def plot_time_series(self, threshold=30, respacing_factor=5, min_val=0, max_val=None):
        if max_val is None:
            max_val = len(self.df)
        
        peaks = self.find_peaks(threshold=threshold, respacing_factor=respacing_factor)

        df_plot = self.df.iloc[min_val:max_val]
        #df_plot = self.df.head(2000)
        fig = px.line(df_plot, x="Zeit in ms", y="Messwerte in mV", title="EKG-Signal mit markierten Peaks")

        peaks_in_range = [p for p in peaks if p < len(df_plot)]
        peak_values = self.df.iloc[peaks_in_range]

        fig.add_trace(go.Scatter(
            x=peak_values["Zeit in ms"],
            y=peak_values["Messwerte in mV"],
            mode='markers',
            marker=dict(color='red', size=6),
            name='Peaks'
        ))

        fig.show()

        

        

if __name__ == "__main__":
    #print("This is a module with some functions to read the EKG data")
    file = open("data/person_db.json")
    person_data = json.load(file)
    ekg_dict = person_data[0]["ekg_tests"][0]
    #print(ekg_dict)
    ekg = EKGdata(ekg_dict)
    #print(ekg.df.head())

    #peaks = EKGdata.find_peaks(ekg.df(['Messwerte in mV']), threshold=0.5, respacing_factor=5)
    peaks = ekg.find_peaks(threshold=340, respacing_factor=5)
    #print(peaks)

    heart_rate = ekg.estimate_heart_rate(peaks)
    print(heart_rate)

    ekg.plot_time_series()