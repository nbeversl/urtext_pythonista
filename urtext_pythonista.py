from urtext.project_list import ProjectList
from urtext.utils import match_compact_node
from sublemon.editor import BaseEditor
import os
import time
import ui
import clipboard
import re
import console
from objc_util import *
from .urtext_syntax import UrtextSyntax

class UrtextEditor(BaseEditor):

	name = "Pythonista Urtext"
	syntax = UrtextSyntax

	def __init__(self, args):
		super().__init__(args)
		self.setup(args)

	def setup(self, args):
		self._UrtextProjectList = None
		self.current_open_file = None

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
			'save_current' : self.urtext_save,
			'save_file' : self.urtext_save,
			'set_clipboard' : self.set_clipboard,
			'write_to_console' : print,
			'open_external_file' : self.open_in,
			'open_file_in_editor' : self.open_file,
			'get_buffer' : self.get_buffer,
			'set_buffer': self.set_buffer,
			'replace' : self.insert_text,
			'refresh_files' : self.refresh_files,
			'show_panel': self.show_panel, 
			'get_current_filename': self.get_current_filename,
			'get_position': self.get_position,
			'set_position': self.set_position,
			'get_line_and_cursor': self.get_line_and_cursor,
			'popup' : self.popup,
			'close_file' : self.close_file,
			'get_selection' : self.get_selection
			
		}
		self._UrtextProjectList = ProjectList(
			self.urtext_project_path,
			editor_methods=editor_methods)
		
		self._UrtextProjectList.set_current_project(self.urtext_project_path)
		self.saved = None
		self.buttons = {}
		self.updating_history = False
		self.setup_syntax_highlighter()
		self.setup_buttons({
			'/' : self.open_link,
			'?' : self.search_node_title,
			'<' : self.nav_back,
			'>' : self.nav_forward,
			'h' : self.urtext_home,
			';' : self.new_node,
			'S' : self.manual_save,
			'{..}' : self.new_inline_node,
			'->': self.tab,
			'::': self.meta_autocomplete,
			'M' : self.all_selectors,
			'-' : self.insert_meta_dash,
			'↓' : self.hide_keyboard,
			'#' : self.add_hash_meta,
			't' : self.timestamp,
			'<..>' : self.manual_timestamp,
			'•' : self.compact_node,
			'o' : self.select_project,
			'[' : self.insert_dynamic_def,
			'*' : self.search_all_projects,
			'c' : self.copy_link_to_here,
			#'^c': self.copy_link_to_here_with_project,
			# 'k' : self.search_keywords,
			'| >': self.link_to_new_node,
			']]' : self.jump_to_def
			})

		self.setup_autocomplete()

		launch_actions = {
			'new_node' : self.new_node
		}

		if 'launch_action' in args and args['launch_action'] in launch_actions:
			launch_actions[args['launch_action']](None)
		self.show()
				
	def urtext_home(self, sender):
		self._UrtextProjectList.run_selector('urtext_home')
		
	def all_selectors(self, sender):
		self._UrtextProjectList.run_selector('all_selectors')
		
	def timestamp(self, sender):
		self._UrtextProjectList.run_selector('insert_timestamp')	

	def insert_text(self, text):
		self.tv.replace_range(self.tv.selected_range, text)

	def get_buffer(self, filename):
		if filename == self.current_open_file:
			return self.tv.text
	
	def get_current_filename(self):
		return self.current_open_file

	def set_buffer(self, filename, contents):
		if filename == self.current_open_file:
			position = self.tv.selected_range[0]
			self.tv.scroll_enabled = False
			self.tv.text = ''
			self.tv.text = contents
			if position >= len(contents):
				position = len(contents) - 1
			self.tv.selected_range = (position, position)
			self.tv.scroll_enabled = True
			self.saved = False
			self.refresh_syntax_highlighting(initial=True)
			return True

	def get_current_filename(self):
		return self.current_open_file

	def get_selection(self):
		return self.tv.text[self.tv.selected_range]

	def close_file(self, filename):
		if filename == self.current_open_file:
			self.save(None)
			self.tv.text = ''
			self.saved = True
			return True

	def copy_link_to_here(self, sender):
		self._UrtextProjectList.run_selector('copy_link_to_here')

	def open_in(self, filename):
		console.open_in(filename)

	def popup(self, message):
		self.thread_pool.submit(console.hud_alert, message, 'info', 2)

	def set_clipboard(self, text):
		clipboard.set(text)
		console.hud_alert(text + ' copied to the clipboard', 'info', 2)
		self.refresh_syntax_highlighting(initial=True) # necessary for some reason

	def insert_at_next_line(self, contents):
		pass #future

	def hide_keyboard(self, sender):
		self.tv.end_editing()

	def search_all_projects(self, sender):
		self._UrtextProjectList.run_selector('select_project')

	def show_panel(self, selections, callback, on_highlight=None):
		self.autoCompleter.set_items(selections, 'quick_panel')
		self.autoCompleter.set_action(callback)
		self.autoCompleter.show()

	def get_position(self):
		return self.tv.selected_range[0]

	def set_position(self, position):
		self.tv.selected_range = (position, position)

	def get_line_and_cursor(self):
		cursor_pos = self.get_position()
		previous_content = 0
		for line in self.tv.text.split('\n'):
			if previous_content + len(line) > cursor_pos:
				break
			previous_content += len(line)

		full_line, cursor_pos = get_full_line(cursor_pos, self.tv)
		return full_line, previous_content - cursor_pos
		
	def insert_dynamic_def(self, sender):
		position = self.tv.selected_range[0]
		self.tv.replace_range(
			self.tv.selected_range, 
			'\n\n[[ >(|  >)\n+( ) +( )\n-( ) -( )\n ]]')
		self.tv.selected_range = (position + 9, position + 9)

	def tab(self, sender):
		self.tv.replace_range(self.tv.selected_range, '\t')

	def add_hash_meta(self, sender):
		hash_values = self._UrtextProjectList.current_project.get_all_values_for_key(
			self._UrtextProjectList.current_project.get_single_setting('hash_key').text)
		self.autoCompleter.set_items(
			hash_values,
			'hash_values',
			allow_new=True)
		self.autoCompleter.set_action(self.insert_hash_meta)
		self.autoCompleter.show()

	def insert_hash_meta(self, value):
		self.tv.replace_range(
			self.tv.selected_range, 
			'#'+value+' ')
		self.tv.begin_editing()
		
	def manual_timestamp(self, sender):
		self._UrtextProjectList.run_selector('insert_timestamp')

	def error_message(self, message):
		console.hud_alert(message, 'error', 5)
		print(message)

	def select_project(self, sender): 
		self.autoCompleter.set_items(
			self._UrtextProjectList.project_titles(),
			'project_titles')
		self.autoCompleter.set_action(self.switch_project)
		self.autoCompleter.show()
		self.thread_pool.submit(self._refresh_project_browser_until_compiled)

	def _refresh_project_browser_until_compiled(self):
		if False in [p.compiled for p in self._UrtextProjectList.projects]:
			time.sleep(1)
			if self.autoCompleter.showing == 'project_titles':
				self.autoCompleter.set_items(
					self._UrtextProjectList.project_titles(),
					'project_titles')			
			self.thread_pool.submit(self._refresh_project_browser_until_compiled)

	def switch_project(self, selection):
		self.tv.begin_editing()
		self._UrtextProjectList.set_current_project(selection)

	def manual_save(self, sender):
		self.urtext_save(self.current_open_file)
		console.hud_alert('Saved','success',0.5)

	def urtext_save(self, filename):
		if filename == self.current_open_file:
			self.save(None, save_as=False, handle_changed_contents=False)
			if self._UrtextProjectList:
				self._UrtextProjectList.on_modified(self.current_open_file)

	def refresh_files(self, file_list):
		if not isinstance(file_list, list):
			file_list = [file_list]
		for filename in file_list:
			if filename == self.current_open_file:
				self.open_file_to_position(self.current_open_file, character=self.tv.selected_range[0])
				 
	def refresh_syntax_highlighting(self, highlight_range=None, initial=False):
		self.syntax_highlighter.refresh(highlight_range=highlight_range, initial=initial)

	def _open_file(self, filename):

		if not os.path.exists(filename):
			console.hud_alert('FILE not found. Synced?', 'error', 1)
			return None

		if self.current_open_file and self.current_open_file != filename:
			self.urtext_save(self.current_open_file)

		contents = self.get_file_contents(filename)
		self.tv.text=''
		self.tv.text=contents
		self.current_open_file = filename

	def open_file_to_position(self, filename, line=None, character=None, highlight_range=None, new_window=False):

		if filename != self.current_open_file:	
			self._open_file(filename)

		if line:
			pass

		if character:
			if character > 0 and character > len(self.tv.text) - 1:
				character = len(self.tv.text) - 1
		else:
			character = 0
		self.tv.selected_range = (character, character)
		self.tvo.scrollRangeToVisible(NSRange(character, 1))

		self.refresh_syntax_highlighting(highlight_range=highlight_range)
		self.tv.begin_editing()
		self.thread_pool.submit(self.delay_unhighlight)
		self.delay_unhighlight()

	def delay_unhighlight(self):
		time.sleep(0.25)
		self.refresh_syntax_highlighting(initial=True)

	def open_link(self, sender):
		line, cursor = self.get_line_and_cursor()
		self._UrtextProjectList.handle_link(line, self.current_open_file, self.get_position(), col_pos=cursor)
				
	def new_inline_node(self, sender, locate_inside=True):
		selection = self.tv.selected_range
		selected_text = self.tv.text[selection[0]:selection[1]]
		self.tv.replace_range(selection, ''.join([
			'{ ', selected_text,' }']))
		self.tv.selected_range = (selection[0]+2, selection[0]+2)

	def new_node(self, sender):
		self._UrtextProjectList.run_selector('new_file_node')

	def meta_autocomplete(self, sender): 
		self._UrtextProjectList.run_selector('browse_metadata')

	def search_node_title(self, sender):
		self._UrtextProjectList.run_selector('node_browser')

	def _set_node_browser_false_and_open_node(self, node_id):
		self.node_browser_open = False
		self._UrtextProjectList.current_project.open_node(node_id)

	def _refresh_node_browser_until_compiled(self):
		while not self._UrtextProjectList.current_project.compiled:
			time.sleep(1)
			if self.autoCompleter.showing == 'node_browser':
				self.autoCompleter.set_items(
					self._UrtextProjectList.current_project.sort_for_node_browser(),
					'node_browser')

	def insert_meta_dash(self, sender):
		self.tv.replace_range(self.tv.selected_range, ' - ')

	def link_to_new_node(self, sender):
		self._UrtextProjectList.run_selector('insert_link_to_new_node')

	def nav_back(self, sender):
		self._UrtextProjectList.run_selector('nav_back')

	def nav_forward(self, sender):
		self._UrtextProjectList.run_selector('nav_forward')

	@ui.in_background
	def delete_node(self, sender):
		self._UrtextProjectList.current_project.delete_file(
			self.current_open_file)
		self.tv.begin_editing()

	def compact_node(self, sender):
		selection = self.tv.selected_range
		end_of_line = self.find_end_of_line(selection[1])
		line, col_pos = get_full_line(selection[1], self.tv)
		contents = ''
		if match_compact_node(line):
			replace = False
			contents = self._UrtextProjectList.current_project.add_compact_node()
		elif end_of_line == len(self.tv.text):
			replace = False
		else:
			# If it is not a compact node, make it one and add an ID
			replace = True
			contents = self._UrtextProjectList.current_project.add_compact_node(
				contents='\n'+line)
		if end_of_line:
			if replace:
				self.tv.replace_range( 
					(end_of_line-len(line), end_of_line),
					contents)
			else:
				self.tv.replace_range(
					(end_of_line,end_of_line), '\n' + contents + '\n')
				self.tv.selected_range = (
					end_of_line + 1 + len(contents), 
					end_of_line + 1 + len(contents))

	def find_end_of_line(self, position):
		contents = self.tv.text
		if contents:
			while ( position < len(contents) - 1) and ( 
				contents[position] != '\n'):
				position += 1
			return position

	def jump_to_def(self, sender):
		self._UrtextProjectList.run_selector('go_to_frame')

def get_full_line(position, tv):
	lines = tv.text.split('\n')
	total_length = 0
	for line in lines:
		total_length += len(line) + 1
		if total_length >= position:
			distance_from_end_of_line = total_length - position
			position_in_line = len(line) - distance_from_end_of_line
			return (line, position_in_line)
