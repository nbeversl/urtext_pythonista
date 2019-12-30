from urtext.project import UrtextProject
import time
import os
import datetime
import ui
import dialogs
import re
import math
import console
from app_single_launch import AppSingleLaunch
import threading

from fuzzywuzzy import fuzz

urtext_project_path = '/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/archive'
node_id_regex = r'\b[0-9,a-z]{3}\b'
command = ''
machine_name = 'Nate\'s iPhone'

print ('Urtext is loading '+urtext_project_path)

# https://stackoverflow.com/questions/49349033/create-auto-complete-textfield-in-pythonista-3

class AutoCompleter(ui.ListDataSource):
	
	def textfield_did_change(self, textfield):
		
		main_view.dropDown.hidden = False
		# an arbitrary list of autocomplete options
		length = len(textfield.text)
		entry = textfield.text.lower()
		self.titles = main_view._UrtextProject.titles()
		self.titles_keys = self.titles.keys()

		options = self.sort_options(entry)

		# setting the items property automatically updates the list
		self.items = options

		# size the dropdown for up to five options
		main_view.dropDown.height = min(main_view.dropDown.row_height * len(options), 5*main_view.dropDown.row_height)

	def sort_options(self, entry):

		matches = []
		for title in self.titles_keys:
			if entry.lower() == title.lower()[:len(entry)]:
				matches.append(title)

		fuzzy_options = sorted(
			self.titles_keys, 
			key=lambda title: fuzz.ratio(entry, title), 
			reverse=True)
		matches.extend(fuzzy_options)
		return matches
		


	def textfield_did_end_editing(self, textfield):
		#done editing, so hide and clear the dropdown
		main_view.dropDown.hidden = True
		main_view.search_field.hidden = True
		self.items = []
		main_view.search_field.text = ''

	def optionWasSelected(self, sender):
		main_view.search_field.text = self.items[self.selected_row]
		main_view.open_node(self.titles[self.items[self.selected_row]])
		main_view.search_field.end_editing()


class TaggingAutoCompleter(ui.ListDataSource):
	
	def textfield_did_change(self, textfield):
		
		main_view.tag_dropDown.hidden = False
		# an arbitrary list of autocomplete options
		length = len(textfield.text)
		entry = textfield.text.lower()
		self.tags = main_view._UrtextProject.tagnames['tags']
		options = [ x for x in self.tags.keys() if len(x) >= length and x[:length].lower() == entry]

		# setting the items property automatically updates the list
		self.items = options

		# size the dropdown for up to five options
		main_view.tag_dropDown.height = min(main_view.tag_dropDown.row_height * len(options), 5*main_view.tag_dropDown.row_height)

	def textfield_did_end_editing(self, textfield):
		#done editing, so hide and clear the dropdown
		if main_view.tag_search_field.text:

			insert = '/-- tags: '+main_view.tag_search_field.text+' --/'
			main_view.text_view.replace_range(main_view.text_view.selected_range, insert)
		main_view.tag_dropDown.hidden = True
		main_view.tag_search_field.hidden = True
		main_view.tag_search_field.text=''
		self.items = []
		
	def optionWasSelected(self, sender):
		main_view.tag_search_field.text = self.items[self.selected_row]       
		main_view.tag_search_field.end_editing()
		
class MainView(ui.View):

	def __init__(self, app: AppSingleLaunch):
		
		self.app = app
		self.name = "Pythonista Urtext" 
		self._UrtextProject = UrtextProject(urtext_project_path)
		self.current_open_file = None
		self.update_thread = None

		"""
		Build view components. 
		"""
		button_height = 32
		button_width = 32
		
		w,h = ui.get_screen_size()         
		self.h = h
		self.scroll_view = ui.ScrollView()
		self.scroll_view.frame = (0,50,w,h-84)
		self.text_view=ui.TextView()
		self.text_view.font = ('Helvetica Neue', 14)
		self.text_view.frame=(0,0,w,h)
		self.text_view.auto_content_inset = True
		
		self.full_txt_search_field = ui.TextField()
		self.full_txt_search_field.height = 40
		self.full_txt_search_field.width = w*.8
		self.full_txt_search_field.x = w/2 - self.full_txt_search_field.width/2
		self.full_txt_search_field.y = h/3 - self.full_txt_search_field.height/2
		self.full_txt_search_field.border_width = 1
		self.full_txt_search_field.hidden = True
		
		self.search_field = ui.TextField()
		self.size_field(self.search_field)
		self.search_field.hidden = True
		
		self.tag_search_field = ui.TextField()
		self.size_field(self.tag_search_field)
		self.tag_search_field.hidden = True
		
		self.dropDown = ui.TableView()
		self.dropDown.hidden = True
	
		self.title_autocompleter = AutoCompleter(items=[])
		self.title_autocompleter.action = self.title_autocompleter.optionWasSelected
		self.dropDown.delegate = self.title_autocompleter
		self.dropDown.data_source = self.title_autocompleter
		self.search_field.delegate = self.title_autocompleter
		
		self.tag_dropDown = ui.TableView()
		self.tag_dropDown.hidden = True

		self.tag_autocompleter = TaggingAutoCompleter(items=[])
		self.tag_autocompleter.action = self.tag_autocompleter.optionWasSelected
		self.tag_search_field.delegate = self.tag_autocompleter

		

		self.tag_dropDown.delegate = self.tag_autocompleter
		self.tag_dropDown.data_source = self.tag_autocompleter

		forward_button = ui.Button(title="->")
		forward_button.action=self.nav_forward

		back_button = ui.Button(title='<-')
		back_button.action=self.nav_back

		home_button=ui.Button(title='H')
		home_button.action=self.open_home

		node_list_button=ui.Button(title='L')
		node_list_button.action = self.node_list

		open_link_button=ui.Button(title=">")
		open_link_button.action = self.open_link

		new_node_button = ui.Button(title=';')
		new_node_button.action = self.new_node

		metadata_button = ui.Button(title='M')
		metadata_button.action = self.metadata_list

		delete_node_button = ui.Button(title='X')
		delete_node_button.action = self.delete_node

		save_button = ui.Button(title='S')
		save_button.action = self.manual_save

		new_inline_node_button = ui.Button(title='{{')
		new_inline_node_button.action = self.new_inline_node
		
		single_line_new_inline_node_button = ui.Button(title='{_')
		single_line_new_inline_node_button.action = self.new_inline_node_single

		tag_from_other_button = ui.Button(title='D')
		tag_from_other_button.action = self.tag_from_other

		insert_tag_button = ui.Button(title='/--')
		insert_tag_button.action = self.tag_autocomplete

		search_button = ui.Button(title='??')
		search_button.action = self.search

		timestamp_button = ui.Button(title='<>')
		timestamp_button.action = self.timestamp

		take_over_button = ui.Button(title='!')
		take_over_button.action = self.take_over

		compact_node_button = ui.Button(title='^')
		compact_node_button.action = self.compact_node

		snt = ui.Button(title='?')
		snt.action = self.search_node_title

		timeline_button = ui.Button(title='::')
		timeline_button.action = self.show_timeline

		insert_split_button = ui.Button(title='%')
		insert_split_button.action = self.insert_split

		buttons = [ 
			open_link_button,
			save_button,
			home_button,
			new_node_button,
			compact_node_button,
			insert_tag_button,
			snt,                   
			single_line_new_inline_node_button,
			back_button,
			forward_button,
			timestamp_button,
			search_button,
			insert_split_button,
			node_list_button,
			new_inline_node_button,
			delete_node_button,
			tag_from_other_button,
			metadata_button,
			take_over_button,
			timeline_button
			]

		button_line = ui.ScrollView()
		button_line.height = 36
		button_line.width = w
		button_line.content_size = (len(buttons) * 32, 32)
		button_line.x=0
		button_line.y=20

		button_x_position = 0
		button_y_position = 0

		self.scroll_view.add_subview(self.text_view)    
		self.add_subview(self.scroll_view)
		self.add_subview(button_line)
		self.add_subview(self.full_txt_search_field)
		self.add_subview(self.dropDown)
		self.add_subview(self.search_field)
		self.add_subview(self.tag_dropDown)
		self.add_subview(self.tag_search_field)

		"""
		Size the buttons
		"""

		for button in buttons:
			button.corner_radius = 5
			button.frame = (button_x_position, 
				button_y_position, 
				button_x_position + button_width, 
				button_y_position + button_height)
			button_line.add_subview(button)
			button_x_position += button_width
			button.size_to_fit()
			button.border_width=1
	
	def manual_save(self, sender):
		self.save(None)
		console.hud_alert('Saved','success',0.5)

	def size_field(self, field):
		field.height = 40
		field.width = self.text_view.width*.80
		field.x = self.text_view.width/2 - field.width/2
		field.y = self.text_view.height/3 - field.height/2
		field.border_width = 1

	def save(self, sender):
		contents = self.text_view.text 
		if self.current_open_file:
			with open(os.path.join(self._UrtextProject.path, self.current_open_file),'w', encoding='utf-8') as d:
				d.write(contents)
				d.close()
			self._UrtextProject.on_modified(self.current_open_file)
			
	def open_file(self, filename, save_first=True):
		if save_first and self.current_open_file:
			self.save(None)
		file = os.path.join(self._UrtextProject.path, filename)
		with open(file,'r', encoding='utf-8') as d:
			contents=d.read() 
			d.close()
		self.text_view.text=contents
		self.current_open_file = file
		self.text_view.begin_editing()


	def timestamp(self, sender):

		now = datetime.datetime.now()
		datestamp = self._UrtextProject.timestamp(now)
		self.text_view.replace_range(
			self.text_view.selected_range, 
			datestamp)

	def open_link(self, sender):
				
		file_position = self.text_view.selected_range[0] 
		line, line_position = get_full_line(file_position, self.text_view)
		link = self._UrtextProject.get_link(line, position=line_position)
		if link:
			if link[0] == 'NODE':
				print('opening '+link[1])
				self.open_node(link[1])
				self._UrtextProject.nav_new(link[1])
				
				# HTTP links not yet handled in Pythonista

	def open_home(self, sender):
		if 'home' not in self._UrtextProject.settings:
			return
		home_id = self._UrtextProject.settings['home']      
		if home_id not in self._UrtextProject.nodes:
			return
		self._UrtextProject.nav_new(home_id)
		self.open_node(home_id)

	def new_inline_node(self, sender):
		metadata={ 'tags': '',
				   'from': 'iPhone'}
		selection = self.text_view.selected_range
		contents = self.text_view.text[selection[0]:selection[1]]
		new_inline_node_contents = self._UrtextProject.add_inline_node(
				date=datetime.datetime.now(),
				contents=contents,
				metadata=metadata)
		self.text_view.replace_range(selection, new_inline_node_contents)
		self.text_view.selected_range = (selection[0]+3, selection[0]+3)

	def new_inline_node_single(self, sender):
		metadata={ 'tags': '',
				   'from': 'iPhone'}
		selection = self.text_view.selected_range
		contents = self.text_view.text[selection[0]:selection[1]]
		new_inline_node_contents = self._UrtextProject.add_inline_node(
				contents=contents,
				metadata=metadata,
				one_line=True)
		self.text_view.replace_range(selection, new_inline_node_contents)
		self.text_view.selected_range = (selection[0]+3, selection[0]+3)

	def open_node(self, node_id):
		filename=self._UrtextProject.nodes[node_id].filename
		self.open_file(filename)

		self._UrtextProject.nav_new(node_id)
		
		#
		# attempt to scroll to position (work in progress)
		# this does not work at all 
		#
	
		"""position = self._UrtextProject.nodes[node_id].ranges[0][0]
		contents = self.text_view.text
		contents_until_position = contents[:position]
		total_view_lines = self.view_lines(contents)
		scroll_past_lines = self.view_lines(contents_until_position)		
		percent_to_scroll = scroll_past_lines / total_view_lines
		
		print('TOTAL LINES')
		print(total_view_lines)

		print('SCROLL PAST')
		print(scroll_past_lines)

		print('PERCENT TO SCROLL IS')
		print(percent_to_scroll)

		# this feature of Pythonista apparently just does not work.
		self.scroll_view.content_offset = (0, self.text_view.height * percent_to_scroll) 
		self.text_view.selected_range = (position, position)"""

	def view_lines(self,content):
		# approximate numbers from the view
		view_width = self.text_view.width
		font_height = self.text_view.font[1]
		font_width = font_height * .5 # aproximation only
		approx_chars_per_line = view_width / font_width
		lines = content.split('\n')
		view_lines = 0
		for line in lines:
			this_line = math.ceil(len(line) / approx_chars_per_line)
			view_lines += this_line

		return view_lines

	def new_node(self, sender):        
		new_node = self._UrtextProject.new_file_node(
			date=datetime.datetime.now(),
			metadata={ 'tags': '',
						'from': 'iPhone'}
			)
		self.open_file(new_node['filename'])
		self._UrtextProject.nav_new(new_node['id'])
		self.text_view.selected_range = (0,0)
		self.text_view.begin_editing()

	def tag_from_other(self, sender):
		position = self.text_view.selected_range[0]
		line = self.text_view.text[position:position+250]
		link = self._UrtextProject.get_link(line)
		if link and link[0] == 'NODE':
			updating_thread = self._UrtextProject.tag_other_node(link[1], 
				'/-- tags: done --/')
			waiting_thread = threading.Thread(
				target=self.reload_file,
				args=(updating_thread,))
			waiting_thread.start()
			
	def reload_file(self, updating_thread):
		updating_thread.join()
		with open(self.current_open_file,'r', encoding='utf-8') as d:
			contents=d.read() 
			d.close()
		if contents != self.text_view.text:
			self.open_file(self.current_open_file, save_first=False)

	def node_list(self, sender):
		self.open_node('zzz')

	def metadata_list(self, sender):
		self.open_node('zzy')

	def search_project(self, sender):
		string = self.full_txt_search_field.text
		self.full_txt_search_field.hidden = True
		results = self._UrtextProject.search(string)
		self.save(None)
		self.text_view.text = results
		self.current_open_file = None # make sure this view doesn't overwrite another

	def search(self, sender):
		self.full_txt_search_field.text = ''
		self.full_txt_search_field.hidden = False
		self.full_txt_search_field.action = self.search_project
		self.full_txt_search_field.begin_editing()

	def search_node_title(self, sender):
		self.search_field.hidden = False
		self.search_field.text=''
		self.dropDown.x = self.search_field.x
		self.dropDown.y = self.search_field.y + self.search_field.height
		self.dropDown.width = self.search_field.width
		self.dropDown.row_height = self.search_field.height
		self.search_field.begin_editing()

	def tag_autocomplete(self, sender):
		self.tag_search_field.hidden = False
		self.tag_search_field.text = ''
		self.tag_dropDown.x = self.tag_search_field.x
		self.tag_dropDown.y = self.tag_search_field.y + self.tag_search_field.height
		self.tag_dropDown.width = self.tag_search_field.width
		self.tag_dropDown.row_height = self.tag_search_field.height
		
		self.tag_search_field.begin_editing() 

	def nav_back(self, sender):

		last_node = self._UrtextProject.nav_reverse()
		if last_node:     
			self.open_node(last_node)

	def nav_forward(self, sender):

		next_node = self._UrtextProject.nav_advance()
		if next_node:
			self.open_node(next_node)

	def delete_node(self, sender):
		os.remove(os.path.join(self._UrtextProject.path, self.current_open_file))
		self._UrtextProject.remove_file(self.current_open_file)
		self.current_open_file = None
		self._UrtextProject.update()
		self.nav_back(None)
		console.hud_alert('Deleted','success',0.5)
	
	def take_over(self, sender):
		self._UrtextProject.lock()
		self._UrtextProject.paused = False
		
	def compact_node(self, sender):
		selection = self.text_view.selected_range
		contents = self.text_view.text[selection[0]:selection[1]]   
		insert_text = self._UrtextProject.add_compact_node(contents=contents)           
		self.text_view.replace_range(selection, insert_text)
		offset = len(contents) + 2
		self.text_view.selected_range = (selection[0] + offset, selection[0]+offset)

	def hide_keyboard(self,sender):
		self.end_editing()

	def show_timeline(self, sender):
		if self.current_open_file:
			self.save(None)
		nodes = [self._UrtextProject.nodes[node_id] for node_id in self._UrtextProject.nodes]
		timeline = self._UrtextProject.build_timeline(nodes)
		self.text_view.text = timeline
		self.current_open_file = None

	def insert_split(self, sender):
		node_id = self._UrtextProject.next_index()
		selection = self.text_view.selected_range
		self.text_view.replace_range(selection, '/-- id: '+node_id+' --/\n% ')

def get_full_line(position, text_view):
	lines = text_view.text.split('\n')
	total_length = 0
	for line in lines:
		total_length += len(line) + 1
		if total_length >= position:
			distance_from_end_of_line = total_length - position
			position_in_line = len(line) - distance_from_end_of_line
			return (line, position_in_line)

"""
Start the app
"""
if __name__ == '__main__':
	app = AppSingleLaunch("Pythonisa Urtext")
	if not app.is_active():
		main_view = MainView(app)
		app.will_present(main_view)         		
		main_view.open_home(None)
		main_view.present(hide_title_bar=True)
		# remnant from the watchdog, currently keeps global variables from being cleared.
		# see this thread for other solutions: https://forum.omz-software.com/topic/5440/prevent-duplicate-launch-from-shortcut/8
		while True:
			time.sleep(.1)
		

