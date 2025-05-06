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
from nystagmus_app.EDF_file_importer.EDF2numpy import EDF2numpy

import numpy as np
import logging

logging.basicConfig(filename='std.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
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
