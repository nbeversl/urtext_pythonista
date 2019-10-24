from urtext.project import UrtextProject
import time
import os
import datetime
import ui
import dialogs
import re
import math
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from app_single_launch import AppSingleLaunch

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
		options = [ x for x in self.titles.keys() if len(x) >= length and x[:length].lower() == entry]

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
		tag_search_field.text = ''
		tag_dropDown.hidden = True
		tag_search_field.hidden = True
		self.items = []
		

	def optionWasSelected(self, sender):
		search_field.text = self.items[self.selected_row]
		tag = self.items[self.selected_row]
		insert = '/-- tags: '+tag+' --/'
		main_view.text_view.replace_range(main_view.text_view.selected_range, insert)
		tag_search_field.end_editing()
		
class MainView(ui.View):

	def __init__(self, app: AppSingleLaunch):
		
		self.app = app
		self.name = "Pythonista Urtext" 
		self._UrtextProject = UrtextWatcher(
			urtext_project_path, 
			machine_lock=machine_name)
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
		save_button.action = self.save

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

		hide_kb = ui.Button(title='hide')
		hide_kb.action = self.hide_keyboard

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
			node_list_button,
			new_inline_node_button,
			delete_node_button,
			tag_from_other_button,
			metadata_button,
			take_over_button,
			compact_node_button,
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
				
		position = self.text_view.selected_range[0] 
		
		line = get_forward_line(position, self.text_view)
		link = self._UrtextProject.project.get_link(line)
		if not link:
			line = get_backward_line(position, self.text_view)
			link = self._UrtextProject.project.get_link(line)
		if link:
			if link[0] == 'NODE':
				print('opening '+link[1])
				self.open_node(link[1])
				self._UrtextProject.project.nav_new(link[1])
				
				# HTTP links not yet handled in Pythonista

	def open_home(self, sender):
		home_id = self._UrtextProject.project.settings['home']      
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
		time.sleep(.5)
		position = self._UrtextProject.project.nodes[node_id].ranges[0][0]
		self._UrtextProject.project.nav_new(node_id)
		view_width = self.text_view.width
		font_height = self.text_view.font[1]
		font_width = font_height * .35 # aproximation only
		approx_chars_per_line = view_width / font_width

		contents = self.text_view.text
		contents_until_position = contents[:position]
		lines_to_scroll_past = contents_until_position.split('\n')
		num_lines_to_scroll = 0
		for line in lines_to_scroll_past:
			view_lines = math.ceil(len(line) / approx_chars_per_line)
			num_lines_to_scroll += view_lines

		self.text_view.content_offset = (0, view_lines * font_height ) 
		self.text_view.selected_range = (position, position)

		# this value just needs to be refined or better approximated

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
		self._UrtextProject.project.lock(machine_name)

	def compact_node(self, sender):
		selection = self.text_view.selected_range
		contents = self.text_view.text[selection[0]:selection[1]]   
		insert_text = self._UrtextProject.project.add_compact_node(contents=contents)           
		self.text_view.replace_range(selection, insert_text)
		offset = len(contents) + 2
		self.text_view.selected_range = (selection[0] + offset, selection[0]+offset)

	def hide_keyboard(self,sender):
		main_view.end_editing()

class UrtextWatcher(FileSystemEventHandler):

	def __init__(self, urtext_project_path, machine_lock=None):
		super().__init__()
		self.project = UrtextProject(urtext_project_path)
		if machine_lock:
			self.project.lock(machine_name)

	def on_created(self, event):
		if not self.project.check_lock(machine_name):
			return
		if event.is_directory:
			return None

		filename = os.path.basename(event.src_path)
		if self.project.parse_file(filename, re_index=True) == None:
		  self.project.log_item(filename + ' not added.')
		  return
		self.project.log_item(filename + ' CREATED/modified. Updating the project object')
		self.project.update()

	def on_modified(self, event):
	
		
		# if filename == self.current_open_file:
		#   reload_file = dialog.list_dialog(
		#       title=filename+' has changed',
		#       items = [ 'Reload','Keep Working'])
		#   if reload_file == 'Reload':
		#       open_file(filename, save_first=False)

		filename = os.path.basename(event.src_path)
		

		if not self.project.check_lock(machine_name):
			return
		
		if event.is_directory:
			return None
		
		if self.filter(filename) == None:
		  return        
		do_not_update = [
		   'index', 
		   os.path.basename(os.path.dirname(self.project.path)),
		   self.project.nodes['zzz'].filename,
		   self.project.nodes['zzy'].filename,
		   self.project.settings['logfile'],
		   '00000.txt'
		  ]
		if filename in do_not_update or '.git' in filename:
		  return

		self.project.log_item('MODIFIED ' + filename +' - Updating the project object')
		self.project.parse_file(filename, re_index=True)
		self.project.update()

	def on_deleted(self, event):
		if not self.project.check_lock('THIS MACHINE'):
		  return

		filename = os.path.basename(event.src_path)
		self.project.log.info(filename + ' DELETED')
		if filename in self.project.files:
		  self.project.remove_file(filename)

	def on_moved(self, event):
		if not self.project.check_lock('THIS MACHINE'):
		  return
		if self.filter(event.src_path) == None:
		  return
		old_filename = os.path.basename(event.src_path)
		new_filename = os.path.basename(event.dest_path)
		if old_filename in self.project.files:
			self.project.log_item('RENAMED'+ old_filename +' to ' + new_filename)
			self.project.handle_renamed(old_filename, new_filename)
	
	def filter(self, filename):
		for fragment in ['urtext_log', '.git','.icloud']:
			if fragment in filename:
				return None
		return filename
 
def get_forward_line(position, text_view):
	forward = position +1		
	length = len(text_view)
	while '\n' not in text_view.text[position:forward]:
		forward += 1
		if forward == length:
			break
	return text_view.text[position:forward]

def get_backward_line(position, text_view):
	backward = position - 1
	while '\n' not in text_view.text[backward:position]:
		backward -= 1
		if backward == 0:
			break
	return text_view.text[backward:position]




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
