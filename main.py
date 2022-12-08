from launch_urtext_editor import LaunchUrtextEditor
from urtext_theme_light import urtext_theme_light

editor = LaunchUrtextEditor({
    'path' : '/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/Urtext Projects',
    'initial' :'/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/Urtext Projects/Nate\'s Big Project',
    'theme' : urtext_theme_light,
    })
editor.start()
