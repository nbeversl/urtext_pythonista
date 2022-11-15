from urtext.project_list import ProjectList
from urtext.project import soft_match_compact_node
import os
import datetime
import time
import ui
import dialogs
import re
import console
import webbrowser
from app_single_launch import AppSingleLaunch
import concurrent.futures
from objc_util import *
import syntax_highlighter
import clipboard
from auto_completer import AutoCompleter
from text_view_delegate import TextViewDelegate

app = None

# Theme
button_border_color = '#e3d9d8'
###

class MainView(ui.View):

	def __init__(self, 
		urtext_project_path,  
		app: AppSingleLaunch,
		initial_project=None):
		
		self.app = app
		self.name = "Pythonista Urtext" 
		self.urtext_project_path = urtext_project_path
		self._UrtextProjectList = ProjectList(
			urtext_project_path, 
			initial_project=initial_project)
		self.initial_project=initial_project
		self.current_open_file = None
		self.current_open_file_hash = None
		self.saved = None
		self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
		self.updating_history = False
		self.refreshing = False

		"""
		Build view components. 
		"""
		button_height = 40
		button_width = 27
		
		w,h = ui.get_screen_size()
		self.height = h
		self.width = w
		self.frame= (0,32,w,h)

		# main text (editor) view
		self.tv = ui.TextView()
		self.tv.frame=(0,32,w,h)
		self.tv.auto_content_inset = True
		self.tv.background_color = '#e5dddc'
			
		# History:
		self.current_file_history = None 
		self.history_stamps = ui.ListDataSource(items=[])
		self.history_view = ui.TableView()
		self.history_view.hidden = True
		# history_viewer = HistoryView()
		# self.history_view.delegate = history_viewer
		# self.history_view.data_source = self.history_stamps


		# Pop Up Urtext Features Menu
		menu_options = ui.ListDataSource(items=[
			'Initialize New Project',  
			'Move file to another project',
			'Reload Projects',
			'Delete Node',
			'Show Project Timeline',          
			'Link >',
			'Point >>',
			'Pop Node',
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

		insert_pipe_button = ui.Button(title='|')
		insert_pipe_button.action = self.insert_pipe

		insert_backtick_button = ui.Button(title='`')
		insert_backtick_button.action = self.insert_backtick

		search_all_projects = ui.Button(title='*')
		search_all_projects.action = self.search_all_projects

		# browse_history_button = ui.Button(title='g')
		# browse_history_button.action = self.browse_history

		copy_link_to_current_node_button = ui.Button(title='c')
		copy_link_to_current_node_button.action = self.copy_link_to_current_node

		copy_link_to_current_node_with_project_button = ui.Button(title='^c')
		copy_link_to_current_node_with_project_button.action = self.copy_link_to_current_node_with_project

		hide_keyboard_button = ui.Button(title='↓')
		hide_keyboard_button.action = self.hide_keyboard

		keywords_button = ui.Button(title='k')
		keywords_button.action=self.search_keywords

		free_associate_button = ui.Button(title='^')
		free_associate_button.action=self.free_associate

		link_to_new_node_button = ui.Button(title='| >')
		link_to_new_node_button.action=self.link_to_new_node

		buttons = [  
			open_link_button,
			search_by_title,
			new_node_button, 
			insert_tag_button,
			back_button,
			forward_button,
			home_button,
			menu_button,
			save_button,
			compact_node_button,            
			timestamp_button,
			manual_timestamp_button,
			new_inline_node_button,
			copy_link_to_current_node_button,
			copy_link_to_current_node_with_project_button,
			switch_project_button,
			tag_from_other_button,
			insert_dynamic_def_button,
			insert_pipe_button,
			insert_backtick_button,
			search_all_projects,
			hide_keyboard_button,
			keywords_button,
			free_associate_button,
			link_to_new_node_button
			]

		button_line = ui.View()
		button_line.name = 'buttonLine'
		button_line.background_color = '#e5dddc'
		# button_line.flex = "HWLR"
	
		"""
		Size the buttons
		"""
		button_x_position = 0
		button_y_position = 10

		for button in buttons:
			button.corner_radius = 4
			if button_x_position >= w :
				button_y_position += 55
				button_x_position = 0
			button.frame = (button_x_position, 
				button_y_position, 
				button_width, 
				button_height)
			button_line.add_subview(button)
			button_x_position += button_width + 3
			button.border_width = 1
			button.border_color = button_border_color
			button.background_color = "#ffffff"

		button_line.height = button_line.height + 5 # add margin

		self.autoCompleter = AutoCompleter(self.width, self.height)
		self.add_subview(self.autoCompleter.search)
		self.add_subview(self.autoCompleter.dropDown)
		self.add_subview(self.tv)
		self.add_subview(button_line)
		self.add_subview(self.menu_list)
		self.add_subview(self.history_view)

		self.tvo = ObjCInstance(self.tv)
		# Set up the button row as input accessory
		btn_ln = ObjCInstance(button_line)
		self.tvo.setInputAccessoryView_(btn_ln)
		self.tv.delegate = TextViewDelegate(self)
		self.tvo.setAllowsEditingTextAttributes_(True)	

	def display_welcome(self, sender):

		welcome_text = "Welcome to Urtext.\n\n"
		if self.initial_project:
			welcome_text += "Loading " + self.initial_project + "\n\n"
			welcome_text += "Home node will display when found, or take any other action first instead." 
		else:
			welcome_text += "No initial project was loaded."
		self.tv.text = welcome_text

	def hide_keyboard(self, sender):
		self.tv.end_editing()

	def search_all_projects(self, sender):
		self.autoCompleter.set_items(items=self._UrtextProjectList.titles())
		self.autoCompleter.set_action(self.open_node)
		self.autoCompleter.show()

	def insert_dynamic_def(self,sender):
		# broken right now
		node_id = self.new_inline_node(None, locate_inside=False)
		position = self.tv.selected_range[0]
		self.tv.replace_range(self.tv.selected_range, '\n\n[[ ID(>' + node_id + ')\n+( ) +( )\n-( ) -( )\n ]]')
		self.tv.selected_range = (position + 12, position + 12)
		
	def insert_pipe(self, sender):
		self.tv.replace_range(self.tv.selected_range, '|')

	def insert_backtick(self, sender):
		self.tv.replace_range(self.tv.selected_range, '`')
	
	def pop_node(self, sender):
		filename = self.current_open_file		
		file_pos = self.tv.selected_range[0] 
		line, col_pos = get_full_line(file_pos, self.tv)
		self.save(None)
		future = self._UrtextProjectList.current_project.run_action('POP_NODE',
			line,
			filename,
			file_pos = file_pos,
			col_pos = col_pos)

		if self._UrtextProjectList.current_project.is_async:
			self.executor.submit(self.refresh_open_file_if_modified, future)
		else:
			self.refresh_open_file_if_modified(future)

	def insert_id(self, sender):
		new_id = self._UrtextProjectList.current_project.next_index()
		self.tv.replace_range(self.tv.selected_range, '@'+new_id)

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
		self._UrtextProjectList = ProjectList(self.urtext_project_path)
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
			3 'Delete Node',
			4 'Link >',
			5 'Point >>',
			6 'Pop Node',
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
			self.delete_node(None)

		if sender.selected_row == 4:
			self.link_to_node(None)

		if sender.selected_row == 5:
			self.point_to_node(None)

		if sender.selected_row == 6:
			self.pop_node(None)

	def show_menu(self, option_list):
		self.menu_list.hidden=False
		self.menu_list.bring_to_front()

	def select_project(self, sender): 

		project_list = ui.ListDataSource(items=self._UrtextProjectList.project_titles()) 
		project_list.action = self.switch_project		
		self.dropDown.data_source = project_list
		self.dropDown.delegate = project_list 
		self.dropDown.height = self.dropDown.height * 8
		self.hide_keyboard(None)
		self.dropDown.hidden=False
		self.dropDown.bring_to_front()

	def switch_project(self, sender):
		selection = sender.selected_row
		self.tv.begin_editing()
		self._UrtextProjectList.set_current_project(self.project_list.items[selection])
		self.dropDown.hidden = True
		node_to_open = self._UrtextProjectList.nav_current()
		if node_to_open:
			return self.open_node(node_to_open)
		console.hud_alert('Project switched, but no navigation position available' ,'success',3)

	def manual_save(self, sender):
		self.save(None)
		console.hud_alert('Saved','success',0.5)

	def save(self, sender):
		if self.saved:
			return
		if self.current_open_file:
			contents = self.tv.text 
			with open(os.path.join(self._UrtextProjectList.current_project.path, self.current_open_file),'w', encoding='utf-8') as d:
				d.write(contents)
			self.current_open_file_hash = hash(contents)
			future = self._UrtextProjectList.current_project.on_modified(self.current_open_file)
			if self._UrtextProjectList.current_project.is_async:
				self.executor.submit(self.refresh_open_file_if_modified, future)
			else:
				self.refresh_open_file_if_modified(future)
			self.saved = True
	
	def refresh_open_file_if_modified(self, filenames):
		if self._UrtextProjectList.current_project.is_async:
			filenames = filenames.result()
		if not isinstance(filenames, list):
			filenames = [filenames]
		self.saved = False
		if self.current_open_file in filenames:
			with open(os.path.join(self._UrtextProjectList.current_project.path, self.current_open_file), encoding="utf-8") as file:
				contents=file.read()
			if hash(contents) == self.current_open_file_hash:
				return False
			self.open_file(self.current_open_file, save_first=False)
			
	def refresh_file(self, text=''):   
		syntax_highlighter.setAttribs(self.tv, self.tvo)
		
	def open_file(self, filename, save_first=True):
		"""
		Receives a basename.
		Path used is always the path of the current project
		"""
		f = os.path.join(self._UrtextProjectList.current_project.path, filename)
		if not os.path.exists(f):
			console.hud_alert('FILE not found. Synced?','error',1)
			return None
		
		if save_first and self.current_open_file != filename:
			self.save(None)

		future = self._UrtextProjectList.visit_file(f)
		with open(f,'r', encoding='utf-8') as d:
			contents=d.read()

		# TODO: Might cause ObjC crash ?
		if filename == self.current_open_file:
			self.tv.scroll_enabled = False
			file_position = self.tv.selected_range[0]
			selected_range = self.tvo.selectedRange()
		
		self.tv.text=contents

		if self._UrtextProjectList.current_project.is_async:
			self.executor.submit(self.refresh_open_file_if_modified, future)
		else:
			self.refresh_open_file_if_modified(future)
		self.refresh_file()

		if filename == self.current_open_file:
			try: 
				self.tvo.scrollRangeToVisible(selected_range)
				self.tv.selected_range = (file_position, file_position)
			except ValueError:
				pass

		self.current_open_file = filename
		self.current_open_file_hash = hash(contents)

		# self.tv.scroll_enabled = True
		return True

	def timestamp(self, sender):

		now = datetime.datetime.now()
		datestamp = self._UrtextProjectList.current_project.timestamp(now)
		self.tv.replace_range(
			self.tv.selected_range, 
			datestamp)

	def open_link(self, sender):
		
		filename = self.current_open_file		
		file_pos = self.tv.selected_range[0] 
		line, col_pos = get_full_line(file_pos, self.tv)
		link = self._UrtextProjectList.get_link_and_set_project(
			line,
			filename, 
			col_pos=col_pos,
			file_pos=file_pos)

		if link == None:
			if self._UrtextProjectList.current_project.compiled:
				console.hud_alert('Link not in the project.','error',1)
			else:
				console.hud_alert('Project is still compiling.','error',1)
			return None

		if link['kind'] == 'EDITOR_LINK':
			return self.open_file(link['link'])
			
		if link['kind'] == 'NODE':
			return self.open_node(link['link'], position=link['dest_position'])
						
		if link['kind'] == 'HTTP':  
			return webbrowser.open('safari-'+link['link'])
			
		if link['kind'] == 'FILE':
			if not os.path.exists(os.path.join(self._UrtextProjectList.current_project.path, link['link'])):
				console.hud_alert(link['link'] + ' not found.', 'error',1)
				return
			# This is the best we can do right now in iOS
			console.open_in(os.path.join(self._UrtextProjectList.current_project.path, link['link']))

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
		if link:
			clipboard.set(link)
			console.hud_alert(link+ ' copied to the clipboard.','success',2)
		else:
			console.hud_alert('No link found here. Trying saving the file first.','error',2)

	
	def copy_link_to_current_node_with_project(self, sender):
		return self.copy_link_to_current_node(None, include_project=True)

	def open_home(self, sender):
		home_id = self._UrtextProjectList.current_project.get_home()      
		if home_id:
			self._UrtextProjectList.nav_new(home_id)
			self.open_node(home_id)
		else:
			if self._UrtextProjectList.current_project.compiled:
				console.hud_alert('No home node for this project','error',0.5)
			else:
				console.hud_alert('Home node will open when found','error',0.5)				
				self.executor.submit(self.open_home_when_found, None)

	def open_home_when_found(self, sender):
		while not self._UrtextProjectList.current_project.get_home():
			if not self._UrtextProjectList.current_project.compiled:
				time.sleep(.5)
				continue
			else:
				console.hud_alert('Project compiled. No home node for this project','error',0.5)
		if not self.current_open_file: # only if another file has not been opened
			self.open_home(None)

	def new_inline_node(self, sender, locate_inside=True):
		selection = self.tv.selected_range
		self.tv.replace_range(selection, '{   }')
		self.tv.selected_range = (selection[0]+1, selection[0]+1)

	def open_node(self, 
			node_id, 
			position=None,
			add_to_nav=True # so method can be called without affecting nav
			):

		if node_id not in self._UrtextProjectList.current_project.nodes:
			if  self._UrtextProjectList.current_project.compiled:
				return console.hud_alert('Node '+node_id+' not in current project' ,'error',0.5)
			else:
				return console.hud_alert('Project is still compiling' ,'error',0.5)
			
		if not position:
			position = self._UrtextProjectList.current_project.nodes[node_id].ranges[0][0]
		else:
			position = int(position)
		
		if add_to_nav:
			self._UrtextProjectList.nav_new(node_id)

		filename = self._UrtextProjectList.current_project.nodes[node_id].filename
		if os.path.join(self._UrtextProjectList.current_project.path, filename) != self.current_open_file:
			self.open_file(filename)
		
		# self.tvo.scrollRangeToVisible(NSRange(position, 1)) 
		self.tv.selected_range = (position, position)
		
	def new_node(self, sender):        
		new_node = self._UrtextProjectList.current_project.new_file_node()
		self.open_file(new_node['filename'])
		self.tv.selected_range = (len(self.tv.text)-1,len(self.tv.text)-1)
		self.tv.begin_editing()

	def tag_from_other(self, sender):
		position = self.tv.selected_range[0]
		line = self.tv.text[position:position+250]
		link = self._UrtextProjectList.current_project.get_link(line)
		if link and link['kind'] == 'NODE':
			future = self._UrtextProjectList.current_project.tag_other_node(link['link'], 'tags::done;')
			if self._UrtextProjectList.current_project.is_async:
				self.executor.submit(self.refresh_open_file_if_modified, future)
			else:
				self.refresh_open_file_if_modified(future)
			console.hud_alert('Tagged Done','success',0.5)

	def meta_autocomplete(self, sender): #works	
		self.autoCompleter.set_items(self._UrtextProjectList.get_all_meta_pairs())
		self.autoCompleter.set_action(self.insert_meta)
		self.autoCompleter.show()	

	def search_node_title(self, sender):
		self.autoCompleter.set_items(self._UrtextProjectList.current_project.titles())
		self.autoCompleter.set_action(self.open_node)
		self.autoCompleter.show()

	def insert_meta(self, text):
		self.tv.replace_range(
			self.tv.selected_range, 
			text + '; ')

	def link_to_node(self, sender):
		self.autoCompleter.set_items(self._UrtextProjectList.current_project.titles())
		self.autoCompleter.set_actino(self.insert_link_to_node)
		self.autoCompleter.show()

	def insert_link_to_node(self, title):
		# could be refactored into Urtext library
		link = main_view._UrtextProjectList.build_contextual_link(title)
		self.tv.replace_range(self.tv.selected_range, link)

	def link_to_new_node(self, title):
		path = self._UrtextProjectList.current_project.path
		new_node = self._UrtextProjectList.current_project.new_file_node()
		self.tv.replace_range(self.tv.selected_range, '| '+ new_node['id'] + '>' )

	def point_to_node(self, title):
		self.autoCompleter.set_items(self._UrtextProjectList.current_project.titles())
		self.autoCompleter.set_action(self.insert_pointer_to_node)
		self.autoCompleter.show()

	def insert_pointer_to_node(self, sender):
		link = main_view._UrtextProjectList.build_contextual_link(
			title,
			pointer=True) 
		self.tv.replace_range(self.tv.selected_range, link)

	def nav_back(self, sender):
		last_node = self._UrtextProjectList.nav_reverse()
		if last_node:
			self.open_node(last_node, add_to_nav=False)

	def nav_forward(self, sender):
		next_node = self._UrtextProjectList.nav_advance()
		if next_node:
			self.open_node(next_node, add_to_nav=False)

	@ui.in_background
	def delete_node(self, sender):
		if console.alert(
			'Delete'
			'',
			'Delete this file node?',
			'Yes'
			) == 1 :
			future = self._UrtextProjectList.current_project.delete_file(self.current_open_file)
			console.hud_alert('Deleted','success',0.5)
			self.current_open_file = None
			self.nav_back(None)
			if self._UrtextProjectList.current_project.is_async:
				self.executor.submit(self.refresh_open_file_if_modified, future)
			else:
				self.refresh_open_file_if_modified(future)
			
	def compact_node(self, sender):
		selection = self.tv.selected_range
		contents = self.tv.text[selection[0]:selection[1]]
		end_of_line = self.find_end_of_line(selection[1])
		line, col_pos = get_full_line(selection[1], self.tv)

		if soft_match_compact_node(line):
			replace = False
			contents = self._UrtextProjectList.current_project.add_compact_node()
		else:
			# If it is not a compact node, make it one and add an ID
			replace = True
			contents = self._UrtextProjectList.current_project.add_compact_node(contents=line)

		if replace:
			self.tv.replace_range( (end_of_line-len(line),end_of_line) ,contents)
		else:
			self.tv.replace_range((end_of_line,end_of_line), '\n' + contents + '\n')
			self.tv.selected_range = (end_of_line + 3, end_of_line + 3)

	def find_end_of_line(self, position):
		contents = self.tv.text
		while contents[position] != '\n':
			position += 1
			if position == len(contents):
				break
		return position

	def search_keywords(self, sender):
		self.autoCompleter.set_items(
			self._UrtextProjectList.current_project.extensions['RAKE_KEYWORDS'].get_keywords())
		self.autoCompleter.set_action(self.select_nodes_from_keywords)     		
		self.autoCompleter.show()

	def select_nodes_from_keywords(self, selected_keyword):
		selections = self._UrtextProjectList.current_project.extensions['RAKE_KEYWORDS'].get_by_keyword(selected_keyword)		
		if len(selections) == 1:
			print('only one chosen')
			print(selections)
			self.tv.begin_editing()
			return self.open_node(selections[0])
		else:
			print('reopening auto completer with')
			print(selections)
			self.autoCompleter.hide()
			self.autoCompleter.set_items(selections)
			self.autoCompleter.set_action(self.open_node)
			self.autoCompleter.show()

	def free_associate(self, sender):
		full_line, col_pos = get_full_line(self.tv.selected_range[0], self.tv)
		self.title_autocompleter.action = self.title_autocompleter.open_node
		titles = {}

		for t in self._UrtextProjectList.current_project.extensions['RAKE_KEYWORDS'].get_assoc_nodes( 
			full_line,
			self.current_open_file,
			self.tv.selected_range[0],
			):
			titles[self._UrtextProjectList.current_project.nodes[t].title] = (self._UrtextProjectList.current_project.title, t)
		self.title_autocompleter.titles = titles
		self.show_search_and_dropdown()

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

	global app

	if 'path' not in args or not args['path']:
		return None

	urtext_project_path = args['path']


	#https://forum.omz-software.com/search/set_idle_timer_disabled?in=titlesposts
	#on_main_thread(console.set_idle_timer_disabled)(True)

	print ('Urtext is loading '+urtext_project_path)
	app = AppSingleLaunch("Pythonisa Urtext")
	if not app.is_active():

		initial_project = args['initial'] if 'initial' in args else None
		main_view = MainView(
			urtext_project_path, 
			app, 
			initial_project=initial_project)

		app.will_present(main_view)
		main_view.present('fullscreen', hide_title_bar=True)
		main_view.display_welcome(None)
		main_view.tv.begin_editing()
