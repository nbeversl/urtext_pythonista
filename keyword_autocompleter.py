import ui
from auto_completer import AutoCompleter
from thefuzz import fuzz

class KeywordAutoCompleter(AutoCompleter):

	def textfield_did_change(self, textfield):
		# size the dropdown for up to five options
		self.main_view.keyword_dropDown.height = min(
			main_view.keyword_dropDown.row_height * len(self.items), 
			5*main_view.keyword_dropDown.row_height)

	def process_textfield(self):

		entry = textfield.text.lower()
		options = self.main_view._UrtextProjectList.current_project.extensions['RAKE_KEYWORDS'].get_keywords()

		# speed this up?
		self.items = sorted(
			options, 
			key=lambda pair: fuzz.ratio(entry, pair), 
			reverse=True)

	def textfield_did_end_editing(self, textfield):
				
		self.main_view.keyword_dropDown.hidden = True
		self.main_view.keyword_search.hidden = True
		self.items = []
		
	def optionWasSelected(self, sender):
		keyword_selected = self.items[self.selected_row]
		self.main_view.keyword_search.text = keyword_selected       
		self.main_view.keyword_search.end_editing()

		selections = self.main_view._UrtextProjectList.current_project.extensions['RAKE_KEYWORDS'].get_by_keyword(keyword_selected)

		if len(selections) == 1:
			self.main_view.tv.begin_editing()
			return self.main_view.open_node(selections[0])
		else:
			titles = {}
			for t in selections:
				titles[self.main_view._UrtextProjectList.current_project.nodes[t].title] = (self.main_view._UrtextProjectList.current_project.title, t) 
			self.main_view.title_autocompleter.titles = titles
			self.main_view.title_autocompleter.action = main_view.title_autocompleter.open_node
			self.main_view.show_search_and_dropdown(
				self.main_view.title_search, 
				self.main_view.title_dropDown)
