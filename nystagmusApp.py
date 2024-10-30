import numpy as np
import logging, time, os, base64, tempfile, copy, json, webbrowser, re
from pathlib import Path

from dash import dcc, Input, Output, callback, State, callback_context, MATCH, ALL, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from EDFTrialParsing import EDFTrialParser
from EDF_file_importer.EyeLinkDataImporter import EDFToNumpy
from appLayout import createGraphControls, app, makeNewCalibratedTab
from linearRegression import applyRecordingLinearRegression

logging.basicConfig(filename='logs\\std.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
logger = logging.getLogger(__name__)


recordingList = []
calibratedRecordingList = []

#----------------- APP FUNCTIONS/CALLBACKS ------------------#

#------- Uploading EDF File and Parsing --------#
'''Update the upload button to show a spinner when loading'''
@callback(Output('upload-edf', 'children'),
        Input('upload-edf', 'loading_state'),
        prevent_initial_call=True)
def updateSpinner(loading_state:dict) -> dbc.Button:

    '''
    Updates to show spinner when file is loading, and disables button

    Parameters: 
        loading_state (dict): dictionary containing loading state of button

    Returns:
        dbc.Button: Button with spinner when loading, original button when not loading
    '''

    if loading_state['is_loading']:
        newButton: dbc.Button = dbc.Button([dbc.Spinner(size = 'sm', spinner_style={'animation-duration':'1s'}), " Loading File..."],
                            id="upload-edf-button", color="primary", className="mr-2", disabled=True)
        return newButton
    
    else:
        originalButton: dbc.Button = dbc.Button("Upload EDF", id="upload-edf-button", color="primary", className="mr-2")
        return originalButton




def applyNumpyConversion(decodedContents:bytes, fileExtension:str) -> tuple[np.ndarray, Path]:
    '''
    Applies EDF file to numpy struct conversion using the EDF file importer module.
    Temp file is made to store the edf file uploaded.

    Parameters:
        decodedContents (bytes): EDF file contents decoded from base64
        fileExtension (str): file extension of the EDF file

    Returns:
        tuple[np.ndarray, Path]: numpy array of the EDF file, and the path of the temp file created
    
    '''
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
    

def parseRecordingData(EDFfileData: object) -> EDFTrialParser:
    '''
    Using EDF file data, parse the recording into trials using the EDFTrialParser class.

    Parameters:
        EDFfileData (EDF2Numpy): EDF2Numpy object of the EDF file, gets passed to the EDFTrialParser class
        and split into individual trial objects.



    Returns:
        EDFTrialParser (EDFTrialParser) : EDFTrialParser object containing the parsed trials
        from the EDF file
    '''
    try:
        recordingParser: EDFTrialParser = EDFTrialParser(EDFfileData)
        recordingParser.extractAllTrials()
        trialCount: int = recordingParser.trialCount
        logging.info(f"EDF file parsed into {trialCount} trials")
        return recordingParser

    except Exception as e:
        logging.error(f"Error parsing EDF file: {str(e)}")
        raise ValueError(f"Error parsing EDF file: {str(e)}")
    

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
    '''
    Uploads EDF file, converts to numpy array, parses into trials, and stores parsed edf file into recording list.
    Triggered on upload button press, returns a message to confirm file upload and parsing.

    Parameters:
        contents: file contents from upload button.
        filename (str) : name of the file uploaded


    Returns:
        outputMessage (str) : message confirming file upload and parsing
        uploadTrigger (int) : incremented trigger to trigger tab generation
    '''
    
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
          State('tabs', 'active_tab'),
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
@callback(Output({'type': 'nystagmus-plot', 'index': MATCH}, 'figure'),
        Input({'type':'trial-dropdown', 'index': MATCH}, 'value'),
        Input({'type':'eye-tracked', 'index': MATCH}, 'value'),
        Input({'type': 'xy-tracked', 'index': MATCH}, 'value'),
        Input({'type': 'remapping-check', 'eye': ALL, 'direction': ALL, 'index': MATCH}, 'value'),
        State({'type': 'remapping-plus10degs-value', 'eye': ALL, 'direction': ALL,  'index': MATCH}, 'data'),
        State({'type': 'remapping-minus10degs-value', 'eye': ALL, 'direction': ALL,  'index': MATCH}, 'data'),  
        )
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
        if (remappingCheck[0] is not None) and remappingCheck[0] and remappingCheck[0][0] == True:
            lines += (updateRemapLine(plus10Value[0], minus10Value[0], 'X', 'Left', endTime))

        if (remappingCheck[1] is not None) and remappingCheck[1] and remappingCheck[1][0] == True:
            lines += (updateRemapLine(plus10Value[1], minus10Value[1], 'Y', 'Left', endTime))

        if (remappingCheck[2] is not None) and remappingCheck[2] and remappingCheck[2][0] == True:
            lines += (updateRemapLine(plus10Value[2], minus10Value[2], 'X', 'Right', endTime))

        if (remappingCheck[3] is not None) and remappingCheck[3] and remappingCheck[3][0] == True:
            lines += (updateRemapLine(plus10Value[3], minus10Value[3], 'Y', 'Right', endTime))
            
        fig.update_layout(shapes = lines)
        fig.update_layout(showlegend=True)
        logger.debug(f"Graph Updated with {'/'.join(str(eye) for eye in eyeTracked)} eye and {'/'.join(str(direction) for direction in xyTracked)} direction.")

    except Exception as e:
        logger.info(f"Error plotting graph with updated filters {str(e)}")
        raise 

    return fig

@callback(Output({'type': 'calibrated-nystagmus-plot', 'index':MATCH}, 'figure'),
          Input({'type': 'calibrated-trial-dropdown', 'index':MATCH}, 'value'),
          Input({'type': 'calibrated-eye-tracked', 'index':MATCH}, 'value'),
          Input({'type': 'calibrated-xy-tracked', 'index':MATCH}, 'value'),
          State('tabs', 'active_tab'),
          prevent_initial_call=True)
def updateCalibratedGraph(inputTrial: str, eyeTracked: list[str], xyTracked: list[str], activeTab) -> go.FigureWidget:
    recordingID: dict = callback_context.outputs_list['id']
    recordingIndex: int = recordingID['index']
    trialNumber: int = int(inputTrial.split(" ")[1]) - 1

    relevantRecording = calibratedRecordingList[recordingIndex]
    relevantCalibrationData = relevantRecording[2]
    relevantTrial = relevantRecording[1][trialNumber]

    fig = go.FigureWidget()
    

    if 'XLeft' in relevantCalibrationData.keys() and 'X' in xyTracked and 'Left' in eyeTracked:
        xLeftData = relevantTrial['posXLeft']
        fig.add_trace(go.Scatter(x=xLeftData.index,y=xLeftData,
                                  mode='lines', name='X Left Eye', line = dict(color='#636EFA')))
    if 'XRight' in relevantCalibrationData.keys() and 'X' in xyTracked and 'Right' in eyeTracked:
        xRightData = relevantTrial['posXRight']
        fig.add_trace(go.Scatter(x=xRightData.index,y=xRightData,
                                  mode='lines', name='X Right Eye', line = dict(color='#00CC96')))

    if 'YLeft' in relevantCalibrationData.keys() and 'Y' in xyTracked and 'Left' in eyeTracked:
        yLeftData = relevantTrial['posYLeft']
        fig.add_trace(go.Scatter(x=yLeftData.index,y=yLeftData,
                                  mode='lines', name='Y Left Eye', line = dict(color='#EF553B')))

    if 'YRight' in relevantCalibrationData.keys() and 'Y' in xyTracked and 'Right' in eyeTracked:    
        yRightData = relevantTrial['posYRight']
        fig.add_trace(go.Scatter(x=yRightData.index,y=yRightData,
                                  mode='lines', name='Y Right Eye', line = dict(color='#AB63FA')))

    return fig


@callback(Output({'type': 'calibrated-eye-tracked', 'index':MATCH}, 'value'),
          Output({'type': 'calibrated-xy-tracked', 'index':MATCH}, 'value'),
         Input({'type': 'calibrated-trial-dropdown', 'index':MATCH}, 'value'),
         State('tabs', 'active_tab'))
def updateCalibratedControls(inputTrial, activeTab) -> list:

    try:
        recordingIndex = int(activeTab.split('-')[1])
    
    except Exception as e:
        logger.error(f"Error extracting recording index from active tab: {str(e)}")
        return ['Left', 'Right'], ['X', 'Y']
    
    relevantRecording = calibratedRecordingList[recordingIndex]
    relevantCalibrationData = relevantRecording[2]
    eyesTracked = set()
    xyTracked = set()

    for key in relevantCalibrationData.keys():
        if key == 'XLeft': 
            eyesTracked.add('Left')
            xyTracked.add('X')

        elif key == 'YLeft':
            eyesTracked.add('Left')
            xyTracked.add('Y')
        
        elif key == 'XRight':
            eyesTracked.add('Right')
            xyTracked.add('X')
        
        elif key == 'YRight':
            eyesTracked.add('Right')
            xyTracked.add('Y')


    return list(eyesTracked), list(xyTracked)


#------- TAB CREATION --------#
'''Creates new tab for a file being uploaded'''
@callback(Output('tabs', 'children', allow_duplicate=True),
          Output('tabs', 'active_tab', allow_duplicate=True),
          Input('upload-trigger', 'data'),
          State('tabs', 'children'),
          prevent_initial_call=True)    
def createNewTab(uploadCount, currentTabs) -> dbc.Tabs:
    recordingCount:int = len(recordingList)
    if recordingCount == 0:
        return currentTabs, "empty-tab"
    
    newTabs = copy.copy(currentTabs)
    newRecordingIndex:int = recordingCount - 1
    trialCount:int = len(recordingList[newRecordingIndex][1])
    newGraphControls = createGraphControls(newRecordingIndex, trialCount)
    newTabID = f"recording-{newRecordingIndex}"

    newTab = dbc.Tab(label=recordingList[newRecordingIndex][0], tab_id=f"recording-{newRecordingIndex}",
                    children=[dbc.Row(
                            [
                            dbc.Col(newGraphControls, width=3, style={"height": "100%"}), 
                            dbc.Col(dcc.Graph(id ={'type': 'nystagmus-plot', 'index':newRecordingIndex}, style={'width':'140vh', 'height': '80vh'},
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
    
@callback(Output('tabs', 'children'),
          Output('tabs', 'active_tab'),
          Input('calibrate-trigger', 'data'),
          State('tabs', 'children'),
          State('tabs', 'active_tab'),
          prevent_initial_call=True)
def addNewCalibratedTab(calibrateTrigger, currentTabs, activeTab) -> tuple:
    calibratedRecordingCount = len(calibratedRecordingList)

    if calibratedRecordingCount == 0 or calibrateTrigger == 0:
        return currentTabs, activeTab
    
    newTabs = copy.copy(currentTabs)
    newCalibratedIndex = calibratedRecordingCount - 1
    relevantRecording = calibratedRecordingList[newCalibratedIndex]
    trialCount = len(relevantRecording[1])

    newTab, newTabID = makeNewCalibratedTab(relevantRecording, newCalibratedIndex, trialCount)
    newTabs.append(newTab)

    return newTabs, newTabID


#------- REMAPPING CONTROLS/LINES --------#

'''Enables/disables remapping input based on checkbox value'''
@callback(
    Output({'type': 'remapping-plus10degs', 'eye':MATCH, 'direction':MATCH, 'index': MATCH}, 'disabled'),
    Output({'type': 'remapping-minus10degs', 'eye':MATCH, 'direction':MATCH, 'index': MATCH}, 'disabled'),
    Input({'type': 'remapping-check', 'eye':MATCH, 'direction':MATCH, 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def enable_remapping_input(remappingCheck):
    return not remappingCheck, not remappingCheck


'''Updates the value of the remapping lines value when they are moved'''
@callback(Output({'type': 'remapping-plus10degs-value', 'eye': MATCH, 'direction': MATCH, 'index': MATCH}, 'data'),
          Output({'type': 'remapping-minus10degs-value', 'eye': MATCH, 'direction': MATCH, 'index': MATCH}, 'data'),
          Input({'type': 'nystagmus-plot', 'index': MATCH}, 'relayoutData'),
          State({'type': 'remapping-plus10degs-value', 'eye': MATCH, 'direction': MATCH, 'index': MATCH}, 'data'),
          State({'type': 'remapping-minus10degs-value', 'eye': MATCH, 'direction': MATCH, 'index': MATCH}, 'data'),
          State({'type': 'nystagmus-plot', 'index': MATCH}, 'figure'),
          prevent_initial_call=True)
def updateRemapLineValue(relayoutData, plus10Value, minus10Value, fig) -> tuple:

    shapeIndex = getShapeIndex(relayoutData)

    if shapeIndex is None:
        return plus10Value, minus10Value
    
    #Get the shape that was moved
    shapeMoved = fig['layout']['shapes'][shapeIndex]
    shapeName = shapeMoved['name']

    #Get the eye and direction from the callback context
    triggered_id = callback_context.states_list[0]['id']
    eye = triggered_id['eye']
    direction = triggered_id['direction']

    contextShapeName = f'{direction}{eye}'

    if shapeName == f'plus{contextShapeName}':
        plus10Value = round(shapeMoved['y0'])

    elif shapeName == f'minus{contextShapeName}':
        minus10Value = round(shapeMoved['y0'])

    return plus10Value, minus10Value

'''Extracts the index of the shape that was moved'''
def getShapeIndex(relayoutData) -> int:
    firstKey = list(relayoutData.keys())[0]

    if 'shapes[' in firstKey:
        # Extract the index using string splitting
        indexStr = firstKey.split('[')[1].split(']')[0]
        return int(indexStr)
    
    return None

'''Updates the input box value when value is changed'''
@callback(Output({'type': 'remapping-plus10degs', 'eye': MATCH, 'direction': MATCH, 'index': MATCH}, 'value'),
        Output({'type': 'remapping-minus10degs',  'eye': MATCH, 'direction': MATCH,   'index': MATCH}, 'value'),
        Input({'type': 'remapping-plus10degs-value', 'eye': MATCH, 'direction': MATCH,  'index': MATCH}, 'data'),
        Input({'type': 'remapping-minus10degs-value', 'eye': MATCH, 'direction': MATCH,  'index': MATCH}, 'data'),
        prevent_initial_call=True)
def updateRemapInput(plus10Value, minus10Value) -> tuple:
    return plus10Value, minus10Value

'''Returns new line to be drawn on the graph'''
def updateRemapLine(plus10Value, minus10Value, direction, eyeTracked, endTime) -> list[dict]:
    if direction == 'X' and eyeTracked == 'Left': colour = '#ee07f2'
    elif direction == 'X' and eyeTracked == 'Right': colour = 'black'
    elif direction == 'Y' and eyeTracked == 'Left': colour = '#0000ff'
    else: colour = 'red'

    lines = [
            dict(
                type="line", y0= plus10Value, y1= plus10Value, x0=0, x1=endTime,
                xref = 'x', yref='y', line_dash='dash', line_color=colour, name=f'plus{direction}{eyeTracked}',
                label=dict(text=(f'+10º {direction} {eyeTracked}'), textposition='top center', font=dict(size=12)), 
                opacity=1, line_width=0.95),

            dict(
                type="line", y0= minus10Value, y1= minus10Value, x0=0, x1=endTime,
                xref = 'x', yref='y', line_dash='dash', line_color=colour, name=f'minus{direction}{eyeTracked}', 
                label=dict(text=(f'-10º {direction} {eyeTracked}'), textposition='top center', font=dict(size=12)), 
                opacity=1, line_width=0.95)
    ]


    return lines

#------- CALIBRATION --------#
@callback(Output({'type':'calibrate-trigger-indexed', 'index':MATCH}, 'data'),
        Input({'type': 'calibrate-button', 'index':MATCH}, 'n_clicks'),
        State({'type':'remapping-check', 'eye': ALL, 'direction': ALL, 'index': MATCH}, 'value'),
        State({'type': 'remapping-plus10degs-value', 'eye': ALL, 'direction': ALL, 'index': MATCH}, 'data'),
        State({'type': 'remapping-minus10degs-value', 'eye': ALL, 'direction': ALL, 'index': MATCH}, 'data'),
        prevent_initial_call=True)
def calibrateData(buttonClicks, remappingChecks, plus10Values, minus10Values) -> int:
    statesList = callback_context.states_list[0]
    relevantRecordingIndex = statesList[0]['id']['index']

    relevantRecording = recordingList[relevantRecordingIndex]

    relevantRecordingName = relevantRecording[0]
    relevantRecordingTrials = relevantRecording[1]

    tickedDirections = getTickedRemapDirections(statesList)
    calibrationData = makeCalibrationDict(tickedDirections, plus10Values, minus10Values)

    calibratedRecording = applyRecordingLinearRegression(relevantRecordingTrials, calibrationData)

    calibratedRecordingName = f'{relevantRecordingName} - Calibrated'
    calibratedRecordingList.append([calibratedRecordingName, calibratedRecording, calibrationData])

    return buttonClicks

@callback(Output('calibrate-trigger', 'data'),
          Input({'type': 'calibrate-trigger-indexed', 'index': ALL}, 'data'),
          State('calibrate-trigger', 'data'),
          prevent_initial_call=True)
def calibrationTriggered(calibrateTriggerIndexed, calibrateTrigger) -> int:
    if all(i > 0 for i in calibrateTriggerIndexed):
        return (calibrateTrigger + 1)

    return no_update



def getTickedRemapDirections(statesList) -> list:
    tickedDirections = []
    for i in range(4):
        currentCheck = statesList[i]
        if 'value' in currentCheck and currentCheck['value'] == [True]:
            direction = currentCheck['id']['direction']
            eye = currentCheck['id']['eye']
            tickedDirections.append((direction + eye))
    
    return tickedDirections

def makeCalibrationDict(tickedDirections, plus10Values, minus10Values) -> dict:
    calibrationData = {}
    directionToIndex = {'XLeft': 0, 'YLeft': 1, 'XRight': 2, 'YRight': 3}

    for direction in tickedDirections:
        index = directionToIndex[direction]
        calibrationData[direction] = {'plus10Degs': plus10Values[index], 'minus10Degs': minus10Values[index]}

    return calibrationData


#------- MAIN FUNCTION --------#
'''Launches Dash app'''
if __name__ == '__main__':
    port = 8050
    webbrowser.open_new(f'http://127.0.0.1:{port}')
    app.run(debug=True, port=port, use_reloader=False)
