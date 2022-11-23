from urtext.syntax import *
from theme import theme
import re

title_pattern = r"(([^>\n\r_])|(?<!\s)_)+"

patterns = {

    # dynamic definition wrapper
    r'\[\[.*?\]\]': {   

        'self': theme['dynamic_definition_wrapper'],       

        'inside' : [ 

            # function names
            { r'(\+|\-|[A-Z]+)(?=\(.*?\))' : { 'self': theme['function_names'] },

            # keys
            r'([\w]+)(?=\:)': { 'self': theme['keys'] },       

            # values, single-word
            r'(?<=\:)([\w]+)' : { 'self' : theme['values'] }, 

            # keywords
            r'\b(-[a-z]+)\b' : { 'self' : theme['keywords'] },
            
            # value strings (quotations)
            r'([\w]+)\:("[\w\s]+")' : { 'self' : theme['value_strings'] }, 
            } 
          ],

      },

    # compact node opener
    r'^[^\S\n]*?•' : {
       'self' : theme['bullet'],
       'flags': re.MULTILINE,
    },

    # metadata ::
    r'::' : { 'self' : theme['metadata_symbol'] },

    # metadata key
    r'\w+?(?=::)' : {
        'self' : {
            'font': theme['font']['bold'],
        },
    },
    
    # metadata value 
    r'(?<=::)[^\n};@]+;?' : {
       'self': theme['metadata_values'] ,
      'inside': [
            # metadata separator
            { '-' : { 'self': theme['metadata_separator'] }  },
        ]
    },

    # hash metadata shorthand
    r'(?:^|\s)#[A-Z,a-z].*?\b' : { 'self':'bold'},

    # timestamps
    r'<.*?>':{  'self': theme['node_pointers'] },                             

    # error messages
    r'<!{2}.*?!{2}>\n?' : { 'self' : theme ['error_messages'] },
    
    #node link or pointer
    r'(\|\s)' + title_pattern + '\s>{1,2}(?!>)': {  
        'self': theme['node_pointers'],
        'flags': 0
        },  
        
    #node titles
     r'(\|\s)'+ title_pattern : {
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