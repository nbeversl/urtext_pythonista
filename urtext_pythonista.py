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
from app_single_launch import AppSingleLaunch
import concurrent.futures
from fuzzywuzzy import fuzz
from objc_util import *
import syntax
import platform

node_id_regex = r'\b[0-9,a-z]{3}\b'
app = None
main_view = None

class AutoCompleter(ui.ListDataSource):
    """ Used for searching Node Names """

    def textfield_did_change(self, textfield):
        
        main_view.dropDown.hidden = False
        main_view.dropDown.bring_to_front()
        
        length = len(textfield.text)
        entry = textfield.text.lower()
        
        self.titles_keys = self.titles.keys()
        options = self.sort_options(entry)

        # setting the items property automatically updates the list
        self.items = options

        # size the dropdown for up to five options
        main_view.dropDown.height = min(main_view.dropDown.row_height * len(options), 5*main_view.dropDown.row_height)

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
        main_view.dropDown.hidden = True
        main_view.search_field.hidden = True
        self.items = []
        main_view.search_field.text = ''

    """ Various functions that can be called from this field """

    def open_node(self, sender):
    
        main_view._UrtextProjectList.set_current_project(self.titles[self.items[self.selected_row]][0])
        main_view.search_field.text = self.items[self.selected_row]    
        main_view.open_node(self.titles[self.items[self.selected_row]][1])
        main_view.search_field.end_editing()        

    def link_to_node(self, sender):
        main_view.search_field.text = self.items[self.selected_row]
        main_view.tv.replace_range(main_view.tv.selected_range, '| >'+self.titles[self.items[self.selected_row]][1])
        main_view.search_field.end_editing()

    def point_to_node(self, sender):
        main_view.search_field.text = self.items[self.selected_row]
        main_view.tv.replace_range(main_view.tv.selected_range, '| >>'+self.titles[self.items[self.selected_row]][1])
        main_view.search_field.end_editing()

class TaggingAutoCompleter(ui.ListDataSource):
    """ Used for searching project tag names """

    def textfield_did_change(self, textfield):
        
        main_view.tag_dropDown.hidden = False
        main_view.tag_dropDown.bring_to_front()
        
        # an arbitrary list of autocomplete options
        length = len(textfield.text)
        entry = textfield.text.lower()
        self.tags = main_view._UrtextProjectList.current_project.tagnames['tags']
        options = [ x for x in self.tags.keys() if len(x) >= length and x[:length].lower() == entry]

        # setting the items property automatically updates the list
        self.items = options

        # size the dropdown for up to five options
        main_view.tag_dropDown.height = min(main_view.tag_dropDown.row_height * len(options), 5*main_view.tag_dropDown.row_height)

    def textfield_did_end_editing(self, textfield):
        #done editing, so hide and clear the dropdown
        if main_view.tag_search_field.text:
            insert = '/-- tags: '+main_view.tag_search_field.text+' --/'
            main_view.tv.replace_range(main_view.tv.selected_range, insert)
        main_view.tag_dropDown.hidden = True
        main_view.tag_search_field.hidden = True
        main_view.tag_search_field.text=''
        self.items = []
        
    def optionWasSelected(self, sender):
        main_view.tag_search_field.text = self.items[self.selected_row]       
        main_view.tag_search_field.end_editing()


class FullTextSearchResults(object):

    def textfield_did_change(self, textfield):
        results = main_view._UrtextProjectList.current_project.search_term(textfield.text)
        main_view.tv.text = results
        on_main_thread(syntax.setAttribs)(main_view.tv, initial=True)

    def textfield_did_end_editing(self, textfield):
        main_view.full_txt_search_field.hidden = True

class SyntaxHighlighter(object):

    def __init__(self):
        self.last_time = time.time()

    def textview_did_change(self, textview):
        """ Re-run syntax highlighting whenever the text content changes"""        
        file_position = textview.selected_range
        syntax.setAttribs(textview)
        if file_position[1] < len(textview.text):         
            textview.selected_range = file_position

        #global browsing_history
        #if browsing_history:
        #    return
        now = time.time()
        if now - self.last_time < 10:
            return
        self.last_time = now 
        main_view.take_snapshot()

    def textview_did_change_selection(self, textview):
        """ Hide all popups which clicking in the text editor """
        main_view.project_selector.hidden = True
        main_view.menu_list.hidden = True
    

class MainView(ui.View):

    def __init__(self, urtext_project_path, app: AppSingleLaunch):
        
        self.app = app
        self.name = "Pythonista Urtext" 
        self.urtext_project_path = urtext_project_path
        self._UrtextProjectList = ProjectList(urtext_project_path)
        self.current_open_file = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        """
        Build view components. 
        """
        button_height = 42
        button_width = 42
        
        w,h = ui.get_screen_size()
        self.height = h
        self.width = w

        # main text (editor) view
        self.tv=ui.TextView()
        self.tv.frame=(0,0,w,h-100)
        
        self.tv.font = ('Helvetica Neue', 40)
        self.tv.auto_content_inset = True
        self.tv.background_color = '#282923'
        self.tv.text_color = 'white'

        viewDelegate = SyntaxHighlighter()
        self.tv.delegate = viewDelegate
        
        self.full_txt_search_field = ui.TextField()
        self.full_txt_search_field.height = 40
        self.full_txt_search_field.width = w*.8
        self.full_txt_search_field.x = w/2 - self.full_txt_search_field.width/2
        self.full_txt_search_field.y = h/3 - self.full_txt_search_field.height/2
        self.full_txt_search_field.border_width = 1
        self.full_txt_search_field.hidden = True
        full_text_search = FullTextSearchResults()
        self.full_txt_search_field.delegate = full_text_search

        self.search_field = ui.TextField()
        self.size_field(self.search_field)
        self.search_field.hidden = True
        
        self.tag_search_field = ui.TextField()
        self.size_field(self.tag_search_field)
        self.tag_search_field.hidden = True
        
        self.dropDown = ui.TableView()
        self.dropDown.hidden = True
        
        # UI List of projects
        self.project_list = ui.ListDataSource(items=[]) 

        self.project_selector = ui.TableView()
        self.project_selector.hidden = False 
        self.project_selector.delegate = self.project_list
        self.project_selector.data_source = self.project_list
        self.size_field(self.project_selector)
        
        # Pop Up Urtext Features Menu
        menu_options = ui.ListDataSource(items=[
            'Initialize New Project',  
            'Move file to another project',
            'Reload Projects',
            'Switch Projects',          
            'Delete Node',
            'Refresh Woosh Index',
            'Show Project Timeline',          
            'Link >',
            'Point >>',
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

        self.title_autocompleter = AutoCompleter(items=[])
        
        self.dropDown.delegate = self.title_autocompleter
        self.dropDown.data_source = self.title_autocompleter
        
        self.search_field.delegate = self.title_autocompleter
        
        self.tag_dropDown = ui.TableView()
        self.tag_dropDown.hidden = True

        self.tag_autocompleter = TaggingAutoCompleter(items=[])
        self.tag_autocompleter.action = self.tag_autocompleter.optionWasSelected
        self.tag_search_field.delegate = self.tag_autocompleter

        self.tag_dropDown.delegate = self.tag_autocompleter
        self.tag_dropDown.data_source = self.tag_autocompleter
        self.tv.width = w
        
        menu_button = ui.Button(title="=")
        menu_button.action = self.show_menu
        
        switch_project_button = ui.Button(title="P")
        switch_project_button.action = self.select_project

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

        manual_timestamp_button = ui.Button(title='<..>')
        manual_timestamp_button.action = self.manual_timestamp

        compact_node_button = ui.Button(title='^')
        compact_node_button.action = self.compact_node

        search_by_title = ui.Button(title='?')
        search_by_title.action = self.search_node_title

        insert_split_button = ui.Button(title='%')
        insert_split_button.action = self.insert_split

        delete_word_button = ui.Button(title='<=')
        delete_word_button.action = self.delete_word

        insert_dynamic_def_button = ui.Button(title='[[')
        insert_dynamic_def_button.action = self.insert_dynamic_def

        insert_id_button = ui.Button(title='id')
        delete_word_button.action = self.insert_id

        insert_pipe_button = ui.Button(title='|')
        insert_pipe_button.action = self.insert_pipe

        insert_backtick_button = ui.Button(title='`')
        insert_backtick_button.action = self.insert_backtick

        search_all_project = ui.Button(title='*')
        search_all_project.action = self.search_all_project

        buttons = [ 
            open_link_button,
            back_button,
            menu_button,
            switch_project_button,
            save_button,
            home_button,
            new_node_button,
            compact_node_button,
            insert_tag_button,
            search_by_title,                   
            single_line_new_inline_node_button,
            forward_button,
            timestamp_button,
            manual_timestamp_button,
            search_button,
            insert_split_button,
            node_list_button,
            new_inline_node_button,
            tag_from_other_button,
            insert_dynamic_def_button,
            metadata_button,
            delete_word_button,
            insert_id_button,
            insert_pipe_button,
            insert_backtick_button,
            search_all_project
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

        self.add_subview(self.full_txt_search_field)
        self.add_subview(self.dropDown)
        self.add_subview(self.search_field)
        self.add_subview(self.tag_dropDown)
        self.add_subview(self.tag_search_field)
        self.add_subview(self.project_selector)
        self.add_subview(self.menu_list)
        
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
        tvo = ObjCInstance(self.tv)
        btn_ln = ObjCInstance(button_line)
        tvo.setInputAccessoryView_(btn_ln)

        # seconds = 10
        # s = sched.scheduler(time.time, time.sleep)
        # s.enter(seconds, 1, self.save_snapshot, argument=(s, seconds))
        # self.executor.submit(s.run)

    def take_snapshot(self):
        if self.current_open_file:
            self._UrtextProjectList.current_project.snapshot_diff(self.current_open_file, self.tv.text)

    def search_all_project(self, sender):
        self.title_autocompleter.action = self.title_autocompleter.open_node
        self.title_autocompleter.titles = self._UrtextProjectList.titles()
        self.show_search_and_dropdown()

    def layout(self):
        w,h = ui.get_screen_size()
        self.height = h
        self.width = w
        self.tv.frame=(0,0,w,h-100)

    def insert_dynamic_def(self,sender):
        node_id = self.new_inline_node(None, locate_inside=False)
        position = self.tv.selected_range[0]
        self.tv.replace_range(self.tv.selected_range, '\n\n[[ ID:' + node_id + '\n\n ]]')
        self.tv.selected_range = (position + 12, position + 12)
        
    def insert_pipe(self, sender):
        self.tv.replace_range(self.tv.selected_range, '|')

    def insert_backtick(self, sender):
        self.tv.replace_range(self.tv.selected_range, '`')

    def insert_id(self, sender):
        new_id = self._UrtextProjectList.current_project.next_index()
        self.tv.replace_range(self.tv.selected_range, '/--id:'+new_id+'--/')

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

    def reload_projects(self, sender):
        self.close()
        self._UrtextProjectList = ProjectList(self.urtext_project_path)
        self.present('fullscreen', hide_title_bar=True)
        self.open_home(None)
        console.hud_alert('Project List Reloaded' ,'success',1)

    def delete_word(self, sender):
        contents = self.tv.text 
        position = self.tv.selected_range[0] 
        distance_back = 1
        selection = contents[position - distance_back:position]
        while len(selection) and selection[0] != ' ' and position - distance_back > 0 :
            distance_back += 1
            selection = contents[position-distance_back:position]
        self.tv.replace_range( (position-distance_back, position),'')
        on_main_thread(syntax.setAttribs)(self.tv)

    def delegate_menu(self, sender):
        self.menu_list.hidden=True
        if sender.selected_row == 0: # Initialize new project
            t=ui.TextField(frame=(0,0,300,75))
            self.add_subview(t)
            def init_new_project(textfield):
                print('textfield changed:', textfield.text )  
                new_project_path = textfield.text
                textfield.hidden=True 
                path = os.path.join(self._UrtextProjectList.base_path, new_project_path)
                self._UrtextProjectList.init_new_project(path)
            t.action=init_new_project
        """
            'Initialize New Project',
            'Move file to another project',
            'Reload Projects',
            'Switch Projects',
            'Delete Node',
            'Show Project Timeline',
            'Link >',
            'Point >>'

        """
        if sender.selected_row == 1:
            self.move_file(None)

        if sender.selected_row == 2:
            self.reload_projects(None)

        if sender.selected_row == 3:
            self.select_project(None)

        if sender.selected_row == 4: 
            self.delete_node(None)

        if sender.selected_row == 5:
            self._UrtextProjectList.current_project.rebuild_search_index()

        if sender.selected_row == 6:
            self.show_timeline(None)

        if sender.selected_row == 7:
            self.link_to_node(None)

        if sender.selected_row == 8:
            self.point_to_node(None)

    
    def show_menu(self, option_list):
        self.menu_list.hidden=False
        self.menu_list.bring_to_front()

    def select_project(self, sender): 
        self.project_list.items = self._UrtextProjectList.project_titles()
        self.project_selector.height = 35*len(self.project_list.items)
        self.project_selector.hidden = False
        self.project_selector.bring_to_front()
        self.project_list.action = self.switch_project

    def switch_project(self, sender):
      
      selection = sender.selected_row
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

        contents = self.tv.text 

        if self.current_open_file:
            with open(os.path.join(self._UrtextProjectList.current_project.path, self.current_open_file),'w', encoding='utf-8') as d:
                d.write(contents)
                d.close()
            future = self._UrtextProjectList.current_project.on_modified(self.current_open_file)
            self.executor.submit(self.refresh_open_file_if_modified, future)

    def refresh_open_file_if_modified(self, future):
        modified_files = future.result()

        if os.path.basename(self.current_open_file) in modified_files:    
            tvo = ObjCInstance(self.tv)
            selected_range = tvo.selectedRange()
            with open(self.current_open_file,'r', encoding='utf-8') as d:
                contents=d.read()
                d.close()
            self.tv.text=contents
            on_main_thread(syntax.setAttribs)(self.tv, initial=True)
            console.hud_alert('Current file was modified, refreshing','success',1) 

            tvo.scrollRangeToVisible(selected_range) 
            self.tv.begin_editing()

    def open_file(self, filename, save_first=True):

        if save_first and self.current_open_file:
            self.save(None)
        file = os.path.join(self._UrtextProjectList.current_project.path, filename)
        with open(file,'r', encoding='utf-8') as d:
            contents=d.read()
            d.close()

        self.tv.text=contents
        self.current_open_file = file
        on_main_thread(syntax.setAttribs)(self.tv, initial=True)
        self.tv.begin_editing()


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
        if link:
            if link[0] == 'NODE':
                self._UrtextProjectList.nav_new(link[1])
                self.open_node(link[1])

    def open_home(self, sender):
        home_id = self._UrtextProjectList.current_project.get_home()      
        if home_id:
            self._UrtextProjectList.nav_new(home_id)
            self.open_node(home_id)
        else:
            console.hud_alert('No home node for this project','error',0.5)

    def new_inline_node(self, sender, locate_inside=True):
        metadata={ 'tags': '',
                   'from': platform.node()}
        selection = self.tv.selected_range
        contents = self.tv.text[selection[0]:selection[1]]
        new_inline_node_contents, node_id = self._UrtextProjectList.current_project.add_inline_node(
                date=datetime.datetime.now(),
                contents=contents,
                metadata=metadata)
        self.tv.replace_range(selection, new_inline_node_contents)
        if locate_inside:
            self.tv.selected_range = (selection[0]+3, selection[0]+3)
        return node_id

    def new_inline_node_single(self, sender):
        metadata={ 'tags': '',
                   'from': platform.node()}
        selection = self.tv.selected_range
        contents = self.tv.text[selection[0]:selection[1]]
        new_inline_node_contents = self._UrtextProjectList.current_project.add_inline_node(
                contents=contents,
                metadata=metadata,
                one_line=True)[0]
        self.tv.replace_range(selection, new_inline_node_contents)
        self.tv.selected_range = (selection[0]+3, selection[0]+3)

    def open_node(self, node_id):
        filename=self._UrtextProjectList.current_project.nodes[node_id].filename
        if os.path.join(self._UrtextProjectList.current_project.path, filename) != self.current_open_file:
            self.open_file(filename)
        position = self._UrtextProjectList.current_project.nodes[node_id].ranges[0][0]
        self.tv.selected_range = (position, position)
        if position:      
          tvo = ObjCInstance(self.tv)
          tvo.scrollRangeToVisible(NSRange(position, 1)) 

    def new_node(self, sender):        
        new_node = self._UrtextProjectList.current_project.new_file_node(
            date=datetime.datetime.now()
            )
        self.open_file(new_node['filename'])
        self._UrtextProjectList.nav_new(new_node['id'],  self._UrtextProjectList.current_project)
        self.tv.selected_range = (0,0)
        self.tv.begin_editing()

    def tag_from_other(self, sender):
        position = self.tv.selected_range[0]
        line = self.tv.text[position:position+250]
        link = self._UrtextProjectList.current_project.get_link(line)
        if link and link[0] == 'NODE':
            future = self._UrtextProjectList.current_project.tag_other_node(link[1], '/-- tags: done --/')
            self.refresh_open_file_if_modified(future)

    def node_list(self, sender):
        if 'zzz' in self._UrtextProjectList.current_project.nodes:
            self.open_node('zzz')
        else:
            console.hud_alert('No zzz node','error',0.5)

    def metadata_list(self, sender):
        if 'zzy' in self._UrtextProjectList.current_project.nodes:
            self.open_node('zzy')

    def search(self, sender):
        self.save(None)
        self.current_open_file = None # scratch view / make sure this view doesn't overwrite another
        self.full_txt_search_field.text = ''
        self.full_txt_search_field.hidden = False
        self.full_txt_search_field.begin_editing()
        self.full_txt_search_field.bring_to_front()

    def show_search_and_dropdown(self):
        self.search_field.hidden = False
        self.search_field.text=''
        self.dropDown.x = self.search_field.x
        self.dropDown.y = self.search_field.y + self.search_field.height
        self.dropDown.width = self.search_field.width
        self.dropDown.row_height = self.search_field.height
        self.search_field.begin_editing()
        self.search_field.bring_to_front()

    def search_node_title(self, sender):
        self.title_autocompleter.action = self.title_autocompleter.open_node
        self.title_autocompleter.titles = self._UrtextProjectList.current_project.titles()
        self.show_search_and_dropdown()

    def link_to_node(self, sender):
        self.title_autocompleter.action = self.title_autocompleter.link_to_node
        self.show_search_and_dropdown()

    def point_to_node(self, sender):
        self.title_autocompleter.action = self.title_autocompleter.point_to_node
        self.show_search_and_dropdown()

    def tag_autocomplete(self, sender):
        self.tag_search_field.hidden = False
        self.tag_search_field.bring_to_front()
        self.tag_search_field.text = ''
        self.tag_dropDown.x = self.tag_search_field.x
        self.tag_dropDown.y = self.tag_search_field.y + self.tag_search_field.height
        self.tag_dropDown.width = self.tag_search_field.width
        self.tag_dropDown.row_height = self.tag_search_field.height
        
        self.tag_search_field.begin_editing() 

    def nav_back(self, sender):

        last_node = self._UrtextProjectList.nav_reverse()
        if last_node:     
            self.open_node(last_node)

    def nav_forward(self, sender):

        next_node = self._UrtextProjectList.nav_advance()
        if next_node:
            self.open_node(next_node)

    def delete_node(self, sender):
        self._UrtextProjectList.current_project.delete_file(self.current_open_file)
        self.current_open_file = None
        self.nav_back(None)
        console.hud_alert('Deleted','success',0.5)
    
    def take_over(self, sender):
        self._UrtextProjectList.current_project.lock()
        self._UrtextProjectList.current_project.paused = False
        
    def compact_node(self, sender):
        selection = self.tv.selected_range
        contents = self.tv.text[selection[0]:selection[1]]   
        insert_text = self._UrtextProjectList.current_project.add_compact_node(contents=contents)           
        self.tv.replace_range(selection, insert_text)
        offset = len(contents) + 2
        self.tv.selected_range = (selection[0] + offset, selection[0]+offset)

    def hide_keyboard(self,sender):
        self.end_editing()

    def show_timeline(self, sender):
        if self.current_open_file:
            self.save(None)
        nodes = [self._UrtextProjectList.current_project.nodes[node_id] for node_id in self._UrtextProjectList.current_project.nodes]
        timeline = self._UrtextProjectList.current_project.build_timeline(nodes)
        self.tv.text = timeline
        self.current_open_file = None

    def insert_split(self, sender):
        node_id = self._UrtextProjectList.current_project.next_index()
        selection = self.tv.selected_range
        self.tv.replace_range(selection, '/-- id: '+node_id+' --/\n% ')
        
    def refresh_project(self, sender):
        pass

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
    if not args['path']:
        return None
    urtext_project_path = args['path']

    global app
    global main_view
    print ('Urtext is loading '+urtext_project_path)
    app = AppSingleLaunch("Pythonisa Urtext")
    if not app.is_active():
        main_view = MainView(urtext_project_path, app)
        #main_view.flex = 'HR'
        app.will_present(main_view)
        if args['first']:
            main_view._UrtextProjectList.set_current_project(args['first'])            
        main_view.open_home(None)
        main_view.present('fullscreen', hide_title_bar=True)

        # remnant from the watchdog, currently keeps global variables from being cleared.
        # see this thread for other solutions: https://forum.omz-software.com/topic/5440/prevent-duplicate-launch-from-shortcut/8
        while True:
             time.sleep(.1) 

