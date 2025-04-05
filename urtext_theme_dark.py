from sublemon.themes.colors import colors
from sublemon.themes.fonts import fonts

urtext_theme_dark = {  
    'name': 'Urtext Dark', 
    'keyboard_appearance': 1,
    'frame' : colors['grey6'],
    'background_color' : colors['black'],
    'call_key': colors['highlight_yellow'],
    '': colors['bright_green2'],
    'foreground_color' : colors['white'],
    'highlight_color': colors['highlight_yellow'],
    'function_names' : colors['white'],
    'keys' : colors['red'],
    'values' : colors['blue_brighter'],
    'flag' : colors['red'],
    'format_key': colors['blue_brighter'],
    'function_keys': colors['red'],
    'function_operators': colors['blue_brighter'],
    'function_values': colors['red'],
    'bullet' : colors['red'],
    'function_keys': colors['red'],
    'metadata_assigner' : colors['grey_reg'],
    'metadata_values' : colors['blue_brighter'],
    'metadata_separator': colors['grey5'],
    'node_pointers' : colors['blue_brighter'],
    'node_link_modifier_action': colors['bright_green2'],
    'node_link_modifier_missing': colors['yellow'],
    'file_link_modifier_file' : colors['bright_green2'],
    'file_link_modifier_missing': colors['yellow'],
    'error_messages' : colors['red'],
    'timestamp': colors['blue_brighter'],

    'font' : {
        'regular' : fonts['Courier New'],
        'bold' : fonts['Courier New Bold'],
        'bold italic': fonts['Courier New Bold Italic'],
    },
    'metadata_flags' : fonts['Courier New Bold'],
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
    'autocompleter': {
        'background_color' : "#000000",
        'foreground_color' : "#ffffff",
        'search_field_background_color': colors['black'],
        'search_field_border_color': 'white',
        'separator_color': 'white',
    }
}
