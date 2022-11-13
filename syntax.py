from objc_util import *
import re

green = UIColor.colorWithRed(0.44, green=0.84, blue=0.42, alpha=1.0)
blue_brighter = UIColor.colorWithRed(0.28, green=0.44, blue=0.92, alpha=1.0)
paper =  UIColor.colorWithRed(0.898, green=0.8667, blue=0.8627, alpha=1.0)
grey5 =  UIColor.colorWithRed(0.3294, green=0.3294, blue=0.3294, alpha=1.0)
grey6 =   UIColor.colorWithRed(0.4, green=0.4, blue=0.4, alpha=1.0)
unobtrusive = UIColor.colorWithRed(0.8392, green=0.8118, blue=0.7961, alpha=1.0)
grey = UIColor.colorWithRed(0.7176, green=0.7176, blue=0.7176, alpha=1.0)
white2 = UIColor.colorWithRed(0, green=0, blue=.97, alpha=1.0)
red = UIColor.colorWithRed(0.498, green=0, blue=0, alpha=1.0)

# wrappers
blue_lighter = UIColor.colorWithRed(0.5098, green=0.6, blue=0.8471, alpha=1.0)
aqua_green2 = UIColor.colorWithRed(0.6157, green=0.7686, blue=0.7176, alpha=1.0)
lime2 = UIColor.colorWithRed(0.2745, green=0.4588, blue=0.4078, alpha=1.0)
bright_green2 = UIColor.colorWithRed(0.451, green=0.698, blue=0.4196, alpha=1.0)
deep_blue2 = UIColor.colorWithRed(0.7647, green=0.5098, blue=0.8471, alpha=1.0)

wrapper_colors = [
    blue_lighter,
    aqua_green2,
    lime2,
    bright_green2,
    deep_blue2
]

font = {
    'name' : 'Fira Code',
    'bold' : 'FiraCode-Bold',
    'size' : 12
} 

patterns = {

    # dynamic definition 
    r'\[\[.*?\]\]': {                                                     
        'self': grey6,       
        'inside' : [ 
          { r'(\+|\-|INCLUDE|ID|HEADER|FOOTER|SHOW|COLLECT|EXCLUDE|EXPORT|LIMIT|SORT)(?=\(.*?\))' : { 'self':grey },
            r'([\w]+)(?=\:)': { 'self':red },       # keys
            r'(?<=\:)([\w]+)' : { 'self' : unobtrusive }, # values, single-word
            r'\b(-r|-t|reverse|preformat|multiline_meta|indent|timestamp|markdown|html|plaintext|source|recursive)\b' :
                  { 'self' : red },   # keywords
            r'([\w]+)\:("[\w\s]+")' : { 'self' : red}, # value strings (quotations)
            } 
          ],

      },

    # compact node opener
    r'^[^\S\n]*?•' : {
       'self':red,
       'flags':re.MULTILINE,
    },

    # metadata ::
    r'::' : {
        'self':UIColor.grayColor()
    },

    # metadata key
    r'\w+?(?=::)' : {
        'self' : 'bold',
    },
    
    # metadata value 
    r'(?<=::)[^\n};@]+;?' : {
       'self': blue_brighter ,
      'inside': [
          { '|' : { 'self': unobtrusive }  },
        ]
    },

    # hash metadata shorthand
    r'(?:^|\s)#[A-Z,a-z].*?\b' :
    {
        'self':'bold',
    },

    # Node Pointers
    r'([>]{2})(.+\b)':{
        'self':grey5
        },

    # timestamps
    r'<.*?>':{ 
        'self':green
        },                             

    # error messages
    r'<!{2}.*?!{2}>\n?' : {
      'self' :UIColor.redColor(),
    },
    
    #link titles
    r'\|[^<][^\s].*?(?=>{1,2}[0-9,a-z]{3}\b[^\n]*?)': {  
        'self':grey5,
        'flags': 0
        },  
        
    #node titles
     r'(?<={)([^\n{_]*?(?= _\b))|(^[^\n_{]*?(?= _\b))':{ 
        'self':'bold',
        },

    # node wrapper:
    r'\{' : {
        'type' : 'push',
        'pop' : r'\}',
    },   

    # compact wrapper:
    r'•' : {
        'type' : 'push',
        'pop' : r'\n'
    },

}



