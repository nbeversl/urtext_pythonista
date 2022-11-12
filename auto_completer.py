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
		self.size_fields(view_width, view_height)

	def textfield_did_change(self, textfield):

		entry = textfield.text.lower()
		matches = []
		for title in self.items.keys():
			if entry.lower() == title.lower()[:len(entry)]:
				matches.append(title)

		fuzzy_options = sorted(
			self.items, 
			key=lambda title: fuzz.ratio(entry, title), 
			reverse=True)

		matches.extend(fuzzy_options)
		self.dropDown.data_source.items= matches[:30]

	def tableview_did_select(self, tableview, section, row):
		self.search.text = self.dropDown.data_source.items[row]   

	def set_items(self, items):
		self.items = items
		self.table_items = items.keys()
		self.dropDown.data_source = ui.ListDataSource(items=self.table_items)

	def show(self):
		self.search.hidden = False
		self.search.bring_to_front()
		self.search.text=''
		self.dropDown.hidden = False
		self.dropDown.bring_to_front()
		
		# self.dropDown.x = self.search.x
		# self.dropDown.y = self.search.y + self.search.height
		# self.dropDown.width = self.search.width
		# self.dropDown.row_height = self.search.height
		self.search.begin_editing()


	def size_fields(self, view_width, view_height):
		self.search.height = 40
		self.search.width = view_width * 0.8
		self.search.x = view_width/2 - self.search.width/2
		self.search.y = view_height/3 - self.search.height/2
		field.border_width = 1


		self.dropDown.height = 35 * 10 #len(self.items.keys())
		self.dropDown.width = 200
		self.dropDown.x = 50
		self.dropDown.y = 50



class SearchFieldDelegate:
	
	def __init__(self):
		pass
		

