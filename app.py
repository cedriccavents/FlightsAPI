# app
from datetime import date
import difflib
import pandas as pd
from datetime import datetime, date
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Output, Input, State, dash_table
import numpy as np
import plotly.graph_objects as go

from helper import holiday_return_dt, roundup
from skyscanner import SkyScannerAPI

external_stylesheets = [dbc.themes.BOOTSTRAP, dbc.themes.YETI]
app = Dash(
    __name__,
    external_stylesheets=external_stylesheets,
)

# static data
airports = pd.read_csv(r'airport_ids.csv')
airports_dict = dict(zip(airports['location'], airports['id']))
airports_id = dict(zip(airports['title'], airports['id']))


# dash objects
class AppObjects():
    """ class to define dash objects used throughout apps
    """
    @staticmethod
    def date_picker(self, id: str):
        return dcc.DatePickerSingle(
            id=id,
            month_format='MMM Do, YY',
            placeholder='MMM Do, YY',
            date=datetime.now().date()
        )

    @staticmethod
    def input_group(self, header_text: str, component):
        return dbc.InputGroup([dbc.InputGroupText(header_text), component])


# building blocks
params = dbc.Card(
    [
        # dbc.CardHeader(html.H4('Parameters')),
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText('API-Key'),
                                dbc.Input(id='api-key')
                            ],
                        )
                    ),
                    dbc.Col([])
                ]
            )
        )
    ]
)

departures = dbc.Card(
    [
        # dbc.CardHeader(html.H4('Departure & Destination')),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(html.H6('Depart'), style={'font-style': 'italic'}),
                        dbc.Col(html.H6('From'), style={'font-style': 'italic'}),
                        dbc.Col(html.H6('When'), style={'font-style': 'italic'}),
                        dbc.Col([]),
                    ],
                    align='start'
                ),
                dbc.Row(
                    [
                        dbc.Col(dbc.Input(id='departure-location', placeholder="Country:", style={'height': 50})),
                        dbc.Col(
                            dcc.Dropdown(
                                placeholder="Airport:",
                                options=['London Heathrow', 'London Gatwick', 'London Stansted'],
                                    id='inbound-airport',
                                    style={'textAlign': 'centre', 'height': '50px', 'font': 'Lucida Sans'},
                                ),
                        ),
                        dbc.Col(
                            dcc.DatePickerRange(
                                id='date-range',
                                month_format='MMM Do, YY',
                                start_date_placeholder_text='Depart',
                                end_date_placeholder_text='Return',
                            )
                        ),
                        dbc.Col([]),
                    ]
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(html.H6('To'), style={'font-style': 'italic'}),
                        dbc.Col([]),
                        dbc.Col([]),
                        dbc.Col([]),
                    ],
                    align='start'
                ),
                dcc.Dropdown(
                    placeholder='Country:',
                    id='dropdown',
                    options=[
                        {'label': country, 'value': country} for country in list(airports['location'].drop_duplicates())
                    ],
                    value=['Option3', 'and 20 more'],
                    style={'font': 'Helvetica Neue'},
                    multi=True,
                ),
                html.Br(),
                html.H6('Select your airports', style={'font-style': 'italic'}),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Checklist(
                               id='outbound-airports-1',
                               options=[],
                               value=[]
                            )
                        ),
                        dbc.Col(
                            dcc.Checklist(
                               id='outbound-airports-2',
                               options=[],
                               value=[]
                            )
                        ),
                        dbc.Col(
                            dcc.Checklist(
                               id='outbound-airports-3',
                               options=[],
                               value=[]
                            )
                        ),
                        dbc.Col(
                            dcc.Checklist(
                               id='outbound-airports-4',
                               options=[],
                               value=[]
                            )
                        ),
                        dbc.Col(
                            dcc.Checklist(
                               id='outbound-airports-5',
                               options=[],
                               value=[]
                            )
                        ),
                    ]
                ),
                html.Br(),
                dcc.Checklist(
                    [' Check all flights for next 5 days after departure date'],
                    [],
                    # className='ml-1'
                ),
                html.Br(),
                dbc.Button('Search', id='run-button'),
            ]
        ),
    ]
)

table_fields = ['airport', 'destination', 'departure', 'arrival', 'duration', 'stops', 'airline']
df = [{'raw_price': None}] + [{f'1_{key}': None} for key in table_fields] + [{f'2_{key}': None} for key in table_fields]

tab_results = html.Div(
    [
        html.Br(),
        html.P("", id='searches', style={'font-style': 'italic'}),
        html.Br(),
        html.Div(
            [
                dbc.DropdownMenu(
                    label="Download",
                    children=[
                        dbc.DropdownMenuItem(".csv", id='button-download-csv'),
                        dbc.DropdownMenuItem(".txt", id='button-download-txt'),
                    ],
                ),
                dcc.Download(id='download-csv'),
                dcc.Download(id='download-txt'),
            ]
        ),
        html.Br(),
        html.Div(
            [
                dash_table.DataTable(
                    id='flights-table',
                    data=df,
                    columns=[
                        {'id': 'raw_price', 'name': 'raw_price'},
                        {'id': '1_airport', 'name': '1_airport'},
                        {'id': '1_destination', 'name': '1_destination'},
                        {'id': '1_departure', 'name': '1_departure'},
                        {'id': '1_arrival', 'name': '1_arrival'},
                        {'id': '1_duration', 'name': '1_duration'},
                        {'id': '1_stops', 'name': '1_stops'},
                        {'id': '1_airline', 'name': '1_airline'},
                        {'id': '2_airport', 'name': '2_airport'},
                        {'id': '2_destination', 'name': '2_destination'},
                        {'id': '2_departure', 'name': '2_departure'},
                        {'id': '2_arrival', 'name': '2_arrival'},
                        {'id': '2_duration', 'name': '2_duration'},
                        {'id': '2_stops', 'name': '2_stops'},
                        {'id': '2_airline', 'name': '2_airline'}
                    ],
                    editable=False,
                    style_header={
                        'color': "#2a3f5f"
                    },
                    style_data={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white',
                    },
                    style_cell={
                        'font_size': '10px',
                        'tex_align': 'center',
                        'color': "#506784"
                    },
                ),
            ],
        ),
    ]
)

tab_visuals = html.Div(
    [
        dcc.Graph(
            id='boxplot-flights',
            config={'displayModeBar': False}
        ),
    ]
)

results = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.Tabs(
                    [
                        dbc.Tab(tab_results, label='Results'),
                        dbc.Tab(tab_visuals, label='Visuals')
                    ]
                )
            ]
        )
    ]
)

# layout
app.layout = html.Div(
    [
        html.H2('Skyscanner Flight Optimiser', className='main-header'),
        html.Br(),
        params,
        html.Br(),
        departures,
        html.Br(),
        dbc.Spinner(results, color="success"),
    ],
)


@app.callback(
    Output('inbound-airport', 'options'),
    Input('departure-location', 'value')
)
def update_outbound_airports(loc: str) -> list:
    try:
        loc_match = difflib.get_close_matches(loc, list(airports_dict.keys()))[0]
        return list(airports[airports['location'] == loc_match]['title'])
    except:
        return []

@app.callback(
    Output('outbound-airports-1', 'options'),
    Output('outbound-airports-2', 'options'),
    Output('outbound-airports-3', 'options'),
    Output('outbound-airports-4', 'options'),
    Output('outbound-airports-5', 'options'),
    Input('dropdown', 'value')
)
def update_inbound_airports(loc: list) -> [list, list, list, list, list]:
    """ update inbound airports based on user countries choice: max choice is currently set to 5 countries
    """
    out = {
        0: [],
        1: [],
        2: [],
        3: [],
        4: []
    }

    if len(loc) < 2:
        try:
            loc_match = difflib.get_close_matches(loc[0], list(airports_dict.keys()))[0]
            out[0] += list(airports[airports['location'] == loc_match]['title'])
        except:
            out[0] += []
    else:
        for k in range(len(loc)):
            try:
                loc_match = difflib.get_close_matches(loc[k], list(airports_dict.keys()))[0]
                out[k] += list(airports[airports['location'] == loc_match]['title'])
            except:
                out[k] += []
    return out[0], out[1], out[2], out[3], out[4]

@app.callback(
    [
        Output('searches', 'children'),
        Output('flights-table', 'data'),
    ],
    [
        State('api-key', 'value'),
        State('inbound-airport', 'value'),
        State('date-range', 'start_date'),
        State('date-range', 'end_date'),
        Input('run-button', 'n_clicks'),
        Input('outbound-airports-1', 'value'),
        Input('outbound-airports-2', 'value'),
        Input('outbound-airports-3', 'value'),
        Input('outbound-airports-4', 'value'),
        Input('outbound-airports-5', 'value'),
    ]
)
def find_all_roundtrips(*args):
    """ query all roundtrips for given destinations
    """
    # parameters
    api_key = args[0]
    departure_location = args[1]
    departure_date = args[2]
    return_date = args[3]
    try:
        num_nights = (
                datetime.strptime(return_date, '%Y-%m-%d')
                - datetime.strptime(departure_date, '%Y-%m-%d')).days
    except:
        pass

    # class instance
    api = SkyScannerAPI(api_key)

    dfs = []
    str_ret = 0
    destinations = sum(args[5:], [])

    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        print(button_id)
        if button_id == 'run-button':
            for destination in destinations:
                try:
                    df_rt = api.get_roundtrip(
                        airports_id[departure_location],
                        airports_id[destination],
                        departure_date,
                        holiday_return_dt(departure_date, int(num_nights)),
                        "economy",
                    )
                    dfs.append(df_rt)
                except Exception as e:
                    print(f"ERROR (!) -- skip {destination}: {e}")

            dfs = pd.concat(dfs, axis=0).reset_index(drop=True)

            # sort cheapest to most expensive
            dfs = dfs.sort_values(by='raw_price', ascending=True).reset_index(drop=True)

            # return string for info
            str_ret = f'Number of flights found: {len(dfs)}'

            # update slider values
            max_stops = dfs['1_stops'].max()
            max_price = roundup(dfs['raw_price'].max())
            step = max_price/4

    if len(dfs) == 0:
        dfs = pd.DataFrame(dfs)

    return str_ret, dfs.to_dict('records')

@app.callback(
    Output('boxplot-flights', 'figure'),
    Input('flights-table', 'data'),
)
def update_boxplot(flights_data):
    """ Create Boxplots to visualize flight price distributions
    """
    df_flights = pd.DataFrame(flights_data)

    # create boxplot for each destination
    fig = go.Figure()
    try:
        destinations = list(df_flights['1_destination'].drop_duplicates())
        for dest in destinations:
            vals = np.array(df_flights[df_flights['1_destination'] == dest]['raw_price'].reset_index(drop=True))
            fig.add_trace(go.Box(x=vals, name=dest))
            fig.update_layout(
                xaxis_title='Flight price',
            )
    except:
        print('No request have been done: SKIP')

    return fig

# downloads
@app.callback(
    Output('download-csv', 'data'),
    Input('button-download-csv', 'n_clicks'),
    Input('flights-table', 'data'),
    prevent_initial_call=True
)
def download_csv(n_clicks, flights_data):
    df = pd.DataFrame(flights_data)
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'button-download-csv':
            return dcc.send_data_frame(df.to_csv, 'flights_data.csv')

@app.callback(
    Output('download-txt', 'data'),
    Input('button-download-txt', 'n_clicks'),
    Input('flights-table', 'data'),
    prevent_initial_call=True
)
def download_txt(n_clicks, flights_data):
    df = pd.DataFrame(flights_data)
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'button-download-txt':
            return dict(content=df.to_dict('records'), filename='flights_data.txt')


if __name__ == "__main__":
    app.run_server(debug=True)
