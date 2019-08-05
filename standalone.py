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

def save_and_compile():
    current_file = editor.get_path()
    editor.open_file(current_file) # this triggers a save of the current file
    event_handler.project.parse_file(current_file) # parse and update explicitly
    event_handler.project.update()


'''HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    # https://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only
    conn, addr = s.accept()
    
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            request = data.decode('utf-8').split('\n')[0]
            print(request)
            command = request.replace('GET /?','').split('HTTP')[0].strip().split('=')
            print (command)
            response = 'HTTP/1.0 200 OK
                              Content-Type: text/plain \r\n\r\n
           
            if command[1] == "next_node":
              r = event_handler.project.next_index()
                   
            if command[1] == "home":
              node_id = event_handler.project.settings['home']
              r = event_handler.project.nodes[node_id].filename
            if command[0] == "link":
               r =''
               if command[1] in event_handler.project.nodes:
                r = event_handler.project.nodes[command[1]].filename
               else:
                print('not not here')
                   
            if command[1] == 'timestamp':
                  now = datetime.datetime.now()
                  r = event_handler.project.timestamp(now)
                  
            if command[1] == 'node_list':
                  r= event_handler.project.nodes['zzz'].filename
               
            response += r
            conn.send(response.encode('utf-8'))
            conn.close()'''

def save():
	global _UrtextProject
	contents = s.text    
	if current_open_file:
		with open(os.path.join(_UrtextProject.path, current_open_file),'w', encoding='utf-8') as d:
			d.write(contents)
			d.close()
		_UrtextProject.update() 
	
def open_file(filename):
	global current_open_file	
	if current_open_file:
		save()
	file = os.path.join(_UrtextProject.path, filename)
	with open(file,'r', encoding='utf-8') as d:
		contents=d.read() 
		d.close()
	s.text=contents
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
  
    position = s.selected_range[0]
    line = s.text[position:position+20]
    link = _UrtextProject.get_link(line)
    print('printing linke')
    print(link)
    if link != None:
        del _UrtextProject.navigation[_UrtextProject.nav_index+1:]
        _UrtextProject.navigation.append(link[1])
      
        # increment the index to match
        _UrtextProject.nav_index += 1

        if link[0] == 'NODE':
            print('opening '+link[1])
            open_node(link[1])            

        # HTTP links not yet handled in Pythonista

w,h=ui.get_screen_size()         
v=ui.View()
b=ui.View()
new=ui.Button(title='+', frame=(120,0,160,50))
s=ui.TextView()
open_link_button=ui.Button(title=">>",frame=(0,0,40,50))
home_button=ui.Button(title='HHH',frame=(60,0,80,50))

b.add_subview(open_link_button)
b.add_subview(home_button)

def open_home(sender):
	home_id = _UrtextProject.settings['home']
	open_node(home_id)

def open_node(node_id):
	filename=_UrtextProject.nodes[node_id].filename
	open_file(filename)
	position = _UrtextProject.nodes[node_id].ranges[0][0]
	s.selected_range = (position, position)

home_button.action=open_home
open_link_button.action = open_link
s.keyboard_type=ui.KEYBOARD_URL
v.add_subview(b)
v.add_subview(s)
b.frame=(0,20,w,80)
s.frame=(0,50,w,h-200)
b.add_subview(new)
open_home(None)
v.present(hide_title_bar=True)



def new_node(sender):        
    filename =  _UrtextProject.new_file_node(datetime.datetime.now())
    time.sleep(0.5)
    open_file(filename)
    
new.action =new_node
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

if command == "node_list":
    save_and_compile()
    filename = event_handler.project.nodes['zzz'].filename
    editor.open_file(filename)

if command == "metadata_list":
    save_and_compile()
    filename = event_handler.project.nodes['zzy'].filename
    editor.open_file(filename)


if command == "back":

    # return if there are no saved locations
    if len( event_handler.project.navigation) == 0:
      print('There is no nav history')
      
    # return if the index is already at the beginning
    elif event_handler.project.nav_index == 0:
      print('index is already at the beginning.')

    else:
      # otherwise, move backwards one
      event_handler.project.nav_index -= 1

      # and open this node
      last_node = event_handler.project.navigation[event_handler.project.nav_index]          
      position = event_handler.project.nodes[last_node].ranges[0][0]

      open_node(last_node)

if command == "forward":

    # return if there are no saved locations
    if len( event_handler.project.navigation) == 0:
      print('There is no more nav history')

    # return if the index is already at the end
    elif event_handler.project.nav_index == len(event_handler.project.navigation) - 1:
      print('index is already at the end.')

    else:
      # otherwise move it forward by one
      event_handler.project.nav_index += 1

      # and open this node
      last_node = event_handler.project.navigation[event_handler.project.nav_index]          
      position = event_handler.project.nodes[last_node].ranges[0][0]
      open_node(last_node)

if command == "last":

    # return only if there are no saved locations
    if len( event_handler.project.navigation) == 0: 
      print('There is no more nav history')
      
    else:

      # and open this node
      last_node = event_handler.project.navigation[event_handler.project.nav_index]          
      position = event_handler.project.nodes[last_node].ranges[0][0]
      open_node(last_node)




