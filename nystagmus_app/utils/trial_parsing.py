import pandas as pd
import numpy as np
import logging

#setup logging
logging.basicConfig(filename='std.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
logger = logging.getLogger(__name__)

#class to parse EDF file data into trials
class EDFTrialParser:
    def __init__(self, EDFfileData: np.ndarray):

        if not isinstance(EDFfileData, np.ndarray) or len(EDFfileData) != 6:
            logger.error("EDFfileData must be a numpy array with 6 elements")
            raise ValueError("Invalid EDF file data input into Trial Parser")
        
        self.EDFfileData:np.ndarray = EDFfileData
        self.trials:list = []
        self.trialCount:int = 0
        self.trialIndices:list[tuple] = []
        self.trialIndices = self._setTrialIndices()
        self.trialCount = self._setTrialCount()

        logger.info(f"Trial Parser Initialized with {self.trialCount} trials")  

    def _setTrialIndices(self) -> list[tuple]:
        #find start and end index of each recording in the EDF buffer 
        #Indices are stored in a list of tuples
        trialIndices:list[tuple] = []
        tempTrialStart:np.int64 = 0
        tempTrialEnd:np.int64 = 0  
        try:
            for i in range(len(self.EDFfileData[1])):

                if self.EDFfileData[1][i]['trackerState'] == "START":
                    tempTrialStart = self.EDFfileData[1][i]['elementIndex']
                if self.EDFfileData[1][i]['trackerState'] == "END":
                    tempTrialEnd = self.EDFfileData[1][i]['elementIndex']
                    trialIndices.append((tempTrialStart, tempTrialEnd))
            logger.info(f"Trial Start and end Indices set. Found {len(trialIndices)} trials")
            return trialIndices
        
        except Exception as e:
            logger.error(f"Error in setting trial indices: {str(e)}")
            raise ValueError("Error setting trial indices")

    def _setTrialCount(self) -> int:
        trialCount:int = len(self.trialIndices)
        return trialCount
    
    def _indexFilter(self, EDFindex, startBufferIndex:np.int64, endBufferIndex:np.int64) -> np.ndarray:
        try:
            indexFilter = (self.EDFfileData[EDFindex]['elementIndex'] >= startBufferIndex) & (self.EDFfileData[EDFindex]['elementIndex'] <= endBufferIndex)
            return indexFilter
        
        except Exception as e:
            logger.error(f"Error in setting index filter: {str(e)}")
            raise ValueError("Error setting index filter")

    def _extractTrialData(self, startBufferIndex:np.int64, endBufferIndex:np.int64) -> list:
        trialData:list = []
        try:
            for EDFindex in range(1, 6):
                newIndexFilter = self._indexFilter(EDFindex, startBufferIndex, endBufferIndex)
                newHeaderData = self.EDFfileData[EDFindex][newIndexFilter]
                trialData.append(newHeaderData)
            logger.debug(f"Extracted Data from EDF Buffer Indexes: {startBufferIndex} to {endBufferIndex}")
            return trialData
        
        except Exception as e:
            logger.error(f"Error in extracting trial data: {str(e)}")
            raise ValueError("Error extracting trial data")

    def extractAllTrials(self) -> list:
        try:
            for trialNumber, trialIndex in enumerate(self.trialIndices):
                newTrialStart = trialIndex[0]
                newTrialEnd = trialIndex[1]
                newExtractedTrialData = self._extractTrialData(newTrialStart, newTrialEnd)

                logger.info(f"Extracted Data for Trial: {trialNumber}")

                self.trials.append(Trial(trialNumber, newExtractedTrialData))

            logger.info(f"Extracted all trials and appended to self.trials")
            return self.trials

        except Exception as e:
            logger.error(f"Error in extracting all trials: {str(e)}")
            raise ValueError("Error extracting all trials")
        

#class to store trial data
class Trial:
    def __init__ (self, trialNumber: int, trialData: list):
        if not isinstance(trialData, list) or len(trialData) != 5:
            logger.error("TrialData must be a list with 5 elements")
            raise ValueError("Invalid Trial Data input into Trial Object")
        
        #convert np.array to pandas dataframe
        self.trialNumber: int = trialNumber
        self.trialData: list = trialData
        self.recordingData: pd.DataFrame = pd.DataFrame(trialData[0])
        self.messageData: pd.DataFrame = pd.DataFrame(trialData[1])
        self.sampleData: pd.DataFrame = pd.DataFrame(trialData[2])
        self.eventData: pd.DataFrame = pd.DataFrame(trialData[3])
        self.ioEventData: pd.DataFrame = pd.DataFrame(trialData[4])
        self.startTime: np.int64 = self.sampleData['time'].iloc[0]
        self.endTime: np.int64 = self.sampleData['time'].iloc[-1]
        
        #remove -32768 values from sample data (missing data)
        self.sampleData.replace(-32768, np.nan, inplace=True)

        try:
            self.eyeTracked: str = self.recordingData['eyeTracked'][0]
            logger.info(f"Trial {self.trialNumber} attributes set with eyeTracked: {self.eyeTracked} and startTime: {self.startTime}")

        except Exception as e:
            logger.error(f"Error finding eyeTracked: {str(e)}")
            raise ValueError("Error setting trial attributes")

    def __str__(self):
        return (f'''Recording Data: {self.recordingData[0]}\nMessage Data: {self.messageData[0]}
        \nSample Data: {self.sampleData[0]}\nEvent Data: {self.eventData[0]}
        \nIO Event Data: {self.ioEventData[0]}\nEye Tracked: {self.eyeTracked} \nStart Time: {self.startTime}''')
    