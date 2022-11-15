import time

class TextViewDelegate(object):

	def __init__(self, main_view):
		self.last_time = time.time()
		self.time = time.time()
		self.main_view = main_view

	def textview_did_change(self, textview):
		self.main_view.saved = False
		now = time.time()
		if now - self.time > .5:
			self.main_view.refresh_file()   
		self.time = time.time()
		
	def textview_did_change_selection(self, textview):
	# 	""" Hide all popups when clicking in the text editor """

		self.main_view.autoCompleter.hide()
		self.main_view.menu_list.hidden = True
		if not self.main_view.updating_history:
			self.main_view.history_view.hidden = True

	def textview_did_begin_editing(self, textview):
	# 	""" Hide all popups when clicking in the text editor """

		self.main_view.autoCompleter.hide()
		if not self.main_view.updating_history:
			self.main_view.history_view.hidden = True
		if not self.main_view.updating_history:
			self.main_view.history_view.hidden = True
