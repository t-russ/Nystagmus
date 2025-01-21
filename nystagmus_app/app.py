from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import nystagmus_app.layout.app_components as app_components

app = Dash(external_stylesheets=[dbc.themes.COSMO])
app.title = "Nystagmus Analyser"

app.layout = dbc.Container(
    [
        dcc.Store(id='upload-trigger', data=0),
        dcc.Store(id='calibrate-trigger', data=0),
        html.H1("Nystagmus Analyser"),
        html.Hr(),
        dbc.Row([
        app_components.upload_button,
        ],
        class_name='h-10',
        ),
        html.Div(
            children=[
                dbc.Row([
                    app_components.tabs,
                ]),
            ]
        )
    ],
    style={"height": "100vh"}, fluid=True,
)
