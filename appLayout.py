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
                            labelStyle={"margin-right": 10},
                            inputStyle={"margin-right": 5}),
                ],
                style= {"margin-bottom": 10, "margin-top":10, "text-align": "center",},
            ),

            html.Div([
                    html.Label('Direction Tracked:'),
                    dbc.Checklist(id={'type': 'xy-tracked', 'index': recordingIndex}, options=['X', 'Y'], inline=True, 
                                labelStyle={"margin-right": 10},
                                inputStyle={"margin-right": 5},
                                value=['X', 'Y']),
                ],
                style= {"margin-bottom": 10, "margin-top":10, "text-align": "center"}
            ),

            html.Div([
                dbc.Checklist(id={'type': 'remapping-check', 'index': recordingIndex}, options=['Enable Remapping'], inline=True,
                            labelStyle={"margin-right": 10},
                            inputStyle={"margin-right": 5}),
                    ],
                    style= {"margin-bottom": 10, "text-align": "center"}
            ),

            html.Div([
                html.Label('+10º'),
                dcc.Store(id={'type': 'remapping-plus10degs-value', 'index': recordingIndex}, data= -6000),
                dbc.Input(id={'type': 'remapping-plus10degs', 'index': recordingIndex}, type='number', placeholder='Enter Remapping Value', disabled=True),
                    ],
                
                style= {"margin-bottom": 10, "margin-top":10, "text-align": "center"},
            ),

            html.Div([
                html.Label('-10º'),
                dcc.Store(id={'type': 'remapping-minus10degs-value', 'index': recordingIndex}, data= -2000),
                dbc.Input(id={'type': 'remapping-minus10degs', 'index': recordingIndex}, type='number', placeholder='Enter Remapping Value', disabled=True),
                    ],
                
                style= {"margin-bottom": 10, "margin-top":10, "text-align": "center"}
            )
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
    style={"height": "100vh"},
)
