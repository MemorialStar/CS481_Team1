import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

import plotly.express as px
import pandas as pd
import datetime

df = pd.read_csv('Exampledata.csv')

token="pk.eyJ1Ijoid2FubWlkc3VtbWVyIiwiYSI6ImNsaGJmYTI5dTBnbDQzZ210YXp6NHVkMDEifQ.1TXrSRLDqsCldGx_1SwkEw"

# Create figures in Express
figure1 = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="size", size="scale", size_max=10, animation_frame="hour", color_continuous_scale=px.colors.cyclical.IceFire, range_color=[0, 20], zoom=14.5)
figure1.update_layout(mapbox_style="stamen-toner")
figure1["layout"].pop("updatemenus")

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(figure=figure1)
])

if __name__ == '__main__':
    app.run_server(debug=True)