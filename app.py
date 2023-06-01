import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import re
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta

#################################################

# create app

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "25%",
    "margin-right": "2rem",
    
    # "padding": "2rem 1rem",
}

# Read in the data
df = pd.read_csv('Example_real.csv')
df['DateTime']=df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x/1000))
df=df.reset_index(drop=True)
for index, row in df.iterrows():
    if row['latitude']=='False':
        df.at[index, 'latitude']=False
    else:
        df.at[index, 'latitude']=float(row['latitude'])
    if row['longitude']=='False':
        df.at[index, 'longitude']=False
    else:
        df.at[index, 'longitude']=float(row['longitude'])

##################################################
# make timetable
def get_cat(col):
  if col in ["TotalSteps", "StepsToday"]:
    return "Movement"
  if col in ["name", "lastUpdateTime", "packageName", "isSystemApp", "firstInstallTime", "isUpdatedSystemApp"]:
    return "App History"
  if col in ["altitude", "longitude", "latitude", "speed", "accuracy"]:
    return "Location"
  if col in ["bucketDisplay", "messageBox", "isPinned", "timesContacted", "number", "contact", "isStarred", "messageClass"]:
    return "Message"
  else:
    return "Other"

def make_timetable(df):

    E_agg=pd.DataFrame()
    E_agg['Movement']=df['TotalSteps'] | df['StepsToday']
    E_agg['App History']=df['name'] | df['lastUpdateTime'] | df["packageName"] | df["isSystemApp"] | df["firstInstallTime"] | df["isUpdatedSystemApp"]
    E_agg['Location']=df['altitude'] | df['longitude'] | df["latitude"] | df["speed"] | df["accuracy"]
    E_agg['Message']=df['bucketDisplay'] | df['messageBox'] | df["isPinned"] | df["timesContacted"] | df["number"] | df["contact"] | df["isStarred"] | df["messageClass"]
    E_agg['Other']=df['mimetype']
    E_agg['DateTime']=df['DateTime']

    agg_starts=[]
    agg_finishes=[]
    agg_categories=[]

    for col in E_agg.columns:
      if col!='index' and col!='timestamp' and col!='DateTime' and col!='level_0' and col!='Day':
        start=-1
        doing=False
        cur=-1
        for index, row in E_agg.iterrows():
            if row[col]:
                if start==-1:
                    agg_starts.append(row['DateTime'])
                    agg_categories.append(col)
                    start=row['DateTime']
                    doing=True
                if doing:
                    cur=row['DateTime']
                if index==len(E_agg)-1:
                    agg_finishes.append(row['DateTime'])
                    start=-1
                    doing=False
                    cur=-1
            else:
                if doing:
                    start=-1
                    agg_finishes.append(cur)
                    cur=-1
                    doing=False

    E_agg_time=pd.DataFrame()
    E_agg_time['Start']=agg_starts
    E_agg_time['Finish']=agg_finishes
    E_agg_time['Category']=agg_categories


    cat_array=list(set(list(E_agg_time['Category'].values)))
    cat_array.sort()
    if 'Other' in cat_array:
        cat_array.append(cat_array.pop(cat_array.index('Other')))
    fig = px.timeline(E_agg_time, x_start="Start", x_end="Finish", y="Category", color="Category")
    fig.update_yaxes(categoryarray=cat_array)
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(width=1000, height=300)

    return fig
timetable = dcc.Graph(id='timetable', figure=make_timetable(df))

all_cats=['TotalSteps', 'StepsToday', 'name', 'lastUpdateTime', "packageName", "isSystemApp", "firstInstallTime", "isUpdatedSystemApp", 'altitude', 'longitude', "latitude", "speed", "accuracy", 'bucketDisplay', 'messageBox', "isPinned", "timesContacted", "number", "contact", "isStarred", "messageClass", 'mimetype']

def make_breakdown(df):

    E_agg=pd.DataFrame()
    E_agg['Movement']=df['TotalSteps'] | df['StepsToday']
    E_agg['App History']=df['name'] | df['lastUpdateTime'] | df["packageName"] | df["isSystemApp"] | df["firstInstallTime"] | df["isUpdatedSystemApp"]
    E_agg['Location']=df['altitude'] | df['longitude'] | df["latitude"] | df["speed"] | df["accuracy"]
    E_agg['Message']=df['bucketDisplay'] | df['messageBox'] | df["isPinned"] | df["timesContacted"] | df["number"] | df["contact"] | df["isStarred"] | df["messageClass"]
    E_agg['Other']=df['mimetype']
    E_agg['DateTime']=df['DateTime']

    agg_starts=[]
    agg_finishes=[]
    agg_categories=[]

    for col in E_agg.columns:
      if col!='index' and col!='timestamp' and col!='DateTime' and col!='level_0' and col!='Day':
        start=-1
        doing=False
        cur=-1
        for index, row in E_agg.iterrows():
            if row[col]:
                if start==-1:
                    agg_starts.append(row['DateTime'])
                    agg_categories.append(col)
                    start=row['DateTime']
                    doing=True
                if doing:
                    cur=row['DateTime']
                if index==len(E_agg)-1:
                    agg_finishes.append(row['DateTime'])
                    start=-1
                    doing=False
                    cur=-1
            else:
                if doing:
                    start=-1
                    agg_finishes.append(cur)
                    cur=-1
                    doing=False
    lengths={'Movement':datetime.timedelta(seconds=0, minutes=0, hours=0), 'App History':datetime.timedelta(seconds=0, minutes=0, hours=0), 'Location':datetime.timedelta(seconds=0, minutes=0, hours=0), 'Message':datetime.timedelta(seconds=0, minutes=0, hours=0), 'Other':datetime.timedelta(seconds=0, minutes=0, hours=0)}
    for i in range(len(agg_starts)):
        if agg_categories[i] in lengths:
            lengths[agg_categories[i]]+=agg_finishes[i]-agg_starts[i]
    content_list=[html.H4('Data Collection Breakdown: '+str(df['DateTime'].loc[0].strftime("%Y-%m-%d")), style={'text-decoration':'underline'})]
    data_list=[]
    for key, val in lengths.items():
        data_list.append("- The "+"**"+key+"**"+" data was collected for "+"**"+str(val.seconds//3600)+" hours and "+str((val.seconds//60)%60)+" minutes**.")
    content_list.append(dcc.Markdown(data_list, style={'font-size': '18px', 'font-family':'Proxima Nova'}))

    fig = make_subplots(rows=2, cols=3, specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}],
                                                [{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]])
    fig.add_trace(go.Pie(labels=['Collected', 'Not Collected'], values=[lengths['Movement'].total_seconds(), (datetime.timedelta(days=1)-lengths['Movement']).total_seconds()], name="Movement", direction='clockwise', sort=False), 1, 1)
    fig.add_trace(go.Pie(labels=['Collected', 'Not Collected'], values=[lengths['App History'].total_seconds(), (datetime.timedelta(days=1)-lengths['App History']).total_seconds()], name="App History", direction='clockwise', sort=False), 1, 2)
    fig.add_trace(go.Pie(labels=['Collected', 'Not Collected'], values=[lengths['Location'].total_seconds(), (datetime.timedelta(days=1)-lengths['Location']).total_seconds()], name="Location", direction='clockwise', sort=False), 1, 3)
    fig.add_trace(go.Pie(labels=['Collected', 'Not Collected'], values=[lengths['Message'].total_seconds(), (datetime.timedelta(days=1)-lengths['Message']).total_seconds()], name="Message", direction='clockwise', sort=False), 2, 1)
    fig.add_trace(go.Pie(labels=['Collected', 'Not Collected'], values=[lengths['Other'].total_seconds(), (datetime.timedelta(days=1)-lengths['Other']).total_seconds()], name="Other", direction='clockwise', sort=False), 2, 2)
    fig.update_traces(hole=.8, hoverinfo="label+name", textinfo='none')
    fig.update_layout(annotations=[dict(text='Movement', x=0.145, y=0.8, xanchor='center', yanchor='middle', font_size=10, showarrow=False),
                                    dict(text='App History', x=0.5, y=0.8, xanchor='center', yanchor='middle', font_size=10, showarrow=False),
                                    dict(text='Location', x=0.855, y=0.8, xanchor='center', yanchor='middle', font_size=10, showarrow=False),
                                    dict(text='Message', x=0.145, y=0.225, xanchor='center', yanchor='middle', font_size=10, showarrow=False),
                                    dict(text='Other', x=0.5, y=0.225, xanchor='center', yanchor='middle', font_size=10, showarrow=False)],
                        width=700, height=400)
    return content_list, fig

breakdown_list, breakdown_fig=make_breakdown(df)
collection_breakdown=html.Div(id='collection-breakdown', children=breakdown_list, style=CONTENT_STYLE)
collection_breakdown_fig=dcc.Graph(id='collection-breakdown-fig', figure=breakdown_fig)

def make_summary(df, starttime, endtime):
    df=df.reset_index(drop=True)
    datatypes=[]
    starts=[]
    finishes=[]
    categories=[]

    for col in df.columns:
      if col!='index' and col!='timestamp' and col!='DateTime' and col!='level_0' and col!='Day':
        start=-1
        doing=False
        cur=-1
        for index, row in df.iterrows():
          if row[col]:
            if start==-1:
              starts.append(row['DateTime'])
              datatypes.append(col)
              categories.append(get_cat(col))
              start=row['DateTime']
              doing=True
            if doing:
              cur=row['DateTime']
            if index==len(df)-1:
              finishes.append(row['DateTime'])
              start=-1
              doing=False
              cur=-1
          else:
            if doing:
              start=-1
              finishes.append(cur)
              cur=-1
              doing=False

    E_time=pd.DataFrame()
    E_time['Data']=datatypes
    E_time['Start']=starts
    E_time['Finish']=finishes
    E_time['Category']=categories

    sums=[]
    for i in list(set(categories)):
        if i=='Movement':
            # added some text-styling
            sums.append(html.B("Movement", style={'color':'white', 'font-family':'Proxima Nova'}))
            sums.append(" data is concerned with how much you move around.")
            sums.append(html.Br())
            sums.append(html.Br())
            sums.append("When this type of data is collected, the number of steps you took per day and the number of steps you took in total is known.")
            sums.append(html.Br())
            # added line for clarity
            sums.append(html.Hr(style={'color':'white'}))
        if i=='App History':
            # added some text-styling
            sums.append(html.B("App History", style={'color':'white', 'font-family':'Proxima Nova'}))
            sums.append(" data is concerned with your app usage.")
            sums.append(html.Br())
            sums.append(html.Br())
            sums.append("When this type of data is collected, if and when you installed a new app, and when and which app you updated is known.")
            sums.append(html.Br())
            # added line for clarity
            sums.append(html.Hr(style={'color':'white'}))
        if i=='Location':
            # added some text-styling
            sums.append(html.B("Location", style={'color':'white', 'font-family':'Proxima Nova'}))
            sums.append(" data is concerned with your geographical location.")
            sums.append(html.Br())
            sums.append(html.Br())
            sums.append("When this type of data is collected, where you are, how high you are from the ground, and how fast you are moving is known.")
            sums.append(html.Br())
            # added line for clarity
            sums.append(html.Hr(style={'color':'white'}))
        if i=='Message':
            # added some text-styling
            sums.append(html.B("Message", style={'color':'white', 'font-family':'Proxima Nova'}))
            sums.append(" data is concerned with your text and messenger app usage.")
            sums.append(html.Br())
            sums.append(html.Br())
            sums.append("When this type of data is collected, the contact information of your correspondent, whether you pinned a message, the number of times you contacted a person, and whether the person is marked as important is known.")
            sums.append(html.Br())
            # added line for clarity
            sums.append(html.Hr(style={'color':'white'}))

    # added styles for color and font-family for Collected Data in as well as the paragraphs of texts
    return html.Div([html.P(['Data Collection', html.Br(), 'Time: ', (starttime.strftime("%H:%M")+"~"+endtime.strftime("%H:%M")+","), html.Br(), 'Date: ', starttime.strftime("%Y-%m-%d"), html.Br()], style={'font-size': '24px','color':'white', 'font-family':'Proxima Nova', 'border':'1px solid white', 'padding':'10px'}), html.P(sums, style={'font-size': '18px', 'color':'white', 'font-family':'Proxima Nova'})])

summary=html.Div(children=make_summary(df, df['DateTime'].iat[0], df['DateTime'].iat[-1]), id='summary')

@app.callback(
    Output("summary", "children"),
    [Input("timetable", "clickData")],
    prevent_initial_call=True)
def update_summary(clickData):
    cats={
      "Movement": ["timestamp", "DateTime", "TotalSteps", "StepsToday"],
      "App History": ["timestamp", "DateTime", "name", "lastUpdateTime", "packageName", "isSystemApp", "firstInstallTime", "isUpdatedSystemApp"],
      "Location": ["timestamp", "DateTime", "altitude", "longitude", "latitude", "speed", "accuracy"],
      "Message": ["timestamp", "DateTime", "bucketDisplay", "messageBox", "isPinned", "timesContacted", "number", "contact", "isStarred", "messageClass"],
      "Other": ["timestamp", "DateTime", "mimetype"]
    }
    select_cat=clickData['points'][0]['y']
    select_end = datetime.datetime.strptime(clickData['points'][0]['x'], '%Y-%m-%d %H:%M:%S.%f')
    select_start = datetime.datetime.strptime(clickData['points'][0]['base'], '%Y-%m-%dT%H:%M:%S.%f')
    cat_df=df[(cats[select_cat])]
    selected_df=cat_df.loc[(cat_df['DateTime']>select_start) & (cat_df['DateTime']<select_end)].reset_index()
    return make_summary(selected_df, select_start, select_end)
##################################################


# make calendar UI
#################################################
calendar_style={
    'display': 'flex',
    'justify-content': 'left',
    'align-items': 'center',
    'margin-bottom':'15px',
    'font-family':'Proxima Nova'
}

calendarUI=dcc.DatePickerSingle(
        id='date-picker',
        display_format='MMM Do, YYYY A',
        date=df['DateTime'].iloc[0],
        style=dict(width='100%'))

calendarresult=html.Table(id='table', children=[
    html.Thead([
        html.Tr([
            html.Th('Data'),
            html.Th('Times')
        ])
    ]),
    html.Tbody(id='table-body')
])
# Function to filter dataframe based on selected date
def filter_dataframe(date):
    if not date:
        # Return entire dataframe if no date selected
        filtered_df = df
    else:
        # Filter dataframe by selected date
        filtered_df = df[df['DateTime'].dt.floor('1d') == pd.to_datetime(date).floor('1d')]
    filtered_df=filtered_df.reset_index(drop=True)
    return filtered_df

# update timetable
@app.callback(Output('timetable', 'figure'),
              [Input('date-picker', 'date')])
def update_timetable(date):
    cur_df=filter_dataframe(date)
    fig=make_timetable(cur_df)
    return fig
def update_summary_date(date):
    filtered_df = filter_dataframe(date)
    return make_summary(filtered_df, filtered_df['DateTime'].iat[0], filtered_df['DateTime'].iat[-1])

@app.callback(Output('collection-breakdown', 'children'),
              [Input('date-picker', 'date')])
def update_breakdown(date):
    filtered_df = filter_dataframe(date)
    breakdown_list, breakdown_fig=make_breakdown(filtered_df)
    return breakdown_list
@app.callback(Output('collection-breakdown-fig', 'figure'),
              [Input('date-picker', 'date')])
def update_breakdown(date):
    filtered_df = filter_dataframe(date)
    breakdown_list, breakdown_fig=make_breakdown(filtered_df)
    return breakdown_fig


#################################################



# create sidebar
#################################################

# the style arguments for the sidebar. We use position:fixed and a fixed width
# changed color
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "23%",
    "padding": "2rem 1rem",
    "background-color": "#000000",
    "overflow-y": "scroll"
}

sidebar = html.Div(
    [
       # added some font styles
        html.H3("Date Selection", style={"color":"#FFFFFF", "margin-bottom":"12px", "font-family":"Proxima Nova"}), 
        html.Div([calendarUI], style=calendar_style),
        html.Hr(style={"color":"#FFFFFF"}),
        summary
    ],
    style=SIDEBAR_STYLE,
)



content = html.Div([
            html.Header(
                [
                   # added some font styles
                    html.H1("Team 1 DP5 Prototype", style={'font-family':'Proxima Nova', 'margin-top':'20px'})
                ], style=CONTENT_STYLE
            ),
            html.Div([timetable], style=CONTENT_STYLE),
            collection_breakdown,
            html.Div([collection_breakdown_fig], style=CONTENT_STYLE),
        ], style={"overflow-y": "scroll"})

app.layout = html.Div([
                html.Div([sidebar, content])
            ])


# run
if __name__ == '__main__':
    app.run_server(debug=True)