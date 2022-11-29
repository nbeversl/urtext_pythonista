from objc_util import *
from urtext_syntax import patterns
from theme import theme
import re

for p in patterns:
	if 'type' in p and p['type'] == 'push':
		push_wrapper = p['pattern'] 
		pop_wrapper = p['pop']['pattern']

all_wrappers = [push_wrapper, pop_wrapper]

def find_wrappers(string, wrappers):
	found_wrappers = {}
	for w in wrappers:
		s = w.finditer(string)
		for item in s:
			found_wrappers[item.start()] = item.group()

	return found_wrappers

@on_main_thread
def setAttribs(tv, tvo, initial=False):

	current_text = tv.text
	str_obj = ObjCClass('NSMutableAttributedString').alloc().initWithString_(current_text)
	original_str_obj = ObjCClass('NSMutableAttributedString').alloc().initWithString_(current_text)  

	str_obj.addAttribute_value_range_(
		ObjCInstance(
			c_void_p.in_dll(c,'NSFontAttributeName')), 
		theme['font']['regular'], 
		NSRange(0,len(current_text)))

	str_obj.addAttribute_value_range_(
		ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')), 
		theme['foreground_color'], 
		NSRange(0,len(current_text)))

	nested_level = 0
	
	found_wrappers = find_wrappers(current_text, all_wrappers)

	positions = sorted(found_wrappers.keys())
	for position in positions:
		# if the found wrapper is a push wrapper
		if push_wrapper.match(found_wrappers[position]):
			nested_level += 1
			if nested_level < len(theme['wrappers']):
				str_obj.addAttribute_value_range_(
				  ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),
				  theme['wrappers'][nested_level],
				  NSRange(position,1))
			continue
		
		if pop_wrapper.match(found_wrappers[position]):
			if nested_level < len(theme['wrappers']):
				str_obj.addAttribute_value_range_(
				  ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),
				  theme['wrappers'][nested_level],
				  NSRange(position,1))
			nested_level -= 1

	nest_colors(str_obj, current_text, 0, patterns)
	if initial or (str_obj != original_str_obj):
	  tvo.setAllowsEditingTextAttributes_(True)
	  tvo.setAttributedText_(str_obj)

def nest_colors(str_obj, current_text, offset, parse_patterns):
	
	for pattern in parse_patterns:

		if 'type' in pattern:
			continue # already done

		sre = pattern['pattern'].finditer(current_text)

		for m in sre:
			start, end = m.span()
			length = end-start
			
			if 'font' in pattern['self']: 
				  
			  str_obj.addAttribute_value_range_(
				ObjCInstance(c_void_p.in_dll(c,'NSFontAttributeName')), 
				pattern['self']['font'], 
				NSRange(start + offset,length))
			
			if 'color' in pattern['self']:
			  str_obj.addAttribute_value_range_(
				ObjCInstance(c_void_p.in_dll(c,'NSForegroundColorAttributeName')),
				pattern['self']['color'],
				NSRange(start + offset,length)
			  )
			
			if 'inside' in pattern:
				substring = current_text[start:end]
				nest_colors(str_obj, substring, start, pattern['inside'])
