import os
import ui
import dialogs
import re
import console
from app_single_launch import AppSingleLaunch
from objc_util import *
import syntax_highlighter
from auto_completer import AutoCompleter
from text_view_delegate import TextViewDelegate

app = None

layout = {
	'button_height' : 40,
	'button_container_height' : 57,
	'button_width' : 27,
	'distance_from_top': 32,
	'button_corner_radius' : 4
}

theme = {
	'button_border_color' : '#e3d9d8',
	'button_line_background_color': '#e5dddc',
	'background_color' : '#e5dddc',
	'button_border_width' : 1,
	'button_background_color' : "#ffffff"
}

welcome_text = "Welcome to the editor.\n\n"

class BaseEditor(ui.View):

	theme = theme
	welcome_text = welcome_text
	layout = layout

	def __init__(self):
		
		self.app = app
		self.name = "Base Editor" 
		self.current_open_file = None
		self.current_open_file_hash = None
		self.saved = None
		self.width, self.height = ui.get_screen_size()
		self.frame = (0, self.layout['distance_from_top'], self.width,self.height)
		self.init_text_view()
		self.setup_obj_instances()

	def setup_buttons(self, buttons):
		if not buttons:
			buttons= {
				'?' : self.search_node_title,
				'S' : self.manual_save,
				'↓' : self.hide_keyboard,
			}
		self._build_button_line(buttons)

	def setup_autocomplete(self):
		self.autoCompleter = AutoCompleter(self.width, self.height)
		self.add_subview(self.autoCompleter.search)
		self.add_subview(self.autoCompleter.dropDown)

	def init_text_view(self):
		self.tv = ui.TextView()
		self.tv.frame=(0, self.layout['distance_from_top'], self.width, self.height)
		self.tv.auto_content_inset = True
		self.tv.background_color = self.theme['background_color']
		self.tv.width = self.width
		self.tv.delegate = TextViewDelegate(self)
		self.add_subview(self.tv)

	def _build_button_line(self, buttons):
		button_x_position = 0
		button_y_position = 10
		button_line = ui.View()
		button_line.name = 'buttonLine'
		button_line.background_color = self.theme['button_line_background_color']

		for button_character in buttons:
			new_button = ui.Button(title=button_character)
			new_button.action = buttons[button_character]

			new_button.corner_radius = self.layout['button_corner_radius']
			if button_x_position >= self.width :
				button_y_position += self.layout['button_container_height']
				button_x_position = 0
			new_button.frame = (button_x_position, 
				button_y_position, 
				self.layout['button_width'], 
				self.layout['button_height'])
			button_line.add_subview(new_button)
			button_x_position += self.layout['button_width'] + 3
			new_button.border_width = self.theme['button_border_width']
			new_button.border_color = self.theme['button_border_color']
			new_button.background_color = self.theme['button_background_color']

		self.button_line = button_line
		self.button_line.height = button_line.height + 5 # add margin
		self.add_subview(self.button_line)
		btn_ln = ObjCInstance(self.button_line)
		self.tvo.setInputAccessoryView_(btn_ln)
		
	def setup_obj_instances(self):
		self.tvo = ObjCInstance(self.tv)
		self.tvo.setAllowsEditingTextAttributes_(True)	

	def display_welcome(self, sender):
		self.tv.text = self.welcome_text
		self.refresh_syntax_highlighting()

	def hide_keyboard(self, sender):
		self.tv.end_editing()

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
			
	def refresh_syntax_highlighting(self, text=''):   
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

		changed_files = self._UrtextProjectList.visit_file(f)
		with open(f,'r', encoding='utf-8') as d:
			contents=d.read()
		self.tv.text=contents
		self.current_open_file = filename
		self.current_open_file_hash = hash(contents)
		return changed_files
