import EyeLinkDataImporter
import os
ValidationFiles = "S:\\My Drive\\EyeLinkData2NumpyArray\\Validation Data"
for i in os.listdir(ValidationFiles):
    print(i)
    if i.endswith(".edf") or i.endswith(".EDF"):
        file = os.path.join(ValidationFiles,i)
        EyeLinkDataImporter.main([file,'output_left_eye= 1','output_right_eye= 1','messages_enabled= 1','recinfo_enabled= 1','gaze_data_type= 2',"text_data_type= 'utf-8'",'output_data_ppd= 1','output_data_velocity= 1','output_data_pupilsize: 1','output_data_debugflags= 1','output_dataviewer_commands= 1','enable_consistency_check= 2','enable_failsafe= 0','disable_large_timestamp_check= 0','events_enabled= 1','output_eventtype_start= 1','output_eventtype_end: 1','output_eventtype_saccade=                          1','output_eventtype_fixation= 1','output_eventtype_fixupdate= 0','output_eventtype_blink= 1','output_eventdata_parse=0','output_eventdata_averages= 1','msg_offset_enabled= 1','samples_enabled:1','output_headtargetdata_enabled=1','output_samplevel_model_type= 0','output_sample_start_enabled= 0','output_sample_end_enabled= 0',"trial_parse_start= 'TRIALID'","trial_parse_end= 'TRIAL_RESULT'",'something_stupid=234234'])
        ProblemFiles = "S:\\My Drive\\EyeLinkData2NumpyArray\\Validation Data\\Problem Files"
for i in os.listdir(ProblemFiles):
    print(i)
    if i.endswith(".edf") or i.endswith(".EDF"):
        file = os.path.join(ProblemFiles,i)
        EyeLinkDataImporter.main([file,'output_left_eye= 1','output_right_eye= 1','messages_enabled= 1','recinfo_enabled= 1','gaze_data_type= 2','text_data_type= latin-1','output_data_ppd= 1','output_data_velocity= 1','output_data_pupilsize: 1','output_data_debugflags= 1','output_dataviewer_commands= 1','enable_consistency_check= 2','enable_failsafe= 0','disable_large_timestamp_check= 0','events_enabled= 1','output_eventtype_start= 1','output_eventtype_end: 1','output_eventtype_saccade=                          1','output_eventtype_fixation= 1','output_eventtype_fixupdate= 0','output_eventtype_blink= 1','output_eventdata_parse=0','output_eventdata_averages= 1','msg_offset_enabled= 1','samples_enabled:1','output_headtargetdata_enabled=1','output_samplevel_model_type= 0','output_sample_start_enabled= 0','output_sample_end_enabled= 0','trial_parse_start= TRIALID','trial_parse_end= TRIAL_RESULT','something_stupid=234234'])