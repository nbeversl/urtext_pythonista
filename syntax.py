from objc_util import *
import re


unobtrusive = UIColor.colorWithRed(0.25, green=0.25, blue=0.25, alpha=1.0)
green = UIColor.colorWithRed(0.44, green=0.84, blue=0.42, alpha=1.0)
bright_yellow = UIColor.colorWithRed(1.0, green=1.0, blue=0.5, alpha=1.0)
blue_bright = UIColor.colorWithRed(0.08, green=0.24, blue=0.72, alpha=1.0)
blue_brighter = UIColor.colorWithRed(0.28, green=0.44, blue=0.92, alpha=1.0)

colors = {

    # dynamic definition 
    r'\[\[.*?\]\]': {                                               
        
        'self': bright_yellow
        
        # 'inside' : [ { r';' : {'self':green } } ] 
        },                       
    
    # metadata wrappers
    r'(\/--(?:(?!\/--).)*?--\/)': {                                 

        'self':UIColor.grayColor()

        # 'inside': [ 

        #     # metadata keys
        #     { r'[\w\s]+:' : {'self' : blue_bright}  },              

        #     # metadata values
        #     { r'(?<=\w:)((?!--\/)[^;\n|])*' : {'self': blue_brighter} }, 

        #     # Metadata separators
        #     { '\|' : { 'self': unobtrusive } }
        #     ]
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
    r'\|.*?(?=>{1,2}[0-9,a-z]{3}\b[^\n]*?)': {  
        'self':bright_yellow,
        'flags': 0
        },
}


wrappers = [ r'\{\{',r'\}\}']
wrapper_color = unobtrusive

def find_wrappers(string):
  
   found_wrappers = {}
   for wrapper in wrappers:
      found = re.finditer(wrapper,string)
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
def setAttribs(tv, initial=False):
   font = ObjCClass('UIFont').fontWithName_size_('Arial',15)
   
   file_position = tv.selected_range[0]
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
    positions = sorted(wrappers.keys())
    for index in range(len(positions)):
        position = positions[index]

        mystro.addAttribute_value_range_(ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),wrapper_color,NSRange(position,2))
        if wrappers[position] == '\{\{':
            value += 0.025
            starting_offset = 0
            amount_offset = 2
        else: # }}
            value -= 0.025
            starting_offset = 2
            amount_offset = 0

        # If this is not the last closing wrapper:
        if position < positions[-1]:

            # set the starting position
            start = position + starting_offset

            # calculate the ending position from the next symbol back to this one
            amount = positions[index+1] - start + amount_offset

            background = UIColor.colorWithRed(value, green=value, blue=value, alpha=1.0)
            mystro.addAttribute_value_range_('NSBackgroundColor', background,NSRange(start,amount))

        else:
            start = position + 2
            amount = len(mystr) - start
            background = UIColor.colorWithRed(value, green=value, blue=value, alpha=1.0)
            mystro.addAttribute_value_range_('NSBackgroundColor',background,NSRange(start, amount))


   if initial or (mystro != original_mystro):
      # putting this line here fixes the crash on iPhone
      tvo=ObjCInstance(tv)
      #tvo.setScrollEnabled_(False)
      tvo.setAllowsEditingTextAttributes_(True)
      tvo.setAttributedText_(mystro)
  
      #if file_position < len(mystr):
      #   tv.selected_range = (file_position, file_position)
          
      #tvo.setScrollEnabled_(True)

