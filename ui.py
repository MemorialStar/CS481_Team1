import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import re

df=pd.read_csv("Exampledata.csv")
app = dash.Dash(__name__)


#### SEARCH BAR ######
# make search function
#################################################

##the SEARCH BAR
searchbar_style={
    'display': 'flex',
    'justify-content': 'left',
    'align-items': 'center',
    "font-family" : "Futura"
}

searchbar=dcc.Input(id='search-input',
                type='text',
                placeholder='Enter search terms...',
                style={'width': '80%',
                       'padding': '10px',
                       'font-size': '16px',
                       'border': '2px solid #ccc',
                       'border-radius': '4px',
                       "font-family" : "Futura" 
                       })


##THE SEARCH BUTTON
searchbutton_style={
    'display': 'flex',
    'justify-content': 'left',
    'align-items': 'center',
    'margin-top': '15px',
    'margin-bottom' : '15px',
    "font-family" : "Futura"

}

searchbutton=html.Button('Search', id='search-button', n_clicks=0)

#################################################


#### SIDEBAR ####

SIDEBAR_STYLE = {
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "15rem",
    "padding": "2rem 1rem",
    "background-color": "#002000",#"#9EECFF",
    "color":"white",
    "font-family" : "Futura",
    "letter-spacing":"2px",
    "font-size":"16px"
}

SIDEBAR_STYLE2 = {
    "overflow" : "scroll",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "margin-left": "5px",
    "width": "300px",
    "max-width" : "350px",
    "padding": "2rem 1rem",
    "background-color": "#002000",
    "color":"white",
    "font-family" : "Futura",
    "letter-spacing":"2px",
    "font-size":"16px",

}

SIDEBAR_CONT = {
    "display":"flex",
    "height":"100vh"
}


sidebar = html.Div(children =
    
    [
    #SIDEBAR 1
    html.Div(children = [
      ## DATE SELECTION STUFF
      html.Div(children = [
          html.H3('Date Selection')
        ],
      ),
      ##space for map stuff i couldn't get to work on my computer
   
      html.Hr(style={'border':'0.5px solid white'}),
  
      ## SEARCH BAR
      html.H3("Search"),
      html.Div([
          html.Div([searchbar], style=searchbar_style),
          html.Div([searchbutton], style=searchbutton_style)
        ]),

      html.Hr(style={'border':'0.5px solid white'}),

         #DROPDOWN FOR CHOOSING DATA
      html.Div([
        html.H3("Date and time:"),
        dcc.Dropdown(
          id='column-dropdown',
          options=[{'label': col, 'value': col} for col in df.columns],
          placeholder='Select a column',
          style={'color':'black'}
        ), 
        html.Div(id='column-description')
      ]),

    

    ], style=SIDEBAR_STYLE),

    #SIDEBAR 2
    html.Div(
        # Initially hidden
        id="sidebar2",       
        children=[         
            ## RESULTS
            html.Div(id='results-table',
                
            style={
                'margin-top': '15px',
                'display': 'flex',
                'justify-content': 'center',
                'align-items': 'center',
                'width': '80%',
                'display': 'flex',
                'justify-content': 'left',
                'font-family': 'Courier New, Courier, monospace',
                'font-size': '10px'
            })

        ],
        style=SIDEBAR_STYLE2,
        className="sidebar2"
    )



    ], style=SIDEBAR_CONT
)

###CALLBACK functions for hide show search bar
@app.callback(
    Output('sidebar2', 'style'),
    [Input('search-button', 'n_clicks')],
    [State('search-input', 'value')]
)
def toggle_sidebar(n_clicks, search_input):
    if not n_clicks or not search_input:
        return {'display': 'none'}
    else:
        return SIDEBAR_STYLE2



###CALLBACK functions for search results
@app.callback(

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
    
    
    column_list = html.Div([
      html.H3("Data summary:", style={'border':'1px solid white', 'padding':'5px','width': 'fit-content'}),
      html.Ul([
        ##THE BULLET LIST
        html.Li([
            html.Span(desc)
        ])
        for desc in matching_columns.keys()
      ]),
    ])

    
    # Combine the column list and table into a single HTML div
    results_div = html.Div([
        column_list,
        #table
    ])
    
    ##return what to use 
    return results_div



@app.callback(
    Output('column-description', 'children'),
    [Input('column-dropdown', 'value')]
)
def update_column_description(selected_column):
    if not selected_column:
        return html.Div("Select a column from the dropdown to see the information.")

    column_info = get_column_description(selected_column)

    return html.Div(column_info)


# search function
def find_matching_columns(queries, df):
    matching_columns = []
    for column in df.columns:
        for query in queries:
            query_words = query.lower().split()
            if any(word in column.lower() for word in query_words):
                matching_columns.append(column)
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




app.layout = html.Div([
                html.Div([sidebar]),
                dcc.Store(id="search-flag", data=False)
  ])
  


if __name__ == '__main__':
    app.run_server(debug=True)


    # Create a list of matching columns and their descriptions 
   # column_list = html.Div([
    #  html.H3("Data summary:", style={'border':'1px solid white', 'padding':'5px','width': 'fit-content'}),
    #  html.Ul([
        ##THE BULLET LIST
   #     html.Li([
   #         html.Span(desc)
   #     ])
   #     for desc in matching_columns.items()
   #   ]),
   # ])
    
    # Create a table of the matching columns
   # df_matching_columns = df[list(matching_columns.keys())]
   # table = html.Table([
   #     html.Thead(html.Tr([html.Th(col) for col in df_matching_columns.columns])),
   #     html.Tbody([html.Tr([html.Td(row[col]) for col in df_matching_columns.columns]) for i, row in df_matching_columns.iterrows()])
   # ])