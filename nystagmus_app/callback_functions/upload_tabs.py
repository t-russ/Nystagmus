from dash import callback, Output, Input, State, MATCH, ALL, no_update, dcc
import logging
import base64
import os
import numpy as np
import tempfile
import copy
import gc
from pathlib import Path
import dash_bootstrap_components as dbc


from nystagmus_app.app import app
from nystagmus_app.EDF_file_importer.EyeLinkDataImporter import EDFToNumpy
from nystagmus_app.utils.trial_parsing import EDFTrialParser
import nystagmus_app.callback_functions.globals as globals
from nystagmus_app.layout.layout_functions import createGraphControls, makeNewCalibratedTab

logging.basicConfig(filename='logs\\std.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
logger = logging.getLogger(__name__)

#------- Uploading EDF File and Parsing --------#
@app.callback(Output('upload-edf', 'children'),
        Input('upload-edf', 'loading_state'),
        prevent_initial_call=True)
def updateSpinner(loading_state:dict) -> dbc.Button:

    '''
    Updates to show spinner when file is loading, and disables button.

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

#maybe make copy of temp file and open that
def createTempFile(decodedContents:bytes, fileExtension:str) -> Path:
    '''
    Creates a temp file to store the uploaded EDF file contents.

    Parameters:
        decodedContents (bytes): EDF file contents decoded from base64
        fileExtension (str): file extension of the EDF file

    Returns: Path: path of the temp file created
    '''
    tempFolderPath: Path = Path.cwd() / 'temp'
    try:
        tempFile: tempfile.NamedTemporaryFile = tempfile.NamedTemporaryFile(delete=False, suffix=fileExtension, dir=tempFolderPath)
        tempFilePath: Path = tempFolderPath / tempFile.name
        tempFile.write(decodedContents)
        tempFile.flush()
        tempFile.close()


        logging.info(f"Temp EDF file created at {str(tempFilePath)}")
        return tempFilePath

    except Exception as e:
        logging.error(f"Error creating temp file: {str(e)}")
        raise IOError(f"Error creating temp file: {str(e)}")
    

def tempDirCleanup() -> None:
    '''
    Initialise the temp directory and clean up temp files.
    Called at start of program.
    This is a workaround as temp file cannot be deleted after numpy conversion due to 
    data importer relying on the file path.
    '''

    tempFolderPath: Path = Path.cwd() / 'temp'
    try:
        if tempFolderPath.exists():
            for file in tempFolderPath.iterdir():
                if file.is_file():
                    os.unlink(file)
    except Exception as e:
        logging.error(f"Error cleaning up temp folder: {str(e)}")
            
    logging.info("Temp folder cleaned up")

    tempFolderPath.mkdir(exist_ok=True)



def applyNumpyConversion(decodedContents:bytes, fileExtension:str) -> tuple[np.ndarray, Path]:
    '''
    Applies EDF file to numpy struct conversion using the EDF file importer module.
    Temp file is made to store the edf file uploaded since the EDF file importer requires a file path.

    Parameters:
        decodedContents (bytes): EDF file contents decoded from base64
        fileExtension (str): file extension of the EDF file

    Returns:
        tuple[np.ndarray, Path]: numpy array of the EDF file, and the path of the temp file created
    
    '''

    tempFilePath: Path = createTempFile(decodedContents, fileExtension)

    try:
        EDFfileData: np.ndarray = EDFToNumpy(tempFilePath, 'gaze_data_type = 0')
        logging.info("EDF file converted to numpy")


    except Exception as e:
        logging.error(f"Error converting EDF file to numpy: {str(e)}")
        raise ValueError(f"Error converting EDF file to numpy: {str(e)}")

    return EDFfileData, tempFilePath

    
    
    

def parseRecordingData(EDFfileData: object) -> EDFTrialParser:
    '''
    Using EDF file data, parse the recording into trials using the EDFTrialParser class.
    This creates an EDFTrialParser object containing a list of Trial objects.

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
    

@app.callback(Output('upload-output', 'children'),
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
def uploadFile(contents, filename:str, uploadTrigger:int) -> str:
    '''
    Uploads EDF file, converts to numpy array, parses into trials, and stores parsed edf file into recording list.
    Triggered on file uploaded.
    Returns a message to confirm file upload and returns incremented upload trigger to update tabs.

    Parameters:
        contents: file contents from upload button.
        filename (str) : name of the file uploaded.

    Returns:
        outputMessage (str) : message confirming file upload and parsing.
        uploadTrigger (int) : triggers tab generation upon uploading of a file.
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
    globals.recordingList.append(filenameAndTrials)
    outputMessage = f"File {filename} uploaded and parsed into {len(recordingTrials)} trials."
    uploadTrigger += 1

    return outputMessage, uploadTrigger


#------- TAB CREATION --------#

@app.callback(Output('tabs', 'children', allow_duplicate=True),
          Output('tabs', 'active_tab', allow_duplicate=True),
          Input('upload-trigger', 'data'),
          State('tabs', 'children'),
          prevent_initial_call=True)    
def createNewTab(uploadCount, currentTabs) -> dbc.Tabs:
    '''
    Creates a new tab for each edf file uploaded.
    Triggers upon upload and processing of a file. 
    upload_trigger is incremented after each completion of the uploadFile function.
    Returns the tab list with the new tab appended.

    Parameters:
        uploadCount (int) : Upload trigger, incremented after each file upload.
                            Used to trigger tab generation callback.
        currentTabs (list) : list of current tab components.

    Returns:
        (str) : active tab to be updated to ensure correct tab is shown.
        (list) : Updated list of tabs with new tab appended.
    '''
        
    recordingCount:int = len(globals.recordingList)
    if recordingCount == 0:
        return currentTabs, "empty-tab"
    
    newTabs = copy.copy(currentTabs)
    newRecordingIndex:int = recordingCount - 1
    trialCount:int = len(globals.recordingList[newRecordingIndex][1])
    newGraphControls = createGraphControls(newRecordingIndex, trialCount)
    newTabID = f"recording-{newRecordingIndex}"

    newTab = dbc.Tab(label=globals.recordingList[newRecordingIndex][0], tab_id=f"recording-{newRecordingIndex}",
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
    
@app.callback(Output('tabs', 'children'),
          Output('tabs', 'active_tab'),
          Input('calibrate-trigger', 'data'),
          State('tabs', 'children'),
          State('tabs', 'active_tab'),
          prevent_initial_call=True)
def addNewCalibratedTab(calibrateTrigger, currentTabs, activeTab) -> tuple:
    '''
    Creates a new tab for each calibration.
    Triggers upon regression calculations of a file. 
    Returns the tab list with the new tab appended.

    Parameters:
        calibrateTrigger (int) : triggers the callback function. Incremented after each calibration.
        currentTabs (list) : list of current tab components.
        activeTab (str) : active tab to be returned if an improper callback is executed.

    Returns:
        (list) : Updated list of tabs with new tab appended.
        (str) : active tab to be updated to ensure correct tab is shown.
    '''

    calibratedRecordingCount = len(globals.calibratedRecordingList)

    if calibratedRecordingCount == 0 or calibrateTrigger == 0:
        return currentTabs, activeTab
    
    newTabs = copy.copy(currentTabs)
    newCalibratedIndex = calibratedRecordingCount - 1
    relevantRecording = globals.calibratedRecordingList[newCalibratedIndex]
    trialCount = len(relevantRecording[1])

    newTab, newTabID = makeNewCalibratedTab(relevantRecording, newCalibratedIndex, trialCount)
    newTabs.append(newTab)

    return newTabs, newTabID
