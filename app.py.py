import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# Read in the data
df=pd.read_csv('Exampledata.csv')

# make map
#################################################

token="pk.eyJ1Ijoid2FubWlkc3VtbWVyIiwiYSI6ImNsaGJmYTI5dTBnbDQzZ210YXp6NHVkMDEifQ.1TXrSRLDqsCldGx_1SwkEw"

# Create figures in Express
figure1 = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="size", size="scale", size_max=10, animation_frame="hour", color_continuous_scale=px.colors.cyclical.IceFire, range_color=[0, 20], zoom=14.5, height=550)
figure1.update_layout(mapbox_style="stamen-toner")
figure1["layout"].pop("updatemenus")

mapUI=dcc.Graph(id='graph', figure=figure1)
#################################################


# make search function
#################################################

##the SEARCH BAR
searchbar_style={
    'display': 'flex',
    'justify-content': 'left',
    'align-items': 'center',
}

searchbar=dcc.Input(id='search-input',
                type='text',
                placeholder='Enter search terms...',
                style={'width': '80%',
                       'padding': '10px',
                       'font-size': '16px',
                       'border': '2px solid #ccc',
                       'border-radius': '4px' 
                       })


##THE SEARCH BUTTON
searchbutton_style={
    'display': 'flex',
    'justify-content': 'left',
    'align-items': 'center',
    'margin-top': '10px'
}

searchbutton=html.Button('Search', id='search-button', n_clicks=0)

#################################################


# make calendar UI
#################################################
calendar_style={
    'display': 'flex',
    'justify-content': 'left',
    'align-items': 'center'
}

calendarUI=dcc.DatePickerSingle(
        id='date-picker',
        display_format='MMM Do, YYYY h:mm:ss A',
        date=df['DateTime'].iloc[0],
        style=dict(width='80%'))

#################################################



# create sidebar
#################################################

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H3("Date Selection"),
        html.Div([calendarUI], style=calendar_style),
        html.Hr(),
        html.H3("Search"),
        html.Div([
            html.Div([searchbar], style=searchbar_style),
            html.Div([searchbutton], style=searchbutton_style)
        ])
    ],
    style=SIDEBAR_STYLE,
)

#################################################

# create app

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "20rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

content = html.Div([
            html.Header(
                [
                    html.H1("Team 1 DP4 Prototype")
                ], style=CONTENT_STYLE
            ),
            html.Div([mapUI], style=CONTENT_STYLE)
        ])

app.layout = html.Div([
                html.Div([sidebar, content])
            ])


# run
if __name__ == '__main__':
    app.run_server(debug=True)