from urtext.project_list import ProjectList
import time
import sched
import os
import datetime
import ui
import dialogs
import re
import math
import console
import webbrowser
from app_single_launch import AppSingleLaunch
import concurrent.futures
from fuzzywuzzy import fuzz
from objc_util import *
import syntax
import platform
import clipboard
import queue
import inspect

node_id_regex = r'\b[0-9,a-z]{3}\b'
app = None
main_view = None
WATCHDOG = False

class MainView(ui.View):

	def __init__(self, 
		urtext_project_path,  
		app: AppSingleLaunch,
		import_project=False,
		first_project=None):
		
		self.app = app
		self.name = "Pythonista Urtext" 
		self.urtext_project_path = urtext_project_path
		self._UrtextProjectList = ProjectList(urtext_project_path, 
			import_project=import_project,
			watchdog=WATCHDOG,
			first_project=first_project)
		self.current_open_file = None
		self.current_open_file_hash = None
		self.saved = None
		self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
		self.updating_history = False
		self.refreshing = False

		"""
		Build view components. 
		"""
		button_height = 42
		button_width = 42
		
		w,h = ui.get_screen_size()
		self.height = h
		self.width = w
		self.frame= (0,0,w,h)

		# main text (editor) view
		self.tv=ui.TextView()
		self.tv.frame=(0,18,w,h)
		self.tv.auto_content_inset = True
		self.tv.background_color = '#e5dddc' # old '#282923'
	
		# Title autocompleter
		self.title_autocompleter = TitleAutoCompleter(items=[])
		self.title_dropDown = ui.TableView()
		self.title_dropDown.hidden = True
		self.title_dropDown.delegate = self.title_autocompleter
		self.title_dropDown.data_source = self.title_autocompleter		
		self.title_search = ui.TextField()
		self.title_search.delegate = self.title_autocompleter
		self.add_subview(self.title_dropDown)
		self.add_subview(self.title_search)
		self.size_field(self.title_search)

		# Metadata autocompleter
		self.meta_autocompleter = MetaAutoCompleter(items=[])
		self.meta_dropDown = ui.TableView()
		self.meta_dropDown.hidden = True
		self.meta_dropDown.delegate = self.meta_autocompleter
		self.meta_dropDown.data_source = self.meta_autocompleter	
		self.meta_search = ui.TextField()
		self.meta_search.delegate = self.title_autocompleter
		self.add_subview(self.meta_dropDown)
		self.add_subview(self.meta_search)
		self.size_field(self.meta_search)
		
		# UI List of projects
		self.textfield=ui.TextField()
		self.textfield.hidden=True
		self.project_list = ui.ListDataSource(items=[]) 
		self.project_selector = ui.TableView()
		self.project_selector.hidden = False 
		self.project_selector.delegate = self.project_list
		self.project_selector.data_source = self.project_list

		# Keyword autocompleter
		self.keyword_autocompleter = KeywordAutoCompleter(items=[])
		self.keyword_dropDown = ui.TableView()
		self.keyword_dropDown.hidden = True
		self.keyword_dropDown.delegate = self.keyword_autocompleter
		self.keyword_dropDown.data_source = self.keyword_autocompleter	
		self.keyword_search = ui.TextField()
		self.keyword_search.delegate = self.keyword_autocompleter
		self.add_subview(self.keyword_dropDown)
		self.add_subview(self.keyword_search)
		self.size_field(self.keyword_search)

		# History:
		self.current_file_history = None 
		self.history_stamps = ui.ListDataSource(items=[])
		self.history_view = ui.TableView()
		self.history_view.hidden = True
		history_viewer = HistoryView()
		self.history_view.delegate = history_viewer
		self.history_view.data_source = self.history_stamps

		# Pop Up Urtext Features Menu
		menu_options = ui.ListDataSource(items=[
			'Initialize New Project',  
			'Move file to another project',
			'Reload Projects',
			'Switch Projects',          
			'Delete Node',
			'Show Project Timeline',          
			'Link >',
			'Point >>',
			'Pop Node',
			'Project Log',
		   ])
		menu_options.action = self.delegate_menu

		self.menu_list = ui.TableView()
		self.menu_list.hidden = True
		self.menu_list.delegate = menu_options
		self.menu_list.data_source = menu_options
		self.menu_list.height = 160
		self.menu_list.width = self.tv.width*.80
		self.menu_list.x = self.tv.width/2 - self.menu_list.width/2
		self.menu_list.y = self.tv.height/3 - self.menu_list.height/2
		self.menu_list.border_width = 1

		self.tv.width = w
		
		"""
		Buttons 
		"""
		menu_button = ui.Button(title="M")
		menu_button.action = self.show_menu
		
		switch_project_button = ui.Button(title="o")
		switch_project_button.action = self.select_project

		forward_button = ui.Button(title=">")
		forward_button.action=self.nav_forward

		back_button = ui.Button(title='<')
		back_button.action=self.nav_back

		home_button=ui.Button(title='h')
		home_button.action=self.open_home

		open_link_button=ui.Button(title="/")
		open_link_button.action = self.open_link

		new_node_button = ui.Button(title=';')
		new_node_button.action = self.new_node

		save_button = ui.Button(title='S')
		save_button.action = self.manual_save

		new_inline_node_button = ui.Button(title='{')
		new_inline_node_button.action = self.new_inline_node
		
		tag_from_other_button = ui.Button(title='D')
		tag_from_other_button.action = self.tag_from_other

		insert_tag_button = ui.Button(title='::')
		insert_tag_button.action = self.meta_autocomplete

		timestamp_button = ui.Button(title='t')
		timestamp_button.action = self.timestamp

		manual_timestamp_button = ui.Button(title='<..>')
		manual_timestamp_button.action = self.manual_timestamp

		compact_node_button = ui.Button(title='•')
		compact_node_button.action = self.compact_node

		search_by_title = ui.Button(title='?')
		search_by_title.action = self.search_node_title

		insert_dynamic_def_button = ui.Button(title='[')
		insert_dynamic_def_button.action = self.insert_dynamic_def

		insert_id_button = ui.Button(title='@')
		insert_id_button.action = self.insert_id

		insert_pipe_button = ui.Button(title='|')
		insert_pipe_button.action = self.insert_pipe

		insert_backtick_button = ui.Button(title='`')
		insert_backtick_button.action = self.insert_backtick

		search_all_project = ui.Button(title='*')
		search_all_project.action = self.search_all_project

		browse_history_button = ui.Button(title='g')
		browse_history_button.action = self.browse_history

		copy_link_to_current_node_button = ui.Button(title='c')
		copy_link_to_current_node_button.action = self.copy_link_to_current_node

		copy_link_to_current_node_with_project_button = ui.Button(title='^c')
		copy_link_to_current_node_with_project_button.action = self.copy_link_to_current_node_with_project

		hide_keyboard_button = ui.Button(title='↓')
		hide_keyboard_button.action = self.hide_keyboard

		keywords_button = ui.Button(title='k')
		keywords_button.action=self.search_keywords

		buttons = [ 
			open_link_button,
			search_by_title,
			new_node_button, 
			insert_tag_button,
			back_button,
			menu_button,
			save_button,
			home_button,
			compact_node_button,            
			forward_button,
			timestamp_button,
			manual_timestamp_button,
			browse_history_button,
			new_inline_node_button,
			copy_link_to_current_node_button,
			copy_link_to_current_node_with_project_button,
			switch_project_button,
			tag_from_other_button,
			insert_dynamic_def_button,
			insert_id_button,
			insert_pipe_button,
			insert_backtick_button,
			search_all_project,
			hide_keyboard_button,
			keywords_button
			]

		button_line = ui.ScrollView()
		button_line.height = 36
		button_line.width = w
		button_line.content_size = (len(buttons) * 42, 32)
		button_line.x=0
		button_line.y=20
		button_line.background_color = '#282923'
		button_x_position = 0
		button_y_position = 0

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

		# Set up the button row as input accessory
		self.add_subview(self.tv)
		self.add_subview(button_line)
		self.add_subview(self.menu_list)
		self.add_subview(self.history_view)
		self.add_subview(self.textfield)   

		self.tvo = ObjCInstance(self.tv)
		btn_ln = ObjCInstance(button_line)
		self.tvo.setInputAccessoryView_(btn_ln)
		self.tv.delegate = SyntaxHighlighter(self.tvo)
		self.tvo.setAllowsEditingTextAttributes_(True)
			  

	def browse_history(self, sender):
		self.take_snapshot()
		self.current_file_history = self._UrtextProjectList.current_project.get_history(self.current_open_file)
		if not self.current_file_history:
			return None
		ts_format = self._UrtextProjectList.current_project.settings['timestamp_format']
		string_timestamps = [
			datetime.datetime.fromtimestamp(
				int(i)).strftime(ts_format) for i in sorted(
					self.current_file_history.keys(), reverse=True
					)]
		self.history_stamps.items = string_timestamps
		self.tv.end_editing()
		self.size_field(self.history_view)
		self.history_view.height = 160     # 4 cels high
		self.history_view.hidden = False
		self.history_view.bring_to_front()
	
	def hide_keyboard(self, sender):
		self.tv.end_editing()

	def take_snapshot(self):
		if self.current_open_file:
			self._UrtextProjectList.current_project.snapshot_diff(self.current_open_file, self.tv.text)

	def search_all_project(self, sender):
		self.title_autocompleter.action = self.title_autocompleter.open_node
		self.title_autocompleter.titles = self._UrtextProjectList.titles()
		self.show_search_and_dropdown(self.title_search, self.title_dropDown)

	def insert_dynamic_def(self,sender):
		node_id = self.new_inline_node(None, locate_inside=False)
		position = self.tv.selected_range[0]
		self.tv.replace_range(self.tv.selected_range, '\n\n[[ ID(>' + node_id + ')\n+( ) +( )\n-( ) -( )\n ]]')
		self.tv.selected_range = (position + 12, position + 12)
		
	def insert_pipe(self, sender):
		self.tv.replace_range(self.tv.selected_range, '|')

	def insert_backtick(self, sender):
		self.tv.replace_range(self.tv.selected_range, '`')
	
	def pop_node(self, sender):
		
		self.save(None)
		filename = self.current_open_file
		position = self.tv.selected_range[0]
		future = self._UrtextProjectList.current_project.pop_node(filename=filename, position=position)
		if future:
			self.executor.submit(self.refresh_open_file_if_modified, future)

	def insert_id(self, sender):
		new_id = self._UrtextProjectList.current_project.next_index()
		self.tv.replace_range(self.tv.selected_range, 'id::'+new_id+'; ')

	def move_file(self, sender):
		self.project_list.items = self._UrtextProjectList.project_titles()
		self.project_list.action = self.execute_move_file
		self.project_selector.height = 35*len(self.project_list.items)
		self.project_selector.hidden = False
		self.project_selector.bring_to_front()
		
	def manual_timestamp(self, sender):
		position = self.tv.selected_range[0]
		self.tv.replace_range(
			self.tv.selected_range, 
			'<>')
		self.tv.selected_range = (position+1,position+1)

	def execute_move_file(self, sender):
		self.project_selector.hidden = True    
		selection = sender.selected_row
		selected_project = self.project_list.items[selection]
		if self._UrtextProjectList.move_file(self.current_open_file, selected_project):
			self.current_open_file = None
			self.nav_back(None)
			console.hud_alert('File Moved' ,'success',2)
		else:
			console.hud_alert('Error happened. Check the Urtext console' ,'error',2)

	def reload_projects(self, sender):
		self.close()
		self._UrtextProjectList = ProjectList(
			self.urtext_project_path, 
			watchdog=WATCHDOG)
		self.present('fullscreen', hide_title_bar=True)
		self.open_home(None)
		
		console.hud_alert('Project List Reloaded' ,'success',1)

	def init_new_project(self, sender):
		self.textfield.hidden=True 
		new_project_path = sender.text
		path = os.path.join(self._UrtextProjectList.base_path, new_project_path)
		self._UrtextProjectList.init_new_project(path)

	def delegate_menu(self, sender):
		self.menu_list.hidden=True
		
		"""
			0  'Initialize New Project', 
			1 'Move file to another project',her project',
			2 'Reload Projects',
			3 'Switch Projects',          
			4 'Delete Node',
			5 'Show Project Timeline',        
			6 'Link >',
			7 'Point >>',
			8 'Pop Node',
			9 'Project Log'
		"""

		if sender.selected_row == 0: # Initialize new project
			self.textfield.action=self.init_new_project
			self.textfield.bring_to_front()
			self.textfield.hidden=False 

		if sender.selected_row == 1:
			self.move_file(None)

		if sender.selected_row == 2:
			self.reload_projects(None)

		if sender.selected_row == 3:
			self.select_project(None)

		if sender.selected_row == 4: 
			self.delete_node(None)

		if sender.selected_row == 5:
			self.show_timeline(None)

		if sender.selected_row == 6:
			self.link_to_node(None)

		if sender.selected_row == 7:
			self.point_to_node(None)

		if sender.selected_row == 8:
			self.pop_node(None)

		if sender.selected_row == 9:
			self.load_log(None)

	def load_log(self, sender):
		log_node = self._UrtextProjectList.current_project.get_log_node()
		if log_node:
			self.open_node(log_node)

	def show_menu(self, option_list):
		self.menu_list.hidden=False
		self.menu_list.bring_to_front()

	def select_project(self, sender): 
	  
		self.tv.end_editing()
		self.project_list.items = self._UrtextProjectList.project_titles()
		self.size_field(self.project_selector)
		self.project_selector.height = 40*len(self.project_list.items)
		
		self.project_selector.hidden = False
		self.project_selector.bring_to_front()
		self.project_list.action = self.switch_project

	def switch_project(self, sender):
	  
		selection = sender.selected_row
		self.tv.begin_editing()
		self._UrtextProjectList.set_current_project(self.project_list.items[selection])
		self.project_selector.hidden = True
		node_to_open = self._UrtextProjectList.nav_current()
		if node_to_open:
			return self.open_node(node_to_open)
		console.hud_alert('Project switched, but no navigation position available' ,'success',3)

	def manual_save(self, sender):
		self.save(None)
		console.hud_alert('Saved','success',0.5)

	def size_field(self, field):
		field.height = 40
		field.width = self.tv.width*.80
		field.x = self.tv.width/2 - field.width/2
		field.y = self.tv.height/3 - field.height/2
		field.border_width = 1

	def save(self, sender):
		if self.saved:
			return
		if self.current_open_file:
			contents = self.tv.text 
			with open(os.path.join(self._UrtextProjectList.current_project.path, self.current_open_file),'w', encoding='utf-8') as d:
				d.write(contents)
			self.current_open_file_hash = hash(contents)
			result = self._UrtextProjectList.current_project.on_modified(self.current_open_file)
			if self._UrtextProjectList.current_project.is_async:
				self.executor.submit(self.refresh_open_file_if_modified, result)
			else:
				self._UrtextProjectList.current_project.on_modified(result)
			self.saved = True
	
	def refresh_open_file_if_modified(self, future):
		s = future.result()
		renamed_file = os.path.basename(s)
		"""print(renamed_file)
		print(self.current_open_file)
		if renamed_file != self.current_open_file:
			console.hud_alert('File renamed, reopened','success',1)
			self.open_file(renamed_file)"""
		self.open_file(self.current_open_file)
		
	def refresh_file(self, text=''):   
		position = self.tv.selected_range
		self.tv.scroll_enabled= False     
		syntax.setAttribs(self.tv, self.tvo)
		self.tv.scroll_enabled= True

	def open_file(self, filename, save_first=True):
		"""
		Receives a basename.
		Path used is always the path of the current project
		"""
		f = os.path.join(self._UrtextProjectList.current_project.path, filename)
		if not os.path.exists(f):
			console.hud_alert('FILE not found. Synced?','error',1)
			return None
			
		with open(f,'r', encoding='utf-8') as d:
			contents=d.read()

		if filename == self.current_open_file and hash(contents) == self.current_open_file_hash:
			return False

		if save_first and self.current_open_file != filename:
			self.save(None)

		# if self.current_open_file == filename:
		#  	self.tv.scroll_enabled = False
		selected_range = self.tvo.selectedRange()
		self.current_open_file = filename
		self.current_open_file_hash = hash(contents)
		self.tv.text=contents
		self.tvo.scrollRangeToVisible(selected_range) 
		syntax.setAttribs(self.tv, self.tvo)
		return True

	def timestamp(self, sender):

		now = datetime.datetime.now()
		datestamp = self._UrtextProjectList.current_project.timestamp(now)
		self.tv.replace_range(
			self.tv.selected_range, 
			datestamp)

	def open_link(self, sender):
				
		file_position = self.tv.selected_range[0] 
		line, line_position = get_full_line(file_position, self.tv)
		link = self._UrtextProjectList.get_link_and_set_project(line, position=line_position)

		if not link:
			if self._UrtextProjectList.current_project.compiled:
				console.hud_alert('Link not in the project.','error',1)
			else:
				console.hud_alert('Project is still compiling.','error',1)
			return None

		if link[0] == 'EDITOR_LINK':
			return self.open_file(link[1])
			
		if link[0] == 'NODE':
			return self.open_node(link[1])
						
		if link[0] == 'HTTP':  
			return webbrowser.open('safari-'+link[1])
			
		if link[0] == 'FILE':
			if not os.path.exists(os.path.join(self._UrtextProjectList.current_project.path, link[1])):
				console.hud_alert(link[1] + ' not found.', 'error',1)
				return
			# This is the best we can do right now in iOS
			console.open_in(os.path.join(self._UrtextProjectList.current_project.path, link[1]))

	def copy_link_to_current_node(self, sender, include_project=False):
		if not self.current_open_file:
			return None
		file_position = self.tv.selected_range[0] 
		node_id = self._UrtextProjectList.current_project.get_node_id_from_position(
				self.current_open_file, 
				file_position)
		link = self._UrtextProjectList.build_contextual_link(
			node_id,
			include_project=include_project)
		clipboard.set(link)
		console.hud_alert(link+ ' copied to the clipboard.','success',2)
	
	def copy_link_to_current_node_with_project(self, sender):
		return self.copy_link_to_current_node(None, include_project=True)

	def open_home(self, sender):
		home_id = self._UrtextProjectList.current_project.get_home()      
		if home_id:
			self._UrtextProjectList.nav_new(home_id)
			self.open_node(home_id)
		else:
			console.hud_alert('No home node for this project','error',0.5)

	def new_inline_node(self, sender, locate_inside=True):
		# metadata={ #'tags': '',
		#          #'from': platform.node()
		#          }
		selection = self.tv.selected_range
		contents = self.tv.text[selection[0]:selection[1]]
		new_inline_node_contents, node_id = self._UrtextProjectList.current_project.add_inline_node(
				date=datetime.datetime.now(),
				trailing_id=True,
				contents=contents)
		self.tv.replace_range(selection, new_inline_node_contents)
		if locate_inside:
			self.tv.selected_range = (selection[0]+3, selection[0]+3)
		return node_id

	def open_node(self, 
			node_id, 
			add_to_nav=True # method can be called without affecting nav
			):

		if node_id not in self._UrtextProjectList.current_project.nodes:
			console.hud_alert('Node '+node_id+' not in current project' ,'error',0.5)
			return

		filename = self._UrtextProjectList.current_project.nodes[node_id].filename
		if os.path.join(self._UrtextProjectList.current_project.path, filename) != self.current_open_file:
			self.open_file(filename)

		position = self._UrtextProjectList.current_project.nodes[node_id].ranges[0][0]	
		self.tv.selected_range = (position, position)
		self.tvo.scrollRangeToVisible(NSRange(position, 1)) 
		
		if add_to_nav:
			self._UrtextProjectList.nav_new(node_id)

	def new_node(self, sender):        
		new_node = self._UrtextProjectList.current_project.new_file_node(
			date=datetime.datetime.now()
			)
		
		self.open_node(new_node['id'])
		self.tv.selected_range = (0,0)
		self.tv.begin_editing()

	def tag_from_other(self, sender):
		position = self.tv.selected_range[0]
		line = self.tv.text[position:position+250]
		link = self._UrtextProjectList.current_project.get_link(line)
		if link and link[0] == 'NODE':
			future = self._UrtextProjectList.current_project.tag_other_node(link[1], 'tags::done;')
			self.executor.submit(self.refresh_open_file_if_modified, future)
			console.hud_alert('Tagged Done','success',0.5)

	def node_list(self, sender):
		if 'zzz' in self._UrtextProjectList.current_project.nodes:
			self.open_node('zzz')
		else:
			console.hud_alert('No zzz node','error',0.5)

	def metadata_list(self, sender):
		if 'zzy' in self._UrtextProjectList.current_project.nodes:
			self.open_node('zzy')

	def meta_autocomplete(self, sender): #works
		
		self.meta_search.delegate = self.meta_autocompleter
		self.meta_dropDown.delegate = self.meta_autocompleter
		self.meta_dropDown.data_source = self.meta_autocompleter		
		self.meta_autocompleter.action = self.meta_autocompleter.optionWasSelected
		self.show_search_and_dropdown(self.meta_search, self.meta_dropDown)

	def search_node_title(self, sender):
		self.title_autocompleter.action = self.title_autocompleter.open_node
		self.show_search_and_dropdown(self.title_search, self.title_dropDown)

	def show_search_and_dropdown(self, search, dropDown):
		search.hidden = False
		search.bring_to_front()
		search.text=''
		dropDown.hidden = False
		dropDown.x = search.x
		dropDown.y = search.y + search.height
		dropDown.width = search.width
		dropDown.row_height = search.height
		search.begin_editing()

	def link_to_node(self, sender):
		self.title_autocompleter.titles = self._UrtextProjectList.titles()
		self.title_autocompleter.action = self.title_autocompleter.link_to_node
		self.show_search_and_dropdown(self.title_search, self.title_dropDown)

	def point_to_node(self, sender):
		self.title_autocompleter.action = self.title_autocompleter.point_to_node
		self.show_search_and_dropdown(self.title_search, self.title_dropDown)

	def nav_back(self, sender):
		last_node = self._UrtextProjectList.nav_reverse()
		if last_node:     
			self.open_node(last_node, add_to_nav=False)

	def nav_forward(self, sender):

		next_node = self._UrtextProjectList.nav_advance()
		if next_node:
			self.open_node(next_node, add_to_nav=False)

	def delete_node(self, sender):
		future = self._UrtextProjectList.current_project.delete_file(self.current_open_file)
		self.current_open_file = None
		self.nav_back(None)
		console.hud_alert('Deleted','success',0.5)
		self.executor.submit(self.refresh_open_file_if_modified, future)
		
	def compact_node(self, sender):
		selection = self.tv.selected_range
		contents = self.tv.text[selection[0]:selection[1]]
		end_of_line = self.find_end_of_line(selection[1])

		insert_text = self._UrtextProjectList.current_project.add_compact_node(contents=contents)           

		self.tv.replace_range((end_of_line,end_of_line), '\n' + insert_text + '\n')
		self.tv.selected_range = (end_of_line + 3, end_of_line + 3)

	def find_end_of_line(self, position):
		contents = self.tv.text
		while contents[position] != '\n':
			position += 1
			if position == len(contents):
				break
		return position


	def show_timeline(self, sender):
		if self.current_open_file:
			self.save(None)
		timeline = self._UrtextProjectList.current_project.build_timeline()
		self.tv.text = timeline
		self.current_open_file = None

	def search_keywords(self, sender):
		self.keyword_autocompleter.hidden = False
		self.keyword_autocompleter.action = self.keyword_autocompleter.optionWasSelected     
		self.show_search_and_dropdown(self.keyword_search, self.keyword_dropDown)

class HistoryView(object):

	def tableview_did_select(self, tableview, section, row):
		state = main_view._UrtextProjectList.current_project.apply_patches(main_view.current_file_history, distance_back=row)
		main_view.updating_history = True
		main_view.tv.text = state
		on_main_thread(syntax.setAttribs, main_view.tv, main_view.tvo)
		main_view.updating_history = False

class TitleAutoCompleter(ui.ListDataSource):
	""" Used for searching Nodes and doing operations on the selected """

	def textfield_did_change(self, textfield):

		main_view.title_dropDown.hidden = False
		main_view.title_dropDown.bring_to_front()
		entry = textfield.text.lower()
		self.titles = main_view._UrtextProjectList.current_project.titles()
		self.titles_keys = main_view._UrtextProjectList.current_project.titles().keys()

		options = sorted(
			self.titles_keys, 
			key=lambda pair: fuzz.ratio(entry, pair), 
			reverse=True)

		self.items = options

		main_view.title_dropDown.height = min(main_view.title_dropDown.row_height * len(options), 5*main_view.title_dropDown.row_height)

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
		main_view.title_dropDown.hidden = True
		main_view.title_search.hidden = True
		self.items = []
		main_view.title_search.text = ''
		
	""" Various functions that can be called from this field """

	def open_node(self, sender):
	
		main_view._UrtextProjectList.set_current_project(self.titles[self.items[self.selected_row]][0])
		main_view.title_search.text = self.items[self.selected_row]    
		node_to_open = self.titles[self.items[self.selected_row]][1]
		main_view.open_node(node_to_open)
		main_view.title_search.end_editing()        

	def link_to_node(self, sender):
		# could be refactored into Urtext library
		main_view.title_search.text = self.items[self.selected_row]
		link = main_view._UrtextProjectList.build_contextual_link(
			self.titles[self.items[self.selected_row]][1],
			project_title=self.titles[self.items[self.selected_row]][0])
		main_view.tv.replace_range(main_view.tv.selected_range, link)
		main_view.title_search.end_editing()

	def point_to_node(self, sender):
		# could be refactored into Urtext library
		main_view.title_search.text = self.items[self.selected_row]
		link = main_view._UrtextProjectList.build_contextual_link(
			self.titles[self.items[self.selected_row]][1], 
			project_title=self.titles[self.items[self.selected_row]][0],
			pointer=True) 
		main_view.tv.replace_range(main_view.tv.selected_range, link)
		main_view.title_search.end_editing()

class MetaAutoCompleter(ui.ListDataSource):
	""" Used for searching project meta key/value pairs """

	def textfield_did_change(self, textfield):
		
		main_view.meta_dropDown.hidden = False
		main_view.meta_dropDown.bring_to_front()

		entry = textfield.text.lower()
		self.meta_pairs = main_view._UrtextProjectList.get_all_meta_pairs()
		options = sorted(
			self.meta_pairs, 
			key=lambda pair: fuzz.ratio(entry, pair), 
			reverse=True)

		# setting the items property automatically updates the list
		self.items = options

		# size the dropdown for up to five options
		main_view.meta_dropDown.height = min(main_view.meta_dropDown.row_height * len(options), 5*main_view.meta_dropDown.row_height)

	def textfield_did_end_editing(self, textfield):
		
		#done editing, so hide and clear the dropdown
		if main_view.meta_search.text:
			insert = main_view.meta_search.text
			main_view.tv.replace_range(main_view.tv.selected_range, insert+'; ')
		main_view.meta_dropDown.hidden = True
		main_view.meta_search.hidden = True
		main_view.meta_search.text=''
		self.items = []
		
	def optionWasSelected(self, sender):
		main_view.meta_search.text = self.items[self.selected_row]       
		main_view.meta_search.end_editing()
		main_view.tv.begin_editing()


class KeywordAutoCompleter(ui.ListDataSource):
	
	def textfield_did_change(self, textfield):
		
		main_view.keyword_dropDown.hidden = False
		main_view.keyword_dropDown.bring_to_front()
		
		entry = textfield.text.lower()

		self.items = main_view._UrtextProjectList.current_project.keywords.keys()

		# size the dropdown for up to five options
		main_view.keyword_dropDown.height = min(main_view.keyword_dropDown.row_height * len(self.items), 5*main_view.keyword_dropDown.row_height)

	def textfield_did_end_editing(self, textfield):
				
		main_view.keyword_dropDown.hidden = True
		main_view.keyword_dropDown.hidden.text=''
		self.items = []
		
	def optionWasSelected(self, sender):
		keyword_selected = self.items[self.selected_row]
		main_view.keyword_search.text = keyword_selected       
		if len(main_view._UrtextProjectList.current_project.keywords[keyword_selected]) == 1:
			main_view.keyword_search.end_editing()
			main_view.tv.begin_editing()	
			return main_view.open_node(main_view._UrtextProjectList.current_project.keywords[keyword_selected][0])
		else:
			main_view.title_autocompleter.action = self.title_autocompleter.open_node
			main_view.show_search_and_dropdown(main_view.title_search, main_view.title_dropDown)

class SyntaxHighlighter(object):

	def __init__(self, tvo):
		self.last_time = time.time()
		self.tvo = tvo
		self.time = time.time()

	def textview_did_change(self, textview):
		main_view.saved = False
		now = time.time()
		if now - self.time > .5:
			main_view.refresh_file()   
		self.time = time.time()
		
	def check_snapshot():

		now = time.time()
		if now - self.last_time < 10:
			return
		self.last_time = now 
		main_view.take_snapshot()

	def textview_did_change_selection(self, textview):
	# 	""" Hide all popups which clicking in the text editor """
	# 	pass
		
	 	main_view.project_selector.hidden = True
	 	main_view.menu_list.hidden = True
	 	if not main_view.updating_history:
	 		main_view.history_view.hidden = True

def get_full_line(position, tv):
	lines = tv.text.split('\n')
	total_length = 0
	for line in lines:
		total_length += len(line) + 1
		if total_length >= position:
			distance_from_end_of_line = total_length - position
			position_in_line = len(line) - distance_from_end_of_line
			return (line, position_in_line)

def launch_urtext_pythonista(args):

	if 'path' not in args or not args['path']:
		return None

	urtext_project_path = args['path']
	import_project = False
	if 'import' in args and args['import'].lower().strip() == 'true':
		import_project = True

	global app
	global main_view

	#https://forum.omz-software.com/search/set_idle_timer_disabled?in=titlesposts
	#on_main_thread(console.set_idle_timer_disabled)(True)

	print ('Urtext is loading '+urtext_project_path)
	app = AppSingleLaunch("Pythonisa Urtext")
	if not app.is_active():

		first_project = args['first'] if 'first' in args else None
		main_view = MainView(
			urtext_project_path, 
			app, 
			import_project=import_project,
			first_project=first_project)

		app.will_present(main_view)
		main_view.open_home(None)
		main_view.present('fullscreen', hide_title_bar=True)
