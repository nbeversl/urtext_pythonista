import ui
from thefuzz import fuzz

class AutoCompleter:
	""" AutoCompleteter Base Class """

	def __init__(self, view_width, view_height):
		self.search = ui.TextField()
		self.search.hidden = True
		self.search.delegate = SearchFieldDelegate()
		self.search.delegate.textfield_did_change = self.textfield_did_change
		self.dropDown = ui.TableView()
		self.dropDown.delegate = SearchFieldDelegate()
		self.dropDown.delegate.tableview_did_select = self.tableview_did_select
		self.dropDown.hidden = True
		self.dropDown.data_source = ui.ListDataSource([])
		self.size_fields(view_width, view_height)

	def textfield_did_change(self, textfield):
		entry = textfield.text
		fuzzy_options = sorted(
			self.items,
			key =lambda option: fuzz.ratio(
				entry.lower(), 
				option.lower()), 
			reverse=True)
		self.dropDown.data_source.items=fuzzy_options[:30]

	def hide(self):		
		self.dropDown.hidden = True
		self.search.hidden = True
		self.reset()

	def reset(self):
		self.search.text=''
		self.items = []

	def tableview_did_select(self, tableview, section, row):
		self.search.text = self.dropDown.data_source.items[row]
		return self.action(self.dropDown.data_source.items[row])
		self.hide()

	def set_items(self, items):
		if isinstance(items, dict):
			self.items = list(items.keys())
		if isinstance(items, list):
			self.items = items
		self.dropDown.data_source.items = self.items[:30]

		#self.dropDown.data_source = ui.ListDataSource(items=self.items)

	def show(self):
		self.search.hidden = False
		self.search.bring_to_front()
		self.search.text=''
		self.dropDown.hidden = False
		self.dropDown.bring_to_front()
		self.dropDown.x = self.search.x
		self.dropDown.y = self.search.y + self.search.height
		self.dropDown.width = self.search.width
		self.dropDown.row_height = self.search.height
		self.search.begin_editing()
		#self.dropDown.height = 35 * len(self.items.keys())

	def set_action(self, action):
		self.action = action

	def size_fields(self, view_width, view_height):
		self.search.height = 40
		self.search.width = view_width * 0.8
		self.search.x = view_width/2 - self.search.width/2
		self.search.y = view_height/3 - self.search.height/2
		self.search.border_width = 1
		#self.dropDown.height = 35 * len(self.items.keys())
		self.dropDown.width = 200
		self.dropDown.x = 50
		self.dropDown.y = 50

class SearchFieldDelegate:
	
	def __init__(self):
		pass