####COPY IF I ACCIDENTALLY MESS IT UP
####DASH cannot be used from google colab, needs to be ran locally (-> copy paste to .py file)
####THIS CODE TO SEARCH ???

import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import re

df = pd.read_csv('Exampledata.csv')
df.columns = df.columns.str.lower()

app = dash.Dash(__name__)

##just html stuff for the search bar and resulting columns, can be changed however
app.layout = html.Div(children=[    
    html.Div([    
        ##the SEARCH BAR    
        dcc.Input(id='search-input',
                type='text',
                placeholder='Enter search terms...',
                style={'width': '10%',
                       'padding': '10px',
                       'font-size': '16px',
                       'border': '2px solid #ccc',
                       'border-radius': '4px' 
                       }
                    ),    
              ], 
            style={
              'display': 'flex',
              'justify-content': 'left',
              'align-items': 'center',
              'margin-top': '50px'
            }),

    ##THE SEARCH BUTTON
    html.Div([        
        html.Button('Search', id='search-button', n_clicks=0),    
        ], 
        style={
          'display': 'flex',
          'justify-content': 'left',
          'align-items': 'center',
          'margin-top': '10px'
        }),

    # IF GRAPH
    # dcc.Graph(id='results-chart')

    # IF TABLE
    ##THE RESULTING DATA SHOWN
    html.Div(id='results-table', style={
      'margin-top': '50px',
      'display': 'flex',
      'justify-content': 'center',
      'align-items': 'center',
      'width': '80%',
      'margin-left': 'auto',
      'margin-right': 'auto',
    }),
])



@app.callback(
    ##FOR GRAPH
   # Output('results-chart', 'figure'),
   # [Input('search-button', 'n_clicks')],
   # [State('search-input', 'value')]

    ##FOR TABLE
    dash.dependencies.Output('results-table', 'children'),
    [dash.dependencies.Input('search-button', 'n_clicks')],
    [dash.dependencies.State('search-input', 'value')]
)

def update_chart(n_clicks, search_input):
    if not n_clicks:
        return []
    
    if not search_input:
        return html.Div("Please enter search terms.",
                        style={
                            "text-align": "center",
                            "margin-top": "50px"
                        })
    
    # Split the query into individual search terms
    queries = re.split(r'[,\s]+', search_input.strip())
    
    # Find the matching columns in the DataFrame
    matching_columns = find_matching_columns(queries, df)
    
    # If no matching columns found, display a message
    if len(matching_columns) == 0:
        return html.P('No matching columns found.')
    
    # Create a list of matching columns and their descriptions
    column_list = html.Ul([html.Li([html.Span(desc)], style={"display": "list-item", "list-style-type": "disc"}) for col, desc in matching_columns.items()],
                      style={"float": "left", "margin-right": "20px", "margin-top": "0px"})

    
    # Create a table of the matching columns
    df_matching_columns = df[list(matching_columns.keys())]
    table = html.Table([
        html.Thead(html.Tr([html.Th(col) for col in df_matching_columns.columns])),
        html.Tbody([html.Tr([html.Td(row[col]) for col in df_matching_columns.columns]) for i, row in df_matching_columns.iterrows()])
    ])
    
    # Combine the column list and table into a single HTML div
    results_div = html.Div([
        html.P("Data summary:"),
        column_list,
        table
    ])
    
    return results_div


# search function
def find_matching_columns(queries, df):
    matching_columns = {}
    for column in df.columns:
        for query in queries:
            query_words = query.lower().split()
            if any(word in column.lower() for word in query_words):
                matching_columns[column] = get_column_description(column)
                break
    return matching_columns


def get_column_description(column):
    # Define a dictionary of column descriptions and display names
    column_info = {
        "messageclass": {"description": "What type of message", "display_name": "Message class"},
        "messagebox": {"description": "Where was this message found?", "display_name": "Message box"},
        "timestamp" : {"description": "When this data was collected", "display_name": "Time stamp"},
        "totalesteps" : {"description": "Distance: Number of steps since this device was turned on", "display_name": "Total number of steps"},
        "stepstoday" : {"description": "Distance: Number of steps today", "display_name": "Number of steps today"},
        "name" : {"description": "App name collecting the data", "display_name": "Name"},

        "lastupdatetime" : {"description": "Time of app update in milliseconds", "display_name": "Latest update"},
        "packagename" : {"description": "Package name of app collecting the data ", "display_name": "Package name"},
        "issystemapp" : {"description": "True if this is a system app", "display_name": "System app"},
        "firstinstalltime" : {"description": "Time of app installation in milliseconds", "display_name": "First install time"},
        "isupdatedsystemapp" : {"description": "True if the app is a new system app", "display_name": "Updated system app"},
        "altitude" : {"description": "Location: Altitude in meter for the location", "display_name": "Altitude"},
        "longitude" : {"description": "Location: Longitude in degree for the location", "display_name": "Longitude"},
        "latitude" : {"description": "Location: Latitude in degree for the location", "display_name": "Latitude"},
        "speed": {"description": "Location: Your speed in meter/seconds", "display_name": "Speed"},
        "accuracy": {"description": "Location: Error bound in meter of the location", "display_name": "Accuracy"},
        "mimetype": {"description": "Media: The type of using multi-media", "display_name": "Mime type"},
        "bucketdisplay": {"description": "Media: thi is the container for the app of currently using media", "display_name": "Bucket display"},
        "ispinned": {"description": "Message/calls: True if shortcut is pinned", "display_name": "Pinned"},
        "timescontacted": {"description": "Message/calls: Number of previous calls or messages", "display_name": "Number of times contacted"},
        "number":{"description": "Message/calls: Number to other party (encrypted) ", "display_name": "Number"},
        "contact": {"description": "Message/calls: Type of contant ", "display_name": "Contact"},
        "isstarred": {"description": "Message/calls: This contact is in your favorites list", "display_name": "Starred"},
        "datetime": {"description": " ", "display_name": " "}
    }
    
    # Get the info for the given column
    info = column_info.get(column, {"description": "No description found.", "display_name": column})
    
    # Return the description and display name for the given column
    return f"{info['display_name']}: {info['description']}"
   


if __name__ == '__main__':
    app.run_server(debug=True)



