#-*- coding: utf-8 -*-
#
# Copyright (c) 2024, SR Research Ltd., All Rights Reserved
#
# Neither name of SR Research Ltd nor the name of contributors may be used
# to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS
# IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Edits:
# WDM - 2024/02/12      Alpha version
#
#
'''
This code illusrates how to utilize the functions of the EDFACCESSwraper.py to unpack an EyeLink Data File (EDF) into a structured numpy data array
To utilize the code one must first install the EyeLink Developers Kit:https://www.sr-research.com/support/thread-13.html and will also need to install numpy for you python environment: https://numpy.org/install/
'''
import os, sys
from EDF_file_importer.EDF2numpy import EDF2numpy
#from EDF2numpy import EDF2numpy
import numpy as np
import logging

logging.basicConfig(filename='logs\\std.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
logger = logging.getLogger(__name__)

def readFileWithInputs(inputs):
    errmsg = None
    options = []
    try:
        EDFI = EDF2numpy()
        # Get EDF filename argument as first arg
        edfFilename = str(inputs[0]).strip()
        # check that it's actually an EDF file
        if edfFilename.endswith('.edf')==True or edfFilename.endswith('.EDF')==True:
            # Check that file actually exists
            if os.path.isfile(edfFilename):
                # Check if there are additional arguments
                if len(inputs)>=2:
                    args = inputs[1:]
                    # if extra args exist, make sure they are in the right format
                    for i in args:
                        fixed = i.replace('=',':').replace(';',':').replace(' ','')
                        options = options + fixed.split(',')
                    inputs = ','.join(options)
                    EDFI.consumeInputArgs(inputs)
                    if os.path.isfile(edfFilename):
                        EDFfileData = EDFI.readEDF(edfFilename)
                        print('Your data has been added to a numpyarray: [HEADERdata,RECORDINGdata,MESSAGEdata,SAMPLEdata,EVENTdata,IOEVENTdata]\n'
                            + '\tHEADERdata: ' + str(EDFfileData[0].size) + ' records;\n\tRECORDINGdata: ' + str(EDFfileData[1].size) 
                            + ' records;\n\tMESSAGEdata: ' + str(EDFfileData[2].size) + ' records;\n\tSAMPLEdata: ' + str(EDFfileData[3].size)
                            + ' records;\n\tEVENTdata: ' + str(EDFfileData[4].size) + ' records;\n\tIOEVENTdata: ' + str(EDFfileData[5].size) + ' records')
                        #----------------------------------------------------
                        return EDFfileData
                        #-----------------------------------------------------
                    else:
                        errmsg = edfFilename + " does not seem to exist. Please doublecheck the input filename'"
            else:
                errmsg = '\nThe path you defined ('+edfFilename+')does not seem to be valid. Please double check your path.'
        else:
            errmsg = errmsg = '\nWrong file type! Only EyeLink Data Files are allowed as input file type.'
    except:
        errmsg = 'Could not execute main import function'
    finally:
        if errmsg != None:
            raise Exception(errmsg) 
        


def EDFToNumpy(EDFfilePath, gazeDataOptionString) -> np.ndarray:
    logging.info("Passing EDF file path to be read.")
    options = []
    inputs = [EDFfilePath, gazeDataOptionString]
    # Get EDF filename argument as first arg
    EDFfile = str(inputs[0]).strip()
    # check that it's actually an EDF file
    if EDFfile.endswith('.edf')==True or EDFfile.endswith('.EDF')==True:
        # Check that file actually exists
        if os.path.isfile(EDFfile):
            # Check if there are additional arguments
            if len(inputs)>=2:
                args = inputs[1:]
                # if extra args exist, make sure they are in the right format
                for i in args:
                    fixed = i.replace('=',':').replace(';',':').replace(' ','')
                    options = options + fixed.split(',')
                inputs = ','.join(options)
                # Call main function
                logging.info(f"Reading EDF file with path: {EDFfile} and options: {' '.join(inputs)}.")
                EDFfileData = readFileWithInputs([EDFfile, inputs])
                return EDFfileData
            else:
                # Call main function
                logging.info(f"Reading EDF file with path: {EDFfile}.")
                readFileWithInputs([EDFfile])
        else:
            logging.info(f"EDF File path {EDFfile} not found.")
            raise FileNotFoundError(EDFfile + " does not seem to exist. Please doublecheck the input filename'")
    else:
        raise TypeError('\nWrong file type! Only EyeLink Data Files are allowed as input file type') 



#shite code
'''if __name__ == '__main__':
    options = []
    # check for input arguments
    if len(sys.argv)>1:
        # strip args from script name
        inputs = sys.argv[1:]
        # Get EDF filename argument as first arg
        EDFfile = str(inputs[0]).strip()
        # check that it's actually an EDF file
        if EDFfile.endswith('.edf')==True or EDFfile.endswith('.EDF')==True:
            # Check that file actually exists
            if os.path.isfile(EDFfile):
                # Check if there are additional arguments
                if len(inputs)>=2:
                    args = inputs[1:]
                    # if extra args exist, make sure they are in the right format
                    for i in args:
                        fixed = i.replace('=',':').replace(';',':').replace(' ','')
                        options = options + fixed.split(',')
                    inputs = ','.join(options)
                    # Call main function
                    readFileWithInputs([EDFfile, inputs])
                else:
                    # Call main function
                    readFileWithInputs([EDFfile])
            else:
                raise FileNotFoundError(EDFfile + " does not seem to exist. Please doublecheck the input filename'")
        else:
            raise TypeError('\nWrong file type! Only EyeLink Data Files are allowed as input file type') 
    else:
        print('The main function of the example will take the following Input arguments and return a numpy data structure.\n'
            + 'EyeLinkData2NumpyArray.py <EDF_FileName> <optional arguments>\n'
            + 'Input Arguments:\n\tREQUIRED:\n\t\t<EDF_FileName>\t[the path and filename of the EDF file to unpack]\n\n\tOPTIONAL:\n'
            + '\t\toutput_left_eye:1\t\t[0=Left eye data disabled;\t\t1=Left eye data enabled]\n'
            + '\t\toutput_right_eye:1\t\t[0=Right eye data disabled;\t\t1=Right eye data enabled]\n'
            + '\t\tgaze_data_type:2\t\t[0=Output Raw Data;\t\t\t1=Output HREF Data;\n\t\t\t\t\t\t2=Output Gaze Data]\n'
            + '\t\tioevents_enabled:1\t\t[0=IOEVENTS data disabled;\t\t1=IOEVENTS Data Enabled]\n'
            + '\t\tmessages_enabled:1\t\t[0=Message Events disabled;\t\t1=Message Events enabled]\n'
            + '\t\tmsg_offset_enabled:0\t\t[0=no integer offset applied;\t\t1=integer offset applied to message events]\n'
            + '\t\toutput_data_ppd:1\t\t[0=PPD Data disabled;\t\t\t1=PPD Data enabled]\n'
            + '\t\toutput_data_velocity:1\t\t[0=Velocity Data disabled;\t\t1=Velocity Data enabled]\n'
            + '\t\toutput_data_pupilsize:1\t\t[0=Pupil Data disabled;\t\t\t1=Pupil Data enabled]\n'
            + '\t\toutput_data_debugflags:0\t[0=Flag Data disabled;\t\t\t1=Flag Data enabled]\n'
            + '\t\toutput_dataviewer_commands:1\t[0=Mask DV commands from output;\t1=Include DV commands in output]\n'
            + '\t\trecinfo_enabled:1\t\t[0=Recording info disabled;\t\t1=recording info Enabled]\n'
            + '\t\tenable_consistency_check:2\t[0=consistency check disabled;\t\t1=enable consistency check and report;\n\t\t\t\t\t\t2=enable consistency check and fix]\n'
            + '\t\tenable_failsafe:0\t\t[0=fail-safe mode disabled;\t\t1=fail-safe enabled]\n'
            + '\t\tdisable_large_timestamp_check:0\t[0=timestamp check enabled;\t\t1=disable timestamp check flag]\n'
            + '\t\tevents_enabled:1\t\t[0=Event data disabled;\t\t\t1=Event Data Enabled]\n'
            + '\t\toutput_eventtype_start:1\t[0=Start Events data disabled;\t\t1=Start Events Data Enabled]\n'
            + '\t\toutput_eventtype_end:1\t\t[0=End Events data disabled;\t\t1=End Events Data Enabled]\n'
            + '\t\toutput_eventtype_saccade:1\t[0=Saccade Events data disabled;\t1=Saccade Events Data Enabled]\n'
            + '\t\toutput_eventtype_fixation:1\t[0=Fixation Events data disabled;\t1=Fixation Events Data Enabled]\n'
            + '\t\toutput_eventtype_fixupdate:0\t[0=FixUpdate Events data disabled;\t1=FixUpdate Events Data Enabled]\n'
            + '\t\toutput_eventtype_blink:1\t[0=Blink Events data disabled;\t\t1=Blink Events Data Enabled]\n'
            + '\t\toutput_eventdata_parse:1\t[0=Parse Event Data disabled;\t\t1=Parse Event Data enabled]\n'
            + '\t\toutput_eventtype_button:1\t[0=Button Events disabled;\t\t1=Button Events enabled]\n'
            + '\t\toutput_eventtype_input:1\t[0=Input Port Data Disabled;\t\t1=Input Port Data enabled]\n'
            + '\t\toutput_eventdata_averages:0\t[0=End Events data disabled;\t\t1=End Events Data Enabled]\n'
            + '\t\tsamples_enabled:0\t\t[0=Sample data disabled;\t\t1=Sample Data Enabled]\n'
            + '\t\toutput_headtargetdata_enabled:0\t[0=headTarget data disabled;\t\t1=headTarget Data Enabled]\n'
            + '\t\toutput_samplevel_model_type:0\t[0=Standard model;\t\t\t1=Fast model]\n'
            + '\t\toutput_sample_start_enabled:1\t[0=Start sample data disabled;\t\t1=Start sample Data Enabled]\n'
            + '\t\toutput_sample_end_enabled:1\t[0=End sample data disabled;\t\t1=End sample Data Enabled]\n'
            + '\t\ttrial_parse_start: "TRIALID"\t[the string used to mark the start of the trial]\n'
            + '\t\ttrial_parse_end:"TRIAL_RESULT"\t[the string used to mark the end of the trial]\n')
'''


#print(type(EDFToNumpy('C:\\Users\\tomru\\AppData\\Local\\Temp\\tmphn42bd8u.edf', 'gaze_data_type=0')))