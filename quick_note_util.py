"""
Create a note quickly with an Urtext timestamp
"""
from urtext_pythonista import MainView

class QuickView(MainView):

	def __init__(self, path):

		self.app = app
        self.name = "Pythonista Urtext" 
        self.urtext_project_path = urtext_project_path
        if compile_project:
            self._UrtextProjectList = ProjectList(urtext_project_path, import_project=import_project)
        self.setup_basics()
        self.setup_fields_and_buttons()
        self.size_and_add_buttons()
        self.consolidate_views()

    def setup_fields_and_buttons(self):
    	pass

    def manual_save(self, sender):
        self.save(None)
        console.hud_alert('Saved','success',0.5)

    def save(self, sender):

        contents = self.tv.text 

        with open(os.path.join(self._UrtextProjectList.current_project.path, self.current_open_file),'w', encoding='utf-8') as d:
            d.write(contents)
            d.close()
        print('saved '+self.current_open_file)
        future = self._UrtextProjectList.current_project.on_modified(self.current_open_file)
        if future:
            self.executor.submit(self.refresh_open_file_if_modified, future)

        self.saved = True


def timestamp(self, date):
    timestamp_format = '<%a., %b. %d, %Y, %I:%M %p>'
    return date.strftime(timestamp_format)


temp_view = QuickView()
temp_view.present('fullscreen', hide_title_bar=True)

    while True:
        time.sleep(1)
        if console.is_in_background() and not main_view.saved:
            print('Focus Lost. Saving current file '+main_view.current_open_file)
            print(datetime.datetime.now())
            main_view.save(None) 