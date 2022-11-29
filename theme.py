from colors import colors
from fonts import fonts

theme = {   
    'dynamic_definition_wrapper' :  colors['grey6'],
    'background_color' :            colors['paper'],
    'foreground_color' :            colors['grey5'],
    'function_names' :              colors['grey_reg'],
    'keys' :                        colors['red'],
    'values' :                      colors['blue_brighter'],
    'flag' :                        colors['red'],
    'value_strings' :               colors['red'],
    'bullet' :                      colors['red'],
    'metadata_assigner' :           colors['grey_reg'],
    'metadata_values' :             colors['blue_brighter'],
    'metadata_separator' :          colors['unobtrusive'],
    'node_pointers' :               colors['grey5'],
    'error_messages' :              colors['red'],
    'timestamp':                    colors['blue_brighter'],
    'font' : {
        'regular' : fonts['Fira Code'],
        'bold' :    fonts['FiraCode-Bold'],
    },
    'wrappers' : [
        colors['blue_lighter'],
        colors['aqua_green2'],
        colors['lime2'],
        colors['bright_green2'],
        colors['deep_blue2']
    ]
}
