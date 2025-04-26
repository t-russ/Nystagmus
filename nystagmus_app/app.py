from dash import Dash, dcc, html, callback, State
import dash_bootstrap_components as dbc
import nystagmus_app.layout.app_components as app_components


def serve_layout():
    return (dbc.Container(
    [
        html.H1("Nystagmus Analyser"),
        html.Hr(),
        dcc.Store(id='upload-trigger', data=0),
        dcc.Store(id='calibrate-trigger', data=0),
        html.Div(id='debug-output'),
        dbc.Row([
        app_components.upload_button,
        ],
        class_name='h-10',
        ),
        html.Div(
            children=[
                dbc.Row([
                    get_tabs(),
                ]),
            ]
        )
    ],
    style={"height": "100vh"}, fluid=True,
    ))

def get_tabs():
    return app_components.tabs


app = Dash(external_stylesheets=[dbc.themes.COSMO])
app.title = "Nystagmus Analyser"
app.layout = serve_layout