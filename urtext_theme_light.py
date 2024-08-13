from sublemon.themes.colors import colors
from sublemon.themes.fonts import fonts

urtext_theme_light = {   
    'name': 'Urtext Light',
    'keyboard_appearance': 0,
    'dynamic_definition_wrapper' : colors['grey6'],
    'background_color' :colors['paper'],
    'foreground_color' : colors['grey5'],
    'highlight_color': colors['highlight_yellow'],
    'function_names' : colors['lightgray'],
    'keys' : colors['red'],
    'values' : colors['blue_brighter'],
    'flag' : colors['red'],
    'bullet' : colors['red'],
    'metadata_assigner' : colors['grey_reg'],
    'metadata_values' : colors['blue_brighter'],
    'metadata_separator' : colors['grey5'],
    'node_pointers' : colors['blue_brighter'],
    'node_link_modifier_action': colors['bright_green2'],
    'node_link_modifier_missing': colors['yellow'],
    'file_link_modifier_file' : colors['bright_green2'],
    'file_link_modifier_missing': colors['yellow'],
    'error_messages' : colors['red'],
    'timestamp': colors['blue_brighter'],
    'font' : {
        'regular' : fonts['Courier New'],
        'bold' :    fonts['Courier New Bold'],
        'bold italic': fonts['Courier New Bold Italic'],
    },
    'metadata_flags' :              fonts['Courier New Bold'],
    'wrappers' : [
        colors['blue_lighter'],
        colors['aqua_green2'],
        colors['lime2'],
        colors['bright_green2'],
        colors['deep_blue2']
    ],
    'button_border_color' :         '#515151',
    'button_line_background_color': '#000000',
    'button_background_color' :     "#515151",
    'button_tint_color' :           '#ffffff',
    'autocompleter': {
        'background_color' : "#ffffff",
        'foreground_color' : "#000000",
        'search_field_background_color': colors['white'],
        'search_field_border_color': 'black',
        'separator_color': 'black',
    }
}
