from urtext.project_list import ProjectList
from urtext.project import match_compact_node
from sublemon.editor import BaseEditor
import os
import time
import ui
import clipboard
import dialogs
import re
import console
import webbrowser
from objc_util import *
from .urtext_syntax import UrtextSyntax

class UrtextEditor(BaseEditor):

	name = "Pythonista Urtext"
	syntax = UrtextSyntax

	def __init__(self, args):
		super().__init__(args)
		self.setup(args)

	def setup(self, args):
		
		self.urtext_project_path = ''
		if 'path' in args:
			self.urtext_project_path = args['path']

		self.initial_project = None
		if 'initial_project' in args:
			self.initial_project = args['initial_project']
		
		editor_methods = {
			'open_file_to_position' : self.open_file_to_position,
			'error_message' : self.error_message,
			'insert_text' : self.insert_text,
			'save_file' : self.urtext_save,
			'set_clipboard' : self.set_clipboard,
			'open_external_file' : self.open_in,
			'open_file_in_editor' : self.open_file,
			'open_http_link' : self.open_http_link,
			'get_buffer' : self.get_buffer,
			'replace' : self.insert_text,
			'insert_at_next_line' : self.insert_at_next_line,
			'popup' : self.popup,
			'write_to_console' : print,
			'set_buffer': self.set_buffer,
			'close_file' : self.close_file,
		}
		self.download_to_local()
		self._UrtextProjectList = ProjectList(
			self.urtext_project_path,
			editor_methods=editor_methods)
		
		self._UrtextProjectList.set_current_project(self.urtext_project_path)
		self.current_open_file = None
		self.saved = None
		self.buttons = {}
		self.updating_history = False
		self.setup_syntax_highlighter()
		self.setup_buttons({
			'/' : self.open_link,
			'?' : self.search_node_title,
			'<' : self.nav_back,
			'>' : self.nav_forward,
			'h' : self.open_home,
			';' : self.new_node,
			'S' : self.manual_save,
			'{' : self.new_inline_node,
			'->': self.tab,
			'::': self.meta_autocomplete,
			'M' : self.main_menu,
			'-' : self.insert_meta_dash,
			'↓' : self.hide_keyboard,
			'#' : self.add_hash_meta,
			't' : self.timestamp,
			'<..>' : self.manual_timestamp,
			'•' : self.compact_node,
			'o' : self.select_project,
			'[' : self.insert_dynamic_def,
			'`' : self.insert_backtick,
			'*' : self.search_all_projects,
			'c' : self.copy_link_to_current_node,
			'^c': self.copy_link_to_current_node_with_project,
			'k' : self.search_keywords,
			'^' : self.free_associate,
			'| >': self.link_to_new_node,
			']]' : self.jump_to_def
			})

		self.setup_autocomplete()

		self.menu_options['Move file to another project'] = self.move_file
		self.menu_options['Reload Projects'] = self.reload_projects
		self.menu_options['Delete Node'] = self.delete_node
		self.menu_options['Link >'] = self.link_to_node
		self.menu_options['Point >>'] = self.point_to_node
		self.menu_options['Pop Node'] = self.pop_node
		self.menu_options['Pull Node'] = self.pull_node

		launch_actions = {
			'new_node' : self.new_node
		}

		if 'launch_action' in args and args['launch_action'] in launch_actions:
			launch_actions[args['launch_action']](None)
		self.show()

	def insert_text(self, text):
		self.tv.replace_range(
			self.tv.selected_range, 
			text)

	def download_to_local(self):
		url = nsurl('file://' + self.urtext_project_path.replace(' ','%20'))
		NSFileManager = ObjCClass('NSFileManager').defaultManager()
		ret = NSFileManager.startDownloadingUbiquitousItemAtURL_error_(
			url, 
			None)

	def get_buffer(self):
		return self.tv.text

	def set_buffer(self, filename, contents):
		if filename == self.current_open_file:
			self.tv.scroll_enabled = False     
			self.tv.text = contents
			self.tv.scroll_enabled = True
			self.saved = False
			self.refresh_syntax_highlighting()
			return True

	def close_file(self, filename):
		if filename == self.current_open_file:
			self.tv.text = ''
			self.saved = True
			return True

	def open_in(self, filename):
		console.open_in(filename)

	def popup(self, message):
		console.hud_alert(message, 'info', 2)

	def set_clipboard(self, text):
		clipboard.set(text)
		console.hud_alert(text + ' copy to the clipboard', 'info', 2)
		self.refresh_syntax_highlighting() # necessary for some reason

	def insert_at_next_line(self, contents):
		pass #future

	def hide_keyboard(self, sender):
		self.tv.end_editing()

	def search_all_projects(self, sender):
		self.autoCompleter.set_items(items=self._UrtextProjectList.titles())
		self.autoCompleter.set_action(self._UrtextProjectList.current_project.open_node)
		self.autoCompleter.show()

	def main_menu(self, sender):
		self.autoCompleter.set_items(items=self.menu_options)
		self.autoCompleter.set_action(self.run_chosen_option)
		self.autoCompleter.show()

	def run_chosen_option(self, function):
		self.menu_options[function](None)

	def insert_dynamic_def(self, sender):
		position = self.tv.selected_range[0]
		self.tv.replace_range(
			self.tv.selected_range, 
			'\n\n[[ >(|  >)\n+( ) +( )\n-( ) -( )\n ]]')
		self.tv.selected_range = (position + 9, position + 9)

	def insert_backtick(self, sender):
		self.tv.replace_range(self.tv.selected_range, '`')
	
	def pop_node(self, sender):
		file_pos = self.tv.selected_range[0] + 1
		full_line, col_pos = get_full_line(file_pos, self.tv)
		r = self._UrtextProjectList.current_project.extensions[
			'POP_NODE'
			].pop_node(
				full_line,
				self.current_open_file,
				file_pos)

	def pull_node(self, sender):
		file_pos = self.tv.selected_range[0] + 1
		full_line, col_pos = get_full_line(file_pos, self.tv)
		self._UrtextProjectList.current_project.extensions[
                'PULL_NODE'
                ].pull_node(
                    full_line,
                    self.current_open_file,
                    file_pos)

	def tab(self, sender):
		self.tv.replace_range(self.tv.selected_range, '\t')

	def move_file(self, sender):
		self.project_list.items = self._UrtextProjectList.project_titles()
		self.project_list.action = self.execute_move_file
		self.project_selector.height = 35*len(self.project_list.items)
		self.project_selector.hidden = False
		self.project_selector.bring_to_front()

	def add_hash_meta(self, sender):
		hash_values = self._UrtextProjectList.current_project.get_all_values_for_key(
				self._UrtextProjectList.current_project.settings['hash_key'])
		self.autoCompleter.set_items(hash_values)
		self.autoCompleter.set_action(self.insert_hash_meta)
		self.autoCompleter.show()

	def insert_hash_meta(self, value):
		self.tv.replace_range(
			self.tv.selected_range, 
			'#'+value+' ')
		
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
			console.hud_alert('File Moved' ,'success',1)
		else:
			console.hud_alert('Error happened. Check the Urtext console' ,'error',2)

	def error_message(self, message):
		console.hud_alert(message, 'error', 5)
		print(message)

	def reload_projects(self, sender):
		self.close()
		self._UrtextProjectList = ProjectList(self.urtext_project_path)
		self.present('fullscreen', hide_title_bar=True)
		self.open_home(None)
		console.hud_alert('Project List Reloaded' ,'success',1)

	def select_project(self, sender): 
		self.autoCompleter.set_items(self._UrtextProjectList.project_titles())
		self.autoCompleter.set_action(self.switch_project)
		self.autoCompleter.show()

	def switch_project(self, selection):
		self.tv.begin_editing()
		self._UrtextProjectList.set_current_project(selection)

	def manual_save(self, sender):
		self.urtext_save()
		console.hud_alert('Saved','success',0.5)

	def urtext_save(self):
		self.download_to_local()
		if self.save(None, save_as=False, handle_changed_contents=False):
			self._UrtextProjectList.on_modified(
				self.current_open_file)

	def open_http_link(self, link):
		webbrowser.open('safari-'+link)

	def refresh_syntax_highlighting(self, highlight_range=None):
		position = self.tv.selected_range
		self.tv.scroll_enabled= False     
		self.syntax_highlighter.setAttribs(self.tv, self.tvo, highlight_range=highlight_range)
		self.tv.scroll_enabled= True
		try:
			self.tv.selected_range = position
		except ValueError:
			pass
	
	def open_file(
		self, 
		filename, 
		save_first=None):

		if save_first == None:
			save_first = True

		if not os.path.exists(filename):
			console.hud_alert(
				'FILE not found. Synced?',
				'error',
				1)
			return None
		
		if save_first and self.current_open_file != filename:
		 	self.urtext_save()

		contents = self.get_file_contents(filename)
		# prevents issue where the text area is too big
		# for the new contents:k
		self.tv.text=''
		#
		self.tv.text=contents
		self.current_open_file_original_contents = contents
		self.current_open_file = filename
		self.refresh_syntax_highlighting()

	def open_file_to_position(
		self,
		filename, 
		position,
		node_range=[]):

		self.open_file(filename)
		self.tv.selected_range = (position, position)
		self.tvo.scrollRangeToVisible(NSRange(position, 1))
		self.refresh_syntax_highlighting(highlight_range=node_range)
		self.thread_pool.submit(self.delay_unhighlight)

	def delay_unhighlight(self):
		time.sleep(0.25)
		self.refresh_syntax_highlighting()

	def timestamp(self, sender):
		self.tv.replace_range(
			self.tv.selected_range, 
			self._UrtextProjectList.current_project.timestamp(as_string=True))

	def open_link(self, sender):
		file_pos = self.tv.selected_range[0] 
		line, col_pos = get_full_line(file_pos, self.tv)
		self._UrtextProjectList.handle_link(
			line, 
			self.current_open_file, 
			col_pos=col_pos)
		
	def copy_link_to_current_node(self, sender, include_project=False):
		if not self.current_open_file:
			return None
		self._UrtextProjectList.current_project.editor_copy_link_to_node(
            self.get_buffer(),
            self.tv.selected_range[0],
            self.current_open_file)

	def copy_link_to_current_node_with_project(self, sender):
		return self.copy_link_to_current_node(None, include_project=True)

	def open_home(self, sender):
		self._UrtextProjectList.current_project.open_home()
	
	def new_inline_node(self, sender, locate_inside=True):
		selection = self.tv.selected_range
		self.tv.replace_range(selection, '{   }')
		self.tv.selected_range = (selection[0]+2, selection[0]+2)

	def new_node(self, sender):        
		new_node = self._UrtextProjectList.current_project.new_file_node(
			path=self._UrtextProjectList.current_project.entry_path)
		
		self.open_file(new_node['filename'])
		self.tv.selected_range = (new_node['cursor_pos'], new_node['cursor_pos'])
		self.tv.begin_editing()

	def meta_autocomplete(self, sender): #works	
		self.autoCompleter.set_items(
			self._UrtextProjectList.get_all_meta_pairs())
		self.autoCompleter.set_action(self.insert_meta)
		self.autoCompleter.show()

	def search_node_title(self, sender):
		self.autoCompleter.set_items(
			self._UrtextProjectList.current_project.sort_for_node_browser())
		self.autoCompleter.set_action(
			self._UrtextProjectList.current_project.open_node)
		self.autoCompleter.show()
		if not self._UrtextProjectList.current_project.compiled:
			self.thread_pool.submit(self._refresh_node_browser_until_compiled)

	def _refresh_node_browser_until_compiled(self):
		while not self._UrtextProjectList.current_project.compiled:
			time.sleep(1)
			self.autoCompleter.set_items(
				self._UrtextProjectList.current_project.sort_for_node_browser())


	def insert_meta(self, text):
		self.tv.replace_range(
			self.tv.selected_range, 
			text + '; ')

	def link_to_node(self, sender):
		self.autoCompleter.set_items(
			items=self._UrtextProjectList.current_project.sort_for_node_browser())
		self.autoCompleter.set_action(self.insert_link_to_node)
		self.autoCompleter.show()

	def insert_meta_dash(self, sender):
		self.tv.replace_range(
			self.tv.selected_range, 
			' - ')

	def insert_link_to_node(self, title):
		link = self._UrtextProjectList.build_contextual_link(title)
		self.tv.replace_range(self.tv.selected_range, link)

	def insert_pointer_to_node(self, title):
		link = self._UrtextProjectList.build_contextual_link(
			title,
			pointer=True) 
		self.tv.replace_range(self.tv.selected_range, link)

	def link_to_new_node(self, title):
		path = self._UrtextProjectList.current_project.entry_path
		new_node = self._UrtextProjectList.current_project.new_file_node()
		self.tv.replace_range(self.tv.selected_range, '| '+ new_node['id'] + ' >' )

	def point_to_node(self, title):
		self.autoCompleter.set_items(
			items=self._UrtextProjectList.current_project.sort_for_node_browser())
		self.autoCompleter.set_action(self.insert_pointer_to_node)
		self.autoCompleter.show()

	

	def nav_back(self, sender):
		if 'NAVIGATION' in self._UrtextProjectList.extensions:
			self._UrtextProjectList.extensions['NAVIGATION'].reverse()

	def nav_forward(self, sender):
		if 'NAVIGATION' in self._UrtextProjectList.extensions:
			self._UrtextProjectList.extensions['NAVIGATION'].forward()

	@ui.in_background
	def delete_node(self, sender):
		if console.alert(
			'Delete'
			'',
			'Delete this file node?',
			'Yes'
			) == 1:
			self._UrtextProjectList.current_project.delete_file(
				self.current_open_file)

	def compact_node(self, sender):
		selection = self.tv.selected_range
		contents = self.tv.text[selection[0]:selection[1]]
		end_of_line = self.find_end_of_line(selection[1])
		line, col_pos = get_full_line(selection[1], self.tv)

		if match_compact_node(line):
			replace = False
			contents = self._UrtextProjectList.current_project.add_compact_node()
		else:
			# If it is not a compact node, make it one and add an ID
			replace = True
			contents = self._UrtextProjectList.current_project.add_compact_node(
				contents=line)
		if end_of_line:
			if replace:
				self.tv.replace_range( (end_of_line-len(line),end_of_line) ,contents)
			else:
				self.tv.replace_range(
					(end_of_line,end_of_line), '\n' + contents + '\n')
				self.tv.selected_range = (end_of_line + 3, end_of_line + 3)

	def find_end_of_line(self, position):
		contents = self.tv.text
		if contents:
			while ( position < len(contents) - 1) and ( 
				contents[position] != '\n'):
				position += 1
			return position

	def search_keywords(self, sender):
		self.autoCompleter.set_items(
			self._UrtextProjectList.current_project.extensions['RAKE_KEYWORDS'].get_keywords())
		self.autoCompleter.set_action(self.select_nodes_from_keywords)     		
		self.autoCompleter.show()

	def select_nodes_from_keywords(self, selected_keyword):
		selections = self._UrtextProjectList.current_project.extensions['RAKE_KEYWORDS'].get_by_keyword(selected_keyword)		
		if len(selections) == 1:
			self.tv.begin_editing()
			return self._UrtextProjectList.current_project.open_node(
				selections[0])
		else:
			self.autoCompleter.hide()
			self.autoCompleter.set_items(selections)
			self.autoCompleter.set_action(
				self._UrtextProjectList.current_project.open_node)
			self.autoCompleter.show()

	def free_associate(self, sender):
		full_line, col_pos = get_full_line(self.tv.selected_range[0], self.tv)
		titles = {}

		for t in self._UrtextProjectList.current_project.extensions[
			'RAKE_KEYWORDS'
			].get_assoc_nodes( 
				full_line,
				self.current_open_file,
				self.tv.selected_range[0],
				):
				titles[self._UrtextProjectList.current_project.nodes[t].title] = (
					self._UrtextProjectList.current_project.title, t)
		self.autoCompleter.set_items(titles)
		self.autoCompleter.set_action(
			self._UrtextProjectList.current_project.open_node)   
		self.show_search_and_dropdown()

	def jump_to_def(self, sender):
		target_id = self.get_node_id()
		self._UrtextProjectList.current_project.go_to_dynamic_definition(
			target_id)

	def get_node_id(self):
		if self.current_open_file:
			return self._UrtextProjectList.current_project.get_node_id_from_position(
				self.current_open_file, 
				self.tv.selected_range[0])

def get_full_line(position, tv):
	lines = tv.text.split('\n')
	total_length = 0
	for line in lines:
		total_length += len(line) + 1
		if total_length >= position:
			distance_from_end_of_line = total_length - position
			position_in_line = len(line) - distance_from_end_of_line
			return (line, position_in_line)
