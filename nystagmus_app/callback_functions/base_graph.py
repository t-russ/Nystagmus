from dash import callback, Output, Input, State, MATCH, ALL, callback_context
import logging
import plotly.graph_objects as go
from nystagmus_app.app import app
import nystagmus_app.callback_functions.globals as globals
from nystagmus_app.callback_functions.calibration_remapping import updateRemapLine

logging.basicConfig(filename='logs\\std.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
logger = logging.getLogger(__name__)


@app.callback(Output({'type':'eye-tracked', 'index': MATCH}, 'value'),
          Input({'type':'trial-dropdown', 'index': MATCH}, 'value'),
          State('tabs', 'active_tab'),
          suppress_callback_exceptions=True)
def updateEyeTracked(inputTrial:str, activeTab:str) -> list[str]:
    '''
    Updates the eye being shown on the graph based on the trial selected in the dropdown.

    Parameters:
        inputTrial (str): trial selected in the dropdown
        activeTab (str): active tab selected

    Returns:
        list[str]: list of eyes being tracked
    '''

    recordingIndex = int(activeTab.split('-')[1]) - 1
    trialNumber:int = int(inputTrial.split(" ")[1]) - 1

    relevantTrial = (globals.recordingList[recordingIndex][1])[trialNumber]

    eyesTracked: list = [relevantTrial.eyeTracked]
    if eyesTracked[0] == 'Binocular': eyesTracked = ['Left', 'Right']

    return eyesTracked

'''Updates graph when value in controls is changed'''
@app.callback(Output({'type': 'nystagmus-plot', 'index': MATCH}, 'figure'),
        Input({'type':'trial-dropdown', 'index': MATCH}, 'value'),
        Input({'type':'eye-tracked', 'index': MATCH}, 'value'),
        Input({'type': 'xy-tracked', 'index': MATCH}, 'value'),
        Input({'type': 'remapping-check', 'eye': ALL, 'direction': ALL, 'index': MATCH}, 'value'),
        State({'type': 'remapping-plus10degs-value', 'eye': ALL, 'direction': ALL,  'index': MATCH}, 'data'),
        State({'type': 'remapping-minus10degs-value', 'eye': ALL, 'direction': ALL,  'index': MATCH}, 'data'),  
        )
def updateGraph(inputTrial, eyeTracked, xyTracked, remappingCheck, plus10Value, minus10Value) -> go.FigureWidget:
    '''
    Parameters:

    Returns:
    '''
    logger.debug("Updating Graph")
    #obtain the index of the graph that was triggered - this is needed for pattern matching callbacks
    triggeredID = callback_context.triggered[0]['prop_id'].split('.')[0]
    recordingIndex = eval(triggeredID)['index']
    trialNumber: int = int(inputTrial.split(" ")[1]) - 1
    
    try:
        relevantTrial = (globals.recordingList[recordingIndex][1])[trialNumber]

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