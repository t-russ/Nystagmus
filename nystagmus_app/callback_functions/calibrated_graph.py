from dash import callback, Output, Input, State, MATCH, ALL, callback_context, no_update, dcc
import logging
from nystagmus_app.app import app
import nystagmus_app.callback_functions.globals as globals
import plotly.graph_objects as go

logging.basicConfig(filename='logs\\std.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
logger = logging.getLogger(__name__)

@app.callback(Output({'type': 'calibrated-nystagmus-plot', 'index':MATCH}, 'figure'),
          Input({'type': 'calibrated-trial-dropdown', 'index':MATCH}, 'value'),
          Input({'type': 'calibrated-eye-tracked', 'index':MATCH}, 'value'),
          Input({'type': 'calibrated-xy-tracked', 'index':MATCH}, 'value'),
          State('tabs', 'active_tab'),
          prevent_initial_call=True)
def updateCalibratedGraph(inputTrial: str, eyeTracked: list[str], xyTracked: list[str], activeTab:str) -> go.FigureWidget:
    '''
    Updates the graph based on the possible filters selected.
    Parameters: 
        inputTrial (str): trial selected in the dropdown
        eyeTracked (list[str]): list of eyes being tracked
        xyTracked (list[str]): list of directions being tracked
        activeTab (str): active tab selected

    Returns:
        go.FigureWidget: updated figure to be displayed
   
    '''

    recordingID: dict = callback_context.outputs_list['id']
    recordingIndex: int = recordingID['index']
    trialNumber: int = int(inputTrial.split(" ")[1]) - 1

    relevantRecording = globals.calibratedRecordingList[recordingIndex]
    relevantCalibrationData = relevantRecording[2]
    relevantTrial = relevantRecording[1][trialNumber]

    fig = go.FigureWidget()
    
    #plot lines on graph based on filters selected and calibration data available
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


@app.callback(Output({'type': 'calibrated-eye-tracked', 'index':MATCH}, 'value'),
          Output({'type': 'calibrated-xy-tracked', 'index':MATCH}, 'value'),
         Input({'type': 'calibrated-trial-dropdown', 'index':MATCH}, 'value'),
         State('tabs', 'active_tab'))
def updateCalibratedControls(inputTrial:str, activeTab:str) -> list:

    '''
    Updates the eye and xy tracked controls for the calibrated graph - based on the active tab selected.

    Parameters:
        inputTrial (str): trial selected in the dropdown
        activeTab (str): active tab selected

    Returns:
        list: list of eyes being tracked, list of directions being tracked
    '''

    try:
        recordingIndex = int(activeTab.split('-')[1])
    
    except Exception as e:
        logger.error(f"Error extracting recording index from active tab: {str(e)}")
        return ['Left', 'Right'], ['X', 'Y']
    
    relevantRecording = globals.calibratedRecordingList[recordingIndex]
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


# take data from relayout when axis is changed and update a dcc.Store with the new axis values
#then the calculation buttons will trigger calculation on these new axis max / min 
@app.callback(Output({'type': 'calibrated-x-range', 'index': MATCH}, 'children'),
              Input({'type': 'calibrated-nystagmus-plot', 'index': MATCH}, 'relayoutData'),
              prevent_initial_call=True)
def updateCalibratedXRange(relayoutData: dict) -> tuple:
    '''
    Updates the x-axis range based on the user's selection.
    Parameters:
        relayoutData (dict): data from the relayout event
    Returns:
        tuple: x-axis max and min values
    '''

    if 'xaxis.range[0]' in relayoutData or 'xaxis.range[1]' in relayoutData:
        xaxis = (relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]'])
        
        print(f"X axis range updated: {xaxis}")
    
        return xaxis
    
    return (None, None)

# [{'xaxis.range[0]': 4968.506137865911, 'xaxis.range[1]': 23123.414542020775, 'yaxis.range[0]': -4526.485985985986, 'yaxis.range[1]': -1495.7452452452453}]