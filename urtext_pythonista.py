from urtext.project import UrtextProject
import time
import os
import datetime
import ui
import dialogs
import watchdog
from app_single_launch import AppSingleLaunch


urtext_project_path = '/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/archive'
node_id_regex = r'\b[0-9,a-z]{3}\b'
command = ''

print ('Urtext is loading '+urtext_project_path)

class MainView(ui.View):

	def __init__(self, app: AppSingleLaunch):
		
		self.app = app
		self.name = "Pythonista Urtext"

		self._UrtextProject = UrtextProject(urtext_project_path)
		self.current_open_file = ''

		"""
		Build view components. 
		"""
		button_height = 32
		button_width = 32
		
		w,h = ui.get_screen_size()         

		button_view = ui.View()
		button_view.font='American Typewriter'
		button_view.frame=(0, 20, w, 84)

		self.text_view=ui.TextView()
		self.text_view.frame=(0,84,w,h-84)
		self.text_view.font = ('American Typewriter', 14)

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
		insert_tag_button.action = self.insert_tag

		search_button = ui.Button(title='?')
		search_button.action = self.search

		pick_tag_button = ui.Button(title="t")
		pick_tag_button.action = self.pick_tag

		timestamp_button = ui.Button(title='<>')
		timestamp_button.action = self.timestamp

		buttons = [ 
			open_link_button,
			home_button,
			new_node_button,
			new_inline_node_button,
			single_line_new_inline_node_button,
			back_button,
			forward_button,
			node_list_button,
			metadata_button,
			delete_node_button,
			save_button,
			tag_from_other_button,
			search_button,
			insert_tag_button,
			pick_tag_button,
			timestamp_button
			]

		button_x_position = 0
		button_y_position = 0

		self.add_subview(button_view)
		self.add_subview(self.text_view)

		"""
		Size the buttons
		"""

		for button in buttons:
			button.frame = (button_x_position, 
				button_y_position, 
				button_x_position + button_width, 
				button_y_position + button_height)
			button_view.add_subview(button)
			button_x_position += button_width
			if button_x_position >= w:
				button_x_position = 0
				button_y_position += 32
			button.size_to_fit()
			button.border_width=1
	
	def save(self, sender):
		
		contents = self.text_view.text 
		if self.current_open_file:
			with open(os.path.join(self._UrtextProject.path, self.current_open_file),'w', encoding='utf-8') as d:
				d.write(contents)
				d.close()
			self._UrtextProject.parse_file(self.current_open_file)
			# move this to the watchdog:
			self._UrtextProject.update() 
		
	def open_file(self, filename):
		
		if self.current_open_file:
			self.save(None)
		file = os.path.join(self._UrtextProject.path, filename)
		with open(file,'r', encoding='utf-8') as d:
			contents=d.read() 
			d.close()
		self.text_view.text=contents
		self.current_open_file = file

	def timestamp(self, sender):

		now = datetime.datetime.now()
		datestamp = self._UrtextProject.timestamp(now)
		self.text_view.replace_range(
			self.text_view.selected_range, 
			datestamp)

	def open_link(self, sender):
		
		position = self.text_view.selected_range[0]
		line = self.text_view.text[position:position+250]
		link = self._UrtextProject.get_link(line)
		if link:

			if link[0] == 'NODE':
				print('opening '+link[1])
				self.open_node(link[1])
				self._UrtextProject.nav_new(link[1])
		
				# HTTP links not yet handled in Pythonista

	def open_home(self, sender):
		home_id = self._UrtextProject.settings['home']		
		self._UrtextProject.nav_new(home_id)
		self.open_node(home_id)

	def new_inline_node(self, sender):
		metadata={ 'tags': '',
				   'from': 'iPhone'}
		selection = self.text_view.selected_range
		contents = self.text_view.text[selection[0]:selection[1]]
		new_inline_node_contents = self._UrtextProject.add_inline_node(
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
		time.sleep(0.2)
		position = self._UrtextProject.nodes[node_id].ranges[0][0]
		self.text_view.selected_range = (position, position)
		self._UrtextProject.nav_new(node_id)

		#scroll_view.content_offset = (0, position / w)

	def pick_tag(self, sender):
		tag_list = sorted(self._UrtextProject.tagnames['tags'].keys())
		tag = dialogs.list_dialog(title="tags",
			items=list(tag_list))
		if not tag:
			return
		insert = '/-- tags: '+tag+' --/'
		self.text_view.replace_range(
			self.text_view.selected_range, 
			insert)

	def new_node(self, sender):        
		new_node = self._UrtextProject.new_file_node(
			datetime.datetime.now(),
			metadata={ 'tags': '',
						'from': 'iPhone'}
			)
		self.open_file(new_node['filename'])
		self._UrtextProject.nav_new(new_node['id'])
		self.text_view.selected_range = (0,0)

	def tag_from_other(self, sender):
		position = self.text_view.selected_range[0]
		line = self.text_view.text[position:position+250]
		link = self._UrtextProject.get_link(line)
		if link and link[0] == 'NODE':
			self._UrtextProject.tag_other_node(link[1], 
				'/-- tags: done --/')
			self._UrtextProject.update()
			self.open_file(self.current_open_file)
	
	def insert_tag(self, sender):
		position = self.text_view.selected_range[0]
		insert_text = u'/\u002D\u002D tags:  \u002D\u002D/'

		self.text_view.replace_range(
			self.text_view.selected_range, 
			insert_text)
		self.text_view.selected_range = (position+10, position+10)

	def node_list(self, sender):
	 	self.open_node('zzz')

	def metadata_list(self, sender):
		self.open_node('zzy')

	def search(self, sender):
		string = dialogs.text_dialog()
		results = self._UrtextProject.search(string)
		self.save(None)
		self.text_view.text = results
		self.current_open_file = None # make sure this view doesn't overwrite another

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
		self._UrtextProject.update()
		self.text_view.text=''

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



