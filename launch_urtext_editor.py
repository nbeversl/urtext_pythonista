"""
Start Urtext Pythonista
"""
from urtext_pythonista import UrtextEditor
from urtext_theme_light import urtext_theme_light
from urtext_theme_light_custom import urtext_theme_light_custom
from editor.launch_editor import LaunchEditor

class LaunchUrtextEditor(LaunchEditor):

    name = "Pythonista Urtext Editor"

    def __init__(self, args):
        super().__init__()
        
        self.urtext_project_path = ''
        if 'path' in args:
            self.urtext_project_path = args['path']

        self.theme = urtext_theme_light #default   
        if 'theme' in args:
            self.theme = args['theme']

        self.initial_project = None
        if 'initial_project' in args:
            self.theme = args['initial_project']

    def start(self):
        if not self.app.is_active():
            print ('Urtext is loading '+ self.urtext_project_path)
            main_view = UrtextEditor(
                self.urtext_project_path, 
                theme=self.theme,
                initial_project=self.initial_project)
            self.app.will_present(main_view)
