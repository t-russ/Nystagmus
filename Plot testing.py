import plotly.graph_objects as go
import numpy as np
import logging

from EDFTrialParsing import EDFTrialParser

logging.basicConfig(filename='logs\\std.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
logger = logging.getLogger(__name__)


with open("C:\\Users\\tomru\Documents\\Sam Interning\\ad_5mn_whole_file.npy", 'rb') as f:
    BREDFfileData = np.load(f, allow_pickle=True)


brTrialParser = EDFTrialParser(BREDFfileData)
brTrialParser.extractAllTrials()

xRightData = brTrialParser.trials[1].sampleData['posXRight']
yRightData = brTrialParser.trials[1].sampleData['posYRight']
xLeftData = brTrialParser.trials[1].sampleData['posXLeft']
yLeftData = brTrialParser.trials[1].sampleData['posYLeft']
timeData = brTrialParser.trials[1].sampleData['time'] - (brTrialParser.trials[1].startTime)

fig = go.FigureWidget()
fig.add_trace(go.Scatter(x=timeData, y=xRightData, mode='lines', name='posXRight'))
fig.add_trace(go.Scatter(x=timeData, y=yRightData, mode='lines', name='posYRight'))
fig.add_trace(go.Scatter(x=timeData, y=xLeftData, mode='lines', name='posXLeft'))
fig.add_trace(go.Scatter(x=timeData, y=yLeftData, mode='lines', name='posYLeft'))
logger.info("Data Plotted")

fig.show()

