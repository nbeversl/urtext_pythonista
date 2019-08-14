from urtext_standalone.urtext.project import UrtextProject
import sys
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import watchdog
import time
import os
import socket
import json
import datetime
urtext_project_path = '/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/archive'
node_id_regex = r'\b[0-9,a-z]{3}\b'
command = ''
import ui

_UrtextProject = UrtextProject(urtext_project_path)
current_open_file = ''

def save():
	contents = text_view.text 
	if current_open_file:
		with open(os.path.join(_UrtextProject.path, current_open_file),'w', encoding='utf-8') as d:
			d.write(contents)
			d.close()
		_UrtextProject.parse_file(current_open_file)
		_UrtextProject.update() 
	
def open_file(filename):
	global current_open_file	
	if current_open_file:
		save()
	file = os.path.join(_UrtextProject.path, filename)
	with open(file,'r', encoding='utf-8') as d:
		contents=d.read() 
		d.close()
	text_view.text=contents
	current_open_file = file

def timestamp():
    now = datetime.datetime.now()
    datestamp = _UrtextProject.timestamp(now)

if command == 'tag': ##?
    tag = sys.argv[1]
    contents = "/-- tags: " +tag+" --/"
    location = editor.get_selection() 
    editor.replace_text(location[0], location[1], contents)    

def open_link(sender):
  
    position = text_view.selected_range[0]
    line = text_view.text[position:position+20]
    link = _UrtextProject.get_link(line)
    if link != None:
        del _UrtextProject.navigation[_UrtextProject.nav_index+1:]
        _UrtextProject.navigation.append(link[1])
      
        # increment the index to match
        _UrtextProject.nav_index += 1

        if link[0] == 'NODE':
            print('opening '+link[1])
            open_node(link[1])            

        # HTTP links not yet handled in Pythonista



def open_home(sender):
	home_id = _UrtextProject.settings['home']
	open_node(home_id)

def open_node(node_id):
	filename=_UrtextProject.nodes[node_id].filename
	open_file(filename)
	time.sleep(0.5)
	position = _UrtextProject.nodes[node_id].ranges[0][0]
	text_view.selected_range = (position, position+1)
	del _UrtextProject.navigation[_UrtextProject.nav_index+1:]
	_UrtextProject.navigation.append(node_id)
	_UrtextProject.nav_index += 1


def new_node(sender):        
    filename =  _UrtextProject.new_file_node(datetime.datetime.now())
    open_file(filename)
    text_view.selected_range = (0,0)


if command == "home":      
    save_and_compile()
    time.sleep(.75)
    node_id = _UrtextProject.settings['home']
    filename = _UrtextProject.nodes[node_id].filename
    editor.open_file(os.path.join(urtext_project_path, filename))

if command == "tag_from_other":
    text = editor.get_text()
    line = editor.get_line_selection()
    selected_text = text[line[0]:line[1]]
    node_id = re.search('>'+node_id_regex ,selected_text).group(0)[1:]
    filename = event_handler.project.nodes[node_id].filename
    event_handler.project.tag_node(node_id, '/-- tags: done --/')
    event_handler.project.update()
    this_file = editor.get_path()
    editor.open_file(this_file)
    # then reload current file

if command == "search":
    string = dialogs.text_dialog()
    results = event_handler.project.search(string)
    editor.make_new_file('search_results', results)

def node_list(sender):
	 open_node('zzz')

def metadata_list(sender):
    open_node('zzy')

def nav_back(sender):

    # return if there are no saved locations
    if len(_UrtextProject.navigation) == 0:
      print('There is no nav history')
      
    # return if the index is already at the beginning
    elif _UrtextProject.nav_index == 0:
      print('index is already at the beginning.')

    else:
      # otherwise, move backwards one
      _UrtextProject.nav_index -= 1

      # and open this node
      last_node = _UrtextProject.navigation[_UrtextProject.nav_index]          
      position = _UrtextProject.nodes[last_node].ranges[0][0]

      open_node(last_node)

def nav_forward(sender):

    # return if there are no saved locations
    if len( _UrtextProject.navigation) == 0:
      print('There is no more nav history')

    # return if the index is already at the end
    elif _UrtextProject.nav_index == len(_UrtextProject.navigation) - 1:
      print('index is already at the end.')

    else:
      # otherwise move it forward by one
      _UrtextProject.nav_index += 1

      # and open this node
      last_node = _UrtextProject.navigation[_UrtextProject.nav_index]          
      position = _UrtextProject.nodes[last_node].ranges[0][0]
      open_node(last_node)

def delete_node(sender):
	os.remove(os.path.join(_UrtextProject.path, current_open_file))
	_UrtextProject.remove_file(current_open_file)
	_UrtextProject.update()
	text_view.text=''

button_height = 60
button_width = 25

w,h = ui.get_screen_size()         

main_view = ui.View()


button_view = ui.View()
button_view.font='<system>'
button_view.frame=(0, 20, w, button_height)

text_view=ui.TextView()
text_view.frame=(0,button_height,w,h-200)

main_view.add_subview(button_view)
main_view.add_subview(text_view)

forward_button = ui.Button(title=">")
forward_button.action=nav_forward

back_button = ui.Button(title='<')
back_button.action=nav_back

home_button=ui.Button(title='H')
home_button.action=open_home

node_list_button=ui.Button(title='L')
node_list_button.action = node_list

open_link_button=ui.Button(title=">")
open_link_button.action = open_link

new_node_button = ui.Button(title='+')
new_node_button.action = new_node

metadata_button = ui.Button(title='M')
metadata_button.action = metadata_list

delete_node_button = ui.Button(title='X')
delete_node_button.action = delete_node

buttons = [ 
  open_link_button,
  home_button,
  new_node_button,
  back_button,
  forward_button,
  node_list_button,
  metadata_button,
  delete_node_button
  ]

button_position = 0

for button in buttons:
  button.frame = (button_position, 0, button_position + button_width, button_height)
  button_view.add_subview(button)
  button_position += button_width
  button.size_to_fit()
  button.border_width=1

open_home(None)
main_view.present(hide_title_bar=True)



