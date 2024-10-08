import pandas as pd
from EDFTrialParsing import EDFTrialParser
import numpy as np

'''for testing purposes'''
with open("C:\\Users\\tomru\\Documents\\Nystagmus Analyser\\EDF_data\\br_whole_file.npy", 'rb') as f:
    BREDFfileData = np.load(f, allow_pickle=True)


brRecordingObj = EDFTrialParser(BREDFfileData)
brRecordingObj.extractAllTrials()



def linearRegression(data, plus10Degs, minus10Degs):
    #apply linear regression to the column
    slope = (-10-10)/(plus10Degs - minus10Degs)
    meanX = (plus10Degs + minus10Degs)/2
    intercept = -(slope * meanX)

    calibratedData = data.apply(lambda x: x*slope + intercept)
    return calibratedData

def applyTrialLinearRegression(trialData, plus10Degs, minus10Degs, eyesCalibrated, directionsCalibrated):
    #apply linear regression to the trial data
    pass

def extractRelevantData(trialData, eyeCalibrated, directionCalibrated):
    #extract relevant columns from the trial data based on eyes / direction 
    #eyesCalibrated = ['Right', 'Left'] directionCalibrated = ['X', 'Y']
    extractedData = pd.DataFrame()
    dfString = 'pos' + eyeCalibrated + directionCalibrated
    extractedData.loc[:, dfString] = trialData.loc[:, dfString]

    return extractedData

def ApplyRecordingLinearRegression(recording, plus10Degs, minus10Degs, eyesCalibrated, directionCalibrated) -> pd.DataFrame:
    #loop over all trials applying linear regression
    #return a dataframe with the results
    pass

