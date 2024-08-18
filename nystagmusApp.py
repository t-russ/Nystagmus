import numpy as np
import logging
import time
import tempfile
import os
import base64
from pathlib import Path

from dash import Dash, html, dcc, Input, Output, callback, State
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

#------- APP LAYOUT --------#
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

upload_button = html.Div([
    dcc.Upload([dbc.Button("Upload EDF", id="upload-edf-button", color="primary", className="mr-2",)], id = 'upload-edf',  accept=".edf"),
    html.Div(id='upload-output', style={"margin-top": "10px" }, ),
])

app.layout = dbc.Container(
    [
        dcc.Store(id='recording-count', data= 0),
        html.H1("Nystagmus Analyser"),
        html.Hr(),
        dbc.Row([
        upload_button,
        ],
        class_name='h-10',
        ),
        dbc.Row(
            [
                dbc.Col(graph_controls, md=2, style={"height": "70%"}),
                dbc.Col(dcc.Graph(id = 'nystagmus-plot', style={'width':'130vh', 'height': '80vh'}), md=10, style={"height": "100%"})
            ],
            align='center',
            class_name='h-100',
        ),
    ],
    style={"height": "100vh"},
)
#------- APP FUNCTIONS/CALLBACKS --------#
'''Update the upload button to show a spinner when loading'''
@callback(Output('upload-edf', 'children'),
        Input('upload-edf', 'loading_state'),
        prevent_initial_call=True)
def updateSpinner(loading_state) -> dbc.Button:
    print(f'Loading state: {loading_state}')

    if loading_state['is_loading']:
        newButton: dbc.Button = dbc.Button([dbc.Spinner(size = 'sm', spinner_style={'animation-duration':'1s'}), " Loading File..."],
                            id="upload-edf-button", color="primary", className="mr-2", disabled=True)
        return newButton
    
    else:
        originalButton: dbc.Button = dbc.Button("Upload EDF", id="upload-edf-button", color="primary", className="mr-2")
        return originalButton


'''Using EDF file data, parse the recording into trials using the EDFTrialParser class'''
def parseRecordingData(EDFfileData) -> EDFTrialParser:
    try:
        recordingParser: EDFTrialParser = EDFTrialParser(EDFfileData)
        recordingParser.extractAllTrials()
        trialCount: int = recordingParser.trialCount
        logging.info(f"EDF file parsed into {trialCount} trials")
        return recordingParser

    except Exception as e:
        logging.error(f"Error parsing EDF file: {str(e)}")
        raise ValueError(f"Error parsing EDF file: {str(e)}")
    

'''Calls EDF_file_importer module to convert EDF file to numpy array'''
def applyNumpyConversion(decodedContents, fileExtension) -> np.ndarray:
    tempFolderPath: Path = Path.cwd() / 'temp'
    try:
        tempFile: tempfile.NamedTemporaryFile = tempfile.NamedTemporaryFile(delete=False, suffix=fileExtension, dir=tempFolderPath)
        tempFilePath = tempFolderPath / tempFile.name
        tempFile.write(decodedContents)

        logging.info(f"Temp EDF file created at {str(tempFilePath)}")
        EDFfileData: np.ndarray = EDFToNumpy(tempFilePath, 'gaze_data_type = 0')
        logging.info("EDF file converted to numpy")

        tempFile.close()
        return EDFfileData

    except Exception as e:
        logging.error(f"Error creating temp file: {str(e)}")
        raise IOError(f"Error creating temp file: {str(e)}")
    

'''Uploads EDF file, converts to numpy array, parses into trials, and stores trials in dcc.Store
    Triggered on upload button press, returns a message to confirm file upload and parsing'''
@callback(Output('upload-output', 'children'),
        Input('upload-edf', 'contents'),
        Input('upload-edf', 'filename'),
        State('recording-count', 'data'),
        prevent_initial_call=True,
        running=[
            Output('upload-edf', 'loading_state'),
            {'is_loading': True},
            {'is_loading': False},
        ]
    )
def uploadFile(contents, filename, recordingCount):
    try:
        fileNameIsolated, fileExtension = os.path.splitext(filename)

    except Exception as e:
        logger.error(f"Couldn't extract filename and extension using os.path.splitext: {str(e)}")
        return "Error extracting filename and extension, please check the logs for more information"
    
    logging.info(f"Uploading file {filename}")
    
    if contents is None:
        logging.error("No file uploaded/no contents detected.")
        return "No contents detected in uploaded file."
    
    try:
        contentType, contentString = contents.split(",")
        decoded = base64.b64decode(contentString)
        logging.info(f"File {filename} decoded")

    except Exception as e:
        logging.error(f"Error decoding file: {str(e)}")
        return "Error decoding file, please check the logs for more information."

    EDFfileData = applyNumpyConversion(decoded, fileExtension)
    recordingParser = parseRecordingData(EDFfileData)
    recordingTrials = recordingParser.trials
    dcc.Store(id= f'recording-{str(recordingCount)}', data=recordingTrials)
    recordingCount += 1

    return f"File {filename} uploaded and parsed into {len(recordingTrials)} trials."
    
'''Updates Eye(s) being shown depending on option selected in checkbox'''
@callback(Output('eye-tracked', 'value'),
          Input('trial-dropdown', 'value'))
def updateEyeTracked(inputTrial):
    trialNumber:int = int(inputTrial.split(" ")[1]) - 1

    eyesTracked: list = [brTrialParser.trials[trialNumber].eyeTracked]
    if eyesTracked[0] == 'Binocular': eyesTracked = ['Left', 'Right']

    return eyesTracked

'''Updates graph when value in controls is changed'''
@callback(Output('nystagmus-plot', 'figure'),
        Input('trial-dropdown', 'value'),
        Input('eye-tracked', 'value'),
        Input('xy-tracked', 'value'))
def updateTrialGraph(inputTrial, eyeTracked, xyTracked):
    logger.debug("Updating Graph")

    trialNumber: int = int(inputTrial.split(" ")[1]) - 1
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

        logger.debug(f"Graph Updated with {'/'.join(str(eye) for eye in eyeTracked)} eye and {'/'.join(str(direction) for direction in xyTracked)} direction.")

    except Exception as e:
        logger.info(f"Error plotting graph with updated filters {str(e)}")
        raise 

    return fig


if __name__ == '__main__':
    app.run(debug=True)
