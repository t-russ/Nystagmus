import numpy as np
import logging, time, os, base64, tempfile, copy, json, webbrowser
from pathlib import Path

from dash import dcc, Input, Output, callback, State, callback_context, MATCH
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from EDFTrialParsing import EDFTrialParser
from EDF_file_importer.EyeLinkDataImporter import EDFToNumpy

from appLayout import createGraphControls, app

logging.basicConfig(filename='logs\\std.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
logger = logging.getLogger(__name__)


recordingList = []

#----------------- APP FUNCTIONS/CALLBACKS ------------------#

#------- Uploading EDF File and Parsing --------#
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




#------- GRAPH/ GRAPH CONTROLS UPDATING --------#
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
        Input({'type': 'xy-tracked', 'index': MATCH}, 'value'),
        Input({'type': 'remapping-check', 'index': MATCH}, 'value'),
        State({'type': 'remapping-plus10degs-value', 'index': MATCH}, 'data'),
        State({'type': 'remapping-minus10degs-value', 'index': MATCH}, 'data')
        ],)
def updateGraph(inputTrial, eyeTracked, xyTracked, remappingCheck, plus10Value, minus10Value) -> go.FigureWidget:
    logger.debug("Updating Graph")

    triggeredID = callback_context.triggered[0]['prop_id'].split('.')[0]
    recordingIndex = eval(triggeredID)['index']
    trialNumber: int = int(inputTrial.split(" ")[1]) - 1
    
    try:
        relevantTrial = (recordingList[recordingIndex][1])[trialNumber]

    except Exception as e:
        logger.error(f"Trial Index not found in file: {str(e)}")
        raise IndexError("Trial index not found in file")

    startTime = relevantTrial.startTime
    relevantSampleData = relevantTrial.sampleData

    xRightData = relevantSampleData['posXRight']
    yRightData = relevantSampleData['posYRight']
    xLeftData = relevantSampleData['posXLeft']
    yLeftData = relevantSampleData['posYLeft']
    timeData = relevantSampleData['time'] - startTime
    endTime = timeData.iat[-1]

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
        lines = []
        if remappingCheck and 'X' in xyTracked:
            lines += (updateRemapLine(plus10Value, minus10Value, 'X', endTime))

        if remappingCheck and 'Y' in xyTracked:
            lines += (updateRemapLine(-6000, -2000, 'Y', endTime))
            
        fig.update_layout(shapes = lines)
        logger.debug(f"Graph Updated with {'/'.join(str(eye) for eye in eyeTracked)} eye and {'/'.join(str(direction) for direction in xyTracked)} direction.")

    except Exception as e:
        logger.info(f"Error plotting graph with updated filters {str(e)}")
        raise 

    return fig



#------- TAB CREATION --------#
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
                            dbc.Col(newGraphControls, width=3, style={"height": "100%"}), 
                            dbc.Col(dcc.Graph(id ={'type': 'nystagmus-plot', 'index':newRecordingIndex}, style={'width':'110vh', 'height': '80vh'},
                                              config={'edits': {'shapePosition': True}, 'displaylogo': False}),
                                    width=9, style={"height": "100%"}),
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




#------- REMAPPING CONTROLS/LINES --------#
@callback(Output({'type': 'remapping-plus10degs', 'index': MATCH}, 'disabled'),
          Output({'type': 'remapping-minus10degs', 'index': MATCH}, 'disabled'),
          Input({'type': 'remapping-check', 'index': MATCH}, 'value'),
          prevent_initial_call=True)        
def enableRemappingInput(remappingCheck) -> tuple:
    if remappingCheck:
        return False, False
    
    else:
        return True, True

@callback(Output({'type': 'remapping-plus10degs-value', 'index': MATCH}, 'data'),
          Output({'type': 'remapping-minus10degs-value', 'index': MATCH}, 'data'),
          Input({'type': 'nystagmus-plot', 'index': MATCH}, 'relayoutData'),
          State({'type': 'remapping-plus10degs-value', 'index': MATCH}, 'data'),
          State({'type': 'remapping-minus10degs-value', 'index': MATCH}, 'data'),
          prevent_initial_call=True)
def updateRemapLineValue(relayoutData, plus10Value, minus10Value) -> tuple:
    print(relayoutData)
    if 'shapes[1].y1' in relayoutData.keys():
        plus10Value = round(relayoutData['shapes[1].y1'])

        
    if 'shapes[0].y1' in relayoutData.keys():
        minus10Value = round(relayoutData['shapes[0].y1'])

    return plus10Value, minus10Value

@callback(Output({'type': 'remapping-plus10degs', 'index': MATCH}, 'value'),
            Output({'type': 'remapping-minus10degs', 'index': MATCH}, 'value'),
            Input({'type': 'remapping-plus10degs-value', 'index': MATCH}, 'data'),
            Input({'type': 'remapping-minus10degs-value', 'index': MATCH}, 'data'),
            prevent_initial_call=True)
def updateRemapInput(plus10Value, minus10Value) -> tuple:
    return plus10Value, minus10Value

def updateRemapLine(plus10Value, minus10Value, direction, endTime) -> list[dict]:
    if direction == 'X': colour = 'black'
    else: colour = 'red'

    lines = [
            dict(
                type="line", y0= plus10Value, y1= plus10Value, x0=0, x1=endTime,
                xref = 'x', yref='y', line_dash='dash', line_color=colour, 
                label=dict(text=(f'+10º {direction}'), textposition='top center', font=dict(size=12)), 
                opacity=0.7, line_width=0.9),

            dict(
                type="line", y0= minus10Value, y1= minus10Value, x0=0, x1=endTime,
                xref = 'x', yref='y', line_dash='dash', line_color=colour, 
                label=dict(text=(f'-10º {direction}'), textposition='top center', font=dict(size=12)), 
                opacity=0.7, line_width=0.9),
    ]
    '''dict(
        type="h_line", y= minus10Value, line_dash='dash', line_color=colour, 
        label=dict(text='-10º', textposition='top center', font=dict(size=12)), 
        opacity=0.7, line_width=0.9)'''

    return lines

#------- MAIN FUNCTION --------#
'''Launches Dash app'''
if __name__ == '__main__':
    port = 8050
    webbrowser.open_new(f'http://127.0.0.1:{port}')
    app.run(debug=True, port=port, use_reloader=False)
    #app.run(debug=True, port=port)

