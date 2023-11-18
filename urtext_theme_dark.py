from sublemon.themes.colors import colors
from sublemon.themes.fonts import fonts

urtext_theme_dark = {  
    'name': 'Urtext Dark', 
    'keyboard_appearance': 1,
    'dynamic_definition_wrapper' :  colors['grey6'],
    'background_color' :            colors['black'],
    'foreground_color' :            colors['white'],
    'highlight_color':              colors['highlight_yellow'],
    'function_names' :              colors['lightgray'],
    'keys' :                        colors['red'],
    'values' :                      colors['blue_brighter'],
    'flag' :                        colors['red'],
    'bullet' :                      colors['red'],
    'metadata_assigner' :           colors['grey_reg'],
    'metadata_values' :             colors['blue_brighter'],
    'metadata_separator' :          colors['grey5'],
    'node_pointers' :               colors['blue_brighter'],
    'error_messages' :              colors['red'],
    'timestamp':                    colors['blue_brighter'],
    'font' : {
        'regular' : fonts['Courier New'],
        'bold' :    fonts['Courier New Bold'],
    },
    'metadata_flags' :              fonts['Courier New Bold'],
    'wrappers' : [
        colors['blue_lighter'],
        colors['aqua_green2'],
        colors['lime2'],
        colors['bright_green2'],
        colors['deep_blue2']
    ],

    # must by hex, not UIColor
    'button_border_color' :         '#515151',
    'button_line_background_color': '#000000',
    'button_background_color' :     "#515151",
    'button_tint_color' :           '#ffffff',
}
