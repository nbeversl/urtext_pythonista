from thefuzz import fuzz
from auto_completer import AutoCompleter

class TitleAutoCompleter(AutoCompleter):
	""" Used for searching Nodes and doing operations on the selected """

	# def sort_options(self, entry):

	# 	matches = []
	# 	for title in self.items:
	# 		if entry.lower() == title.lower()[:len(entry)]:
	# 			matches.append(title)

	# 	fuzzy_options = sorted(
	# 		self.items, 
	# 		key=lambda title: fuzz.ratio(entry, title), 
	# 		reverse=True)
	# 	matches.extend(fuzzy_options)
	# 	return matches

		
	""" Various functions that can be called from this field """
	   

	def link_to_node(self, sender):
		# could be refactored into Urtext library
		self.main_view.title_search.text = self.items[self.selected_row]
		link = main_view._UrtextProjectList.build_contextual_link(
			self.titles[self.items[self.selected_row]][1],
			project_title=self.titles[self.items[self.selected_row]][0])
		self.main_view.tv.replace_range(main_view.tv.selected_range, link)
		self.main_view.title_search.end_editing()

	def point_to_node(self, sender):
		# could be refactored into Urtext library
		self.main_view.title_search.text = self.items[self.selected_row]
		link = main_view._UrtextProjectList.build_contextual_link(
			self.titles[self.items[self.selected_row]][1], 
			project_title=self.titles[self.items[self.selected_row]][0],
			pointer=True) 
		self.main_view.tv.replace_range(main_view.tv.selected_range, link)
		self.main_view.title_search.end_editing()

	def textfield_did_end_editing(self, textfield):
		
		#done editing, so hide and clear the dropdown
		if self.main_view.meta_search.text:
			insert = self.main_view.meta_search.text
			self.main_view.tv.replace_range(
				self.main_view.tv.selected_range, 
				insert + '; ')
		self.main_view.meta_dropDown.hidden = True
		self.main_view.meta_search.hidden = True
		self.main_view.meta_search.text=''
		self.items = []
		
	def optionWasSelected(self, sender):
		self.main_view.meta_search.text = self.items[self.selected_row]       
		self.main_view.meta_search.end_editing()
		self.main_view.tv.begin_editing()
