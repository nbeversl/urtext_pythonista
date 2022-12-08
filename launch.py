"""
Start Urtext Pythonista
"""
from urtext_pythonista import UrtextEditor
from urtext_theme_light import urtext_theme_light
from app_single_launch import AppSingleLaunch
from urtext_theme_light_custom import urtext_theme_light_custom

app = None

def launch_urtext_pythonista(args):

    global app

    if 'path' not in args or not args['path']:
        return None

    urtext_project_path = args['path']
    theme = urtext_theme_light
    if 'theme' in args:
        theme = args['theme']

    print ('Urtext is loading '+urtext_project_path)
    app = AppSingleLaunch("Pythonisa Urtext")
    if not app.is_active():
        initial_project = args['initial'] if 'initial' in args else None
        main_view = UrtextEditor(
            urtext_project_path, 
            app,
            theme=theme,
            initial_project=initial_project)
        app.will_present(main_view)

launch_urtext_pythonista({
    'path' : '/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/Urtext Projects',
    'initial' :'/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/Urtext Projects/Nate\'s Big Project',
    'theme' : urtext_theme_light,
    })

