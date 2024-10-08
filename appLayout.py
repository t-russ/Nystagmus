import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

app = Dash(external_stylesheets=[dbc.themes.COSMO])

def createGraphControls(recordingIndex, trialCount):

    new_graph_controls = dbc.Card(
        [
            html.Div([
                html.Label('Trial:'),
                dcc.Dropdown(id={'type':'trial-dropdown', 'index': recordingIndex}, options=["Trial " + str(i + 1) for i in range(trialCount)], value="Trial 1",
                            clearable= False),
                ],
                style= {"margin-bottom": "10px"},
            ),

            html.Div([
                html.Label('Eye Tracked:'),
                dbc.Checklist(id ={'type':'eye-tracked', 'index': recordingIndex}, options=['Left', 'Right'],inline=True, 
                            inputStyle={"margin-right": 5}),
                ],
                style= {"margin-bottom": 10, "margin-top":10, "text-align": "center",},
            ),

            html.Div([
                    html.Label('Direction Tracked:'),
                    dbc.Checklist(id={'type': 'xy-tracked', 'index': recordingIndex}, options=['X', 'Y'], inline=True, 
                                inputStyle={"margin-right": 5},
                                value=['X', 'Y']),
                ],
                style= {"margin-bottom": 10, "margin-top":10, "text-align": "center"}
            ),

            html.Div([
                dcc.Store(id={'type': 'remapping-minus10degs-value', 'eye':'Left', 'direction':'X', 'index': recordingIndex}, data= -2000),
                dcc.Store(id={'type': 'remapping-plus10degs-value', 'eye':'Left', 'direction':'X', 'index': recordingIndex}, data= -6000),
                dbc.Checklist(id={'type': 'remapping-check',  'eye':'Left', 'direction':'X', 'index': recordingIndex}, 
                options=[{'label': 'Enable X Left Calibration','value': True}],
                inline=True, labelStyle={"margin-right": 10},inputStyle={"margin-right": 5}),

                dbc.Row([
                    dbc.Col([
                        html.Label('+10º'),
                        dbc.Input(id={'type': 'remapping-plus10degs', 'eye':'Left', 'direction':'X', 'index': recordingIndex},
                                 type='number', placeholder='', disabled=True),
                        ], 
                        width='5'),

                    dbc.Col([
                        html.Label('-10º'),
                        dbc.Input(id={'type': 'remapping-minus10degs', 'eye':'Left', 'direction':'X', 'index': recordingIndex},
                                type='number', placeholder='', disabled=True),
                        ], 
                        width='5'),
                    ],
                    justify='center',
                ),

                ],      
                style= {"margin-bottom": 10, "text-align": "center"}, id={'type': 'calibration-x-left', 'index': recordingIndex},
            ),

            html.Div([
                dcc.Store(id={'type': 'remapping-minus10degs-value', 'eye':'Left', 'direction':'Y', 'index': recordingIndex}, data= -4000),
                dcc.Store(id={'type': 'remapping-plus10degs-value', 'eye':'Left', 'direction':'Y', 'index': recordingIndex}, data= -8000),
                dbc.Checklist(id={'type': 'remapping-check', 'eye':'Left', 'direction':'Y', 'index': recordingIndex}, 
                            options=[{'label': 'Enable Y Left Calibration','value': True}], inline=True,
                            labelStyle={"margin-right": 10},inputStyle={"margin-right": 5}),
                            
                dbc.Row([
                    dbc.Col([
                        html.Label('+10º'),
                        dbc.Input(id={'type': 'remapping-plus10degs', 'eye':'Left', 'direction':'Y', 'index': recordingIndex},
                                 type='number', placeholder='', disabled=True),
                        ], 
                        width='5'),

                    dbc.Col([
                        html.Label('-10º'),
                        dbc.Input(id={'type': 'remapping-minus10degs', 'eye':'Left', 'direction':'Y', 'index': recordingIndex},
                                type='number', placeholder='', disabled=True),
                        ], 
                        width='5'),
                    ],
                    justify='center'
                ),

                ],      
                style= {"margin-bottom": 10, "margin-top": 10, "text-align": "center"}, id={'type': 'calibration-y-left', 'index': recordingIndex},
            ),
            html.Div([
                dcc.Store(id={'type': 'remapping-minus10degs-value', 'eye':'Right', 'direction':'X', 'index': recordingIndex}, data= -2000),
                dcc.Store(id={'type': 'remapping-plus10degs-value', 'eye':'Right', 'direction':'X', 'index': recordingIndex}, data= -6000),
                dbc.Checklist(id={'type': 'remapping-check', 'eye':'Right', 'direction':'X', 'index': recordingIndex}, 
                            options=[{'label': 'Enable X Right Calibration','value': True}], inline=True,
                            labelStyle={"margin-right": 10},inputStyle={"margin-right": 5}),

                dbc.Row([
                    dbc.Col([
                        html.Label('+10º'),
                        dbc.Input(id={'type': 'remapping-plus10degs', 'eye':'Right', 'direction':'X', 'index': recordingIndex},
                                 type='number', placeholder='', disabled=True),
                        ], 
                        width='5'),

                    dbc.Col([
                        html.Label('-10º'),
                        dbc.Input(id={'type': 'remapping-minus10degs', 'eye':'Right', 'direction':'X', 'index': recordingIndex},
                                type='number', placeholder='', disabled=True),
                        ], 
                        width='5'),
                    ],
                    justify='center',
                ),

                ],      
                style= {"margin-bottom": 10, "text-align": "center"}, id={'type': 'calibration-x-right', 'index': recordingIndex},
            ),

            html.Div([
                dcc.Store(id={'type': 'remapping-minus10degs-value', 'eye':'Right', 'direction':'Y', 'index': recordingIndex}, data= -4000),
                dcc.Store(id={'type': 'remapping-plus10degs-value', 'eye':'Right', 'direction':'Y', 'index': recordingIndex}, data= -8000),
                dbc.Checklist(id={'type': 'remapping-check', 'eye':'Right', 'direction':'Y', 'index': recordingIndex},
                            options=[{'label': 'Enable Y Right Calibration','value': True}], inline=True,
                            labelStyle={"margin-right": 10},inputStyle={"margin-right": 5}),
                            
                dbc.Row([
                    dbc.Col([
                        html.Label('+10º'),
                        dbc.Input(id={'type': 'remapping-plus10degs', 'eye':'Right', 'direction':'Y', 'index': recordingIndex},
                                 type='number', placeholder='', disabled=True),
                        ], 
                        width='5'),

                    dbc.Col([
                        html.Label('-10º'),
                        dbc.Input(id={'type': 'remapping-minus10degs', 'eye':'Right', 'direction':'Y', 'index': recordingIndex},
                                type='number', placeholder='', disabled=True),
                        ], 
                        width='5'),
                    ],
                    justify='center'
                ),

                ],      
                style= {"margin-bottom": 10, "margin-top": 10, "text-align": "center"}, id={'type': 'calibration-input-div', 'eye':'right', 'direction':'y', 'index': recordingIndex},
            ),

            html.Div([
                dbc.Button("Calibrate Data", id={'type': 'calibrate-button', 'index': recordingIndex}, color="primary", className="mr-2"),
                ], 
            id={'type': 'calibrate-button-div', 'index': recordingIndex}, className="d-flex justify-content-center", style={"margin-top": "10px"},
            ),
        ],
        body=True,
        )
   
    return new_graph_controls

upload_button = html.Div([
    dcc.Upload([dbc.Button("Upload EDF", id="upload-edf-button", color="primary", className="mr-2",)], id = 'upload-edf',  accept=".edf"),
    html.Div(id='upload-output', style={"margin-top": "10px" }, ),
])


tabs = dbc.Tabs(
    [
        dbc.Tab(label="No Data Uploaded", tab_id="empty-tab",
                children=[dbc.Card(dbc.CardBody([
                        html.H5("No data has been uploaded. Please upload a file."),
                        html.P("Once a file has been uploaded, it will appear here.")]
                        ))
                    ],
                ),
    ],
    id="tabs",
    active_tab="empty-tab",
)

app.layout = dbc.Container(
    [
        dcc.Store(id='upload-trigger', data=0),
        html.H1("Nystagmus Analyser"),
        html.Hr(),
        dbc.Row([
        upload_button,
        ],
        class_name='h-10',
        ),
        dbc.Row([
            tabs,
        ]),
    ],
    style={"height": "100vh"}, fluid=True,
)
