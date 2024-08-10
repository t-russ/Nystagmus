This example illustrates how to extract EyeLink Data files (EDFs) to structured Numpy data arrays via the EyeLink Developers Kit’s EDFAccess API.  The example consists of three main files; EDFACCESSWrapper.py, EDF2numpy.py, and EyeLinkDataImporterExample.py

EyeLinkDataImporterExample.py is a wrapper functions that takes command line arguments and preformats the inputs into the expected structures to call the functions from EDF2Numpy.

EDF2numpy.py utilizes the functions defined in EDFAccessWarper.py to unpack the data contained in the EyeLink data file into a Numpy strcutured array.

The EDFAccessWarper.py file is a wrapper for the functions contains in the C-Based EDFAPI.DLL.  This library and it's dependencies are part of the EyeLink Developers Kit, which must be installed for the code to function.

EyeLinkDataImporterExample.py
The main function of the example will take the following Input arguments and return the following data struture. Not the section of the code that lists "PLACE YOUR ANALYSIS CODE HERE" would be the appropriate place to add your own code to further process the returned numpy array to analyze your data as you see fit.
	Input Arguments: = 
	# Required
		EDF filename								= the path to the EDF file to unpack
	# Optional
		# Global level toggles
			'output_left_eye'						= 0 = Left eye data disabled;					1 = Left eye data enabled (default)
			'output_right_eye'						= 0 = Right eye data disabled;					1 = Right eye data enabled (default)
			'gaze_data_type'						= 0 = Output Raw Data;							1 = Output HREF Data;								2 = Output Gaze Data (default)
			'text_data_type': 'utf-8',				= default is 'utf-8' but could be any standard encoding: https://docs.python.org/3/library/codecs.html#standard-encodings
			'ioevents_enabled'						= 0 = IOEVENTS data disabled;					1 = IOEVENTS Data Enabled (default)
			'messages_enabled'						= 0 = Message Events disabled;					1 = Message Events enabled (default)
			'msg_offset_enabled'					= 0 = no integer offset applied (default);		1 = integer offset applied to message events
			'output_data_ppd'						= 0 = PPD Data disabled;						1 = PPD Data enabled (default)
			'output_data_velocity'					= 0 = Velocity Data disabled;					1 = Velocity Data enabled (default)
			'output_data_pupilsize'					= 0 = Pupil Data disabled;						1 = Pupil Data enabled (default)
			'output_data_debugflags'				= 0 = Flag Data disabled (default);				1 = Flag Data enabled
			'output_dataviewer_commands'			= 0 = Mask DV commands from output				1 = Include DV commands in output (default)
			'recinfo_enabled'						= 0 = Recording info disabled					1 = recording info Enabled (default)
		# Consistency check toggles
			'enable_consistency_check'				= 0 = consistency check disabled;				1 = enable consistency check and report;			2 = enable consistency check and fix (default).
			'enable_failsafe'						= 0 = fail-safe mode disabled (default);		1 = fail-safe enabled
			'disable_large_timestamp_check': 0,		# 0 = timestamp check enabled;					1 = disable timestamp check flag
		# Event toggles
			'events_enabled'						= 0 = Event data disabled;						1 = Event Data Enabled (default)
			'output_eventtype_start'				= 0 = Start Events data disabled;				1 = Start Events Data Enabled (default)
			'output_eventtype_end'					= 0 = End Events data disabled;					1 = End Events Data Enabled (default)
			'output_eventtype_saccade'				= 0 = Saccade Events data disabled;				1 = Saccade Events Data Enabled (default)
			'output_eventtype_fixation'				= 0 = Fixation Events data disabled;			1 = Fixation Events Data Enabled (default)
			'output_eventtype_fixupdate'			= 0 = FixUpdate Events data disabled (default);	1 = FixUpdate Events Data Enabled
			'output_eventtype_blink'				= 0 = Blink Events data disabled;				1 = Blink Events Data Enabled (default)
			'output_eventdata_parse'				= 0 = Parse Event Data disabled;				1 = Parse Event Data enabled (default)
			'output_eventtype_button'				= 0 = Button Events disabled;					1 = Button Events enabled (default)
			'output_eventtype_input'				= 0 = Input Port Data Disabled;					1 = Input Port Data enabled (default)
			'output_eventdata_averages'				= 0 = End Events data disabled (default);		1 = End Events Data Enabled
			
		# Sample toggles
			'samples_enabled'						= 0 = Sample data disabled;						1 = Sample Data Enabled (default)
			'output_headtargetdata_enabled'			= 0 = headTarget data disabled;					1 = headTarget Data Enabled (default)
			'output_samplevel_model_type':			= 0 = Standard model (default);					1 = Fast model
			'output_sample_start_enabled': 1,		= 0 = Start sample data disabled;				1 = Start sample Data Enabled (default)
			'output_sample_end_enabled': 1,			= 0 = End sample data disabled;					1 = End sample Data Enabled (default)
		# Trial Parsing messages
			'trial_parse_start': 'TRIALID',         = the string used to mark the start of the trial
			'trial_parse_end': 'TRIAL_RESULT'       = the string used to mark the end of the trial


	Output Data Structures:
	The output data structure will be a structured numpy array: [HEADER DATA STRUCTURE, SAMPLE DATA STRUCTURE, EVENT DATA STRUCTURE, IOEVENT DATA STRUCTURE, MESSAGE DATA STRUCTURERECORDINGS DATA STRUCTURE]
		# HEADER DATA STRUCTURE
			'Header' 			= text from EDF file header
		# SAMPLE DATA STRUCTURE
			'time'				= timestamp in milliseconds
			'rawX'				= [left_eye, right_eye] - X RAW pupil-center position from camera
			'rawY'				= [left_eye, right_eye] - Y RAW pupil-center position from camera
			'hrefX'				= [left_eye, right_eye] - X Tangent of the rotational angle of the eye relative to the head
			'hrefY'				= [left_eye, right_eye] - Y Tangent of the rotational angle of the eye relative to the head
			'gazeX'				= [left_eye, right_eye] - X GAZE position in screen pixel coordinates
			'gazeY'				= [left_eye, right_eye] - Y GAZE position in screen pixel coordinates
			'pupilSize'			= [left_eye, right_eye] - Area or diameter the pupil subtends in arbitrary camera pixel units
			'PpdX'				= X pixels per degree
			'PpdY'				= Y pixels per degree
			'RawVelX'			= [left_eye, right_eye] - X eye velocity for RAW data in degrees per second
			'RawVelY'			= [left_eye, right_eye] - Y eye velocity for RAW data in degrees per second
			'HrefVelX'			= [left_eye, right_eye] - X eye velocity for HREF data in degrees per second
			'HrefVelY'			= [left_eye, right_eye] - Y eye velocity for HREF data in degrees per second
			'GazeVelX'			= [left_eye, right_eye] - X eye velocity for GAZE data in degrees per second
			'GazeVelY'			= [left_eye, right_eye] - Y eye velocity for GAZE data in degrees per second
			'fastRawVelX'		= [left_eye, right_eye] - X eye velocity for RAW data in degrees per second using fast velocity model
			'fastRawVelY'		= [left_eye, right_eye] - Y eye velocity for RAW data in degrees per second using fast velocity model
			'fastHrefVelX'		= [left_eye, right_eye] - X eye velocity for HREF data in degrees per second using fast velocity model
			'fastHrefVelY'		= [left_eye, right_eye] - Y eye velocity for HREF data in degrees per second using fast velocity model
			'fastGazeVelX'		= [left_eye, right_eye] - X eye velocity for GAZE data in degrees per second using fast velocity model
			'fastGazeVelY'		= [left_eye, right_eye] - Y eye velocity for GAZE data in degrees per second using fast velocity model
			'headTrackerType'	= Head tracker data type
			'headTargetData'	= [X, Y, Z, flags] -  Head target data 
			'inputPortData'		= Status of the input port
			'buttonData'		= Status of BUTTON state
			'flags'				= Sample Flags
			'errors'			= Error Flags
			'elementIndex'		= index in EDF buffer
			'sampleIndex'		= index of sample data
		# EVENT DATA STRUCTURE
			'time'				= Timestamp in milliseconds
			'eventType'			= Event type StartBlink, EndBlink, StartSacc, EndSacc, StartFix, EndFix, FixUpdate, MSG
			'eyeTracked'		= Eye that generate event: Left, Right, or Binocular
			'gazeType'			= Type of gaze data reported: HREF or GAZE
			'startTime'			= Start time of event type
			'startPosX'			= Start X position of event type in [GAZE or HREF]
			'startPosY'			= Start Y position of event type in [GAZE or HREF]
			'StartPupilSize'	= Pupil size at start of event type
			'startVEL'			= Velocity at start of event type in degrees per second
			'startPPDX'			= X pixels per degree at start of event type
			'startPPDY'			= Y pixels per degree at start of event type
			'endTime'			= End time of event type
			'duration'			= Total duration of event for End events (endTime-startTime)
			'endPosX'			= End X position of event type in [GAZE or HREF]
			'endPosY'			= End Y position of event type in [GAZE or HREF]
			'endPupilSize'		= Pupil size at end of event type
			'endVEL'			= Velocity at end of event type in degrees per second
			'endPPDX'			= X pixels per degree at end of event type
			'endPPDY'			= Y pixels per degree at end of event type
			'avgPosX'			= Average X position for duration of event type in [GAZE or HREF]
			'avgPosY'			= Average Y position for duration of event type in [GAZE or HREF]
			'avgPupilSize'		= Average of pupil size over duration of event type
			'avgVEL'			= Average velocity for duration of event type in degrees per second
			'peakVEL'			= Peak velocity for duration of event type in degrees per second
			'message'			= Message data from event
			'readFlags'			= reading warnings
			'flags'				= event warnings
			'parsedby'			= parsing flags
			'status'			= event status
			'elementIndex'		= Index in EDF buffer
			'eventIndex'		= Index of Event data
		# IOEVENT DATA STRUCTURE
			'ioEventType'		= Event type Button or INPUT
			'time'				= Timestamp in milliseconds
			'IOData'			= Data from IO event
			'iotype'			= Data Type Code
			'elementIndex'		= Index in EDF buffer
			'ioEventIndex'		= Index of Event data
		# MESSAGE DATA STRUCTURE
			'time'				= Timestamp in milliseconds
			'message'			= Message data from event
			'messageLength'		= Message length from msg event
			'readFlags'			= reading warnings
			'flags'				= event warnings
			'parsedby'			= parsing flags
			'status'			= event status
			'elementIndex'		= Index in EDF buffer
			'msgIndex'			= Index of Event data
		# RECORDINGS DATA STRUCTURE
			'samplingRate'		= samplingRate in hertz
			'eyeTracked'		= Eye that generate event: Left, Right, or Binocular
			'pupilDataType'		= Pupil size data type: Area or Diameter
			'trackerState'		= Tracker state: Start or End
			'recordType'		= Type of data recorded: Samples,Events, or Samples & Events
			'parsedbyType'		= Event parsing data type: RAW, HREF, GAZE
			'filterType'		= File Sample Filter type: Off,Standard or Extra
			'recordingMode'		= Data Recording type: Pupil Only or Pupil-CR
			'endflags'			= end event flags
			'startflags'		= start event flags
			'elementIndex'		= Index in EDF buffer
			'recordingIndex'	= Index of Event data