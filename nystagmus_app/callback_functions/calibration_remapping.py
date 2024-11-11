from dash import callback, Output, Input, State, MATCH, ALL, callback_context, no_update
from nystagmus_app.app import app
import nystagmus_app.callback_functions.globals as globals
from nystagmus_app.utils.regression import applyRecordingLinearRegression

##--------------------------REMAPPING LINE CALLBACKS---------------------------------##
'''Enables/disables remapping input based on checkbox value'''
@app.callback(
    Output({'type': 'remapping-plus10degs', 'eye':MATCH, 'direction':MATCH, 'index': MATCH}, 'disabled'),
    Output({'type': 'remapping-minus10degs', 'eye':MATCH, 'direction':MATCH, 'index': MATCH}, 'disabled'),
    Input({'type': 'remapping-check', 'eye':MATCH, 'direction':MATCH, 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def enable_remapping_input(remappingCheck):
    return not remappingCheck, not remappingCheck


'''Updates the value of the remapping lines value when they are moved'''
@app.callback(Output({'type': 'remapping-plus10degs-value', 'eye': MATCH, 'direction': MATCH, 'index': MATCH}, 'data'),
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
@app.callback(Output({'type': 'remapping-plus10degs', 'eye': MATCH, 'direction': MATCH, 'index': MATCH}, 'value'),
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


##----------------- CALIBRATION --------------------##
@app.callback(Output({'type':'calibrate-trigger-indexed', 'index':MATCH}, 'data'),
        Input({'type': 'calibrate-button', 'index':MATCH}, 'n_clicks'),
        State({'type':'remapping-check', 'eye': ALL, 'direction': ALL, 'index': MATCH}, 'value'),
        State({'type': 'remapping-plus10degs-value', 'eye': ALL, 'direction': ALL, 'index': MATCH}, 'data'),
        State({'type': 'remapping-minus10degs-value', 'eye': ALL, 'direction': ALL, 'index': MATCH}, 'data'),
        prevent_initial_call=True)
def calibrateData(buttonClicks, remappingChecks, plus10Values, minus10Values) -> int:
    statesList = callback_context.states_list[0]
    relevantRecordingIndex = statesList[0]['id']['index']

    relevantRecording = globals.recordingList[relevantRecordingIndex]

    relevantRecordingName = relevantRecording[0]
    relevantRecordingTrials = relevantRecording[1]

    tickedDirections = getTickedRemapDirections(statesList)
    calibrationData = makeCalibrationDict(tickedDirections, plus10Values, minus10Values)

    calibratedRecording = applyRecordingLinearRegression(relevantRecordingTrials, calibrationData)

    calibratedRecordingName = f'{relevantRecordingName} - Calibrated'
    globals.calibratedRecordingList.append([calibratedRecordingName, calibratedRecording, calibrationData])

    return buttonClicks

@app.callback(Output('calibrate-trigger', 'data'),
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

