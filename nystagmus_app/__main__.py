import webbrowser
from nystagmus_app.app import app
from nystagmus_app.callback_functions.upload_tabs import *
from nystagmus_app.callback_functions.calibration_remapping import *
from nystagmus_app.callback_functions.base_graph import *
from nystagmus_app.callback_functions.calibrated_graph import *

#------- MAIN FUNCTION --------#
'''Launches Dash app'''
if __name__ == '__main__':
    port = 8050
    webbrowser.open_new(f'http://127.0.0.1:{port}')
    app.run(debug=True, port=port, use_reloader=False)
