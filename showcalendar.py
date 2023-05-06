import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Example dataframe
df = pd.read_csv('Data/Exampledata.csv', parse_dates=['DateTime'])

# Dash app initialization
app = dash.Dash(__name__)

# UI layout
app.layout = html.Div([
    dcc.DatePickerSingle(
        id='date-picker',
        display_format='MMM Do, YYYY h:mm:ss A',
        date=df['DateTime'].iloc[0]
    ),
    html.Br(),
    html.Table(id='table', children=[
        html.Thead([
            html.Tr([
                html.Th('DateTime'),
                html.Th('TotalSteps')
            ])
        ]),
        html.Tbody(id='table-body')
    ])
])

# Function to filter dataframe based on selected date
def filter_dataframe(date):
    if not date:
        # Return entire dataframe if no date selected
        filtered_df = df
    else:
        # Filter dataframe by selected date
        filtered_df = df[df['DateTime'].dt.floor('1d') == pd.to_datetime(date).floor('1d')]
    return filtered_df

# Function to generate table rows from filtered dataframe
def generate_table_rows(filtered_df):
    rows = [
        html.Tr([
            html.Td(row['DateTime'].strftime('%Y-%m-%d %H:%M:%S')),
            html.Td(row['TotalSteps'])
        ]) for _, row in filtered_df.iterrows()
    ]
    return rows

# Callback to update table based on selected date
@app.callback(Output('table-body', 'children'),
              [Input('date-picker', 'date')])
def update_table(date):
    filtered_df = filter_dataframe(date)
    rows = generate_table_rows(filtered_df)
    return rows

if __name__ == '__main__':
    app.run_server(debug=True)
