import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

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


