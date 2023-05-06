import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALL
from config import colors, size, colors_clicked

# Load the data
data = pd.read_csv('Data/Exampledata.csv')

# Define the function to show the data
def showdata(data, column=None):
    if column:
        data = data.drop(column, axis=1)
    return html.Div([
        html.H2('Input Data'),
        html.Table([
            html.Thead(html.Tr([html.Th(col) for col in data.columns])),
            html.Tbody([
                html.Tr([html.Td(data.iloc[i][col]) for col in data.columns]) for i in range(len(data))
            ])
        ])
    ])

# Define the function to show the filter buttons
def showfilterbutton(data):
    buttons = [
        html.Button(col, id={'type': 'filter-button', 'index': col}, style={'backgroundColor': colors[i % len(colors)], 'fontSize': size}) for i, col in enumerate(data.columns)
    ]
    return html.Div(buttons)

# Define the app and layout
app = dash.Dash(__name__)
app.layout = html.Div([
    showfilterbutton(data),
    html.Div(id='data-container', children=showdata(data))
])

# Define the callback for updating the button color
@app.callback(
    Output({'type': 'filter-button', 'index': MATCH}, 'style'),
    Input({'type': 'filter-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'filter-button', 'index': MATCH}, 'id')
)
def update_button_color(n_clicks, button_id):
    col = button_id['index']
    if n_clicks and n_clicks % 2 != 0:
        return {'backgroundColor': colors_clicked[data.columns.get_loc(col) % len(colors)], 'fontSize': size}
    else:
        return {'backgroundColor': colors[data.columns.get_loc(col) % len(colors)], 'fontSize': size}


# Define the callback for updating the data table
@app.callback(
    Output('data-container', 'children'),
    Input({'type': 'filter-button', 'index': ALL}, 'n_clicks'),
    State({'type': 'filter-button', 'index': ALL}, 'id')
)
def update_data_table(n_clicks, button_ids):
    ctx = dash.callback_context
    filtered_data = data.copy()

    for i, button_id in enumerate(button_ids):
        if n_clicks[i] and n_clicks[i] % 2 != 0:
            col = button_id['index']
            filtered_data = filtered_data.drop(col, axis=1)

    return showdata(filtered_data)

if __name__ == '__main__':
    app.run_server(debug=True)
