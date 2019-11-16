from urtext.project import UrtextProject
import time
import os
import datetime
import ui
import dialogs
import re
import math
import console
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from app_single_launch import AppSingleLaunch

from fuzzywuzzy import fuzz


urtext_project_path = '/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/archive'
node_id_regex = r'\b[0-9,a-z]{3}\b'
command = ''
machine_name = 'Nate\'s iPhone'

print ('Urtext is loading '+urtext_project_path)

# https://stackoverflow.com/questions/49349033/create-auto-complete-textfield-in-pythonista-3

class AutoCompleter(ui.ListDataSource):
	
	def textfield_did_change(self, textfield):
		
		dropDown.hidden = False
		# an arbitrary list of autocomplete options
		length = len(textfield.text)
		entry = textfield.text.lower()
		self.titles = main_view._UrtextProject.project.titles()


		titles_keys = self.titles.keys()

		options = sorted(
			titles_keys, 
			key=lambda title: fuzz.ratio(entry, title), 
			reverse=True)

		# setting the items property automatically updates the list
		self.items = options

		# size the dropdown for up to five options
		dropDown.height = min(dropDown.row_height * len(options), 5*dropDown.row_height)

	def textfield_did_end_editing(self, textfield):
		#done editing, so hide and clear the dropdown
		dropDown.hidden = True
		search_field.hidden = True
		self.items = []
		search_field.text = ''

	def optionWasSelected(self, sender):
		search_field.text = self.items[self.selected_row]
		main_view.open_node(self.titles[self.items[self.selected_row]])
		search_field.end_editing()

class TaggingAutoCompleter(ui.ListDataSource):
	
	def textfield_did_change(self, textfield):
		
		tag_dropDown.hidden = False
		# an arbitrary list of autocomplete options
		length = len(textfield.text)
		entry = textfield.text.lower()
		self.tags = main_view._UrtextProject.project.tagnames['tags']
		options = [ x for x in self.tags.keys() if len(x) >= length and x[:length].lower() == entry]

		# setting the items property automatically updates the list
		self.items = options

		# size the dropdown for up to five options
		tag_dropDown.height = min(tag_dropDown.row_height * len(options), 5*tag_dropDown.row_height)

	def textfield_did_end_editing(self, textfield):
		#done editing, so hide and clear the dropdown
		if tag_search_field.text:

			insert = '/-- tags: '+tag_search_field.text+' --/'
			main_view.text_view.replace_range(main_view.text_view.selected_range, insert)
		tag_dropDown.hidden = True
		tag_search_field.hidden = True
		tag_search_field.text=''
		self.items = []
		
	def optionWasSelected(self, sender):
		tag_search_field.text = self.items[self.selected_row]       
		tag_search_field.end_editing()
		
class MainView(ui.View):

	def __init__(self, app: AppSingleLaunch):
		
		self.app = app
		self.name = "Pythonista Urtext" 
		self._UrtextProject = UrtextWatcher(urtext_project_path)
		self.current_open_file = None

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
			compact_node_button,
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
		console.hud_alert('Saved')


	def save(self, sender):
		self.current_open_file
		contents = self.text_view.text 
		if self.current_open_file:
			with open(os.path.join(self._UrtextProject.project.path, self.current_open_file),'w', encoding='utf-8') as d:
				d.write(contents)
				d.close()
		
	def open_file(self, filename, save_first=True):
		if save_first and self.current_open_file:
			self.save(None)
		file = os.path.join(self._UrtextProject.project.path, filename)
		with open(file,'r', encoding='utf-8') as d:
			contents=d.read() 
			d.close()
		self.text_view.text=contents
		self.current_open_file = file

	def timestamp(self, sender):

		now = datetime.datetime.now()
		datestamp = self._UrtextProject.project.timestamp(now)
		self.text_view.replace_range(
			self.text_view.selected_range, 
			datestamp)

	def open_link(self, sender):
				
		file_position = self.text_view.selected_range[0] 
		line, line_position = get_full_line(file_position, self.text_view)
		link = self._UrtextProject.project.get_link(line, position=line_position)
		if link:
			if link[0] == 'NODE':
				print('opening '+link[1])
				self.open_node(link[1])
				self._UrtextProject.project.nav_new(link[1])
				
				# HTTP links not yet handled in Pythonista

	def open_home(self, sender):
		if 'home' not in self._UrtextProject.project.settings:
			return
		home_id = self._UrtextProject.project.settings['home']      
		if home_id not in self._UrtextProject.project.nodes:
			return
		self._UrtextProject.project.nav_new(home_id)
		self.open_node(home_id)

	def new_inline_node(self, sender):
		metadata={ 'tags': '',
				   'from': 'iPhone'}
		selection = self.text_view.selected_range
		contents = self.text_view.text[selection[0]:selection[1]]
		new_inline_node_contents = self._UrtextProject.project.add_inline_node(
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
		new_inline_node_contents = self._UrtextProject.project.add_inline_node(
				contents=contents,
				metadata=metadata,
				one_line=True)
		self.text_view.replace_range(selection, new_inline_node_contents)
		self.text_view.selected_range = (selection[0]+3, selection[0]+3)

	def open_node(self, node_id):
		filename=self._UrtextProject.project.nodes[node_id].filename
		self.open_file(filename)
		self._UrtextProject.project.nav_new(node_id)
		
		#
		# attempt to scroll to position (work in progress)
		# this does not work at all 
		#
	
		"""position = self._UrtextProject.project.nodes[node_id].ranges[0][0]
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
		new_node = self._UrtextProject.project.new_file_node(
			date=datetime.datetime.now(),
			metadata={ 'tags': '',
						'from': 'iPhone'}
			)
		self.open_file(new_node['filename'])
		self._UrtextProject.project.nav_new(new_node['id'])
		self.text_view.selected_range = (0,0)

	def tag_from_other(self, sender):
		self.current_open_file
		position = self.text_view.selected_range[0]
		line = self.text_view.text[position:position+250]
		link = self._UrtextProject.project.get_link(line)
		if link and link[0] == 'NODE':
			self._UrtextProject.project.tag_other_node(link[1], 
				'/-- tags: done --/')
			self._UrtextProject.project.update()
			self.open_file(self.current_open_file)

	def node_list(self, sender):
		self.open_node('zzz')

	def metadata_list(self, sender):
		self.open_node('zzy')

	def search_project(self, sender):
		string = self.full_txt_search_field.text
		self.full_txt_search_field.hidden = True
		results = self._UrtextProject.project.search(string)
		self.save(None)
		self.text_view.text = results
		self.current_open_file = None # make sure this view doesn't overwrite another

	def search(self, sender):
		self.full_txt_search_field.text = ''
		self.full_txt_search_field.hidden = False
		self.full_txt_search_field.action = self.search_project
		self.full_txt_search_field.begin_editing()

	def search_node_title(self, sender):
		search_field.hidden = False
		search_field.text=''
		dropDown.x = search_field.x
		dropDown.y = search_field.y + search_field.height
		dropDown.width = search_field.width
		dropDown.row_height = search_field.height
		search_field.begin_editing()

	def tag_autocomplete(self, sender):
		tag_search_field.hidden = False
		tag_search_field.text = ''
		tag_dropDown.x = tag_search_field.x
		tag_dropDown.y = tag_search_field.y + tag_search_field.height
		tag_dropDown.width = tag_search_field.width
		tag_dropDown.row_height = tag_search_field.height
		
		tag_search_field.begin_editing() 

	def nav_back(self, sender):

		last_node = self._UrtextProject.project.nav_reverse()
		if last_node:     
			self.open_node(last_node)

	def nav_forward(self, sender):

		next_node = self._UrtextProject.project.nav_advance()
		if next_node:
			self.open_node(next_node)

	def delete_node(self, sender):
		self.current_open_file
		os.remove(os.path.join(self._UrtextProject.project.path, self.current_open_file))
		self._UrtextProject.project.remove_file(self.current_open_file)
		self._UrtextProject.project.update()
		self.nav_back(None)
	
	def take_over(self, sender):
		self._UrtextProject.project.lock()
		self._UrtextProject.paused = False
		
	def compact_node(self, sender):
		selection = self.text_view.selected_range
		contents = self.text_view.text[selection[0]:selection[1]]   
		insert_text = self._UrtextProject.project.add_compact_node(contents=contents)           
		self.text_view.replace_range(selection, insert_text)
		offset = len(contents) + 2
		self.text_view.selected_range = (selection[0] + offset, selection[0]+offset)

	def hide_keyboard(self,sender):
		main_view.end_editing()

	def show_timeline(self, sender):
		if self.current_open_file:
			self.save(None)
		nodes = [self._UrtextProject.project.nodes[node_id] for node_id in self._UrtextProject.project.nodes]
		timeline = self._UrtextProject.project.build_timeline(nodes)
		self.text_view.text = timeline
		self.current_open_file = None

	def insert_split(self, sender):
		node_id = self._UrtextProject.project.next_index()
		selection = self.text_view.selected_range
		self.text_view.replace_range(selection, '/-- id: '+node_id+' --/\n% ')

class UrtextWatcher(FileSystemEventHandler):

	def __init__(self, urtext_project_path):
		super().__init__()
		self.project = UrtextProject(urtext_project_path)
		self.paused = False
	
	def on_created(self, event):
		if self.paused:
			return 
		successful, lock_name = self.project.on_created(event.src_path)
		if not successful:
			self.show_lock(lock_name)

	def on_modified(self, event):
		if self.paused:
			return 
		successful, lock_name = self.project.on_modified(event.src_path)    
		if not successful:
			self.show_lock(lock_name)

	def on_moved(self, event):
		if self.paused:
			return 
		successful, lock_name = self.project.on_moved(event.src_path)   
		if not successful:
			self.show_lock(lock_name)
	
	def show_lock(self, lock_name):
		self.paused = True
		take_over = console.alert('Compile Lock','Urtext watch is locked by '+ lock_name +'.',
			'Take Over', 'Use without watch')

		if take_over == 0:
			self.project.lock()
			self.paused=False
			return True
		return False

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
		observer = Observer()
		observer.schedule(main_view._UrtextProject, path=urtext_project_path, recursive=False)
		observer.start()
		main_view.open_home(None)
		main_view.present(hide_title_bar=True)

		# title search field

		search_field = ui.TextField()
		search_field.height = 40
		search_field.width = main_view.width*.80
		search_field.x = main_view.width/2 - search_field.width/2
		search_field.y = main_view.height/3 - search_field.height/2
		search_field.border_width = 1
		search_field.hidden = True

		dropDown = ui.TableView()
		dropDown.hidden = True

		title_autocompleter = AutoCompleter(items=[])
		title_autocompleter.action = title_autocompleter.optionWasSelected

		search_field.delegate = title_autocompleter
		
		main_view.add_subview(dropDown)
		main_view.add_subview(search_field)

		dropDown.delegate = title_autocompleter
		dropDown.data_source = title_autocompleter

		# repeating all the same for tag search

		tag_search_field = ui.TextField()
		tag_search_field.height = 40
		tag_search_field.width = main_view.width*.80
		tag_search_field.x = main_view.width/2 - search_field.width/2
		tag_search_field.y = main_view.height/3 - search_field.height/2
		tag_search_field.border_width = 1
		tag_search_field.hidden = True

		tag_dropDown = ui.TableView()
		tag_dropDown.hidden = True

		tag_autocompleter = TaggingAutoCompleter(items=[])
		tag_autocompleter.action = tag_autocompleter.optionWasSelected

		tag_search_field.delegate = tag_autocompleter

		main_view.add_subview(tag_dropDown)
		main_view.add_subview(tag_search_field)

		tag_dropDown.delegate = tag_autocompleter
		tag_dropDown.data_source = tag_autocompleter

		while True:
			time.sleep(1)
