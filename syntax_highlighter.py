from objc_util import *
from syntax import colors, wrapper_colors
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

font_settings = {
    'name' : 'Fira Code',
    'bold' : 'FiraCode-Bold',
    'size' : 12
} 

font_reg = ObjCClass('UIFont').fontWithName_size_(font_settings['name'], font_settings['size'])
font_bold = ObjCClass('UIFont').fontWithName_size_(font_settings['bold'], font_settings['size'])

@on_main_thread
def setAttribs(tv, tvo, initial=False):

   file_position = tv.selected_range
   mystr = tv.text
   mystro = ObjCClass('NSMutableAttributedString').alloc().initWithString_(mystr)
   original_mystro = ObjCClass('NSMutableAttributedString').alloc().initWithString_(mystr)  
   mystro.addAttribute_value_range_(ObjCInstance(c_void_p.in_dll(c,'NSFontAttributeName')), font_reg, NSRange(0,len(mystr)))
   mystro.addAttribute_value_range_(
        ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')), 
        grey5, 
        NSRange(0,len(mystr)))
   nested_level = 0

   wrappers = find_wrappers(mystr)
   
   if wrappers:
    compact_node_open = False
    positions = sorted(wrappers.keys())
    for index in range(len(positions)):
        position = positions[index]

        if wrappers[position] == '\n':
            compact_node_open = False
            continue

        if wrappers[position] == '{' :
            nested_level += 1 
            if nested_level < len(wrapper_colors):
	            mystro.addAttribute_value_range_(
	              ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),
	              wrapper_colors[nested_level],
	              NSRange(position,1))
        
        if wrappers[position] == '^[^\S\n]*?\\^':        
            nested_level += 1
            compact_node_open = True

        if wrappers[position] == '}' and len(wrapper_colors) >= nested_level:           
            if nested_level < len(wrapper_colors):
	            mystro.addAttribute_value_range_(
	              ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),
	              wrapper_colors[nested_level], #grey5, #
	              NSRange(position,1))
            nested_level -= 1

        # If this is not the last closing wrapper:
        if position < positions[-1]:
            if compact_node_open:
              compact_node_open = False
              nested_level -=1

   nest_colors(mystro, mystr, 0, colors)
   if initial or (mystro != original_mystro):
      tvo.setAllowsEditingTextAttributes_(True)
      tvo.setAttributedText_(mystro)

def find_wrappers(string):
   found_wrappers = {}
   s = re.finditer( r'(\{|\}|^[^\S\n]*?\^|\n)', string, flags=re.MULTILINE)
   for item in s:
     found_wrappers[item.start()] = item.group()
   return found_wrappers

def nest_colors(mystro, mystr, offset, colors):
 
   for pattern in colors:
        flags = re.DOTALL
        if 'flags' in colors[pattern]:
          flags = colors[pattern]['flags']
        sre = re.finditer(pattern, mystr, flags=flags)
        color = colors[pattern]['self']
        for m in sre:
            start, end = m.span()
            length = end-start
            if color == 'bold':   
              mystro.addAttribute_value_range_(
                ObjCInstance(c_void_p.in_dll(c,'NSFontAttributeName')), 
                font_bold, 
                NSRange(start+offset,length))
            else:
              mystro.addAttribute_value_range_(
                ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),
                color,
                NSRange(start+offset,length)
              )            
            
            if 'inside' in colors[pattern]:
                substring = mystr[start:end]
                for nested_item in colors[pattern]['inside']:
                    nest_colors(mystro, substring, start, nested_item)
