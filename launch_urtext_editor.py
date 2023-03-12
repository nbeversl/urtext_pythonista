"""
Start Urtext Pythonista
"""
from urtext_pythonista import UrtextEditor
from urtext_theme_light import urtext_theme_light
from urtext_theme_light_custom import urtext_theme_light_custom

s = UrtextEditor({
    'path' : '/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/Urtext Projects/Nate\'s Big Project',        
    'theme' : urtext_theme_light,   
    # 'launch_action' : 'new_node',
})

if not s.app.is_active():
    s.show()
