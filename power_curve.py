import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"

def load_data():
    df = pd.read_csv('data/activities/activity.csv')
    power_series = df['PowerOriginal']
    return power_series

def find_best_effort(power_series, window_size, sampling_interval):
    window_samples = int(window_size / sampling_interval)
    return power_series.rolling(window=window_samples).mean().max()

def create_power_curve(power_series, window_sizes, sampling_interval):
    results = []
    for window in window_sizes:
        best_effort = find_best_effort(power_series, window, sampling_interval)
        results.append((window, best_effort))
    return pd.DataFrame(results, columns=['Time (s)', 'Best effort (W)'])


def plot_power_curve(df):
    
    fig = go.Figure(data=go.Scatter(
    x=df['Time (s)'],
    y=df['Best effort (W)'],
    mode='lines+markers',
    name='Power Curve',
    hovertemplate='Zeit: %{x} s<br>Leistung: %{y} W<extra></extra>'
))
    
    fig.update_layout(
        title='Power Curve - maximale Durchschnittsleistung (W), die über das jeweilige Zeitintervall (s) aufrechterhalten wurde',
        xaxis_title='Time (s)',
        yaxis_title='Best effort (W)',
        xaxis=dict(type='log', tickmode='array', tickvals=window_sizes),
        yaxis=dict(type='log'),
        template='plotly_white'
    )

    fig.show()

if __name__ == "__main__":
    window_sizes = [1, 3, 5, 10, 15, 30, 60, 120, 180, 300, 600, 1200, 1800]
    sampling_interval = 1
    power_series = load_data()
    power_curve_df = create_power_curve(power_series, window_sizes, sampling_interval)
    plot_power_curve(power_curve_df)

