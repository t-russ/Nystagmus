import pandas as pd
from nystagmus_app.utils.trial_parsing import EDFTrialParser
import numpy as np
from plotly import graph_objects as go

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

def applyRecordingLinearRegression(recording:list, calibrationData: dict) -> list:
    #loop over all trials applying linear regression
    #return a list of all the calibrated trials data
    calibratedTrialsSampleData = []

    for trial in recording:
        calibratedTrial = applyTrialLinearRegression(trial.sampleData, calibrationData)
        calibratedTrialsSampleData.append(calibratedTrial)

    return calibratedTrialsSampleData