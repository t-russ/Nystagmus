import pandas as pd
from EDFTrialParsing import EDFTrialParser
import numpy as np
from plotly import graph_objects as go

'''for testing purposes'''
with open("C:\\Users\\tomru\\Documents\\Nystagmus Analyser\\EDF_data\\br_whole_file.npy", 'rb') as f:
    BREDFfileData = np.load(f, allow_pickle=True)


brRecordingObj = EDFTrialParser(BREDFfileData)
brRecordingObj.extractAllTrials()

dataTest = brRecordingObj.trials[0].sampleData

testDict = {'XRight':{'plus10Degs': -6000, 'minus10Degs': -2000}, 'YRight':{'plus10Degs': -6000, 'minus10Degs': -2000}}


def linearRegression(data: pd.Series, plus10Degs:int, minus10Degs:int) -> pd.Series:
    #apply linear regression to the column
    slope = (-10-10)/(plus10Degs - minus10Degs)
    meanX = (plus10Degs + minus10Degs)/2
    intercept = -(slope * meanX)

    calibratedData = data.apply(lambda x: x*slope + intercept)
    return calibratedData

def applyTrialLinearRegression(trialSampleData: pd.DataFrame, calibrationData: dict) -> pd.DataFrame:
    #apply linear regression to the trial data
    newTrialSampleData = pd.DataFrame()
    for key in calibrationData.keys():
        eyesDirectionString = 'pos' + key
        eyesDirectionData = extractRelevantData(trialSampleData, eyesDirectionString)

        plus10Degs = calibrationData[key]['plus10Degs']
        minus10Degs = calibrationData[key]['minus10Degs']

        calibratedData = linearRegression(eyesDirectionData, plus10Degs, minus10Degs)
        newTrialSampleData.loc[:, eyesDirectionString] = calibratedData
        
    return newTrialSampleData

def extractRelevantData(trialData: pd.DataFrame, eyeDirectionString: str) -> pd.DataFrame:
    #extract relevant columns from the trial data based on eyes / direction 
    extractedData = pd.DataFrame()

    extractedData.loc[:, eyeDirectionString] = trialData.loc[:, eyeDirectionString]

    return extractedData

def applyRecordingLinearRegression(recording: EDFTrialParser, calibrationData: dict) -> list:
    #loop over all trials applying linear regression
    #return a list of all the calibrated trials data
    calibratedTrialsSampleData = []
    for trial in recording.trials:
        calibratedTrial = applyTrialLinearRegression(trial.sampleData, calibrationData)
        calibratedTrialsSampleData.append(calibratedTrial)

    return calibratedTrialsSampleData


test = applyRecordingLinearRegression(brRecordingObj, testDict)

fig = go.FigureWidget()
fig.add_trace(go.Scatter(x=test[0].index, y=test[0]['posXRight'], mode='lines', name='X Right'))
fig.add_trace(go.Scatter(x=test[1].index, y=test[1]['posYRight'], mode='lines', name='Y Right'))
fig.show()
