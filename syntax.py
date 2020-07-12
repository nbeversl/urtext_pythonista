from objc_util import *
import re
import time

unobtrusive = UIColor.colorWithRed(0.25, green=0.25, blue=0.25, alpha=1.0)
green = UIColor.colorWithRed(0.44, green=0.84, blue=0.42, alpha=1.0)
bright_yellow = UIColor.colorWithRed(1.0, green=1.0, blue=0.5, alpha=1.0)
blue_bright = UIColor.colorWithRed(0.08, green=0.24, blue=0.72, alpha=1.0)
blue_brighter = UIColor.colorWithRed(0.28, green=0.44, blue=0.92, alpha=1.0)
red = UIColor.colorWithRed(1, green=0.44, blue=0.92, alpha=1.0)


colors = {

    # dynamic definition 
    r'\[\[.*?\]\]': {                                                     
        'self': bright_yellow,       
        'inside' : [ 
          { r'(INCLUDE|METADATA|ID|TREE|SHOW|TIMELINE|EXCLUDE|FORMAT|SEARCH|LIMIT|SORT|EXPORT|FILE|TAG_ALL)(?=\(.*?\))' : { 'self':green },
            r'([\w]+)(?=\:)': { 'self':red },       # keys
            r'(?<=\:)([\w]+)' : { 'self' : unobtrusive }, # values, single-word
            r'\b(reverse|preformat|all|meta|inline|indexed|and|or|multiline_meta|indent|timestamp|markdown|html|plaintext|source|recursive)\b' :
                  { 'self' : red },   # keywords
            r'([\w]+)\:("[\w\s]+")' : { 'self' : red}, # value strings (quotations)
            } 
          ],

      },


    #trailing node ids
    r'\b[0-9,a-z]{3}(?=}})': {
      'self': unobtrusive,
    },

    # compact node opener
    r'^[^\S\n]*?\^' : {
       'self':red,
       'flags':re.MULTILINE,
    },

    # metadata wrappers
    r'(\/--(?:(?!\/--).)*?--\/)': {                                 

        'self':UIColor.grayColor(),

        'inside': [ 

             # metadata keys
            { r'[\w\s]+:' : {'self' : blue_bright}  },              

            # metadata values
            { r'(?<=\w:)((?!--\/)[^;\n])*' : {

                'self': blue_brighter,

                'inside': [
                  { '|' : { 'self': unobtrusive }  },

                  ]
                }
             },
           ]
        },   

    # Node Pointers
    r'>>[0-9,a-z]{3}\b':{
        'self':UIColor.purpleColor()
        },

    # timestamps
    r'<.*?>':{ 
        'self':green
        },                             

    # Project Links
    r'/{\"(.*?)\"}>([0-9,a-z]{3})\b/':{

        'self':UIColor.colorWithRed(0.98, green=0.92, blue=0.36, alpha=1.0) },
    
    # link prefix (>)
    r'>(?=([0-9,a-z]{3}))':{ 
        'self':green
        },               
    
    # nodeIDs in links
    r'(?<=>)[0-9,a-z]{3}':{ 
        'self':unobtrusive
        },         
   
    #link titles
    r'\|[^<][^\s].*?(?=>{1,2}[0-9,a-z]{3}\b[^\n]*?)': {  
        'self':bright_yellow,
        'flags': 0
        },  

    # other project link (change to bold, or something)
    r'\{\"(.*?)\"\}' : {
        'self':bright_yellow,
    }
}

wrappers = [ 
  r'\{\{',
  r'\}\}',
  r'^[^\S\n]*?\^', # compact node opener
  r'\n',
  ]

wrapper_color = unobtrusive

def find_wrappers(string):
   found_wrappers = {}
   for wrapper in wrappers:
      found = re.finditer(wrapper,string, flags=re.MULTILINE)
      for item in found:
         found_wrappers[item.start()] = wrapper
   return found_wrappers

def nest_colors(mystro, mystr, offset, colors):
   # go through each thing i want to highlight, and addAttribute to that range
   for pattern in colors:
        flags = re.DOTALL
        if 'flags' in colors[pattern]:
          flags = colors[pattern]['flags']
        sre = re.finditer(pattern, mystr, flags=flags)
        color = colors[pattern]['self']
        for m in sre:
            start, end = m.span()
            length = end-start
            mystro.addAttribute_value_range_(ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),color,NSRange(start+offset,length))            
            
            if 'inside' in colors[pattern]:
                substring = mystr[start:end]
                for nested_item in colors[pattern]['inside']:
                    nest_colors(mystro, substring, start, nested_item)

@on_main_thread
def setAttribs(tv, tvo, text='', initial=False):

   font = ObjCClass('UIFont').fontWithName_size_('Arial',15)
   file_position = tv.selected_range
   if text:
    tv.text = text 	      
   mystr = tv.text
   
   mystro = ObjCClass('NSMutableAttributedString').alloc().initWithString_(mystr)
   original_mystro = ObjCClass('NSMutableAttributedString').alloc().initWithString_(mystr)
   mystro.addAttribute_value_range_(ObjCInstance(c_void_p.in_dll(c,'NSFontAttributeName')),font,NSRange(0,len(mystr)))
   mystro.addAttribute_value_range_(ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),UIColor.whiteColor(),NSRange(0,len(mystr)))
   nest_colors(mystro, mystr, 0, colors)
   value = 0.16
   # matching sublime:
   # [UIColor colorWithRed:0.16 green:0.16 blue:0.14 alpha:1.0];
   background = UIColor.colorWithRed(value, green=value, blue=value, alpha=1.0)
   mystro.addAttribute_value_range_('NSBackgroundColor',background,NSRange(0,len(mystr)))

   wrappers = find_wrappers(mystr)
   
   if wrappers:    
    compact_node_open = False
    positions = sorted(wrappers.keys())
    for index in range(len(positions)):
        position = positions[index]

        if wrappers[position] == '\\n':
            compact_node_open = False
            continue

        if wrappers[position] == '\\{\\{' :
            value += 0.025
            starting_offset = 0
            amount_offset = 2
            mystro.addAttribute_value_range_(ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),wrapper_color,NSRange(position,2))
        
        if wrappers[position] == '^[^\\S\\n]*?\\^':        
            value += 0.025
            starting_offset = 0
            amount_offset = 0
            compact_node_open = True

        if wrappers[position] == '\\}\\}' :
            value -= 0.025
            starting_offset = 2
            amount_offset = 0
            mystro.addAttribute_value_range_(ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),wrapper_color,NSRange(position,2))

        # If this is not the last closing wrapper:
        if position < positions[-1]:

            # set the starting position
            start = position + starting_offset

            # calculate the ending position from the next symbol back to this one

            # get position
            next_index = index + 1
            if not compact_node_open:
              while wrappers[positions[next_index]] == '\\n' and next_index < len(positions) - 1:
                next_index += 1;
            
            amount = positions[next_index] - start + amount_offset

            background = UIColor.colorWithRed(value, green=value, blue=value, alpha=1.0)
            mystro.addAttribute_value_range_('NSBackgroundColor', background,NSRange(start,amount))
            if compact_node_open:
              compact_node_open = False
              value -= 0.025

        else:
            start = position + 2
            amount = len(mystr) - start
            background = UIColor.colorWithRed(value, green=value, blue=value, alpha=1.0)
            mystro.addAttribute_value_range_('NSBackgroundColor',background,NSRange(start, amount))
   

   if initial or (mystro != original_mystro):
      #tv.scroll_enabled = False

      tvo.setAllowsEditingTextAttributes_(True)
      tvo.setAttributedText_(mystro)
      #time.sleep(1)
      #tv.scroll_enabled =True
      
   print(file_position)
   print(len(tv.text))
   if file_position[1] < len(tv.text):         
      tv.selected_range = file_position




