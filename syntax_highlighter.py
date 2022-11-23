from objc_util import *
from urtext_syntax import patterns
import re
from theme import theme

font_reg = ObjCClass('UIFont').fontWithName_size_(theme['font']['name'], theme['font']['size'])
font_bold = ObjCClass('UIFont').fontWithName_size_(theme['font']['bold'], theme['font']['size'])

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

    mystro.addAttribute_value_range_(
        ObjCInstance(
            c_void_p.in_dll(c,'NSFontAttributeName')), 
        font_reg, 
        NSRange(0,len(mystr)))

    mystro.addAttribute_value_range_(
        ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')), 
        theme['foreground_color'], 
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
            if nested_level < len(theme['wrappers']):
                mystro.addAttribute_value_range_(
                  ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),
                  theme['wrappers'][nested_level],
                  NSRange(position,1))
            pop_wrapper = patterns[found_wrappers[position]]['pop']
            continue
        if found_wrappers[position] == pop_wrapper:
            if nested_level < len(theme['wrappers']):
                mystro.addAttribute_value_range_(
                  ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),
                  theme['wrappers'][nested_level],
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
        font = None
        attribute = patterns[pattern]['self']
        if 'font' in attribute:
            font =  patterns[pattern]['self']['font']

        for m in sre:
            start, end = m.span()
            length = end-start
            if font:   
              mystro.addAttribute_value_range_(
                ObjCInstance(c_void_p.in_dll(c,'NSFontAttributeName')), 
                font, 
                NSRange(start+offset,length))
            else:
              mystro.addAttribute_value_range_(
                ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),
                attribute,
                NSRange(start+offset,length)
              )            
            
            if 'inside' in patterns[pattern]:
                substring = mystr[start:end]
                for nested_item in patterns[pattern]['inside']:
                    nest_colors(mystro, substring, start, nested_item)
