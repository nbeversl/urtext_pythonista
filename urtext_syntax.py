import urtext.syntax as syntax
import re
class UrtextSyntax:

    def __init__(self, theme):
        
        self.theme = theme
        self.name = 'Urtext'

        node_link_or_pointer_syntax = {
            'pattern': syntax.node_link_or_pointer_c,       
            'self': {
                'font' : theme['font']['bold'],
                },
            'groups' : {
                    6 : { 
                        'color': theme['node_pointers']
                        },
                    },
            'inside': [
                {
                    'pattern': syntax.node_link_modifiers_regex_c['action'],
                    'self': {
                        'color': theme['node_link_modifier_action']
                    }
                },
                {
                    'pattern': syntax.node_link_modifiers_regex_c['missing'],
                    'self': {
                        'color': theme['node_link_modifier_missing']
                    }
                },
            ],
        }

        file_link_syntax = {
            'pattern': syntax.file_link_c,       
            'self': {
                'font' : theme['font']['bold'],
                },
            'groups' : {
                    },
            'inside': [
                {
                    'pattern': re.compile(syntax.file_link_modifiers['file']),
                    'self': {
                        'color': theme['file_link_modifier_file']
                    }
                },
                {
                    'pattern': re.compile(re.escape(syntax.file_link_modifiers['missing'])),
                    'self': {
                        'color': theme['file_link_modifier_missing']
                    }
                },
            ],
        }

        self.syntax = [
   
            {   'pattern': syntax.dynamic_def_c,
                'self': {
                	   'color': theme['dynamic_definition_wrapper'],
                       'font' : theme['font']['bold italic'],
                },

                'inside' : [ 

                    {   'pattern': syntax.function_c, 
                        'self': {
                            'color' : theme['function_names'],
                            'font' : theme['font']['bold'],
                        },
                        'inside' : [
                            {
                                'pattern': syntax.dd_flags_c, 
                                'self' : {
                                    'color' : theme['flag'] 
                                    },
                            },
                        ]
                    },
                    node_link_or_pointer_syntax,
                    file_link_syntax,
                ]
            },

            node_link_or_pointer_syntax,
            file_link_syntax,

            {
                'pattern': syntax.sh_metadata_key_c, 
                'self': {
                    'color': theme['keys'],
                    'font': theme['font']['regular'],
                    },
            },
            {
                'pattern' : syntax.metadata_flags_c,
                'self' : {
                    'font' : theme['metadata_flags']
                }

            },
            {
                'pattern': syntax.bullet_c,
                'self' : {
                    'color' : theme['bullet']
                    }
            },
            {   
                'pattern': syntax.metadata_assigner_c,
                'self' : {
                    'color' : theme['metadata_assigner'] 
                },
            },
            {
                'pattern': syntax.sh_metadata_values_c,
                'self': {
                    'color' : theme['metadata_values'] 
                },

                'inside': [
                    { 
                        'pattern':syntax.metadata_separator_pattern_c, 
                        'self': {
                            'color': theme['metadata_separator'] 
                            }  
                    },
                ]
            },
            {
                'pattern':syntax.hash_meta_c,
                'self': {
                    'font' : theme['font']['bold']
                    }
            },   
            {
                'pattern': syntax.timestamp_c,
                'self': {
                    'color': theme['timestamp'] 
                    },
            },
            {
                'pattern':  syntax.urtext_messages_c, 
                'self' : {
                    'color' : theme['error_messages'] 
                    },
            },
            {
                'pattern': syntax.node_link_or_pointer_c,       
                'self': {
                    'font' : theme['font']['bold'],
                    },
                'groups' : {
                        6 : { 
                            'color': theme['node_pointers']
                            },
                        },
                'inside': [
                    { 
                        'pattern':syntax.metadata_separator_pattern_c, 
                        'self': {
                            'color': theme['metadata_separator'],
                            }
                    },
                    {
                        'pattern': syntax.node_link_modifiers_regex_c['action'],
                        'self': {
                            'color': theme['node_link_modifier_action']
                        }
                    },
                    {
                        'pattern': syntax.node_link_modifiers_regex_c['missing'],
                        'self': {
                            'color': theme['node_link_modifier_missing']
                        }
                    },
                ],
            },
            {  
                # from ST syntax definition
                'pattern': re.compile('(?!<=\{)((([^\|>\{\}\n\r_])|(?<!\s)_)+)(\s_)(\s|$)'),
                'self': {
                    'font' : theme['font']['bold']
                },
            },
            {
                'pattern': syntax.opening_wrapper_c,
                'type' : 'push',
                'pop' : {
                    'pattern': syntax.closing_wrapper_c
                    }
            },
            {
                'pattern': re.compile('`.*?`'),
                'self' : {
                    'color' : theme['error_messages']
                    },
            },
        ]
