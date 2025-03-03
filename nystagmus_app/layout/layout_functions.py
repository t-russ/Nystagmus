from dash import dcc, html
import dash_bootstrap_components as dbc

def createGraphControls(recordingIndex, trialCount):

    new_graph_controls = dbc.Card(
        [   
            dcc.Store(id={'type':'calibrate-trigger-indexed', 'index':recordingIndex}, data=0),
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
                style= {"margin-bottom": 10, "margin-top": 10, "text-align": "center"}, id={'type': 'calibration-y-right','index': recordingIndex},
            ),

            html.Div([
                dbc.Button("Calibrate Data", id={'type': 'calibrate-button', 'index': recordingIndex}, color="primary", className="mr-2"),
                ], 
            id={'type': 'calibrate-button-div', 'index': recordingIndex}, className="d-flex justify-content-center", style={"margin-top": "10px"},
            ),
        ],
        body=True, style={"height": "100%"},
        )
   
    return new_graph_controls


def createCalibratedGraphControls(calibratedIndex, trialCount):
    controls = dbc.Card([
        html.Div([
                html.Label('Trial:'),
                dcc.Dropdown(id={'type':'calibrated-trial-dropdown', 'index': calibratedIndex}, options=["Trial " + str(i + 1) for i in range(trialCount)], value="Trial 1",
                            clearable= False),
                ],
                style= {"margin-bottom": "10px"},
            ),

        html.Div([
            html.Label('Eye Tracked:'),
            dbc.Checklist(id ={'type':'calibrated-eye-tracked', 'index': calibratedIndex}, options=['Left', 'Right'], inline=True, 
                        inputStyle={"margin-right": 5}),
            ],
            style= {"margin-bottom": 10, "margin-top":10, "text-align": "center",},
        ),

        html.Div([
                html.Label('Direction Tracked:'),
                dbc.Checklist(id={'type': 'calibrated-xy-tracked', 'index': calibratedIndex}, options=['X', 'Y'], inline=True, 
                            inputStyle={"margin-right": 5},
                            value=['X', 'Y']),
            ],
            style= {"margin-bottom": 10, "margin-top":10, "text-align": "center"}
        ),
        
        html.Div([
            dbc.Button("Calculate Amplitude", id={'type': 'calculate-velocity-amplitude', 'index': calibratedIndex}, color="primary",
                    className="mr-2", style={"margin-top": "10px"},
                    ),
            
            html.Div("Fast Phase Amplitude: ", id={'type': 'calibrated-amplitude', 'index': calibratedIndex},
                    style={"white-space": "pre", "margin-bottom": 10, "margin-top":10, "text-align": "center",},

                    ),
                ],
            style= {"margin-bottom": 10, "margin-top":30, "text-align": "center"},
        ),
        
                
        html.Div([
            dbc.Button("Calculate Velocity", id={'type': 'calculate-velocity-button', 'index': calibratedIndex}, color="primary",
                    className="mr-2", style={"margin-top": "10px"},
                      ),
            
            html.Div("Fast Phase Velocity: ", id={'type': 'calibrated-frequency', 'index': calibratedIndex},
                    style={"white-space": "pre", "margin-bottom": 10, "margin-top":10, "text-align": "center",},
                    ),
            ],
                
                style= {"margin-bottom": 10, "margin-top":30, "text-align": "center"},
            ),
        

    ], body=True, style={"height": "100%"})

    return controls

def makeNewCalibratedTab(relevantRecording, calibratedIndex, trialCount):
    recordingName = f'{relevantRecording[0]}'
    newGraphControls = createCalibratedGraphControls(calibratedIndex, trialCount)
    newTabID = f"calibrated-{calibratedIndex}"
    newTab = dbc.Tab(label=recordingName, tab_id=newTabID,
                    children=[dbc.Row(
                            [
                            dbc.Col(newGraphControls, width=3, style={"height": "100%"}), 
                            dbc.Col(dcc.Graph(id ={'type': 'calibrated-nystagmus-plot', 'index':calibratedIndex},
                                              style={'width':'140vh', 'height': '80vh'},
                                              config={'edits': {'shapePosition': True}, 'displaylogo': False}),
                                    width=9, style={"height": "100%"}),
                            ],
                            align='center',
                            class_name='h-100'),
                        ]
                    )
    return newTab, newTabID