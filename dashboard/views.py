import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests 
from pandas import DataFrame as df

from dashboard.utils import get_analytics_dict,  init_jobs


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

dash_app = dash.Dash(__name__,  external_stylesheets=external_stylesheets)
server = dash_app.server

dash_app.layout = html.Div([

    html.H1("Covid19 ", style={"text-align":"center"}),

    html.Div(
        [
            dcc.Input(
                placeholder="Enter country name",
                id="query-input",
                style={"width":"60%"},
                ),
            html.Button(id='submit-button', n_clicks=0, children='Submit'),
            html.Div(id='dummy'),
            
        ]
        , style={"text-align":"center", "width":"100%", "columnCount":2}),
    

    html.Table(
        [
            html.Thead(
                html.Tr(
                    [html.Th("No. of Confirmed"),
                     html.Th("No. of Deaths"),
                   #  html.Th("No. of Recovered"),
                      html.Th("No. of Population"), ]
                )
            ),

            html.Tbody([
                html.Th(0),
                html.Th(0),
               # html.Th(0),
                html.Th(0),
            ], id="count-table")
        ], style={"width": "100%"}
    ),

    html.H2("Top confirmed and deaths countries", style={"text-align": "center"}),

    dcc.Graph(id="top_five_countries"),

    html.H2("covid19 world map", style={"text-align": "center"}),

    html.Hr(),
    dcc.Graph(id="world_graph"),
    
    dcc.Interval(
        id='interval-component',
        interval=1000*1000,  # in milliseconds
        n_intervals=0
    ),
    dcc.Interval(
        id='interval-com',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    )

])

# ------------------------------- CALLBACKS ---------------------------------------- #

@dash_app.callback(Output("dummy", "children"), [Input("submit-button", "n_clicks")],
                    [State("query-input", "value")])
def new_search(n_clicks, query):
    if not query:
        return "Please enter a country name"
    query = query.strip()
   # query = list(map(lambda x: x.strip(), query))
    print(f"got a query{query}")
    init_jobs(query)
    return f"Dashboard started working on {query}..."

@dash_app.callback(Output('count-table', 'children'),
                   [Input('interval-com', 'n_intervals')])
def update_table(n):
    analytics = get_analytics_dict()
    return [
        html.Th(analytics['no_of_confirmed'], style={"color": "#3366ff"}),
        html.Th(analytics['no_of_deaths'], style={"color": "#009900"}),
       # html.Th(analytics['no_of_recovered'], style={"color": "#ff0066"}),
        html.Th(analytics['no_of_population'], style={"color": "#3366ff"}),
    ]

@dash_app.callback(Output('top_five_countries', 'figure'),
                  [Input('interval-component', 'n_intervals')] ) #
def update_top_five_countries(n):

    r = requests.get('http://coronavirus-tracker-api.herokuapp.com/v2/locations')

    r=df(r.json()['locations'])
    confirmed = []
    deaths = []
    for x in r['latest']:
        confirmed.append(x['confirmed'])
        deaths.append(x['deaths'])
    r['confirmed'] = df(confirmed)
    r['deaths'] = df(deaths)
    confirmed_top=r[['country','confirmed']]
    top_con=(confirmed_top.sort_values(by='confirmed',ascending=False))[0:5]
    x_con=top_con['country'].to_list()
    y_con=top_con['confirmed'].to_list()
    deaths_top=r[['country','deaths']]
    top_dth=(deaths_top.sort_values(by='deaths',ascending=False))[0:5]
    x_dth=top_dth['country'].to_list()
    y_dth=top_dth['deaths'].to_list()
    confirmed = {"x": x_con, "y": y_con}
    deaths = {"x": x_dth, "y": y_dth}


    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        "Confirmed Count", "Deaths Count"))

    fig.add_trace(

        go.Bar(x=confirmed['x'], y=confirmed['y'], orientation='v'),
        row=1, col=1
    )

    fig.add_trace(

        go.Bar(x=deaths['x'], y=deaths['y'], orientation='v'),
        row=1, col=2
    )

    fig.update_layout(showlegend=False)

    return fig

@dash_app.callback(Output('world_graph', 'figure'),
                   [Input('interval-component', 'n_intervals')])
def update_world_graph(n):
    r = requests.get('http://coronavirus-tracker-api.herokuapp.com/v2/locations')

    r=df(r.json()['locations'])
    lon = []
    lat = []
    for x in r['coordinates']:
        lon.append(x['longitude'])
        lat.append(x['latitude'])

    r['lon'] = df(lon)
    r['lat'] = df(lat)

    confirmed = []
    confirmed_size=[]
    recovered = []
    recovered_size =[]
    deaths = []
    deaths_size = []
    for x in r['latest']:
        confirmed_size.append(int(x['confirmed'])/10000)
        recovered_size.append(int(x['recovered'])/10000)
        deaths_size.append(int(x['deaths'])/1000)
        confirmed.append(x['confirmed'])
        recovered.append(x['recovered'])
        deaths.append(x['deaths'])
    r['confirmed'] = df(confirmed)
    r['recovered'] = df(recovered)
    r['deaths'] = df(deaths)
    r['confirmed_size'] = df(confirmed_size)
    r['recovered_size'] = df(recovered_size)
    r['deaths_size'] = df(deaths_size)
    map_confirmed = go.Scattermapbox(customdata=r.loc[:,['confirmed','recovered','deaths']],
                                        name='coronavirus',
                                        lon=r['lon'],
                                        lat=r['lat'],
                                        text=r['country'],
                                        hovertemplate="<b>%{text}</b><br><br>"+
                                        "confirmed : %{customdata[0]}<br>"+
                                        "<extra></extra>",
                                        mode='markers',
                                        showlegend=True,
                                        marker=go.scattermapbox.Marker(
                                            size=r['confirmed_size'],
                                            color='green',
                                            opacity=0.7
                                        )) 

    v_layout=go.Layout(
                mapbox_style='white-bg',
                autosize=True,
                mapbox_layers=[
                    {
                        'below':'traces',
                        'sourcetype':'raster',
                        'source':[ "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                        ]  
                    }
                            ]
                )


    data= [map_confirmed]
    fig = go.Figure(data=data,layout=v_layout)
    return fig