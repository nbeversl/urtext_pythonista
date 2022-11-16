from objc_util import *
from syntax import patterns
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


push_wrappers = [re.compile(p, flags=re.MULTILINE) for p in patterns if 'type' in patterns[p] and patterns[p]['type'] == 'push']
push_wrappers_plain = [p for p in patterns if 'type' in patterns[p] and patterns[p]['type'] == 'push']
pop_wrappers = [re.compile(patterns[p]['pop'], flags=re.MULTILINE) for p in patterns if 'pop' in patterns[p]]
pop_wrappers_plain = [patterns[p]['pop'] for p in patterns if 'pop' in patterns[p]]
all_wrappers = push_wrappers
all_wrappers.extend(pop_wrappers)

def find_wrappers(string, wrappers):
   found_wrappers = {}
   for w in wrappers:
       s = re.finditer(w, string)
       for item in s:
         found_wrappers[item.start()] = w.pattern
   return found_wrappers

@on_main_thread
def setAttribs(tv, tvo, initial=False):

    mystr = tv.text
    mystro = ObjCClass('NSMutableAttributedString').alloc().initWithString_(mystr)
    original_mystro = ObjCClass('NSMutableAttributedString').alloc().initWithString_(mystr)  
    mystro.addAttribute_value_range_(ObjCInstance(c_void_p.in_dll(c,'NSFontAttributeName')), font_reg, NSRange(0,len(mystr)))
    mystro.addAttribute_value_range_(
        ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')), 
        grey5, 
        NSRange(0,len(mystr)))

    nested_level = 0
    
    found_wrappers = find_wrappers(mystr, all_wrappers)
    looking_for_pop = False
    pop_wrapper = ''
    positions = sorted(found_wrappers.keys())
    for index in range(len(positions)):
        position = positions[index]
        if found_wrappers[position] in push_wrappers_plain:
            nested_level += 1
            if nested_level < len(wrapper_colors):
                mystro.addAttribute_value_range_(
                  ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),
                  wrapper_colors[nested_level],
                  NSRange(position,1))
            pop_wrapper = patterns[found_wrappers[position]]['pop']
            continue
        if found_wrappers[position] == pop_wrapper:
            if nested_level < len(wrapper_colors):
                mystro.addAttribute_value_range_(
                  ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),
                  wrapper_colors[nested_level],
                  NSRange(position,1))
            nested_level -= 1

    nest_colors(mystro, mystr, 0, patterns)
    if initial or (mystro != original_mystro):
      tvo.setAllowsEditingTextAttributes_(True)
      tvo.setAttributedText_(mystro)

def nest_colors(mystro, mystr, offset, patterns):
    
    for pattern in patterns:
        if 'type' in patterns[pattern]:
            continue # already done
        
        flags = re.DOTALL
        if 'flags' in patterns[pattern]:
          flags = patterns[pattern]['flags']

        sre = re.finditer(pattern, mystr, flags=flags)
        color = patterns[pattern]['self']

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
            
            if 'inside' in patterns[pattern]:
                substring = mystr[start:end]
                for nested_item in patterns[pattern]['inside']:
                    nest_colors(mystro, substring, start, nested_item)
