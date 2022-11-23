from urtext.syntax import *
from theme import theme
import re

title_pattern = r"(([^>\n\r_])|(?<!\s)_)+" # get these from python syntax patterns instead

patterns = {

    # dynamic definition wrapper
    r'\[\[.*?\]\]': {   

        'self': {
            'color':theme['dynamic_definition_wrapper']
            },

        'inside' : [ 

            # function names
            {   r'(\+|\-|[A-Z]+)(?=\(.*?\))' : { 
                
                    'self': {
                        'color' : theme['function_names']
                        }
                    },

                # keys
                r'([\w]+)(?=\:)': { 
                    
                    'self': {
                        'color': theme['keys'] 
                        },
                    },

                # values, single-word
                r'(?<=\:)([\w]+)' : { 

                    'self' : {
                        'color' : theme['values'] 
                        },
                    },

                # keywords
                r'\b(-[a-z]+)\b' : { 

                    'self' : {
                        'color' : theme['keywords'] 
                        },
                    },   
                
                # value strings (quotations)
                r'([\w]+)\:("[\w\s]+")' : { 

                    'self' : {
                        'color' : theme['value_strings'] 
                        }
                    }  
                } 
          ],

      },

    # compact node opener
    r'^[^\S\n]*?•' : {
        
        'flags': re.MULTILINE,
        'self' : {
            'color' : theme['bullet']
            }
       
    },

    # metadata ::
    r'::' : { 
    
        'self' : {
            'color' : theme['metadata_symbol'] 
            },
        },

    # metadata key
    r'\w+?(?=::)' : {

        'self' : {
            'font': theme['font']['bold'],
        },
    },
    
    # metadata value 
    r'(?<=::)[^\n};@]+;?' : {

       'self': {
            'color' : theme['metadata_values'] 
        },

      'inside': [
            # metadata separator
            { '-' : { 

                'self': {
                    'color': theme['metadata_separator'] 
                    }  
                },
            }
        ]
    },

    # hash metadata shorthand
    r'(?:^|\s)#[A-Z,a-z].*?\b' : { 

        'self': {
            'font' : theme['font']['bold']
            }
        },   

    # timestamps
    r'<.*?>':{  

        'self': {
            'color': theme['node_pointers'] 
            },
        },                             

    # error messages
    r'<!{2}.*?!{2}>\n?' : { 
        'self' : {
            'color' : theme ['error_messages'] 
            },
        },
    
    #node link or pointer
    r'(\|\s)' + title_pattern + '\s>{1,2}(?!>)': {  
        
        'flags': 0,
        'self': {
            'color' : theme['node_pointers'],
            },

        },  
        
    #node titles
     r'(\|\s)' + title_pattern : {
        'self': {
            'font' : theme['font']['bold']
        },
    },

    # node wrapper:
    r'\{' : {
        'type' : 'push',
        'pop' : r'\}',
    },
}