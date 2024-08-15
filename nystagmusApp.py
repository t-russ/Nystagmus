import numpy as np
import logging

from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from EDFTrialParsing import EDFTrialParser
from EDF_file_importer.EyeLinkDataImporter import EDFToNumpy

logging.basicConfig(filename='logs\\std.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
logger = logging.getLogger(__name__)


with open("C:\\Users\\tomru\\Documents\\Nystagmus Analyser\\EDF_data\\ad_5mn_whole_file.npy", 'rb') as f:
    BREDFfileData = np.load(f, allow_pickle=True)


brTrialParser = EDFTrialParser(BREDFfileData)
brTrialParser.extractAllTrials()
trialCount = brTrialParser.trialCount

app = Dash(external_stylesheets=[dbc.themes.COSMO])

graph_controls = dbc.Card(
    [
        html.Div([
            html.Label('Select Trial:'),
            dcc.Dropdown(id='trial-dropdown', options=["Trial " + str(i + 1) for i in range(trialCount)], value="Trial 1",
                        clearable= False),
            ],
            style= {"margin-bottom": "10px"},
        ),

        html.Div([
            html.Label('Select Eye Tracked:'),
            dcc.Checklist(id='eye-tracked', options=['Left', 'Right'],inline=True, 
                        labelStyle={"padding": 5, "margin-right": 10},
                        inputStyle={"margin-right": 5}),
            ],
            style= {"margin-bottom": 10, "margin-top":10, "text-align": "center",},
        ),

        html.Div([
                html.Label('Select Direction Tracked:'),
                dcc.Checklist(id='xy-tracked', options=['X', 'Y'], inline=True, 
                            labelStyle={"padding": 5, "margin-right": 10},
                            inputStyle={"margin-right": 5},
                            value=['X', 'Y']),
            ],
            style= {"margin-bottom": 10, "margin-top":10, "text-align": "center"}
        ),
    ],
    body=True,
)


'''app.layout = html.Div([

    html.H2(children = "Nystagmus Analyser",
            style = {
                'textAlign': 'center',
                'color': '#5C5A57'
            }),
    html.Div([

    ]),

    dcc.Graph(id = 'nystagmus-plot')
])'''


app.layout = dbc.Container(
    [
        html.H1("Nystagmus Analyser"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(graph_controls, md=2),
                dbc.Col(dcc.Graph(id = 'nystagmus-plot'), md=10)
            ],
            align='center',
        ),
    ],
    fluid=True
)

@callback(Output('eye-tracked', 'value'),
          Input('trial-dropdown', 'value'))
def updateEyeTracked(inputTrial):
    trialNumber = int(inputTrial.split(" ")[1]) - 1

    eyesTracked = [brTrialParser.trials[trialNumber].eyeTracked]
    if eyesTracked[0] != 'Left' or eyesTracked != 'Right': eyesTracked = ['Left', 'Right']

    return eyesTracked



@callback(Output('nystagmus-plot', 'figure'),
        Input('trial-dropdown', 'value'),
        Input('eye-tracked', 'value'),
        Input('xy-tracked', 'value'))
def updateTrialGraph(inputTrial, eyeTracked, xyTracked):
    logger.debug("Updating Graph")

    trialNumber = int(inputTrial.split(" ")[1]) - 1
    xRightData = brTrialParser.trials[trialNumber].sampleData['posXRight']
    yRightData = brTrialParser.trials[trialNumber].sampleData['posYRight']
    xLeftData = brTrialParser.trials[trialNumber].sampleData['posXLeft']
    yLeftData = brTrialParser.trials[trialNumber].sampleData['posYLeft']
    timeData = brTrialParser.trials[trialNumber].sampleData['time'] - (brTrialParser.trials[trialNumber].startTime)

    logger.info('Plotting new data')
    try:
        fig = go.FigureWidget()

        if 'Left' in eyeTracked and 'X' in xyTracked:
            fig.add_trace(go.Scatter(x=timeData, y=xLeftData, mode='lines', name='X Left Eye', line = dict(color='#636EFA')))
        if 'Left' in eyeTracked and 'Y' in xyTracked:
            fig.add_trace(go.Scatter(x=timeData, y=yLeftData, mode='lines', name='Y Left Eye', line = dict(color='#EF553B')))
        if 'Right' in eyeTracked and 'X' in xyTracked:
            fig.add_trace(go.Scatter(x=timeData, y=xRightData, mode='lines', name='X Right Eye', line = dict(color='#00CC96')))
        if 'Right' in eyeTracked and 'Y' in xyTracked:
            fig.add_trace(go.Scatter(x=timeData, y=yRightData, mode='lines', name='Y Right Eye', line = dict(color='#AB63FA')))

        logger.debug(f"Graph Updated with {'/'.join(str(eye) for eye in eyeTracked)} eye and f{'/'.join(str(direction) for direction in xyTracked)}")

    except Exception as e:
        logger.info(f"Error plotting graph with updated filters {str(e)}")
        raise 

    return fig


if __name__ == '__main__':
    app.run(debug=True)
