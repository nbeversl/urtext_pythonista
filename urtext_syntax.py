import urtext.syntax as syntax
import re

class UrtextSyntax:

    def __init__(self, theme):
        
        self.theme = theme
        self.name = 'Urtext'
        self.syntax = [
   
            {   'pattern': syntax.dynamic_def_c,
                'self': {
                	   'color':theme['dynamic_definition_wrapper']
                },

                'inside' : [ 

                    {   'pattern': syntax.function_c, 
                        'self': {
                            'color' : theme['function_names']
                        },
                        'inside' : [
                            {
                                'pattern': syntax.dd_flag_c, 
                                'self' : {
                                    'color' : theme['flag'] 
                                    },
                            },
                        ]
                    }
                ]
            },
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
                        5 : { 
                            'color': theme['node_pointers']
                            },
                        }   
            },
            {  
                'pattern':syntax.node_title_c,
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
