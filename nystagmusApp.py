import numpy as np
import logging, time, os, base64, tempfile, copy, json
from pathlib import Path

from dash import Dash, html, dcc, Input, Output, callback, State, callback_context, MATCH
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from EDFTrialParsing import EDFTrialParser
from EDF_file_importer.EyeLinkDataImporter import EDFToNumpy

logging.basicConfig(filename='logs\\std.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
logger = logging.getLogger(__name__)


recordingList = []


#------- APP LAYOUT --------#
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
                dcc.Checklist(id ={'type':'eye-tracked', 'index': recordingIndex}, options=['Left', 'Right'],inline=True, 
                            labelStyle={"padding": 5, "margin-right": 10},
                            inputStyle={"margin-right": 5}),
                ],
                style= {"margin-bottom": 10, "margin-top":10, "text-align": "center",},
            ),

            html.Div([
                    html.Label('Direction Tracked:'),
                    dcc.Checklist(id={'type': 'xy-tracked', 'index': recordingIndex}, options=['X', 'Y'], inline=True, 
                                labelStyle={"padding": 5, "margin-right": 10},
                                inputStyle={"margin-right": 5},
                                value=['X', 'Y']),
                ],
                style= {"margin-bottom": 10, "margin-top":10, "text-align": "center"}
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
def applyNumpyConversion(decodedContents, fileExtension) -> tuple[np.ndarray, Path]:
    tempFolderPath: Path = Path.cwd() / 'temp'
    try:
        tempFile: tempfile.NamedTemporaryFile = tempfile.NamedTemporaryFile(delete=False, suffix=fileExtension, dir=tempFolderPath)
        tempFilePath = tempFolderPath / tempFile.name
        tempFile.write(decodedContents)

        logging.info(f"Temp EDF file created at {str(tempFilePath)}")
        EDFfileData: np.ndarray = EDFToNumpy(tempFilePath, 'gaze_data_type = 0')
        logging.info("EDF file converted to numpy")

        tempFile.close()

        return EDFfileData, tempFilePath

    except Exception as e:
        logging.error(f"Error creating temp file: {str(e)}")
        raise IOError(f"Error creating temp file: {str(e)}")
    

'''Uploads EDF file, converts to numpy array, parses into trials, and stores trials in dcc.Store
    Triggered on upload button press, returns a message to confirm file upload and parsing'''
@callback(Output('upload-output', 'children'),
          Output('upload-trigger', 'data'),
        [Input('upload-edf', 'contents'),
        Input('upload-edf', 'filename')],
        State('upload-trigger', 'data'),
        prevent_initial_call=True,
        running=[
            Output('upload-edf', 'loading_state'),
            {'is_loading': True},
            {'is_loading': False},
        ]
    )
def uploadFile(contents, filename, uploadTrigger) -> str:
    try:
        fileNameIsolated, fileExtension = os.path.splitext(filename)

    except Exception as e:
        logger.error(f"Couldn't extract filename and extension using os.path.splitext: {str(e)}")
        return "Error extracting filename and extension, please check the logs for more information", uploadTrigger
    
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
        return "Error decoding file, please check the logs for more information.", uploadTrigger

    EDFfileData, tempFilePath = applyNumpyConversion(decoded, fileExtension)
    recordingParser = parseRecordingData(EDFfileData)
    recordingTrials = recordingParser.trials
    filenameAndTrials = [fileNameIsolated, recordingTrials]
    recordingList.append(filenameAndTrials)
    outputMessage = f"File {filename} uploaded and parsed into {len(recordingTrials)} trials."
    uploadTrigger += 1
    #os.remove(tempFilePath)

    return outputMessage, uploadTrigger
    

'''Updates Eye(s) being shown depending on option selected in checkbox'''
@callback(Output({'type':'eye-tracked', 'index': MATCH}, 'value'),
          Input({'type':'trial-dropdown', 'index': MATCH}, 'value'),
          Input('tabs', 'active_tab'),
          suppress_callback_exceptions=True)
def updateEyeTracked(inputTrial, activeTab) -> list:
    recordingIndex = int(activeTab.split('-')[1]) - 1
    trialNumber:int = int(inputTrial.split(" ")[1]) - 1
    ''' triggeredID = callback_context.triggered[0]['prop_id'].split('.')[0]
    recordingIndex = json.loads(triggeredID)['index']'''

    relevantTrial = (recordingList[recordingIndex][1])[trialNumber]

    eyesTracked: list = [relevantTrial.eyeTracked]
    if eyesTracked[0] == 'Binocular': eyesTracked = ['Left', 'Right']

    return eyesTracked

'''Updates graph when value in controls is changed'''
@callback(Output({'type': 'nystagmus-plot', 'index':MATCH}, 'figure'),
        [Input({'type':'trial-dropdown', 'index': MATCH}, 'value'),
        Input({'type':'eye-tracked', 'index': MATCH}, 'value'),
        Input({'type': 'xy-tracked', 'index': MATCH}, 'value')])
def updateTrialGraph(inputTrial, eyeTracked, xyTracked) -> go.FigureWidget:
    logger.debug("Updating Graph")

    triggeredID = callback_context.triggered[0]['prop_id'].split('.')[0]
    recordingIndex = eval(triggeredID)['index']
    trialNumber: int = int(inputTrial.split(" ")[1]) - 1
    
    try:
        relevantTrial = (recordingList[recordingIndex][1])[trialNumber]

    except Exception as e:
        logger.error(f"Trial Index not found in file: {str(e)}")
        raise IndexError("Trial indedx not found in file")

    startTime = relevantTrial.startTime
    relevantSampleData = relevantTrial.sampleData

    xRightData = relevantSampleData['posXRight']
    yRightData = relevantSampleData['posYRight']
    xLeftData = relevantSampleData['posXLeft']
    yLeftData = relevantSampleData['posYLeft']
    timeData = relevantSampleData['time'] - startTime

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

'''Creates new tab for a file being uploaded'''
@callback(Output('tabs', 'children'),
          Output('tabs', 'active_tab'),
          Input('upload-trigger', 'data'),
        [State('tabs', 'children')],
        prevent_initial_call=True)    
def createNewTab(uploadCount, currentTabs) -> dbc.Tabs:
    recordingCount:int = len(recordingList)
    if recordingCount == 0:
        return currentTabs, "empty-tab"
    
    newTabs = copy.copy(currentTabs)
    newRecordingIndex:int = recordingCount - 1
    trialCount:int = len(recordingList[newRecordingIndex][1])
    print(f'new Trial Count: {trialCount}')
    newGraphControls = createGraphControls(newRecordingIndex, trialCount)
    newTabID = f"recording-{newRecordingIndex}"

    newTab = dbc.Tab(label=recordingList[newRecordingIndex][0], tab_id=f"recording-{newRecordingIndex}",
                    children=[dbc.Row(
                            [
                            dbc.Col(newGraphControls, md=2, style={"height": "90%"}), 
                            dbc.Col(dcc.Graph(id ={'type': 'nystagmus-plot', 'index':newRecordingIndex}, style={'width':'110vh', 'height': '80vh'}),
                                     md=10, style={"height": "100%"}),
                            ],
                            align='center',
                            class_name='h-100'),
                        ]
                    )
    
    if recordingCount ==1:
        return [newTab], newTabID
    else:
        newTabs.append(newTab)
        return newTabs, newTabID



if __name__ == '__main__':
    app.run(debug=True)
